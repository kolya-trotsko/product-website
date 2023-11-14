document.addEventListener("DOMContentLoaded", function () {
    const showPopupButton = document.getElementById("show-popup-button");
    const popupContainer = document.getElementById("popup-container");
    const closePopupButton = document.getElementById("close-popup-button");

    if (showPopupButton && popupContainer && closePopupButton) {
        showPopupButton.addEventListener("click", function () {
            popupContainer.style.display = "block";
        });

        closePopupButton.addEventListener("click", function () {
            popupContainer.style.display = "none";
        });
    }

    const cleaningSteps = document.querySelectorAll('.cleaning-step');
    const carousel = document.querySelector('.carousel');
    const images = carousel ? carousel.querySelectorAll('img') : [];
    let currentIndex = 0;
    let autoSwitchInterval;

    function showImage(index) {
        images.forEach(image => image.style.display = 'none');
        images[index].style.display = 'block';
        cleaningSteps.forEach(step => step.classList.remove('active'));
        cleaningSteps[index].classList.add('active');
    }

    function autoSwitch() {
        currentIndex = (currentIndex + 1) % images.length;
        showImage(currentIndex);
    }

    showImage(currentIndex);
    autoSwitchInterval = setInterval(autoSwitch, 2000);

    cleaningSteps.forEach((step, index) => {
        step.addEventListener('mouseenter', () => {
            showImage(index);
            clearInterval(autoSwitchInterval);
        });

        step.addEventListener('mouseleave', () => {
            autoSwitchInterval = setInterval(autoSwitch, 2000);
        });
    });

    let currentReview = 1;

    function showReview(reviewNumber) {
        const reviewElement = document.getElementById(`review${currentReview}`);
        reviewElement && (reviewElement.style.display = 'none');

        const newReviewElement = document.getElementById(`review${reviewNumber}`);
        newReviewElement && (newReviewElement.style.display = 'block');

        currentReview = reviewNumber;
    }

    function prevReview() {
        const prev = currentReview === 1 ? document.querySelectorAll('.customer-review').length : currentReview - 1;
        showReview(prev);
    }

    function nextReview() {
        const next = currentReview === document.querySelectorAll('.customer-review').length ? 1 : currentReview + 1;
        showReview(next);
    }

    showReview(1);

    const prevReviewButton = document.getElementById("prevReviewButton");
    const nextReviewButton = document.getElementById("nextReviewButton");

    prevReviewButton && prevReviewButton.addEventListener("click", prevReview);
    nextReviewButton && nextReviewButton.addEventListener("click", nextReview);

    const faqItems = document.querySelectorAll('.faq-item');

    faqItems.forEach(faqItem => {
        const question = faqItem.querySelector('h3');
        const answer = faqItem.querySelector('p');

        if (question) {
            question.addEventListener('click', () => {
                faqItem.classList.toggle('active');
            });
        }
    });
});
