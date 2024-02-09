export function setupNavbar() {
    const buttons = document.querySelectorAll(".navbar-nav .nav-link");

    buttons.forEach((button) => {
        button.addEventListener("click", function () {
            buttons.forEach((otherButton) => {
                otherButton.classList.remove("active");
            });
            this.classList.add("active");
        });
    });
    console.log("Navbar setup complete");
}
