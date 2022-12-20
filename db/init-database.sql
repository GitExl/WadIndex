CREATE DATABASE IF NOT EXISTS `idgames`;
USE `idgames`;

-- MySQL dump 10.13  Distrib 8.0.19, for Win64 (x86_64)
--
-- Host: localhost    Database: idgames
-- ------------------------------------------------------
-- Server version	5.5.5-10.6.8-MariaDB

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
-- Table structure for table `author`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `author` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` text COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9998 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `entry`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `entry` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `collection` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `path` varchar(127) COLLATE utf8mb4_unicode_ci NOT NULL,
  `file_modified` int(10) unsigned NOT NULL,
  `entry_updated` int(10) unsigned NOT NULL,
  `title` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `game` tinyint(4) DEFAULT NULL,
  `engine` tinyint(4) DEFAULT NULL,
  `is_singleplayer` tinyint(1) DEFAULT NULL,
  `is_cooperative` tinyint(1) DEFAULT NULL,
  `is_deathmatch` tinyint(1) DEFAULT NULL,
  `description` text COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description_preview` varchar(199) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `tools_used` text COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `known_bugs` text COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `credits` text COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `build_time` text COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `comments` text COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `entries_updated_IDX` (`entry_updated`) USING BTREE,
  KEY `entries_game_IDX` (`game`) USING BTREE,
  KEY `entry_engine_IDX` (`engine`) USING BTREE,
  KEY `entry_is_singleplayer_IDX` (`is_singleplayer`) USING BTREE,
  KEY `entry_is_cooperative_IDX` (`is_cooperative`) USING BTREE,
  KEY `entry_is_deathmatch_IDX` (`is_deathmatch`) USING BTREE,
  KEY `entry_collection_IDX` (`collection`,`path`) USING BTREE,
  FULLTEXT KEY `entry_path_IDX` (`path`,`title`)
) ENGINE=InnoDB AUTO_INCREMENT=19567 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `entry_authors`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `entry_authors` (
  `entry_id` int(10) unsigned NOT NULL,
  `author_id` int(10) unsigned NOT NULL,
  PRIMARY KEY (`entry_id`,`author_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `entry_images`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `entry_images` (
  `entry_id` int(10) unsigned NOT NULL,
  `name` varchar(27) COLLATE utf8mb4_unicode_ci NOT NULL,
  `width` smallint(5) unsigned NOT NULL,
  `height` smallint(5) unsigned NOT NULL,
  PRIMARY KEY (`entry_id`,`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `entry_levels`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `entry_levels` (
  `entry_id` int(10) unsigned NOT NULL,
  `name` char(8) COLLATE utf8mb4_unicode_ci NOT NULL,
  `title` varchar(1022) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `format` tinyint(4) NOT NULL,
  `line_count` int(10) unsigned NOT NULL,
  `side_count` int(10) unsigned NOT NULL,
  `thing_count` int(10) unsigned NOT NULL,
  `sector_count` int(10) unsigned NOT NULL,
  `allow_jump` tinyint(1) unsigned DEFAULT NULL,
  `allow_crouch` tinyint(1) unsigned DEFAULT NULL,
  `par_time` int(10) unsigned DEFAULT NULL,
  `music` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `next` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `next_secret` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `cluster` int(11) DEFAULT NULL,
  PRIMARY KEY (`entry_id`,`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `entry_music`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `entry_music` (
  `entry_id` int(10) unsigned NOT NULL,
  `music_id` int(10) unsigned NOT NULL,
  `name` varchar(27) NOT NULL,
  KEY `entry_music_entry_id_IDX` (`entry_id`,`name`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `entry_tags`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `entry_tags` (
  `entry_id` int(10) unsigned NOT NULL,
  `tag_id` int(10) unsigned NOT NULL,
  PRIMARY KEY (`entry_id`,`tag_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `entry_textfile`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `entry_textfile` (
  `entry_id` int(10) unsigned NOT NULL,
  `text` mediumtext COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`entry_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `music`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `music` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `type` varchar(8) NOT NULL,
  `hash` binary(20) NOT NULL,
  `author_id` int(10) unsigned DEFAULT NULL,
  `title` varchar(255) DEFAULT NULL,
  `duration` int(10) unsigned DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `music_hash_IDX` (`hash`) USING BTREE,
  KEY `music_author_id_IDX` (`author_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=12710 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tags`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `tags` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `key` varchar(32) NOT NULL,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`,`key`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping routines for database 'idgames'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-12-10 19:50:01
