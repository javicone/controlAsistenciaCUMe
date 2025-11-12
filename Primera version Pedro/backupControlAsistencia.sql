/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19-11.7.2-MariaDB, for Win64 (AMD64)
--
-- Host: localhost    Database: control_asistencia
-- ------------------------------------------------------
-- Server version	11.7.2-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*M!100616 SET @OLD_NOTE_VERBOSITY=@@NOTE_VERBOSITY, NOTE_VERBOSITY=0 */;

--
-- Table structure for table `asistencias`
--

DROP TABLE IF EXISTS `asistencias`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `asistencias` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `usuario_id` int(11) NOT NULL,
  `aula_id` int(11) NOT NULL,
  `fecha_hora` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `usuario_id` (`usuario_id`),
  KEY `aula_id` (`aula_id`),
  CONSTRAINT `asistencias_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`),
  CONSTRAINT `asistencias_ibfk_2` FOREIGN KEY (`aula_id`) REFERENCES `aulas` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `asistencias`
--

LOCK TABLES `asistencias` WRITE;
/*!40000 ALTER TABLE `asistencias` DISABLE KEYS */;
INSERT INTO `asistencias` VALUES
(1,1,1,'2025-03-01 07:05:00'),
(2,1,1,'2025-03-02 07:10:00'),
(3,1,2,'2025-03-03 08:00:00'),
(4,1,1,'2025-03-04 07:45:00'),
(5,1,1,'2025-03-09 19:22:43'),
(6,1,1,'2025-03-09 19:23:36'),
(7,1,1,'2025-03-10 16:04:06'),
(8,1,1,'2025-03-10 16:04:59'),
(9,1,1,'2025-03-10 16:05:51'),
(10,1,1,'2025-03-10 16:06:43'),
(11,1,1,'2025-03-10 16:07:36'),
(12,1,1,'2025-03-10 16:08:28'),
(13,1,1,'2025-03-10 16:09:20'),
(14,1,1,'2025-03-10 16:10:13'),
(15,1,1,'2025-03-10 16:11:05'),
(16,1,1,'2025-03-10 16:11:58'),
(17,1,1,'2025-03-10 16:12:50'),
(18,1,1,'2025-03-10 16:15:36'),
(19,1,1,'2025-03-10 16:15:36'),
(20,1,1,'2025-03-10 16:15:38'),
(21,1,1,'2025-03-10 16:16:41'),
(22,1,1,'2025-03-10 16:32:29'),
(23,1,1,'2025-03-10 16:33:18'),
(24,1,1,'2025-03-10 16:34:21'),
(25,4,1,'2025-04-01 17:09:01'),
(26,4,1,'2025-04-01 17:26:20');
/*!40000 ALTER TABLE `asistencias` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `aulas`
--

DROP TABLE IF EXISTS `aulas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `aulas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `password_aula` varchar(100) DEFAULT '',
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `aulas`
--

LOCK TABLES `aulas` WRITE;
/*!40000 ALTER TABLE `aulas` DISABLE KEYS */;
INSERT INTO `aulas` VALUES
(1,'Aula 101','pass321'),
(2,'Aula 102','pass123');
/*!40000 ALTER TABLE `aulas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `clases`
--

DROP TABLE IF EXISTS `clases`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `clases` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `aula_id` int(11) NOT NULL,
  `profesor_id` int(11) NOT NULL,
  `asignatura` varchar(100) DEFAULT '',
  `hora_inicio` datetime NOT NULL,
  `hora_fin` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `aula_id` (`aula_id`),
  KEY `profesor_id` (`profesor_id`),
  CONSTRAINT `clases_ibfk_1` FOREIGN KEY (`aula_id`) REFERENCES `aulas` (`id`),
  CONSTRAINT `clases_ibfk_2` FOREIGN KEY (`profesor_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clases`
--

LOCK TABLES `clases` WRITE;
/*!40000 ALTER TABLE `clases` DISABLE KEYS */;
INSERT INTO `clases` VALUES
(1,1,1,'ASLE','2025-03-01 08:00:00','2025-03-01 09:30:00'),
(2,1,1,'TD','2025-03-10 18:00:00','2025-03-10 20:00:00'),
(3,1,3,'ASLE','2025-03-31 19:00:00','2025-03-31 20:00:00'),
(4,1,3,'ASLE','2025-03-31 20:00:00','2025-03-31 21:00:00'),
(5,1,3,'ASLE','2025-03-31 21:30:00','2025-03-31 22:00:00'),
(6,1,3,'ASLE','2025-03-31 22:00:00','2025-03-31 23:00:00'),
(7,1,3,'ASLE','2025-03-31 21:43:00','2025-03-31 23:00:00'),
(8,1,3,'ASLE','2025-04-01 09:15:00','2025-04-01 09:35:00'),
(9,1,3,'ASLE','2025-04-01 10:00:00','2025-04-01 11:00:00'),
(10,1,3,'ASLE','2025-04-01 18:45:00','2025-04-01 19:00:00'),
(11,1,3,'ASLE','2025-04-01 18:57:00','2025-04-01 19:00:00'),
(12,1,3,'ASLE','2025-04-01 19:10:00','2025-04-01 19:30:00'),
(13,1,3,'ASLE','2025-04-01 19:28:00','2025-04-01 19:30:00'),
(14,1,3,'ASLE','2025-04-04 18:05:00','2025-04-04 18:30:00');
/*!40000 ALTER TABLE `clases` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `correo` varchar(100) DEFAULT '',
  `password` varchar(255) DEFAULT '',
  `uid_tarjeta` varchar(50) NOT NULL,
  `rol` enum('profesor','conserje','administrador') NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uid_tarjeta` (`uid_tarjeta`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES
(1,'Juan Pérez','juan.perez@example.com','pass123','ABC123456','profesor'),
(2,'María López','maria.lopez@example.com','pass456','DEF789012','conserje'),
(3,'Carlos Gómez','carlos.gomez@example.com','pass789','GHI345678','administrador'),
(4,'Pedro José Pardo Fernández','pjpardo@unex.es','pass123','46982502','profesor');
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2025-10-06 10:12:56
