document.addEventListener("DOMContentLoaded", () => {
    const mainImage = document.querySelector(".product-main-image img");
    const thumbs = document.querySelectorAll(".product-thumb img");

    if (!mainImage || thumbs.length < 2) {
        return;
    }

    thumbs.forEach((thumb) => {
        thumb.closest(".product-thumb").addEventListener("click", () => {
            mainImage.src = thumb.src;
            mainImage.alt = thumb.alt || mainImage.alt;
            document.querySelectorAll(".product-thumb").forEach((button) => {
                button.classList.remove("is-active");
            });
            thumb.closest(".product-thumb").classList.add("is-active");
        });
    });
});
