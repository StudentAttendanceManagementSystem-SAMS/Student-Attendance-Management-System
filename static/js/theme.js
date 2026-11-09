(function () {
  const root = document.documentElement;
  const storageKey = "sams-theme";
  let saved = "light";
  try { saved = localStorage.getItem(storageKey) || "light"; } catch (_) {}
  function apply(theme) {
    root.dataset.theme = theme;
    document.querySelectorAll("[data-theme-label]").forEach(el => el.textContent = theme === "dark" ? "Light mode" : "Dark mode");
    document.querySelectorAll("[data-theme-icon]").forEach(el => el.textContent = theme === "dark" ? "☼" : "◐");
    document.querySelectorAll("[data-theme-toggle]").forEach(el => el.setAttribute("aria-label", theme === "dark" ? "Switch to light mode" : "Switch to dark mode"));
    try { localStorage.setItem(storageKey, theme); } catch (_) {}
  }
  apply(saved === "dark" ? "dark" : "light");
  document.addEventListener("click", event => {
    const toggle = event.target.closest("[data-theme-toggle]");
    if (toggle) apply(root.dataset.theme === "dark" ? "light" : "dark");
    const passwordToggle = event.target.closest("[data-password-toggle]");
    if (passwordToggle) {
      const input = document.getElementById("id_password");
      if (!input) return;
      const reveal = input.type === "password";
      input.type = reveal ? "text" : "password";
      passwordToggle.textContent = reveal ? "Hide" : "Show";
      passwordToggle.setAttribute("aria-label", reveal ? "Hide password" : "Show password");
    }
  });
})();
