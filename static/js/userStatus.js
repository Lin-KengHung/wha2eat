// 點入登入按鈕
document.querySelector(".user_status").addEventListener("click", (e) => {
  document.querySelector(".signin").style.display = "block";
  document.querySelector(".signin-email").value = "test@test.com";
  document.querySelector(".signin-password").value = "test";
  messageReset();
});
// 關掉登入表單
document.querySelector(".signin-close").addEventListener("click", (e) => {
  document.querySelector(".signin").style.display = "none";
  messageReset();
});
// 切換成註冊
document.querySelector(".change2signup").addEventListener("click", (e) => {
  document.querySelector(".signin").style.display = "none";
  document.querySelector(".signup").style.display = "block";
  messageReset();
});
// 切換成登入
document.querySelector(".change2signin").addEventListener("click", (e) => {
  document.querySelector(".signin").style.display = "block";
  document.querySelector(".signup").style.display = "none";
  messageReset();
});
// 關掉登出表單
document.querySelector(".signup-close").addEventListener("click", (e) => {
  document.querySelector(".signup").style.display = "none";
  messageReset();
});

// 回到首頁
document.querySelector(".title").addEventListener("click", (e) => {
  location.href = "/";
});

// 去到會員頁
document.querySelector(".profile_icon").addEventListener("click", (e) => {
  location.href = "/member";
});

// 登入
document
  .querySelector("button.signin-form")
  .addEventListener("click", async (e) => {
    messageReset();
    const email = document.querySelector(".signin-email").value;
    const password = document.querySelector(".signin-password").value;
    const error = document.querySelector(".signin-error");
    let message = checkSigninData(email, password);
    if (message === "ok") {
      const user_data = {
        email: email,
        password: password,
      };
      const response = await fetch("/api/user/auth", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(user_data),
      });

      const result = await response.json();
      if (result.token) {
        localStorage.setItem("user_token", result.token);
        location.reload();
      } else if (result.error) {
        error.style.display = "block";
        error.innerHTML = result.message;
      } else {
        error.style.display = "block";
        error.innerHTML = "伺服器錯誤，請稍後嘗試";
      }
    } else {
      error.style.display = "block";
      error.innerHTML = message;
    }
  });

// 註冊
document
  .querySelector("button.signup-form")
  .addEventListener("click", async (e) => {
    messageReset();
    const name = document.querySelector(".signup-name").value;
    const email = document.querySelector(".signup-email").value;
    const password = document.querySelector(".signup-password").value;
    const gender_tag = document.querySelector('input[name="gender"]:checked');
    gender = gender_tag ? gender_tag.value : null;
    let age = document.querySelector(".age").value;
    if (age == "") {
      age = null;
    }
    const error = document.querySelector(".signup-error");
    const success = document.querySelector(".signup-success");
    const message = checkSignupData(name, email, password, age);
    if (message === "ok") {
      const user_data = {
        name: name,
        email: email,
        password: password,
        gender: gender,
        age: age,
      };
      const response = await fetch("/api/user", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(user_data),
      });

      const result = await response.json();
      if (result.ok) {
        error.style.display = "none";
        success.style.display = "block";
      } else if (result.error) {
        error.style.display = "block";
        error.innerHTML = result.message;
      } else {
        error.style.display = "block";
        error.innerHTML = "伺服器錯誤，請稍後嘗試";
      }
    } else {
      error.style.display = "block";
      error.innerHTML = message;
    }
  });

function checkSigninData(email, password) {
  const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  if (!email) {
    message = "請輸入email";
  } else if (!emailPattern.test(email)) {
    message = "email格式有錯";
  } else if (!password) {
    message = "請輸入密碼";
  } else {
    message = "ok";
  }
  return message;
}
function checkSignupData(name, email, password, age) {
  const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  if (!name) {
    message = "請輸入姓名";
  } else if (!email) {
    message = "請輸入email";
  } else if (!emailPattern.test(email)) {
    message = "email格式有錯";
  } else if (!password) {
    message = "請輸入密碼";
  } else if (age < 0 || age > 100) {
    message = "請輸入正確年紀";
  } else {
    message = "ok";
  }
  return message;
}
function messageReset() {
  document.querySelector(".signup-error").style.display = "none";
  document.querySelector(".signup-success").style.display = "none";
  document.querySelector(".signin-error").style.display = "none";
}
