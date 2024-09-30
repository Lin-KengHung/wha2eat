# Description

[**wha2eat**](https://wha2eat.com/) aims to solve the common dilemma: "What should we eat later?" The platform recommends restaurants based on the user's interaction history and input conditions.

![Wha2eat](https://github.com/user-attachments/assets/a5191857-240b-4472-bf61-90696ad0aab6)

The idea is came from matching systems in dating apps, where users can match with restaurants based on their preferences. Users can choose to save matched restaurants, pass, or even block them. Through these repeated matches, users can gradually resolve the affliction of choosing where to eat.

**Test account**
+ eamil: test@test.com
+ passward: test

# Demo
https://github.com/user-attachments/assets/eea0e75f-1289-494e-ae25-05a79c63e8a6

# Function map

![function map](https://github.com/user-attachments/assets/5332d119-1126-4499-bf72-f01f5b023442)

- **User System**: Users can sign up, sign in, and upload image profile.
- **Pockets System**: Users can collect their favorite restaurants in personalized pockets.
- **Comments System**: Users can leave comments on restaurants and view comments from other users.
- **Match System**: Restaurants are recommended based on users' historical behavior, input conditions, or by searching with keywords.
- **Automatic Data Updates**: Automatically update the latest restaurant information from the Google Place API every Sunday.

# Core technologies

### Backend

- **Python** / **FastAPI**: Backend framework.
- **Scikit-learn**: Used for restaurant similarity calculations.
- **Google Place API**: Provides restaurant information.
- **JWT**: User authentication.
- **Crontab**: Automatically updates restaurant data every Sunday.
- **RESTful API & MVC** architecture to ensure code maintainability and scalability ([API Doc](https://app.swaggerhub.com/apis-docs/ALFYNLIN/wha2eat/1.0.0)).

### Database

- **MySQL**: Designed with 3NF normalization to ensure data consistency.
- **Redis**: Serve as cache for batch writing user actions into the database.

### Cloud Services

- **AWS EC2**
- **AWS S3**
- **AWS CloudFront**
- **AWS Elastic Load Balancer**
- **AWS Route 53**
- **AWS RDS**
- **AWS ElastiCache**

### Deployment and Management

- **Git** / **GitHub**: Version control.
- **Docker** / **Docker-Compose**: Ensures consistency between local and cloud environments.
- **Nginx**: Reverse proxy server.
- **Let's Encrypt**: Provides SSL certificates to ensure secure HTTPS connections.

# System Architecture

<img width="2384" alt="wha2eat系統架構圖" src="https://github.com/user-attachments/assets/707066ef-9773-401d-a909-06861736ee71">

1. After local development, version control is managed using Git and GitHub, and the application is packaged with Docker and deployed to AWS EC2.
2. pytest is used for unit testing to ensure the core logic of the recommendation system is correct.
3. RDS and ElastiCache is located in the private subnet of AWS VPC (Virtual Private Cloud) to prevent direct access from the internet.
4. AWS load balancer is used to distribute traffic to different EC2 instances (currently only one instance is running).
5. Web services and data updates are executed on separate EC2 instances to avoid resource contention during data updates.

# Database Architecture

![Database Architecture Diagram](https://github.com/user-attachments/assets/30cf7ccd-35e9-4ad4-bb77-631e317ffa90)

1. **restaurants**: Stores restaurant names, addresses, and other information.
2. **opening_hours**: Stores restaurant opening hours (a restaurant may have multiple business hours in a single day).
3. **images**: Stores restaurant images from google place api and user upload when leaving comments.
4. **users**: Stores basic user information.
5. **pockets**: Stores users' browsing history and preferences for restaurants (liked, viewed without preference, or disliked).
6. **comments**: Stores users' restaurant comments records.
7. The user's average rating (**user.avg_rating**) is recalculated from the comments when a user adds or deletes a comment and is stored in the user.avg_rating field. Since this data is frequently used, this field is designed in a way that does not conform to normalization principles to avoid excessive redundant calculations.
