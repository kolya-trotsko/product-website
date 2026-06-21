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
