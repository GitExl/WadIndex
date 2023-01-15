-- MariaDB dump 10.19  Distrib 10.10.2-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: idgames
-- ------------------------------------------------------
-- Server version 10.10.2-MariaDB-1:10.10.2+maria~ubu2204

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `authors`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `authors` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` text NOT NULL,
  `full_name` varchar(255) DEFAULT NULL,
  `nickname` varchar(127) DEFAULT NULL,
  `path_alias` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `directories`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `directories` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `parent_id` int(10) unsigned DEFAULT NULL,
  `collection` varchar(15) NOT NULL,
  `path` varchar(127) NOT NULL,
  `name` varchar(31) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `directories_collection_IDX` (`collection`,`path`) USING BTREE,
  KEY `directories_parent_id_IDX` (`parent_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `entry`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `entry` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `collection` varchar(15) NOT NULL,
  `path` varchar(127) NOT NULL,
  `directory_id` int(10) unsigned DEFAULT NULL,
  `file_modified` int(10) unsigned NOT NULL,
  `file_size` int(10) unsigned NOT NULL,
  `entry_updated` int(10) unsigned NOT NULL,
  `title` varchar(255) DEFAULT NULL,
  `game` tinyint(4) NOT NULL DEFAULT 0,
  `engine` tinyint(4) NOT NULL DEFAULT 0,
  `is_singleplayer` tinyint(1) DEFAULT NULL,
  `is_cooperative` tinyint(1) DEFAULT NULL,
  `is_deathmatch` tinyint(1) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `description_preview` varchar(199) DEFAULT NULL,
  `tools_used` text DEFAULT NULL,
  `known_bugs` text DEFAULT NULL,
  `credits` text DEFAULT NULL,
  `build_time` text DEFAULT NULL,
  `comments` text DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `entries_updated_IDX` (`entry_updated`) USING BTREE,
  KEY `entries_game_IDX` (`game`) USING BTREE,
  KEY `entry_engine_IDX` (`engine`) USING BTREE,
  KEY `entry_is_singleplayer_IDX` (`is_singleplayer`) USING BTREE,
  KEY `entry_is_cooperative_IDX` (`is_cooperative`) USING BTREE,
  KEY `entry_is_deathmatch_IDX` (`is_deathmatch`) USING BTREE,
  KEY `entry_directory_id_IDX` (`directory_id`) USING BTREE,
  KEY `entry_collection_IDX` (`collection`,`path`) USING BTREE,
  FULLTEXT KEY `entry_path_ft_IDX` (`path`),
  FULLTEXT KEY `entry_title_ft_IDX` (`title`),
  FULLTEXT KEY `entry_description_ft_IDX` (`description`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `entry_authors`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `entry_images` (
  `entry_id` int(10) unsigned NOT NULL,
  `name` varchar(27) NOT NULL,
  `width` smallint(5) unsigned NOT NULL,
  `height` smallint(5) unsigned NOT NULL,
  `is_primary` tinyint(3) unsigned NOT NULL DEFAULT 0,
  PRIMARY KEY (`entry_id`,`name`),
  KEY `entry_images_is_primary_IDX` (`is_primary`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `entry_music`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `entry_music` (
  `entry_id` int(10) unsigned NOT NULL,
  `music_id` int(10) unsigned NOT NULL,
  `name` varchar(27) NOT NULL,
  KEY `entry_music_entry_id_IDX` (`entry_id`,`name`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `entry_textfile`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `entry_textfile` (
  `entry_id` int(10) unsigned NOT NULL,
  `text` mediumtext NOT NULL,
  PRIMARY KEY (`entry_id`),
  FULLTEXT KEY `entry_ft_IDX` (`text`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `map_authors`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `map_authors` (
  `map_id` int(10) unsigned NOT NULL,
  `author_id` int(10) unsigned NOT NULL,
  PRIMARY KEY (`map_id`,`author_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `maps`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `maps` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `entry_id` int(10) unsigned NOT NULL,
  `name` char(8) NOT NULL,
  `title` varchar(1022) DEFAULT NULL,
  `format` tinyint(4) NOT NULL,
  `line_count` int(10) unsigned NOT NULL,
  `side_count` int(10) unsigned NOT NULL,
  `thing_count` int(10) unsigned NOT NULL,
  `sector_count` int(10) unsigned NOT NULL,
  `allow_jump` tinyint(1) unsigned DEFAULT NULL,
  `allow_crouch` tinyint(1) unsigned DEFAULT NULL,
  `par_time` int(10) unsigned DEFAULT NULL,
  `music` varchar(255) DEFAULT NULL,
  `next` varchar(255) DEFAULT NULL,
  `next_secret` varchar(255) DEFAULT NULL,
  `cluster` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `maps_entry_id_IDX` (`entry_id`,`name`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `music`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE IF NOT EXISTS `music` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `type` varchar(8) NOT NULL,
  `hash` binary(20) NOT NULL,
  `duration` int(10) unsigned DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `music_hash_IDX` (`hash`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-01-15 10:10:27
