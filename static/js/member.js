let pocket_next_page = 0;
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
  if (data.data == false) {
    document.querySelector(".no-pocket").style.display = "flex";
    document.querySelector(".pocket-restaurants").style.display = "none";
    console.log("沒東西");
  } else {
    for (let i = 0; i < data.data.length; i++) {
      renderPocket(data.data[i]);
      // 新增lister導向餐廳
      document
        .querySelector(".pocket" + data.data[i].id)
        .addEventListener("click", (e) => {
          location.href = "/restaurant/" + data.data[i].id;
        });
      // 新增lister刪除口袋名單
      document
        .querySelector(".pocket-delete" + data.data[i].id)
        .addEventListener("click", (e) => {
          deletePocketRestaurant(e.target.id);
        });
    }
    pocket_next_page = data.next_page;

    return "ok";
  }
}
// 刪除會員口袋清單
async function deletePocketRestaurant(restaurant_id) {
  const response = await fetch("/api/pocket?restaurant_id=" + restaurant_id, {
    method: "DELETE",
    headers: {
      Authorization: "Bearer " + localStorage.getItem("user_token"),
    },
  });
  const result = await response.json();
  if (result.ok) {
    location.reload();
  } else {
    alert("口袋餐廳刪除錯誤");
  }
}
// 獲得會員留言並渲染
async function getComment() {
  const response = await fetch("/api/comment/member", {
    method: "GET",
    headers: {
      Authorization: "Bearer " + localStorage.getItem("user_token"),
    },
  });
  const data = await response.json();
  if (data == false) {
    document.querySelector(".no-comment").style.display = "flex";
  } else {
    for (let i = 0; i < data.length; i++) {
      renderComment(data[i]);
      const deleteBtn = document.querySelector(".comment" + data[i].id);
      deleteBtn.addEventListener("click", async (e) => {
        deleteCommnet(e.target.id);
      });
    }
  }
}

// 刪除會員留言
async function deleteCommnet(comment_id) {
  const response = await fetch("/api/comment?comment_id=" + comment_id, {
    method: "DELETE",
    headers: {
      Authorization: "Bearer " + localStorage.getItem("user_token"),
    },
  });
  const result = await response.json();
  if (result.ok) {
    location.reload();
  } else {
    alert("留言刪除錯誤");
  }
}
// 初始化
async function init() {
  //確認登入
  if (localStorage.getItem("user_token")) {
    document.querySelector(".logout").style.display = "block";
    document.querySelector(".user_status").style.display = "none";
    try {
      const response = await fetch("/api/user/profile", {
        method: "GET",
        headers: {
          Authorization: "Bearer " + localStorage.getItem("user_token"),
        },
      });

      if (response.status === 403) {
        location.href = "/";
        return;
      }
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
  } else {
    location.href = "/";
  }
  // 口袋清單
  let init_result = await getMyPocket(0);
  if (init_result == "ok") {
    if (document.querySelectorAll(".restaurant-box").length < 3) {
      document.querySelector(".pocket-right-arrow").style.display = "none";
      document.querySelector(".pocket-left-arrow").style.display = "none";
    }
  }
  // 會員評論
  getComment();
}

// 渲染會員資訊
function renderProfile(name, photoURL, avg_rating, pocketCount, commentCount) {
  document.querySelector(".user-name").innerHTML = name;
  document.querySelector(".user-photo-url").src = "/static/image/profile.svg";
  score = avg_rating ? avg_rating : "--";
  document.querySelector(".user-rating").innerHTML = score;
  document.querySelector(".user-pocket-count").innerHTML = pocketCount;
  document.querySelector(".user-checkIn-count").innerHTML = commentCount;
}

// 渲染口袋清單
function renderPocket(data) {
  //確認營業
  let open_tag;
  if (data.open === true) {
    open_tag = '<div class="restaurant-open">營業中</div>';
  } else if (data.open === false) {
    open_tag = '<div class="restaurant-close">休息中</div>';
  } else {
    open_tag = "";
  }
  // 確認圖片
  let imgSrc;
  if (data.img !== null) {
    imgSrc = data.img;
  } else {
    imgSrc = "/static/image/logo.png";
  }
  const restaurantBox = `
    <div class="restaurant-box">
      <img
        src="${imgSrc}"
        alt="餐廳圖片"
        class="restaurant-img"
      />
      <div class="restaurant-info">
        <div class="restaurant-name pocket${data.id}" id=${data.id}>${data.name}</div>
        <img
          src="/static/image/trash-solid.svg"
          alt="垃圾桶"
          class="pocket-delete pocket-delete${data.id}"
          id=${data.id}
        />
      </div>
      ${open_tag}
    </div>`;
  document
    .querySelector(".restaurant-box-group")
    .insertAdjacentHTML("beforeend", restaurantBox);
}
// 渲染留言
function renderComment(comment) {
  // 確認圖片
  let imgSrc;
  if (comment.url !== null) {
    imgSrc = comment.url;
  } else {
    imgSrc = "/static/image/logo.png";
  }
  let starGroup = "";
  const solidStar = `
  <img
      src="/static/image/star-solid.svg"
      alt="實星"
      class="star star-solid"
  />`;
  const regularStar = `
  <img
      src="/static/image/star-regular.svg"
      alt="空星"
      class="star star-regular"
  />`;
  for (let i = 1; i < 6; i++) {
    if (i <= comment.rating) {
      starGroup += solidStar;
    } else {
      starGroup += regularStar;
    }
  }

  const comment_box = `
          <div class="comment" id=${comment.id}>
            <div class="comment-img-container">
              <img
                src=${imgSrc}
                alt="評論圖片"
                class="comment-img"
              />
              </div>
            <div class="comment-content">
              <div class="comment-restaurant">
                <p class="comment-restaurant_name">${comment.restaurant_name}</p>
                <p class="comment-time">（${comment.created_at}）</p>
              </div>
              <div class="comment-star">
                ${starGroup}
              </div>
              <h3 class="comment-text">
                ${comment.context}
              </h3>
            </div>
            <img
              src="/static/image/trash-solid.svg"
              alt="刪除"
              class="comment-delete comment${comment.id}"
              id="${comment.id}"
            />
          </div>`;
  document
    .querySelector(".comments-group")
    .insertAdjacentHTML("beforeend", comment_box);
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

// 回到首頁
document.querySelector(".title").addEventListener("click", (e) => {
  location.href = "/";
});
// 登出
document.querySelector(".logout").addEventListener("click", (e) => {
  localStorage.removeItem("user_token");
  localStorage.removeItem("restaurantFilter");
  location.href = "/";
});
