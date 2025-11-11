
async function tweet() {
  // be default it is a GET
  const conn = await fetch ("/tweet")
  const dataFromServer = await conn.text();
  console.log(dataFromServer);

  document.querySelector("#message").innerHTML = dataFromServer
};

async function save () {
  // if other methods (anything but GET) are nedded, use the second argument 
  // use the second argument
  console.log(event) // click
  console.log(event.target) // button
  console.log(event.target.form) // form

  const theForm = event.target.form


  const conn = await fetch("/save", {
    method: "POST",
    body : new FormData(theForm)
  })

  // const dataFromServer = await conn.text()
  const dataFromServer = await conn.json()
  console.log(dataFromServer)
  // document.querySelector("#message").innerHTML = dataFromServer
  document.querySelector("#message").innerHTML = `Hi ${dataFromServer.user_name} ${dataFromServer.user_last_name} ${dataFromServer.user_nick_name}`
}

async function likeTweet () {
  console.log("like tweet")
  const conn = await fetch("/api-like-tweet")
  if (conn.ok) {
    const data = await conn.json()
    document.querySelector("#like_tweet").classList.toggle("hidden")
    document.querySelector("#unlike_tweet").classList.toggle("hidden")
    console.log(data);
  } else {
    console.log("error")
  }
}

async function unlikeTweet () {
  console.log("unlike tweet")
  const conn = await fetch("/api-unlike-tweet")
  if (conn.ok) {
    const data = await conn.json()
     document.querySelector("#like_tweet").classList.toggle("hidden")
    document.querySelector("#unlike_tweet").classList.toggle("hidden")
  } else {
    console.log("error")
  }
}

/*
const burger = document.querySelector(".burger");
const nav = document.querySelector("nav");

burger.addEventListener("click", () => {
  // toggle nav
  nav.classList.toggle("active");

  // toggle icon
  burger.classList.toggle("open");
});
*/