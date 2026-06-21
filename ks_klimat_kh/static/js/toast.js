document.addEventListener("DOMContentLoaded", () => {
    const toasts = document.querySelectorAll("[data-toast]");

    toasts.forEach((toast) => {
        let closeTimer = window.setTimeout(() => hideToast(toast), 5000);
        const closeButton = toast.querySelector(".toast-close");

        if (closeButton) {
            closeButton.addEventListener("click", () => {
                window.clearTimeout(closeTimer);
                hideToast(toast);
            });
        }
    });
});

function hideToast(toast) {
    if (!toast || toast.classList.contains("is-hiding")) {
        return;
    }

    toast.classList.add("is-hiding");
    window.setTimeout(() => toast.remove(), 240);
}
