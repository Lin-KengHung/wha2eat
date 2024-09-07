-- MySQL dump 10.13  Distrib 8.3.0, for Win64 (x86_64)
--
-- Host: localhost    Database: wha2eat_ncku
-- ------------------------------------------------------
-- Server version	8.3.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `comments`
--

DROP TABLE IF EXISTS `comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `comments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `restaurant_id` int NOT NULL,
  `image_id` int DEFAULT NULL,
  `rating` tinyint(1) NOT NULL,
  `context` text,
  `checkin` tinyint(1) DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `restaurant_id` (`restaurant_id`),
  KEY `user_id` (`user_id`),
  KEY `image_id` (`image_id`),
  CONSTRAINT `comments_ibfk_1` FOREIGN KEY (`restaurant_id`) REFERENCES `restaurants` (`id`),
  CONSTRAINT `comments_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `comments_ibfk_3` FOREIGN KEY (`image_id`) REFERENCES `images` (`id`),
  CONSTRAINT `comments_chk_1` CHECK (((`rating` >= 1) and (`rating` <= 5)))
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `images`
--

DROP TABLE IF EXISTS `images`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `images` (
  `id` int NOT NULL AUTO_INCREMENT,
  `place_id` varchar(255) NOT NULL,
  `url` text NOT NULL COMMENT 'image url',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `upload_by_user` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `place_id` (`place_id`),
  CONSTRAINT `images_ibfk_1` FOREIGN KEY (`place_id`) REFERENCES `restaurants` (`place_id`)
) ENGINE=InnoDB AUTO_INCREMENT=15182 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `opening_hours`
--

DROP TABLE IF EXISTS `opening_hours`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `opening_hours` (
  `id` int NOT NULL AUTO_INCREMENT,
  `place_id` varchar(255) NOT NULL,
  `day_of_week` tinyint(1) NOT NULL,
  `open_time` time NOT NULL,
  `close_time` time NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `place_id` (`place_id`),
  CONSTRAINT `opening_hours_ibfk_1` FOREIGN KEY (`place_id`) REFERENCES `restaurants` (`place_id`)
) ENGINE=InnoDB AUTO_INCREMENT=30173 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pockets`
--

DROP TABLE IF EXISTS `pockets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pockets` (
  `user_id` int NOT NULL,
  `restaurant_id` int NOT NULL,
  `attitude` varchar(255) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `update_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`,`restaurant_id`),
  KEY `restaurant_id` (`restaurant_id`),
  CONSTRAINT `pockets_ibfk_1` FOREIGN KEY (`restaurant_id`) REFERENCES `restaurants` (`id`),
  CONSTRAINT `pockets_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `restaurants`
--

DROP TABLE IF EXISTS `restaurants`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `restaurants` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `address` varchar(255) NOT NULL,
  `district` varchar(255) DEFAULT NULL,
  `lat` double NOT NULL,
  `lng` double NOT NULL,
  `place_id` varchar(255) NOT NULL,
  `google_rating` decimal(2,1) DEFAULT NULL,
  `google_rating_count` int DEFAULT NULL,
  `takeout` tinyint(1) DEFAULT NULL,
  `dineIn` tinyint(1) DEFAULT NULL,
  `delivery` tinyint(1) DEFAULT NULL,
  `reservable` tinyint(1) DEFAULT NULL,
  `type` varchar(255) DEFAULT NULL,
  `businessStatus` tinyint(1) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `place_id` (`place_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4118 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `gender` enum('male','female') DEFAULT NULL,
  `age` tinyint unsigned DEFAULT NULL,
  `avg_rating` decimal(2,1) DEFAULT NULL,
  `profile_picture` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-08-18 15:24:10
