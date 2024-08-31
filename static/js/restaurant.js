let recentData;
let photoN = 0;
let loginState = false;
let userId;
const pattern = /^http.+\/restaurant\/(\d+)$/;
const restaurantId = location.href.match(pattern)[1];

async function get_restaurant_card() {
  const url = "/api/card/" + restaurantId;
  const response = await fetch(url, { method: "GET" });
  recentData = await response.json();
  console.log(recentData);
  render_restaurant_card(recentData);
  render_arrow();
  if (recentData.imgs == null) {
    render_photo(null);
  } else {
    render_photo("with url");
  }
  return recentData.id;
}

async function getComment(restaurant_id) {
  const url = "/api/comment/restaurant?restaurant_id=" + restaurant_id;
  // const data = { restaurant_id: restaurant_id };
  const response = await fetch(url, {
    method: "GET",
  });

  const comments = await response.json();
  for (let i = 0; i < comments.length; i++) {
    render_comment(comments[i]);
  }
}

function randerStar(n) {
  const starGroup = document.querySelector(".star-group");
  starGroup.innerHTML = "";
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
    if (i <= n) {
      starGroup.insertAdjacentHTML("beforeend", solidStar);
    } else {
      starGroup.insertAdjacentHTML("beforeend", regularStar);
    }
  }
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
    document.querySelector(".restaurant-img").src = recentData.imgs[photoN];
  } else {
    document.querySelector(".restaurant-img").src = "/static/image/logo.png";
  }
}

function render_comment(comment) {
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

async function init() {
  console.log("初始化");
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
      userId = data.id;
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
  // 取的餐廳資訊
  let restaurant_id = await get_restaurant_card();

  // 取的評論資訊
  getComment(restaurant_id);
}

// 流程與事件
// 初始化
init();

// 切換圖片
const leftBtn = document.querySelector(".left-arrow");
const rightBtn = document.querySelector(".right-arrow");
function render_arrow() {
  if (recentData.imgs == null) {
    leftBtn.style.display = "none";
    rightBtn.style.display = "none";
  } else if (recentData.imgs.length == 1) {
    leftBtn.style.display = "none";
    rightBtn.style.display = "none";
  } else if (photoN == 0) {
    leftBtn.style.display = "none";
    rightBtn.style.display = "block";
  } else if (photoN == recentData.imgs.length - 1) {
    leftBtn.style.display = "block";
    rightBtn.style.display = "none";
  } else {
    leftBtn.style.display = "block";
    rightBtn.style.display = "block";
  }
}
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

// 上傳圖片
let imgInput = document.querySelector(".img-upload-btn");
const CompressOptions = {
  maxSizeMB: 2,
  maxWidthOrHeight: 800,
  useWebWorker: true,
};

imgInput.addEventListener("change", async (e) => {
  const compressedFile = await imageCompression(
    imgInput.files[0],
    CompressOptions
  );
  const url = window.URL.createObjectURL(compressedFile);
  console.log(url);
  document.querySelector(".uploadIcon").style.display = "none";
  const previewImg = document.querySelector(".preview");
  previewImg.src = url;
  previewImg.style.display = "block";
});

// 評分星星改變
let ratingScore = document.querySelector(".rating_range");
ratingScore.addEventListener("change", (e) => {
  randerStar(ratingScore.value);
});

// 返回主畫面
document.querySelector(".back").addEventListener("click", (e) => {
  history.back();
});

// 提交評論
document
  .querySelector(".comment-submit")
  .addEventListener("click", async (e) => {
    const comment = document.querySelector(".comment-content");
    if (comment.value !== "") {
      e.preventDefault();
      if (loginState === false) {
        document.querySelector(".signin").style.display = "block";
      } else {
        // 提交評論
        const formData = new FormData();
        let inputFile = document.querySelector(".fileInput");
        if (inputFile.files.length == 0) {
          console.log("沒有上傳檔案");
        } else {
          console.log("有上傳檔案");
          const compressedFile = await imageCompression(
            imgInput.files[0],
            CompressOptions
          );
          formData.append("image", compressedFile);
        }

        formData.append("user_id", userId);
        formData.append("restaurant_id", restaurantId);
        formData.append("place_id", recentData.place_id);
        formData.append("rating", ratingScore.value);
        formData.append("context", comment.value);
        formData.append("checkin", false);

        const commentResponse = await fetch("/api/comment", {
          method: "POST",
          headers: {
            Authorization: "Bearer " + localStorage.getItem("user_token"),
          },
          body: formData,
        });
        const commentResult = await commentResponse.json();

        if (commentResult.ok) {
          location.reload();
        }
      }
    }
  });
