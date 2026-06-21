document.addEventListener("DOMContentLoaded", () => {
    const showPopupButton = document.getElementById("show-popup-button");
    const extraPopupButtons = document.querySelectorAll("[data-open-order]");
    const popupContainer = document.getElementById("popup-container");
    const closePopupButton = document.getElementById("close-popup-button");

    if (!showPopupButton || !popupContainer || !closePopupButton) {
        return;
    }

    function openPopup() {
        popupContainer.style.display = "flex";
    }

    function closePopup() {
        popupContainer.style.display = "none";
    }

    showPopupButton.addEventListener("click", openPopup);
    extraPopupButtons.forEach((button) => {
        button.addEventListener("click", (event) => {
            event.preventDefault();
            openPopup();
        });
    });
    closePopupButton.addEventListener("click", closePopup);
    popupContainer.addEventListener("click", (event) => {
        if (event.target === popupContainer) {
            closePopup();
        }
    });
    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && popupContainer.style.display === "flex") {
            closePopup();
        }
    });
});
