# [wha2eat](https://wha2eat.com/)
<p align="center">
  <img src="https://github.com/user-attachments/assets/46c61540-c70c-4a76-82a9-12e52465db5d" alt="logo" />
</p>

<div align="center">
   <h3 font-size="600"> wha2eat 是一個餐廳推薦平台，專為解決使用者不知道要吃什麼的問題</h3>
  <p>根據使用者的瀏覽、收藏、評論紀錄，並結合使用者輸入的條件來推薦最合適的餐廳</p>
</div>

## 主要功能

- **會員系統**：註冊、登入，收藏喜愛餐廳，撰寫餐廳評論。
- **推薦系統**：根據使用者的歷史行為與條件篩選推薦餐廳。
- **資料自動更新**：每周自動向 Google Place API 更新最新的餐廳資訊。

## 開發技術

### 後端

- **Python** / **FastAPI**：後端框架。
- **Scikit-learn**：用於餐廳的相似度計算。
- **Google Place API**：提供餐廳資訊。
- **JWT**：使用者登入驗證。
- **Crontab**：每周日自動更新餐廳資料。
- **RESTful API & MVC** 架構，保持程式碼的可維護性與擴展性([API Doc](https://app.swaggerhub.com/apis-docs/ALFYNLIN/wha2eat/1.0.0))。

### 資料庫

- **MySQL**：使用3NF正規化設計，確保資料一致性。

### 雲端服務

- **AWS EC2**
- **AWS S3**
- **AWS CloudFront**
- **AWS Elastic Load Balancer**
- **AWS Route 53**
- **AWS RDS**

### 部屬與管理

- **Git** / **GitHub**：版本控管。
- **Docker** / **Docker-Compose**：確保本地與雲端環境一致。
- **Nginx**：反向代理伺服器。
- **Let's Encrypt**：提供 SSL 證書，確保 HTTPS 安全連線。

## 系統架構
<img width="2288" alt="系統架構圖0908" src="https://github.com/user-attachments/assets/281b9a22-e894-41be-89a7-fb1310c726a0">
1. 在本地開發後，使用Git與Github做版本控制，並用docker打包，部屬到AWS EC2上
2. RDS在 AWS VPC(Virtual Private Cloud)的private subnet中，避免從internet直接訪問
3. 使用AWS load balancer服務分配流量到不同EC2上(目前只有開一台)
4. 網頁服務與資料更新分別在不同EC2執行，避免資料更新時與網頁伺服器搶占硬體資源


## 資料庫架構
![資料庫架構圖](https://github.com/user-attachments/assets/30cf7ccd-35e9-4ad4-bb77-631e317ffa90)
1. restaurants : 儲存餐廳名稱地址等資訊
2. opening_hours : 儲存餐廳的營業時間(一天的營業時間可能有複數個)
3. images : 儲存餐廳與使用者評論上傳的圖片
4. users : 儲存使用者的基本資訊
5. pockets : 使用者對餐廳的瀏覽紀錄與表態(喜歡，只看過沒表態，不喜歡)
6. comments : 使用者對餐廳的評論紀錄
7. 使用者平均評分(user.avg_rating)會在當使用者新增或刪除評論時重新從comments計算，並儲存在user avg_rating欄位中，由於會頻繁使用此資料，為減輕過多重複的計算，故此欄位的設計不符合正規化原則

