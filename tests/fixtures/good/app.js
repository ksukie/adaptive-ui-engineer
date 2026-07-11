document.addEventListener("click", (event) => {
  const button = event.target.closest("[data-disclosure]");
  if (!button) return;
  const details = document.querySelector("#details");
  const expanded = button.getAttribute("aria-expanded") === "true";
  button.setAttribute("aria-expanded", String(!expanded));
  details.hidden = expanded;
});
