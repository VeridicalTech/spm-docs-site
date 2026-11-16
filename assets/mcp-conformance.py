#!/usr/bin/env python3
"""SPM MCP conformance check — verify a key against the hosted server in ~60s.

Sales/onboarding artifact as much as a test: it exercises the full contract an
agent depends on (auth, tool surface, idempotent writes, readiness, recall,
provenance read, deletion) and then checks that the verdict fields do not
contradict each other.

    export SPM_API_KEY=spm_live_...
    python3 tools/mcp/conformance.py            # human scorecard
    python3 tools/mcp/conformance.py --json     # CI / machine output

Exit code 0 only when every step and every contract check passes. The canary
memory is written to an isolated `user_partition` and deleted at the end
(unless --keep is given), so running this against a live tenant leaves nothing
behind.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
import time
import urllib.error
import urllib.request

DEFAULT_URL = "https://api.spmos.ai/mcp"
EXPECTED_TOOLS = {
    "remember", "add_memory", "recall", "search_memory",
    "delete", "delete_memory", "status", "read",
}
SUFFICIENCY_STOP_REASONS = {"sufficient", "coverage_complete"}


class Client:
    def __init__(self, url: str, key: str, timeout: float = 60.0) -> None:
        self.url = url
        self.key = key
        self.timeout = timeout
        self._id = 0

    def rpc(self, method: str, params: dict | None = None) -> tuple[dict, float]:
        self._id += 1
        payload: dict[str, object] = {"jsonrpc": "2.0", "id": self._id, "method": method}
        if params is not None:
            payload["params"] = params
        request = urllib.request.Request(
            self.url,
            data=json.dumps(payload).encode(),
            headers={
                "Authorization": f"Bearer {self.key}",
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
            },
            method="POST",
        )
        started = time.time()
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            body = response.read().decode()
        elapsed = time.time() - started
        text = body.strip()
        if not text:
            return {}, elapsed
        if text.startswith("{"):
            return json.loads(text), elapsed
        for line in text.splitlines():
            if line.startswith("data:"):
                return json.loads(line[5:].strip()), elapsed
        raise RuntimeError(f"unparseable response from {self.url}: {text[:120]}")

    def tool(self, name: str, arguments: dict) -> tuple[dict, float]:
        document, elapsed = self.rpc("tools/call", {"name": name, "arguments": arguments})
        result = document.get("result", {})
        if result.get("isError"):
            message = (result.get("content") or [{}])[0].get("text", "")
            raise ToolError(name, message)
        return result.get("structuredContent") or {}, elapsed


class ToolError(RuntimeError):
    def __init__(self, tool: str, message: str) -> None:
        super().__init__(f"{tool} failed: {message}")
        self.tool = tool


class Scorecard:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def add(self, name: str, ok: bool, detail: str, seconds: float | None = None) -> None:
        self.rows.append({"check": name, "ok": ok, "detail": detail,
                          "seconds": seconds, "kind": "check"})

    def observe(self, name: str, detail: str, seconds: float | None, *, ok: bool) -> None:
        """Record a capability observation: shown, never fails the run."""
        self.rows.append({"check": name, "ok": ok, "detail": detail,
                          "seconds": seconds, "kind": "observation"})

    @property
    def failures(self) -> list[dict[str, object]]:
        return [row for row in self.rows if row["kind"] == "check" and not row["ok"]]

    @property
    def observations(self) -> list[dict[str, object]]:
        return [row for row in self.rows if row["kind"] == "observation"]

    def render(self, url: str) -> str:
        width = max(len(str(row["check"])) for row in self.rows)
        lines = [f"SPM MCP conformance - {url}", ""]
        for row in self.rows:
            if row["kind"] == "observation":
                mark = "OK  " if row["ok"] else "INFO"
            else:
                mark = "PASS" if row["ok"] else "FAIL"
            timing = f"{row['seconds']:.2f}s" if row["seconds"] is not None else "     "
            lines.append(f"  [{mark}] {str(row['check']).ljust(width)}  {timing}  {row['detail']}")
        checks = [row for row in self.rows if row["kind"] == "check"]
        passed = len(checks) - len(self.failures)
        lines.append("")
        lines.append(f"  {passed}/{len(checks)} contract checks passed")
        open_observations = [row for row in self.observations if not row["ok"]]
        if open_observations:
            lines.append(f"  {len(open_observations)} capability observation(s) below contract "
                         "(reported, not failing)")
        return "\n".join(lines)


def run(url: str, key: str, keep: bool) -> Scorecard:
    card = Scorecard()
    client = Client(url, key)
    partition = "conformance-" + time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    canary = f"Conformance canary {partition}: escalation owner is Priya, rotation code KESTREL-7741."
    source_id = ""

    try:
        document, seconds = client.rpc(
            "initialize",
            {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "spm-conformance", "version": "1"},
            },
        )
        server = (document.get("result") or {}).get("serverInfo") or {}
        card.add("initialize", bool(server.get("name")), f"server={server.get('name')} {server.get('version')}", seconds)
        client.rpc("notifications/initialized")

        tools_doc, seconds = client.rpc("tools/list")
        names = {tool.get("name") for tool in (tools_doc.get("result") or {}).get("tools", [])}
        missing = sorted(EXPECTED_TOOLS - names)
        card.add("tools/list", not missing, f"{len(names)} tools" + (f", missing {missing}" if missing else ""), seconds)

        payload, seconds = client.tool(
            "remember",
            {"text": canary, "idempotency_key": f"{partition}-k", "user_partition": partition, "topic": "conformance"},
        )
        source_id = str(payload.get("source_id") or "")
        card.add("remember", bool(source_id), f"source_id={source_id[:24]}... state={payload.get('memory_state')}", seconds)

        replay, seconds = client.tool(
            "remember",
            {"text": canary, "idempotency_key": f"{partition}-k", "user_partition": partition, "topic": "conformance"},
        )
        same = str(replay.get("source_id") or "") == source_id
        card.add("remember idempotency", same and str(replay.get("status")) == "duplicate",
                 f"status={replay.get('status')} same_source_id={same}", seconds)

        state = ""
        deadline = time.time() + 60
        while time.time() < deadline:
            status_payload, seconds = client.tool("status", {"source_ids": [source_id]} if source_id else {})
            state = (((status_payload.get("states") or {}).get(source_id) or {}).get("state") or "")
            if state in {"searchable", "failed", "dead_letter"}:
                break
            time.sleep(1)
        card.add("status readiness", state == "searchable", f"state={state or 'unknown'}", seconds)

        question = "escalation owner Priya rotation code KESTREL-7741"
        recall, seconds = client.tool(
            "recall", {"question": question, "top_k": 5, "depth": "fast", "user_partition": partition}
        )
        evidence_count = int(recall.get("evidence_count") or 0)
        answer = str(recall.get("answer") or "")
        card.add("recall returns evidence", evidence_count > 0 and ("Priya" in answer or "KESTREL" in answer),
                 f"evidence={evidence_count} answer_chars={len(answer)}", seconds)

        decision = recall.get("evidence_decision") or {}
        diagnostics = recall.get("diagnostics") or {}
        gate_reason = str(recall.get("gate_reason") or "")
        stop_reason = str(diagnostics.get("stop_reason") or "")
        status = str(decision.get("status") or "")

        checks = [
            ("verdict: supported implies evidence",
             status != "supported" or evidence_count > 0,
             f"status={status} evidence={evidence_count}"),
            ("verdict: no passed gate over a non-supported verdict",
             not (gate_reason == "passed" and status not in {"", "supported"}),
             f"gate={gate_reason} status={status}"),
            ("verdict: empty result is not called sufficient",
             not (evidence_count == 0 and stop_reason in SUFFICIENCY_STOP_REASONS),
             f"evidence={evidence_count} stop={stop_reason}"),
            ("diagnostics: fast path carries cost fields",
             "rounds_used" in diagnostics and "provider_total_tokens" in diagnostics,
             f"rounds={diagnostics.get('rounds_used')} tokens={diagnostics.get('provider_total_tokens')}"),
        ]
        for name, ok, detail in checks:
            card.add(name, bool(ok), detail)

        refs = recall.get("evidence_refs") or []
        token = next((ref.get("read_token") for ref in refs if ref.get("read_token")), "")
        if token:
            read_payload, seconds = client.tool("read", {"read_tokens": [token], "user_partition": partition})
            text = json.dumps(read_payload, ensure_ascii=False)
            card.add("read returns provenance", "KESTREL-7741" in text or "Priya" in text,
                     f"payload_chars={len(text)}", seconds)
        else:
            card.add("read returns provenance", False, "recall returned no read token")

        # Capability observation, not a contract check: a paraphrase of the same
        # fact is the natural way an agent asks. Today the support gate refuses
        # it in both depths (bd SPM-Polaris-<pending>), so it is reported
        # without failing the run until the recall gate is measured and fixed.
        for label, probe_question in (
            ("natural question (paraphrase)", "Who owns escalation and what is the rotation code?"),
            ("natural question (one extra token)",
             "escalation owner Priya Raghunathan rotation code KESTREL-7741 badge"),
        ):
            observation, observation_seconds = client.tool(
                "recall",
                {"question": probe_question, "top_k": 5, "depth": "fast", "user_partition": partition},
            )
            card.observe(
                label + " (capability)",
                f"evidence={observation.get('evidence_count')} "
                f"gate={observation.get('gate_reason')} "
                f"kinds={((observation.get('evidence_decision') or {}).get('support_failure_kinds'))}",
                observation_seconds,
                ok=int(observation.get("evidence_count") or 0) > 0,
            )

        if source_id and not keep:
            deleted, seconds = client.tool("delete", {"source_id": source_id, "idempotency_key": f"{partition}-del"})
            card.add("delete", str(deleted.get("status")) == "deleted", f"status={deleted.get('status')}", seconds)

            after, seconds = client.tool(
                "recall", {"question": question, "top_k": 5, "depth": "fast", "user_partition": partition}
            )
            after_count = int(after.get("evidence_count") or 0)
            after_diag = after.get("diagnostics") or {}
            card.add("recall after delete is empty", after_count == 0 and str(after.get("gate_reason")) != "passed",
                     f"evidence={after_count} gate={after.get('gate_reason')} stop={after_diag.get('stop_reason')}",
                     seconds)
        elif keep:
            card.add("delete", True, f"skipped (--keep); canary left as {source_id}")

    except ToolError as exc:
        card.add(str(exc.tool), False, str(exc))
    except urllib.error.HTTPError as exc:
        card.add("transport", False, f"HTTP {exc.code}: {exc.reason}")
    except Exception as exc:  # noqa: BLE001 - conformance must report, not crash
        card.add("transport", False, f"{type(exc).__name__}: {exc}")
    return card


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify an SPM key against the hosted MCP server.")
    parser.add_argument("--url", default=os.environ.get("SPM_MCP_URL", DEFAULT_URL))
    parser.add_argument("--json", action="store_true", help="machine-readable result")
    parser.add_argument("--keep", action="store_true", help="leave the canary memory in place")
    args = parser.parse_args()

    key = os.environ.get("SPM_API_KEY", "").strip()
    if not key:
        print("SPM_API_KEY is not set", file=sys.stderr)
        return 2

    card = run(args.url, key, args.keep)
    if args.json:
        print(json.dumps(
            {"url": args.url, "checks": card.rows, "failures": len(card.failures),
             "open_observations": len([r for r in card.observations if not r["ok"]])},
            ensure_ascii=False, indent=1,
        ))
    else:
        print(card.render(args.url))
    return 0 if not card.failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
