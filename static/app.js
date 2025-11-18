document.querySelectorAll(".selector")?.forEach(button => {
    button.addEventListener("click", e => {
        e.target.parentNode.classList.toggle("open");
    });

    button.parentNode.addEventListener("mouseleave", e => {
        e.currentTarget.classList.remove("open");
    });
});

document.getElementById("burger_menu")?.addEventListener("click", e => {
    document.querySelector("nav").classList.toggle("shown");
})

nav_links = document.querySelectorAll("nav ul li a");
nav_links?.forEach(link => {
    link.addEventListener("click", e => {
        document.querySelector("nav ul li a.active")?.classList.remove("active");
        e.target.classList.add("active");
    })
})