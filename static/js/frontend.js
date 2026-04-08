function initBannerSlider() {
  const slides = document.querySelectorAll("#bannerSlider .slide");
  if (!slides.length) return;
  let index = 0;
  setInterval(() => {
    slides[index].classList.remove("active");
    index = (index + 1) % slides.length;
    slides[index].classList.add("active");
  }, 4500);
}

function initContactForm() {
  const form = document.getElementById("contactForm");
  if (!form) return;
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const result = document.getElementById("contactResult");
    const formData = new FormData(form);
    const response = await fetch(form.action, {
      method: "POST",
      body: formData,
      headers: { "X-Requested-With": "XMLHttpRequest" },
    });
    const data = await response.json();
    result.textContent = data.message || "Yuborildi";
    if (data.success) form.reset();
  });
}

function switchProductImage(url) {
  const main = document.getElementById("mainProductImage");
  if (main) main.src = url;
}

function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach((a) => {
    a.addEventListener("click", (e) => {
      const id = a.getAttribute("href");
      if (id.length > 1) {
        const target = document.querySelector(id);
        if (target) {
          e.preventDefault();
          target.scrollIntoView({ behavior: "smooth" });
        }
      }
    });
  });
}

document.addEventListener("DOMContentLoaded", () => {
  initBannerSlider();
  initContactForm();
  initSmoothScroll();
});
