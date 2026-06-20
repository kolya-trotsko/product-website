document.addEventListener("DOMContentLoaded", function () {
    const cleaningSteps = document.querySelectorAll('.cleaning-step');
    const carousel = document.querySelector('.carousel');
    const images = carousel ? carousel.querySelectorAll('img') : [];
    let currentIndex = 0;
    let autoSwitchInterval;
    images.forEach(image => {
        image.style.display = '';
    });

    function showImage(index) {
        if (!images.length) {
            return;
        }

        images.forEach(image => image.classList.remove('is-active'));
        images[index] && images[index].classList.add('is-active');

        cleaningSteps.forEach(step => step.classList.remove('active'));
        cleaningSteps[index] && cleaningSteps[index].classList.add('active');
    }

    function autoSwitch() {
        if (!images.length) {
            return;
        }

        currentIndex = (currentIndex + 1) % images.length;
        showImage(currentIndex);
    }

    if (images.length) {
        showImage(currentIndex);
        carousel && carousel.classList.add('is-ready');

        if (images.length > 1) {
            autoSwitchInterval = setInterval(autoSwitch, 2000);
        }
    }

    cleaningSteps.forEach((step, index) => {
        step.addEventListener('mouseenter', () => {
            showImage(index);
            autoSwitchInterval && clearInterval(autoSwitchInterval);
        });

        step.addEventListener('click', () => {
            showImage(index);
            autoSwitchInterval && clearInterval(autoSwitchInterval);
        });

        step.addEventListener('mouseleave', () => {
            if (images.length > 1) {
                autoSwitchInterval = setInterval(autoSwitch, 2000);
            }
        });
    });

    const sliderContainer = document.getElementById('slider-container');
    const reviews = document.querySelectorAll('.customer-review');
    let currentReview = 1;
    reviews.forEach(review => {
        review.style.display = '';
    });

    function showReview(reviewNumber) {
        if (!reviews.length) {
            return;
        }

        reviews.forEach(review => review.classList.remove('is-active'));

        const newReviewElement = document.getElementById(`review${reviewNumber}`);
        if (newReviewElement) {
            newReviewElement.classList.add('is-active');
            currentReview = reviewNumber;
        }
    }

    function prevReview() {
        if (!reviews.length) {
            return;
        }

        const prev = currentReview === 1 ? reviews.length : currentReview - 1;
        showReview(prev);
    }

    function nextReview() {
        if (!reviews.length) {
            return;
        }

        const next = currentReview === reviews.length ? 1 : currentReview + 1;
        showReview(next);
    }

    if (reviews.length) {
        showReview(1);
        sliderContainer && sliderContainer.classList.add('is-ready');
    }

    const prevReviewButton = document.getElementById("prevReviewButton");
    const nextReviewButton = document.getElementById("nextReviewButton");

    if (reviews.length > 1) {
        prevReviewButton && prevReviewButton.addEventListener("click", prevReview);
        nextReviewButton && nextReviewButton.addEventListener("click", nextReview);
    } else {
        prevReviewButton && (prevReviewButton.style.display = 'none');
        nextReviewButton && (nextReviewButton.style.display = 'none');
    }

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
