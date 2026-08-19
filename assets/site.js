// Copy buttons on code blocks.
document.querySelectorAll("pre").forEach((pre) => {
  const btn = document.createElement("button");
  btn.className = "copy-btn";
  btn.textContent = "copy";
  btn.addEventListener("click", async () => {
    await navigator.clipboard.writeText(pre.innerText.replace(/^copy\n/, ""));
    btn.textContent = "copied";
    setTimeout(() => (btn.textContent = "copy"), 1200);
  });
  pre.appendChild(btn);
});
