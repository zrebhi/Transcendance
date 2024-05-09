export function setupNavbar() {
    const buttons = document.querySelectorAll(".navbar-nav .nav-link");

    buttons.forEach((button) => {
        button.addEventListener("click", function () {
            if (this.id === "adminButton") return;
            buttons.forEach((otherButton) => {
                otherButton.classList.remove("active");
            });
            this.classList.add("active");
        });
    });
}
