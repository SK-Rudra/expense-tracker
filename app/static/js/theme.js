(() => {
    const storageKey = "expense-tracker-theme";
    const root = document.documentElement;
    const toggle = document.getElementById("theme-toggle");
    const icon = document.getElementById("theme-toggle-icon");
    const text = document.getElementById("theme-toggle-text");

    if (!toggle || !icon || !text) {
        return;
    }

    function applyTheme(theme, savePreference = false) {
        const isDark = theme === "dark";

        root.dataset.theme = isDark ? "dark" : "light";
        root.style.colorScheme = isDark ? "dark" : "light";

        toggle.setAttribute("aria-pressed", String(isDark));
        toggle.setAttribute(
            "aria-label",
            isDark
                ? "Switch to light mode"
                : "Switch to dark mode"
        );

        icon.textContent = isDark ? "☀️" : "🌙";
        text.textContent = isDark ? "Light" : "Dark";

        if (savePreference) {
            localStorage.setItem(
                storageKey,
                isDark ? "dark" : "light"
            );
        }
    }

    applyTheme(root.dataset.theme);

    toggle.addEventListener("click", () => {
        const nextTheme =
            root.dataset.theme === "dark" ? "light" : "dark";

        applyTheme(nextTheme, true);
    });
})();