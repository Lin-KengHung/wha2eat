let cardN = 0;
let photoN = 0;
let recentData = [];
let user_id;
let showDetail = false;
let loginState = false;

async function get_restaurant_card() {
  const response = await fetch("/api/suggest_cards", { method: "GET" });
  const data = await response.json();
  recentData = recentData.concat(data.data);
  return true;
}

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
}

function render_restaurant_card(data) {
  document.querySelector(".restaurant-name").innerHTML = data.name;
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
      recentData[cardN].imgs[photoN];
  } else {
    document.querySelector(".restaurant-img").src = "/static/image/logo.png";
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