document.addEventListener('DOMContentLoaded', function () {
    const carousel = document.querySelector('.carousel-wrapper');

    if (!carousel) return;

    const imagesContainer = carousel.querySelector('.post-images');
    const images = imagesContainer.querySelectorAll('.post-image');
    const prevButton = carousel.querySelector('.prev-button');
    const nextButton = carousel.querySelector('.next-button');

    if (images.length <= 1) {
        prevButton.style.display = 'none';
        nextButton.style.display = 'none';
        return; // No need for carousel if there's only one image
    }

    let currentIndex = 0;

    function showImage(index) {
        images.forEach((img, i) => {
            img.style.display = i === index ? 'block' : 'none';
        });
    }

    showImage(currentIndex); // Show the first image initially

    prevButton.addEventListener('click', function () {
        currentIndex = (currentIndex - 1 + images.length) % images.length;
        showImage(currentIndex);
    });

    nextButton.addEventListener('click', function () {
        currentIndex = (currentIndex + 1) % images.length;
        showImage(currentIndex);
    });
});


document.addEventListener('DOMContentLoaded', function() {
    const sizeSelect = document.getElementById('id_size');
    const addToCartButton = document.getElementById('add-to-cart-button');

    if (sizeSelect && addToCartButton) {
        addToCartButton.disabled = true; // Initially disable

        sizeSelect.addEventListener('change', function() {
            if (sizeSelect.value) {
                addToCartButton.disabled = false;
            }
        });
    }
});