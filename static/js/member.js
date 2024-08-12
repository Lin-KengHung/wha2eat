let pocket_next_page = 0;

// 回到首頁
document.querySelector(".title").addEventListener("click", (e) => {
  location.href = "/";
});
// 登出
document.querySelector(".logout").addEventListener("click", (e) => {
  localStorage.removeItem("user_token");
  location.href = "/";
});

// 獲得會員口袋清單並渲染
async function getMyPocket(page) {
  let url = "/api/pocket?page=" + page;
  // 渲染口袋
  const response = await fetch(url, {
    method: "GET",
    headers: {
      Authorization: "Bearer " + localStorage.getItem("user_token"),
    },
  });

  const data = await response.json();
  // console.log(data);
  for (let i = 0; i < data.data.length; i++) {
    renderPocket(data.data[i]);
  }
  pocket_next_page = data.next_page;
}

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
  getMyPocket(0);
}

// 渲染會員資訊
function renderProfile(name, photoURL, avg_rating, pocketCount, commentCount) {
  document.querySelector(".user-name").innerHTML = name;
  document.querySelector(".user-photo-url").src =
    "https://kk-promote-template.v3mh.com/answer-admin/prod/image/230216/LY71waSJB.png";
  score = avg_rating ? avg_rating : "--";
  document.querySelector(".user-rating").innerHTML = score;
  document.querySelector(".user-pocket-count").innerHTML = pocketCount;
  document.querySelector(".user-checkIn-count").innerHTML = commentCount;
}

// 渲染口袋清單
function renderPocket(data) {
  let open_tag;
  if (data.open === true) {
    open_tag = '<div class="restaurant-open">營業中</div>';
  } else if (data.open === false) {
    open_tag = '<div class="restaurant-close">休息中</div>';
  } else {
    open_tag = "";
  }
  const restaurantBox = `
    <div class="restaurant-box" id=${data.id}>
      <img
        src="${data.img}"
        alt="餐廳圖片"
        class="restaurant-img"
      />
      <div class="restaurant-info">
        <div class="restaurant-name">${data.name}</div>
        <img
          src="/static/image/trash-solid.svg"
          alt="垃圾桶"
          class="delete-btn"
        />
      </div>
      ${open_tag}
    </div>`;
  document
    .querySelector(".restaurant-box-group")
    .insertAdjacentHTML("beforeend", restaurantBox);
}

init();

// 滾動口袋清單
const mrtContainer = document.querySelector(".restaurant-box-group");
const rightBtn = document.querySelector(".pocket-right-arrow");
const leftBtn = document.querySelector(".pocket-left-arrow");
rightBtn.addEventListener("click", (e) => {
  mrtContainer.scrollLeft += mrtContainer.clientWidth * 0.75;
  if (
    mrtContainer.scrollLeft + mrtContainer.clientWidth >=
      mrtContainer.scrollWidth * 0.8 &&
    pocket_next_page != null
  ) {
    getMyPocket(pocket_next_page);
  }
});
leftBtn.addEventListener("click", (e) => {
  mrtContainer.scrollLeft -= mrtContainer.clientWidth * 0.75;
});
