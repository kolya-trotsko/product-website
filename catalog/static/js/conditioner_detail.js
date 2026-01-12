function setupPopup() {
    const showPopupButton = document.getElementById("show-popup-button");
    const popupContainer = document.getElementById("popup-container");
    const closePopupButton = document.getElementById("close-popup-button");

    if (showPopupButton && popupContainer && closePopupButton) {
        showPopupButton.addEventListener("click", function () {
            popupContainer.style.display = "flex";
        });

        closePopupButton.addEventListener("click", function () {
            popupContainer.style.display = "none";
        });
        clearInterval(checkInterval);
    } else {
        console.warn("One or more elements not found. Retrying...");
    }
}

const checkInterval = setInterval(setupPopup, 300);
