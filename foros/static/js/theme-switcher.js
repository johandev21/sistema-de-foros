function applyTheme(theme) {
  const lightIcons = document.querySelectorAll(".theme-icon-light");
  const darkIcons = document.querySelectorAll(".theme-icon-dark");

  if (theme === "dark") {
    document.documentElement.classList.add("dark");
    lightIcons.forEach((icon) => (icon.style.display = "block"));
    darkIcons.forEach((icon) => (icon.style.display = "none"));
  } else {
    document.documentElement.classList.remove("dark");
    lightIcons.forEach((icon) => (icon.style.display = "none"));
    darkIcons.forEach((icon) => (icon.style.display = "block"));
  }
}

function setTheme(theme) {
  if (theme === "system") {
    localStorage.removeItem("theme");
    initTheme();
  } else {
    localStorage.setItem("theme", theme);
    applyTheme(theme);
  }
}

function initTheme() {
  const savedTheme = localStorage.getItem("theme");

  if (savedTheme) {
    applyTheme(savedTheme);
  } else {
    const prefersDark = window.matchMedia(
      "(prefers-color-scheme: dark)"
    ).matches;
    applyTheme(prefersDark ? "dark" : "light");
  }
}

initTheme();
