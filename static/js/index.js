let cardN = 0;
let photoN = 0;
let recentData = [];
let user_id;
let showDetail = false;
let loginState = false;
let nextPage = null;
let keyword;

// 獲得推薦餐廳資訊
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

// 搜尋餐廳
async function searchRestaurantCard() {
  if (nextPage === null) {
    nextPage = 0;
  }
  url = "/api/cards/search?keyword=" + keyword + "&page=" + nextPage;
  const response = await fetch(url, { method: "GET" });
  const data_list = await response.json();
  if (data_list.data == false) {
    return false;
  }
  if (nextPage == 0) {
    console.log("目前的next page = 0，第一次搜尋，清空recentData");
    recentData = [];
    photoN = 0;
    cardN = 0;
    if (data_list.data.length == 1) {
      console.log("只有一筆資料");
      get_restaurant_card();
    }
  } else {
    console.log("目前的next page是" + nextPage);
  }
  nextPage = data_list.next_page;

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

  console.log("更新後的nexPage是" + nextPage);
  console.log("recentData的長度是" + recentData.length);

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
  console.log("目前cardN是" + cardN);
  render_restaurant_card(recentData[cardN]);
  if (recentData[cardN].imgs == null) {
    render_photo(null);
  } else {
    render_photo("with url");
  }
  render_arrow();
  if (nextPage !== null && cardN == recentData.length - 3) {
    searchRestaurantCard();
  } else if (cardN == recentData.length - 3) {
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

// 事件
init();
console.log("ttest");
//搜尋
document.querySelector(".search").addEventListener("keydown", async (e) => {
  if (e.key === "Enter" && e.target.value !== "") {
    keyword = e.target.value;
    nextPage = null;
    let getData = await searchRestaurantCard();
    if (getData) {
      getComment(recentData[cardN].id);
      render_restaurant_card(recentData[cardN]);
      if (recentData[cardN].imgs == null) {
        render_photo(null);
      } else {
        render_photo("with url");
      }
      render_arrow();
    } else {
      alert("搜尋不到相關餐廳");
    }
  }
});

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

// Function to update the button text and close the dropdown
function updateButton(btnId, value) {
  const button = document.getElementById(btnId);
  button.textContent = value;
}

// Function to handle the dropdown item click
function handleDropdownClick(event, btnId) {
  event.preventDefault();
  const value = event.target.getAttribute("data-value");
  updateButton(btnId, value);
  // Close the dropdown menu
  event.target
    .closest(".btn-group")
    .querySelector(".dropdown-menu")
    .classList.remove("show");
}

// Function to log the current selections when 'apply' button is clicked
function applySelections() {
  const algorithm = document.getElementById("algorithm-btn").textContent;
  const type = document.getElementById("type-btn").textContent;
  const distance = document.getElementById("distance-btn").textContent;

  console.log(`Algorithm: ${algorithm}`);
  console.log(`Type: ${type}`);
  console.log(`Distance: ${distance}`);
}

// 條件搜尋
// 更新按鈕文本並關閉下拉選單的函數
function updateButton(btnId, displayText, value) {
  const button = document.getElementById(btnId);
  button.textContent = displayText;
  button.setAttribute("data-selected-value", value); // 將選中的值存儲為 data 屬性
}

// 處理下拉選單項目點擊的函數
function handleDropdownClick(event, btnId) {
  event.preventDefault();
  const displayText = event.target.textContent; // 使用可見的文字
  const value = event.target.getAttribute("data-value");
  updateButton(btnId, displayText, value);

  // 關閉下拉選單
  const dropdownMenu = event.target
    .closest(".btn-group")
    .querySelector(".dropdown-menu");
  const dropdownButton = event.target
    .closest(".btn-group")
    .querySelector(".btn");
  dropdownMenu.classList.remove("show");
  dropdownButton.setAttribute("aria-expanded", "false");
}

// 當點擊「套用」按鈕時，記錄當前選擇並將其存儲到 cookie 中的函數
function applySelections() {
  const algorithm = document
    .getElementById("algorithm-btn")
    .getAttribute("data-selected-value");
  const type = document
    .getElementById("type-btn")
    .getAttribute("data-selected-value");
  const distance = document
    .getElementById("distance-btn")
    .getAttribute("data-selected-value");

  console.log(`Algorithm: ${algorithm}`);
  console.log(`Type: ${type}`);
  console.log(`Distance: ${distance}`);
}

// 為每個下拉選單項目附加事件監聽器
document.querySelectorAll("#algorithm-menu .dropdown-item").forEach((item) => {
  item.addEventListener("click", (event) =>
    handleDropdownClick(event, "algorithm-btn")
  );
});

document.querySelectorAll("#type-menu .dropdown-item").forEach((item) => {
  item.addEventListener("click", (event) =>
    handleDropdownClick(event, "type-btn")
  );
});

document.querySelectorAll("#distance-menu .dropdown-item").forEach((item) => {
  item.addEventListener("click", (event) =>
    handleDropdownClick(event, "distance-btn")
  );
});

// 為「套用」按鈕附加事件監聽器
document.getElementById("apply-btn").addEventListener("click", applySelections);
