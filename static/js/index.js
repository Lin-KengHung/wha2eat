let cardN = 0;
let photoN = 0;
let recentData = [];
let commentData = [];
let user_id;
let showDetail = false;
let loginState = false;

// 獲得餐廳資訊
async function get_restaurant_card() {
  const response = await fetch("/api/cards/suggest", { method: "GET" });
  const data_list = await response.json();

  // 圖片preload
  for (let i = 0; i < data_list.data.length; i++) {
    if (data_list.data[i].imgs !== null) {
      let preloadImg = [];
      for (let j = 0; j < data_list.data[i].imgs.length; j++) {
        const img = new Image();
        img.src = data_list.data[i].imgs[j];
        preloadImg.push(img);
      }
      data_list.data[i].imgs = preloadImg;
    }
  }
  recentData = recentData.concat(data_list.data);
  return true;
}

// 獲得留言資訊
async function getComment(restaurant_id) {
  const url = "/api/comment/restaurant?restaurant_id=" + restaurant_id;
  const response = await fetch(url, {
    method: "GET",
  });

  const comments = await response.json();
  document.querySelector(".comments_group").innerHTML = "";
  if (comments == false) {
    document.querySelector(".no-comment").style.display = "block";
    render_comment(null);
  } else {
    document.querySelector(".no-comment").style.display = "none";
    for (let i = 0; i < comments.length; i++) {
      render_comment(comments[i]);
    }
  }
}

// 頁面上更換餐廳
function change_restaurant_card() {
  cardN += 1;
  photoN = 0;
  render_restaurant_card(recentData[cardN]);
  if (recentData[cardN].imgs == null) {
    render_photo(null);
  } else {
    render_photo("with url");
  }
  render_arrow();
  if (cardN == recentData.length - 3) {
    get_restaurant_card();
  }
  getComment(recentData[cardN].id);
}

function render_restaurant_card(data) {
  const restaurantName = document.querySelector(".restaurant-name");
  restaurantName.innerHTML = data.name;
  restaurantName.id = data.id;
  document.querySelector(".restaurant-type").innerHTML = data.restaurant_type;
  document.querySelector(".address").innerHTML = data.address;
  document.querySelector(".restaurant-rating").innerHTML =
    "Google評分: " +
    data.google_rating +
    "（" +
    data.google_rating_count +
    "）";

  // 營業判斷
  openTag = document.querySelector(".restaurant-open");
  closeTag = document.querySelector(".restaurant-close");
  if (data.open === true) {
    openTag.style.display = "block";
    closeTag.style.display = "none";
  } else if (data.open === false) {
    openTag.style.display = "none";
    closeTag.style.display = "block";
  } else {
    openTag.style.display = "none";
    closeTag.style.display = "none";
  }

  // 判斷內用，外帶，外送，訂位
  const services = ["takeout", "dineIn", "delivery", "reservable"];
  services.forEach((service) => {
    if (data[service] === null) {
      document.querySelector("." + service).style.display = "none";
    } else {
      tickTag = document.querySelector("." + service + "-tick");
      errorTag = document.querySelector("." + service + "-error");
      if (data[service] === true) {
        document.querySelector("." + service).style.display = "flex";
        tickTag.style.display = "block";
        errorTag.style.display = "none";
      } else {
        document.querySelector("." + service).style.display = "flex";
        tickTag.style.display = "none";
        errorTag.style.display = "block";
      }
    }
  });
}

function render_photo(url = null) {
  if (url !== null) {
    document.querySelector(".restaurant-img").src =
      recentData[cardN].imgs[photoN].src;
  } else {
    document.querySelector(".restaurant-img").src = "/static/image/logo.png";
  }
}
function render_comment(comment) {
  if (comment === null) {
    return;
  } else {
    // 確認圖片
    let imgSrc;
    if (comment.url !== null) {
      imgSrc = comment.url;
    } else {
      imgSrc = "/static/image/logo.png";
    }
    // 確認星星
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
       <div class="comment">
         <div class="img-container">
           <img
             src=${imgSrc}
             alt="評論圖片"
             class="comment-img"
           />
         </div>

         <div class="comment-content">
           <div class="comment-user_info">
             <p class="comment-user">${comment.username}</p>
             <p class="comment-user_score">（平均打分： ${comment.avg_rating} ）</p>
           </div>
           <div class="comment-star">
             ${starGroup}
           </div>
           <h3 class="comment-text">${comment.context}</h3>
         </div>
       </div>`;
    document
      .querySelector(".comments_group")
      .insertAdjacentHTML("beforeend", comment_box);
  }
}

const leftBtn = document.querySelector(".left-arrow");
const rightBtn = document.querySelector(".right-arrow");
function render_arrow() {
  if (recentData[cardN].imgs == null) {
    leftBtn.style.display = "none";
    rightBtn.style.display = "none";
  } else if (recentData[cardN].imgs.length == 1) {
    leftBtn.style.display = "none";
    rightBtn.style.display = "none";
  } else if (photoN == 0) {
    leftBtn.style.display = "none";
    rightBtn.style.display = "block";
  } else if (photoN == recentData[cardN].imgs.length - 1) {
    leftBtn.style.display = "block";
    rightBtn.style.display = "none";
  } else {
    leftBtn.style.display = "block";
    rightBtn.style.display = "block";
  }
}

// 初始化
async function init() {
  // 取得登入狀態
  if (localStorage.getItem("user_token")) {
    try {
      let response = await fetch("/api/user/auth", {
        method: "GET",
        headers: {
          Authorization: "Bearer " + localStorage.getItem("user_token"),
        },
      });
      let data = await response.json();
      //特殊修改token或是過期的情況
      user_id = data.id;
      if (data.error) {
        localStorage.removeItem("user_token");
        location.reload();
      }
    } catch (error) {
      console.error("沒抓到/api/user/auth的資料", error);
    }
    document.querySelector(".profile_icon").style.display = "block";
    document.querySelector(".user_status").style.display = "none";
    loginState = true;
  } else {
    document.querySelector(".profile_icon").style.display = "none";
    document.querySelector(".user_status").style.display = "block";
  }
  // 餐廳
  let getData = await get_restaurant_card();

  if (getData === true) {
    getComment(recentData[cardN].id);
    render_restaurant_card(recentData[cardN]);
    if (recentData[cardN].imgs == null) {
      render_photo(null);
    } else {
      render_photo("with url");
    }
  }
  render_arrow();
}

init();
// 換餐廳與加入口袋
// 喜歡
document.querySelector(".like").addEventListener("click", async (e) => {
  if (loginState) {
    const data = {
      user_id: user_id,
      restaurant_id: recentData[cardN].id,
      attitude: "like",
    };
    const response = await fetch("/api/pocket", {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("user_token"),
      },
      body: JSON.stringify(data),
    });
    const result = await response.json();
    if (result.error) {
      alert("有錯快跟我講");
    }
  }

  change_restaurant_card();
});
// 不喜歡
document.querySelector(".dislike").addEventListener("click", async (e) => {
  if (loginState) {
    const data = {
      user_id: user_id,
      restaurant_id: recentData[cardN].id,
      attitude: "dislike",
    };
    const response = await fetch("/api/pocket", {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("user_token"),
      },
      body: JSON.stringify(data),
    });
    const result = await response.json();
    if (result.error) {
      alert("有錯快跟我講");
    }
  }

  change_restaurant_card();
});
// 考慮
document.querySelector(".consider").addEventListener("click", async (e) => {
  if (loginState) {
    const data = {
      user_id: user_id,
      restaurant_id: recentData[cardN].id,
      attitude: "consider",
    };
    const response = await fetch("/api/pocket", {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("user_token"),
      },
      body: JSON.stringify(data),
    });
    const result = await response.json();
    if (result.error) {
      alert("有錯快跟我講");
    }
  }

  change_restaurant_card();
});

// 換圖片
leftBtn.addEventListener("click", (e) => {
  photoN -= 1;
  render_arrow();
  render_photo("with url");
});
rightBtn.addEventListener("click", (e) => {
  photoN += 1;
  render_arrow();
  render_photo("with url");
});

// 顯示詳細資訊
const detailInfo = document.querySelector(".restaurant-detail_info");
document
  .querySelector(".restaurant-detail_btn")
  .addEventListener("click", (e) => {
    if (showDetail) {
      detailInfo.style.display = "none";
      showDetail = false;
    } else {
      detailInfo.style.display = "flex";
      showDetail = true;
    }
  });

// 導向到餐廳頁面
const restaurant = document.querySelector(".restaurant-name");
document
  .querySelector(".restaurant-name")
  .addEventListener("click", async (e) => {
    location.href = "/restaurant/" + restaurant.id;
  });
