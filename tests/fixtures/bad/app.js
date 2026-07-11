const carousel = document.querySelector(".carousel");
window.addEventListener("wheel", (event) => event.preventDefault(), { passive: false });
const viewport = window.innerWidth;
carousel.style.width = `${viewport}px`;
carousel.append(carousel.cloneNode(true));

function nextSlide() {
  carousel.dataset.slide = String(Number(carousel.dataset.slide || 0) + 1);
}

setInterval(nextSlide, 3000);
