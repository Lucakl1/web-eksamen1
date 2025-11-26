function addSelectorButton() {
    document.querySelectorAll(".selector")?.forEach(button => {
        button.classList.remove("selector");
        button.addEventListener("click", e => {
            e.target.parentNode.classList.toggle("open");
        });
    
        button.parentNode.addEventListener("mouseleave", e => {
            e.currentTarget.classList.remove("open");
        });
    });
}
addSelectorButton();

function previewEditProfileImage() {
    document.getElementById("user_avatar")?.addEventListener("change", function (event) {
        const file = event.target.files[0];

        if (!file) return;

        const img = document.querySelector(".profile_img");
        img.src = URL.createObjectURL(file);
    });
    document.getElementById("user_banner")?.addEventListener("change", function (event) {
        const file = event.target.files[0];

        if (!file) return;

        const img = document.querySelector(".banner_img");
        img.src = URL.createObjectURL(file);
    });
}
previewEditProfileImage();

canClick = true;
window.addEventListener("scroll", () => {
    const button = document.getElementById("auto_show_more");
    if(!button) return
    const buttonTop = button.getBoundingClientRect().top;
    const winHeight = window.innerHeight;
    if (buttonTop <= winHeight && canClick) {
        button.click()
        canClick = false;
    }
    else if (buttonTop > winHeight) {
        canClick = true;
    }
});

document.getElementById("edit_profile")?.addEventListener("click", e => {
    document.querySelector("nav ul li a.active")?.classList.remove("active");
    document.getElementById("profile").classList.add("active");
})

document.getElementById("burger_menu")?.addEventListener("click", () => {
    document.querySelector("nav").classList.toggle("shown");
})

document.querySelectorAll("nav ul li a")?.forEach(link => {
    link.addEventListener("click", e => {
        document.querySelector("nav ul li a.active")?.classList.remove("active");
        e.target.classList.add("active");
    })
})

const observer = new MutationObserver( () => {
    addSelectorButton();
    previewEditProfileImage();
});

const mainContainer = document.querySelector("body");
observer.observe(mainContainer, { childList: true, subtree: true });