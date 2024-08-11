// 回到首頁
document.querySelector(".title").addEventListener("click", (e) => {
  location.href = "/";
});
// 登出

// 初始化
async function init() {
  //確認登入
  if (localStorage.getItem("user_token")) {
    document.querySelector(".logout").style.display = "block";
    document.querySelector(".user_status").style.display = "none";
    try {
      let response = await fetch("/api/user/profile", {
        method: "GET",
        headers: {
          Authorization: "Bearer " + localStorage.getItem("user_token"),
        },
      });
      const data = await response.json();
      //特殊修改token或是過期的情況
      if (data.error) {
        localStorage.removeItem("user_token");
        location.href = "/";
      } else {
        renderProfile(
          data.name,
          data.photo,
          data.avg_rating,
          data.pocket_No,
          data.comment_No
        );
      }
    } catch (error) {
      console.error("沒抓到/api/user/auth的資料", error);
    }
  }
}
init();

function renderProfile(name, photoURL, avg_rating, pocketCount, commentCount) {
  document.querySelector(".user-name").innerHTML = name;
  document.querySelector(".user-photo-url").src =
    "https://kk-promote-template.v3mh.com/answer-admin/prod/image/230216/LY71waSJB.png";
  score = avg_rating ? avg_rating : "--";
  document.querySelector(".user-rating").innerHTML = score;
  document.querySelector(".user-pocket-count").innerHTML = pocketCount;
  document.querySelector(".user-checkIn-count").innerHTML = commentCount;
}
