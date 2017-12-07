-- MySQL dump 10.13  Distrib 5.5.35, for Linux (x86_64)
--
-- Host: 127.0.0.1    Database: cloud_mongodb
-- ------------------------------------------------------
-- Server version	5.5.35-rel33.0-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `tb_backup_mongodb_statistic`
--

DROP TABLE IF EXISTS `tb_backup_mongodb_statistic`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tb_backup_mongodb_statistic` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `objective_host` varchar(20) NOT NULL COMMENT '备份目标ip地址',
  `port` int(10) NOT NULL COMMENT '备份目标ip端口',
  `storage_machine` varchar(20) NOT NULL COMMENT '存储机ip地址',
  `backup_mode` varchar(20) NOT NULL COMMENT '备份方式',
  `backup_directory` varchar(100) NOT NULL COMMENT '备份的路径',
  `backup_status` varchar(10) NOT NULL COMMENT '备份状态值',
  `start_time` datetime NOT NULL COMMENT '备份开始时间',
  `finish_time` datetime NOT NULL COMMENT '备份结束时间',
  `statdate_time` date NOT NULL COMMENT '统计日期',
  `before_compress` varchar(10) DEFAULT NULL COMMENT '压缩前备份大小',
  `after_compress` varchar(10) DEFAULT NULL COMMENT '压缩后备份大小',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5357 DEFAULT CHARSET=utf8 COMMENT='备份日志状态信息';
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2017-07-05 14:59:41
