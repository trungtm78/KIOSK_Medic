-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: localhost    Database: medicagent-directory-db
-- ------------------------------------------------------
-- Server version	8.0.43

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `SERVICE_PRICES`
--

DROP TABLE IF EXISTS `SERVICE_PRICES`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `SERVICE_PRICES` (
  `price_id` int NOT NULL AUTO_INCREMENT,
  `service_id` int NOT NULL,
  `hospital_id` int DEFAULT NULL,
  `price` decimal(12,2) NOT NULL,
  `currency` varchar(3) COLLATE utf8mb4_unicode_ci NOT NULL,
  `payer_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'BHYT, tu_chi_tra, doanh_nghiep...',
  `area_tag` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Khu vực/tầng/khu VIP nếu có',
  `effective_from` date NOT NULL,
  `effective_to` date DEFAULT NULL,
  `notes` text COLLATE utf8mb4_unicode_ci,
  `status` int DEFAULT NULL COMMENT '1: Active, 0: Inactive',
  PRIMARY KEY (`price_id`),
  UNIQUE KEY `uq_service_price_period` (`service_id`,`hospital_id`,`effective_from`,`effective_to`),
  KEY `ix_SERVICE_PRICES_hospital_id` (`hospital_id`),
  KEY `ix_SERVICE_PRICES_service_id` (`service_id`),
  CONSTRAINT `SERVICE_PRICES_ibfk_1` FOREIGN KEY (`service_id`) REFERENCES `SERVICES` (`service_id`),
  CONSTRAINT `SERVICE_PRICES_ibfk_2` FOREIGN KEY (`hospital_id`) REFERENCES `HOSPITALS` (`hospital_id`)
) ENGINE=InnoDB AUTO_INCREMENT=201 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-30 10:40:02
