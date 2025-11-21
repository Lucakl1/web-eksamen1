function addSelectorButton() {
    document.querySelectorAll(".selector")?.forEach(button => {
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

function auto_show_more_onscroll() {
    document.querySelectorAll(".auto_show_more")?.forEach(button => {
        console.log("hej")
        // TODO make scroll work eventlistenere dont start
        button.addEventListener("scroll", () => {
            console.log(button.getBoundingClientRect().top)
            console.log(screenTop)
            if (button.getBoundingClientRect().top >= screenTop) {
                console.log("HEJ")
            }
        })
    })
}
auto_show_more_onscroll();

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
    auto_show_more_onscroll();
});

const mainContainer = document.querySelector("body");
observer.observe(mainContainer, { childList: true, subtree: true });