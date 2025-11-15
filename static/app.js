document.querySelectorAll(".selector")?.forEach(button => {
    button.addEventListener("click", e => {
        e.target.parentNode.classList.toggle("open");
    });

    button.parentNode.addEventListener("mouseleave", e => {
        e.currentTarget.classList.remove("open");
    });
});

document.getElementById("burger_menu")?.addEventListener("click", e => {
    document.querySelector("nav").classList.toggle("shown")
})