document.querySelectorAll(".selector").forEach(button => {
    button.addEventListener("click", e => {
        e.target.parentNode.classList.toggle("open");
    });

    button.parentNode.addEventListener("mouseleave", e => {
        e.currentTarget.classList.remove("open");
    });
});