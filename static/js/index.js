let cardN = 0;
let photoN = 0;
let recentData = [];
let user_id;
let showDetail = false;
let loginState = false;
let nextPage = null;
let keyword;
let lat;
let lng;
// 獲得推薦餐廳資訊
async function get_restaurant_card() {
  let url = "/api/cards/suggest";
  let setting = { method: "GET" };
  if (localStorage.getItem("user_token")) {
    url += "/login";
    setting = {
      method: "GET",
      headers: {
        Authorization: "Bearer " + localStorage.getItem("user_token"),
      },
    };
  }

  if (localStorage.getItem("restaurantFilter")) {
    let constrain = JSON.parse(localStorage.getItem("restaurantFilter"));
    url += "?distance_limit=" + constrain.distance.value;

    if (constrain.algorithm.displayText !== "random") {
      url += "&algorithm=" + constrain.algorithm.value;
    }
    if (constrain.type.value !== "all") {
      url += "&restaurant_type=" + constrain.type.value;
    }
    if (constrain.seen.value !== "seen-all" && loginState) {
      url += "&have_seen=" + constrain.seen.value;
    }
    if (constrain.mustOpen.value === "true") {
      url += "&is_open=true";
    }
  }

  const response = await fetch(url, setting);
  const data_list = await response.json();

  if (data_list.data == false) {
    console.log(data_list);
    showDataLength(0);

    resetTypeToDefault();
    return false;
  } else {
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
    const len = recentData.length;
    while (recentData.length < 4 && recentData.length > 1) {
      recentData = recentData.concat(data_list.data);
    }
    return len;
  }
}

// 搜尋餐廳
async function searchRestaurantCard() {
  if (nextPage === null) {
    nextPage = 0;
  }
  let url = "/api/cards/search";
  let setting = { method: "GET" };
  if (localStorage.getItem("user_token")) {
    url += "/login";
    setting = {
      method: "GET",
      headers: {
        Authorization: "Bearer " + localStorage.getItem("user_token"),
      },
    };
  }
  url += "?keyword=" + keyword + "&page=" + nextPage;
  const response = await fetch(url, setting);
  const data_list = await response.json();
  const len = data_list.data.length;
  if (data_list.data == false) {
    return false;
  }
  document.querySelector(".restaurant-img").src = "/static/image/logo.png";

  if (nextPage == 0) {
    recentData = [];
    photoN = 0;
    cardN = 0;
    if (data_list.data.length == 1) {
      get_restaurant_card();
    }
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

  return len;
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

  if (nextPage !== null && cardN == recentData.length - 3) {
    searchRestaurantCard();
  } else if (cardN == recentData.length - 3) {
    get_restaurant_card();
  }
  getComment(recentData[cardN].id);
}

async function getUserLocation() {
  try {
    // 等待使用者允許或拒絕位置存取
    const position = await new Promise((resolve, reject) => {
      // 請求使用者位置
      navigator.geolocation.getCurrentPosition(resolve, reject);
    });

    // 提取經緯度
    lat = position.coords.latitude;
    lng = position.coords.longitude;
  } catch (error) {
    console.error("Error getting user location:", error);
    throw error; // 如果失敗，丟出錯誤
  }
}

function render_restaurant_card(data) {
  const restaurantName = document.querySelector(".restaurant-name");
  restaurantName.innerHTML = data.name;
  restaurantName.id = data.id;
  document.querySelector(".restaurant-type").innerHTML = data.restaurant_type;
  document.querySelector(".address").innerHTML = data.address;

  // google 評論
  const googleTag = document.querySelector(".restaurant-rating");
  if (data.google_rating === null || data.google_rating_count === null) {
    googleTag.style.display = "none";
  } else {
    googleTag.style.display = "block";
    googleTag.innerHTML =
      "Google評分: " +
      data.google_rating +
      "（" +
      data.google_rating_count +
      "）";
  }

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

  // 態度判斷
  if (localStorage.getItem("user_token")) {
    const newTag = document.querySelector(".attitude-new");
    const likeTag = document.querySelector(".attitude-like");
    const considerTag = document.querySelector(".attitude-consider");
    const solidHeart = document.querySelector(".solid-heart");
    const regularHeart = document.querySelector(".regular-heart");
    if (data.attitude === "consider") {
      considerTag.style.display = "block";
      newTag.style.display = "none";
      likeTag.style.display = "none";
      regularHeart.style.display = "block";
      solidHeart.style.display = "none";
    } else if (data.attitude === "like") {
      considerTag.style.display = "none";
      newTag.style.display = "none";
      likeTag.style.display = "block";
      regularHeart.style.display = "none";
      solidHeart.style.display = "block";
    } else if (data.attitude === null) {
      considerTag.style.display = "none";
      newTag.style.display = "block";
      likeTag.style.display = "none";
      regularHeart.style.display = "block";
      solidHeart.style.display = "none";
    }
  }

  // 距離判斷
  distanceTag = document.querySelector(".distance");
  if (data.distance > 1000) {
    distanceTag.innerHTML = data.distance / 1000 + "公里";
  } else {
    distanceTag.innerHTML = data.distance + "公尺";
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
  let indicatorGroup = document.querySelector(".indicators-group");
  indicatorGroup.innerHTML = "";
  if (url !== null) {
    indicatorGroup.insertAdjacentHTML(
      "beforeend",
      '<div class="indicator active" id="0"></div>'
    );
    let indicator = '<div class="indicator" id="0"></div>';
    for (let i = 1; i < recentData[cardN].imgs.length; i++) {
      indicatorGroup.insertAdjacentHTML("beforeend", indicator);
    }

    let n = photoN % recentData[cardN].imgs.length;
    document.querySelector(".restaurant-img").src =
      recentData[cardN].imgs[n].src;
    const indicators = document.querySelectorAll(".indicator");
    for (let i = 0; i < recentData[cardN].imgs.length; i++) {
      if (i == n) {
        indicators[i].classList.add("active");
      } else {
        indicators[i].classList.remove("active");
      }
    }
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
    document.querySelector(".regular-heart").style.display = "block";
  } else {
    document.querySelector(".profile_icon").style.display = "none";
    document.querySelector(".user_status").style.display = "block";
  }

  // 讀取local storage 的餐廳搜尋條件
  loadRestaurantFilter();
  // 餐廳
  let getData = await get_restaurant_card();

  if (getData) {
    console.log("初始化的getData長度 " + getData);
    getComment(recentData[cardN].id);
    render_restaurant_card(recentData[cardN]);
    if (recentData[cardN].imgs == null) {
      render_photo(null);
    } else {
      render_photo("with url");
    }
  }
  // getUserLocation();
}

// 事件
init();
//搜尋
document.querySelector(".search").addEventListener("keydown", async (e) => {
  if (e.key === "Enter" && e.target.value !== "") {
    keyword = e.target.value;
    nextPage = null;
    let getData = await searchRestaurantCard();
    if (getData) {
      console.log("搜尋後的長度" + getData);
      showDataLength(getData);
      document.querySelector(".restaurant-img").src =
        "static/image/loading.gif";
      getComment(recentData[cardN].id);
      render_restaurant_card(recentData[cardN]);
      if (recentData[cardN].imgs == null) {
        render_photo(null);
      } else {
        render_photo("with url");
      }
    } else {
      showDataLength(0);
    }
  }
});

// 換餐廳與加入口袋
const solidHeart = document.querySelector(".solid-heart");
const regularHeart = document.querySelector(".regular-heart");
solidHeart.addEventListener("click", (e) => {
  solidHeart.style.display = "none";
  regularHeart.style.display = "block";
});
regularHeart.addEventListener("click", (e) => {
  solidHeart.style.display = "block";
  regularHeart.style.display = "none";
});

document.querySelector(".next-page").addEventListener("click", async (e) => {
  if (loginState) {
    let data = {};
    if (solidHeart.style.display == "block") {
      data = {
        user_id: user_id,
        restaurant_id: recentData[cardN].id,
        attitude: "like",
      };
    } else if (regularHeart.style.display == "block") {
      data = {
        user_id: user_id,
        restaurant_id: recentData[cardN].id,
        attitude: "consider",
      };
    }
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
      console.log("按讚過快");
    } else {
      change_restaurant_card();
    }
  } else {
    change_restaurant_card();
  }
});

// 換圖片
let photoContainer = document.querySelector(".restaurant-photo");
photoContainer.addEventListener("click", (e) => {
  photoN += 1;
  render_photo("with url");
});

// 導向到餐廳頁面
const restaurant = document.querySelector(".restaurant-name");
document
  .querySelector(".restaurant-name")
  .addEventListener("click", async (e) => {
    location.href = "/restaurant/" + restaurant.id;
  });

// -------------------------------------------------- //
// 條件相關
// 切換下拉選單的顯示和隱藏
function toggleDropdownMenu(btnId) {
  // 先關閉其他所有下拉選單
  document.querySelectorAll(".btn-group .dropdown-menu").forEach((menu) => {
    const parentButton = menu.closest(".btn-group").querySelector(".btn");
    if (parentButton.id !== btnId) {
      menu.style.display = "none";
      parentButton.setAttribute("aria-expanded", "false");
    }
  });

  // 然後打開當前的下拉選單
  const dropdownMenu = document
    .getElementById(btnId)
    .closest(".btn-group")
    .querySelector(".dropdown-menu");

  // 切換顯示狀態
  if (dropdownMenu.style.display === "block") {
    dropdownMenu.style.display = "none";
  } else {
    dropdownMenu.style.display = "block";
  }
}

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

  // 手動控制顯示與隱藏
  const dropdownMenu = event.target.closest(".dropdown-menu");

  // 使用 display 控制顯示與隱藏
  dropdownMenu.style.display = "none";

  // 更新按鈕的 aria-expanded 屬性
  const dropdownButton = document.getElementById(btnId);
  dropdownButton.setAttribute("aria-expanded", "false");
}

// 當點擊「套用」按鈕時，記錄當前選擇並將其存儲到 cookie 中的函數
async function applySelections() {
  const algorithmButton = document.getElementById("algorithm-btn");
  const typeButton = document.getElementById("type-btn");
  const distanceButton = document.getElementById("distance-btn");
  const mustOpenButton = document.getElementById("open-btn");
  const seenButton = document.getElementById("seen-btn");

  const algorithmDisplayText = algorithmButton.textContent;
  const algorithmValue = algorithmButton.getAttribute("data-selected-value");

  const typeDisplayText = typeButton.textContent;
  const typeValue = typeButton.getAttribute("data-selected-value");

  const distanceDisplayText = distanceButton.textContent;
  const distanceValue = distanceButton.getAttribute("data-selected-value");

  const mustOpenDisplayText = mustOpenButton.textContent;
  const mustOpenValue = mustOpenButton.getAttribute("data-selected-value");

  const seenDisplayText = seenButton.textContent;
  const seenValue = seenButton.getAttribute("data-selected-value");

  if (loginState == false) {
    if (
      seenValue == "true" ||
      seenValue == "false" ||
      algorithmValue == "IBCF" ||
      algorithmValue == "UBCF"
    ) {
      document.querySelector(".signin").style.display = "block";
      return;
    }
  }
  // if (distanceValue != 2000) {
  //   try {
  //     const location = await getUserLocation();
  //     console.log("User's location:", location);
  //   } catch (error) {
  //     console.error("Failed to get user's location.");
  //   }
  // } else {
  //   return;
  // }

  // 將顯示文字和值儲存到 localStorage
  localStorage.setItem(
    "restaurantFilter",
    JSON.stringify({
      algorithm: { displayText: algorithmDisplayText, value: algorithmValue },
      type: { displayText: typeDisplayText, value: typeValue },
      distance: { displayText: distanceDisplayText, value: distanceValue },
      mustOpen: { displayText: mustOpenDisplayText, value: mustOpenValue },
      seen: { displayText: seenDisplayText, value: seenValue },
    })
  );

  // 在這裡可以發送 fetch 請求以獲取推薦餐廳
  recentData = [];
  photoN = 0;
  cardN = 0;
  document.querySelector(".restaurant-img").src = "static/image/loading.gif";
  let getData = await get_restaurant_card();
  if (getData == 1) {
  }
  if (getData) {
    console.log("套用的getData長度 " + getData);
    showDataLength(getData);
    getComment(recentData[cardN].id);
    render_restaurant_card(recentData[cardN]);
    if (recentData[cardN].imgs == null) {
      render_photo(null);
    } else {
      render_photo("with url");
    }
    if (getData == 1) {
      resetTypeToDefault();
      let getData = await get_restaurant_card();
      getComment(recentData[cardN].id);
      render_restaurant_card(recentData[cardN]);
      if (recentData[cardN].imgs == null) {
        render_photo(null);
      } else {
        render_photo("with url");
      }
    }
  } else {
    console.log("按下套用後get card回傳false");
    showDataLength(0);
    let getData = await get_restaurant_card();
    getComment(recentData[cardN].id);
    render_restaurant_card(recentData[cardN]);
    if (recentData[cardN].imgs == null) {
      render_photo(null);
    } else {
      render_photo("with url");
    }
  }
}

// 為每個下拉選單按鈕附加點擊事件監聽器
document.querySelectorAll(".btn.dropdown-toggle").forEach((button) => {
  button.addEventListener("click", (event) => {
    event.preventDefault();
    toggleDropdownMenu(event.currentTarget.id);
  });
});

// 為每個下拉選單項目附加事件監聽器
document.querySelectorAll(".dropdown-menu .dropdown-item").forEach((item) => {
  item.addEventListener("click", (event) => {
    handleDropdownClick(
      event,
      event.target.closest(".btn-group").querySelector(".btn").id
    );
  });
});

// 套用」按鈕附加事件監聽器
document.getElementById("apply-btn").addEventListener("click", applySelections);

function loadRestaurantFilter() {
  const savedFilters = JSON.parse(localStorage.getItem("restaurantFilter"));

  // 預設初始值
  const defaultFilters = {
    algorithm: { displayText: "隨機推薦", value: "random" },
    type: { displayText: "全部類型", value: "all" },
    distance: { displayText: "2公里以內", value: 2000 },
    mustOpen: { displayText: "營業中", value: "true" },
    seen: { displayText: "全都看看", value: "seen-all" },
  };

  const filters = savedFilters || defaultFilters;

  updateButton(
    "algorithm-btn",
    filters.algorithm.displayText,
    filters.algorithm.value
  );
  updateButton("type-btn", filters.type.displayText, filters.type.value);
  updateButton(
    "distance-btn",
    filters.distance.displayText,
    filters.distance.value
  );
  updateButton(
    "open-btn",
    filters.mustOpen.displayText,
    filters.mustOpen.value
  );
  updateButton("seen-btn", filters.seen.displayText, filters.seen.value);
}

// reset餐廳類型
function resetTypeToDefault() {
  console.log("套用reset");
  const defaultType = { displayText: "全部類型", value: "all" };
  const defaultAlgorithm = { displayText: "隨機推薦", value: "random" };

  // 更新按鈕顯示為預設值
  updateButton("type-btn", defaultType.displayText, defaultType.value);
  updateButton(
    "algorithm-btn",
    defaultAlgorithm.displayText,
    defaultAlgorithm.value
  );
  // 更新 localStorage 中的條件
  const savedFilters =
    JSON.parse(localStorage.getItem("restaurantFilter")) || {};
  savedFilters.type = defaultType;
  savedFilters.algorithm = defaultAlgorithm;
  // 設定 type 為預設值
  localStorage.setItem("restaurantFilter", JSON.stringify(savedFilters));

  console.log("Type reset to default: 全部類型 (all)");
}

// data比數動畫
function showDataLength(n, delay = 3000) {
  const element = document.querySelector(".data-length");

  // 設置元素的內容並將其透明度設為1以顯示內容
  if (n == 10) {
    element.textContent = "超過" + n + "筆資料！";
  } else if (n == 0) {
    element.textContent = "沒有資料😭";
  } else {
    element.textContent = "有" + n + "筆資料！";
  }

  element.style.opacity = 1;
  element.style.display = "block"; // 確保元素可見

  // 延遲指定時間（毫秒）後執行淡出效果
  setTimeout(() => {
    let opacity = 1; // 元素初始透明度
    const fadeOut = setInterval(() => {
      if (opacity <= 0.1) {
        clearInterval(fadeOut);
        element.style.display = "none"; // 完全消失後隱藏元素
      }
      element.style.opacity = opacity;
      opacity -= opacity * 0.1; // 每次減少透明度的10%
    }, 50); // 每50毫秒更新一次透明度
  }, delay);
}

// 地址導航
document.querySelector(".navigation-btn").addEventListener("click", (e) => {
  const address = document.querySelector(".address").innerHTML;
  encodedAddress = encodeURIComponent(address);
  const googleMapsUrl = `https://www.google.com/maps/dir/?api=1&destination=${encodedAddress}`;
  window.location.href = googleMapsUrl;
});
