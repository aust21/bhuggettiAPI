const primaryNav = document.querySelector(".navigation");
const toggleButton = document.querySelector(".toggle");

toggleButton.addEventListener("click", () => {
  const vis = primaryNav.getAttribute("data-visible");
  if (vis === "false") {
    primaryNav.setAttribute("data-visible", "true");
    toggleButton.setAttribute("aria-expanded", "true");
    toggleButton.innerHTML = "Close";
  } else {
    primaryNav.setAttribute("data-visible", "false");
    toggleButton.setAttribute("aria-expanded", "false");
    toggleButton.innerHTML = "Menu";
  }
});
