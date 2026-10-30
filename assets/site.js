// Copy buttons on code blocks. Keep the control keyboard-visible, announce the
// async result, and copy only the code rather than the control label.
document.querySelectorAll("pre").forEach((pre) => {
  const code = pre.querySelector("code");
  if (!code) return;

  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "copy-btn";
  btn.setAttribute("aria-label", "Copy code");
  btn.textContent = "copy";
  const live = document.createElement("span");
  live.className = "sr-only";
  live.setAttribute("role", "status");
  live.setAttribute("aria-live", "polite");
  pre.appendChild(live);
  code.setAttribute("translate", "no");

  btn.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(code.innerText);
      btn.textContent = "copied";
      btn.setAttribute("aria-label", "Code copied");
      live.textContent = "Code copied to clipboard.";
    } catch {
      btn.textContent = "copy";
      btn.setAttribute("aria-label", "Copy code; clipboard unavailable");
      live.textContent = "Copy failed. Select the code manually.";
    }
    window.setTimeout(() => {
      btn.textContent = "copy";
      btn.setAttribute("aria-label", "Copy code");
    }, 1200);
  });
  pre.appendChild(btn);
});

// Mobile: keep the full sidebar from pushing every article below the fold. On
// narrow screens the navigation starts as a closed disclosure; on desktop it
// stays open and the summary is hidden.
const navDisclosure = document.querySelector(".nav-disclosure");
if (navDisclosure) {
  const narrow = window.matchMedia("(max-width: 900px)");
  const syncNav = () => {
    navDisclosure.open = !narrow.matches;
  };
  syncNav();
  narrow.addEventListener("change", syncNav);
}
