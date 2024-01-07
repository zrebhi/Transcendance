function setupNavbar() {
    const buttons = document.querySelectorAll(".navbar-nav .nav-link");

    buttons.forEach((button) => {
        button.addEventListener("click", function () {
            buttons.forEach((otherButton) => {
                otherButton.classList.remove("active");
            });
            this.classList.add("active");
        });
    });
}

// Call this function when you load/reload the navbar
setupNavbar();
