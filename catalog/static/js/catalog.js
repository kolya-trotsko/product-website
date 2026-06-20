document.addEventListener("DOMContentLoaded", () => {
    const cards = document.querySelectorAll(".conditioner-item");
    const compareForm = document.querySelector(".compare-form");
    const compareButton = document.querySelector(".compare-submit");
    const compareStatus = document.querySelector(".compare-status");
    const compareCheckboxes = document.querySelectorAll('input[name="ids"]');
    const maxCompareItems = 4;

    cards.forEach((card) => {
        card.addEventListener("click", (event) => {
            if (event.target.closest("input, button, label, a, form")) {
                return;
            }

            const href = card.dataset.href;
            if (href) {
                window.location.href = href;
                return;
            }

            console.error("Missing data-href attribute for the clicked element.");
        });
    });

    function selectedCount() {
        return Array.from(compareCheckboxes).filter((checkbox) => checkbox.checked).length;
    }

    function updateCompareState() {
        if (!compareButton || !compareStatus) {
            return;
        }

        const count = selectedCount();
        compareButton.disabled = count < 2;

        if (count === 0) {
            compareStatus.textContent = "Оберіть від 2 до 4 моделей для порівняння";
        } else if (count === 1) {
            compareStatus.textContent = "Оберіть ще одну модель для порівняння";
        } else {
            compareStatus.textContent = `Обрано ${count} з ${maxCompareItems} моделей`;
        }
    }

    compareCheckboxes.forEach((checkbox) => {
        checkbox.addEventListener("change", () => {
            if (selectedCount() > maxCompareItems) {
                checkbox.checked = false;
            }
            updateCompareState();
        });
    });

    if (compareForm) {
        compareForm.addEventListener("submit", (event) => {
            if (selectedCount() < 2) {
                event.preventDefault();
                updateCompareState();
            }
        });
    }

    updateCompareState();
});
