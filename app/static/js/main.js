// function setCardHeight() {
//     const card = document.querySelector('#dynamicCard');
//     const screenHeight = window.innerHeight;

//     // Dynamically calculate height and top position
//     const cardHeight = screenHeight * 0.65; // reduce 200px from the screen
//     card.style.height = `${cardHeight}px`; 
//     card.style.minHeight = `${cardHeight}px`;
//     // card.style.top = `calc(${cardHeight})px`; // Center vertically
// }

// Tooltip
const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))

// Toggle dropdown
const dropdownElementList = document.querySelectorAll('.dropdown-toggle')
const dropdownList = [...dropdownElementList].map(dropdownToggleEl => new bootstrap.Dropdown(dropdownToggleEl))

// Toggle toast
const toastDiv = document.getElementById('liveToast');
const flash_message = document.getElementById('flashMesssageDiv')
if (flash_message) {
        if (flash_message.innerText.trim() !== 'false' && flash_message.innerText.trim() !== '') {
        const toastBootstrap = bootstrap.Toast.getOrCreateInstance(toastDiv);
        toastBootstrap.show();
    }
}

// Toggle spinner
function toggleSpinner() {
    const spinner = document.getElementById('loading-spinner');
    spinner.style.display = (spinner.style.display === 'none' || spinner.style.display === '') ? 'block' : 'none';
    }

// Toggle button
    const carousel = document.querySelector("#cardCarousel");
    const radio1 = document.querySelector("#radio-1");
    const radio2 = document.querySelector("#radio-2");
    if (carousel){
        document.querySelectorAll('.tab').forEach((label, index) => {
        label.addEventListener('click', () => {
            // Update the carousel slide using Bootstrap's API
            const carousel = new bootstrap.Carousel('#cardCarousel');
            carousel.to(index);
            });
        });
        // Add event listener for the carousel slide
        if (radio1){
                carousel.addEventListener("slid.bs.carousel", function (event) {
                const activeIndex = [...carousel.querySelectorAll(".carousel-item")].indexOf(
                    carousel.querySelector(".carousel-item.active")
                );

                if (activeIndex === 0) {
                    radio1.checked = true;
                } else if (activeIndex === 1) {
                    radio2.checked = true;
                }
            });
        }            
    }

// Set height on page load and resize
// window.addEventListener('load', setCardHeight);
// window.addEventListener('resize', setCardHeight);