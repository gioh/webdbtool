-- --------------------------------------------------------
-- 主机:                           192.168.203.128
-- 服务器版本:                        5.1.73 - Source distribution
-- 服务器操作系统:                      redhat-linux-gnu
-- HeidiSQL 版本:                  8.3.0.4694
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;

-- 导出 config4oracle 的数据库结构
CREATE DATABASE IF NOT EXISTS `config4oracle` /*!40100 DEFAULT CHARACTER SET latin1 */;
USE `config4oracle`;


-- 导出  表 config4oracle.T_DB_APPS 结构
CREATE TABLE IF NOT EXISTS `T_DB_APPS` (
  `app_id` int(12) NOT NULL AUTO_INCREMENT,
  `app_code` varchar(20) DEFAULT NULL,
  `app_name` varchar(100) DEFAULT NULL,
  `app_manager` varchar(100) DEFAULT NULL,
  `state` int(2) DEFAULT NULL,
  `create_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `creator` int(12) DEFAULT NULL,
  `last_update_date` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `modifier` int(12) DEFAULT NULL,
  `remark` varchar(500) DEFAULT NULL,
  `plat_id` int(12) DEFAULT NULL,
  PRIMARY KEY (`app_id`)
) ENGINE=InnoDB AUTO_INCREMENT=10004 DEFAULT CHARSET=utf8 COMMENT='项目配置表';

-- 正在导出表  config4oracle.T_DB_APPS 的数据：~2 rows (大约)
DELETE FROM `T_DB_APPS`;
/*!40000 ALTER TABLE `T_DB_APPS` DISABLE KEYS */;
INSERT INTO `T_DB_APPS` (`app_id`, `app_code`, `app_name`, `app_manager`, `state`, `create_date`, `creator`, `last_update_date`, `modifier`, `remark`, `plat_id`) VALUES
	(10000, 'test_app', 'test_1', 'luozj', 1, '2015-08-19 21:09:56', 10000, '0000-00-00 00:00:00', NULL, NULL, 10000),
	(10003, 'test_app2', 'test_app2', 'luozj', 1, '2015-08-24 16:37:12', 10001, '0000-00-00 00:00:00', NULL, NULL, 10002);
/*!40000 ALTER TABLE `T_DB_APPS` ENABLE KEYS */;


-- 导出  表 config4oracle.T_DB_DATABASES 结构
CREATE TABLE IF NOT EXISTS `T_DB_DATABASES` (
  `database_id` int(12) NOT NULL AUTO_INCREMENT,
  `db_name_en` varchar(20) DEFAULT NULL,
  `db_unique_name` varchar(50) DEFAULT NULL,
  `db_global_name` varchar(50) DEFAULT NULL,
  `db_name_cn` varchar(50) DEFAULT NULL,
  `db_type` int(2) DEFAULT NULL COMMENT '数据库类型 1）开发库 2）业务测试库 3）综合测试库 4）功能测试库 5）迁移库 9）正式库',
  `db_version` varchar(20) DEFAULT NULL,
  `app_id` int(12) DEFAULT NULL,
  `is_cluster` int(2) DEFAULT NULL,
  `is_archivelog` int(2) DEFAULT NULL,
  `is_dataguard` int(2) DEFAULT NULL,
  `os_platform` varchar(50) DEFAULT NULL COMMENT '操作系统平台',
  `db_info` varchar(2000) DEFAULT NULL,
  `state` int(2) DEFAULT NULL,
  `create_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `creator` int(12) DEFAULT NULL,
  `last_update_date` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `modifier` int(12) DEFAULT NULL,
  `remark` varchar(500) DEFAULT NULL,
  `db_master` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`database_id`)
) ENGINE=InnoDB AUTO_INCREMENT=10005 DEFAULT CHARSET=utf8 COMMENT='数据库配置表';

-- 正在导出表  config4oracle.T_DB_DATABASES 的数据：~5 rows (大约)
DELETE FROM `T_DB_DATABASES`;
/*!40000 ALTER TABLE `T_DB_DATABASES` DISABLE KEYS */;
INSERT INTO `T_DB_DATABASES` (`database_id`, `db_name_en`, `db_unique_name`, `db_global_name`, `db_name_cn`, `db_type`, `db_version`, `app_id`, `is_cluster`, `is_archivelog`, `is_dataguard`, `os_platform`, `db_info`, `state`, `create_date`, `creator`, `last_update_date`, `modifier`, `remark`, `db_master`) VALUES
	(10000, 'test_db1', 'test_db1', 'test__db1', '测试库1', 1, '11.2.0.2', 10000, 0, 1, 0, 'linux 32bit', NULL, 1, '2015-08-21 14:09:51', 10000, '0000-00-00 00:00:00', NULL, NULL, '罗灼军'),
	(10001, 'vv1', 'vv', NULL, 'vv', 1, 'vv', 10003, 0, 0, 0, 'vv', NULL, 1, '2015-08-24 15:14:46', 10001, '0000-00-00 00:00:00', NULL, NULL, 'dsadf'),
	(10002, 'vv2', 'vv', NULL, 'vv', 1, 'vv', 10003, 0, 0, 0, 'vv', NULL, 1, '2015-08-24 15:20:15', 10001, '0000-00-00 00:00:00', NULL, NULL, 'saf'),
	(10003, 'vv3', 'vv', NULL, 'vv', 1, 'vv', 10000, 0, 0, 0, 'vv', NULL, 1, '2015-08-24 15:27:06', 10001, '0000-00-00 00:00:00', NULL, NULL, 'dsdsfd'),
	(10004, 'vv4', 'vv', NULL, 'vv', 1, 'vv', 10000, 0, 0, 0, 'vv', NULL, 1, '2015-08-24 15:40:53', 10001, '0000-00-00 00:00:00', NULL, NULL, 'luozj111');
/*!40000 ALTER TABLE `T_DB_DATABASES` ENABLE KEYS */;


-- 导出  表 config4oracle.T_DB_INSTANCES 结构
CREATE TABLE IF NOT EXISTS `T_DB_INSTANCES` (
  `instance_id` int(12) NOT NULL AUTO_INCREMENT,
  `database_id` int(12) DEFAULT NULL,
  `IP` varchar(50) DEFAULT NULL,
  `listen_port` varchar(5) DEFAULT NULL,
  `instance_name` varchar(20) DEFAULT NULL,
  `service_name` varchar(20) DEFAULT NULL,
  `is_cluster` int(2) DEFAULT NULL,
  `inst_id` int(2) DEFAULT NULL,
  `host_name` varchar(50) DEFAULT NULL,
  `instance_version` varchar(20) DEFAULT NULL,
  `startup_time` datetime DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  `instance_info` varchar(2000) DEFAULT NULL,
  `state` int(2) DEFAULT NULL,
  `create_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `creator` int(12) DEFAULT NULL,
  `last_update_date` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `modifier` int(12) DEFAULT NULL,
  `remark` varchar(500) DEFAULT NULL,
  `os_oracle_username` varchar(50) DEFAULT NULL,
  `os_oracle_password` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`instance_id`)
) ENGINE=InnoDB AUTO_INCREMENT=10019 DEFAULT CHARSET=utf8 COMMENT='数据库实例配置表';

-- 正在导出表  config4oracle.T_DB_INSTANCES 的数据：~4 rows (大约)
DELETE FROM `T_DB_INSTANCES`;
/*!40000 ALTER TABLE `T_DB_INSTANCES` DISABLE KEYS */;
INSERT INTO `T_DB_INSTANCES` (`instance_id`, `database_id`, `IP`, `listen_port`, `instance_name`, `service_name`, `is_cluster`, `inst_id`, `host_name`, `instance_version`, `startup_time`, `status`, `instance_info`, `state`, `create_date`, `creator`, `last_update_date`, `modifier`, `remark`, `os_oracle_username`, `os_oracle_password`) VALUES
	(10000, 10000, '192.168.203.128', '1521', 'orc1', 'orc1', 0, 1, 'localhost.localdomain', '11.2.0.2', '2015-08-21 14:12:49', 'opened', NULL, 1, '2015-08-21 14:13:03', 10000, '0000-00-00 00:00:00', NULL, NULL, NULL, NULL),
	(10016, 10002, '192.168.203.128', '1521', 'orc1', NULL, 0, 1, 'vv', 'vv', NULL, NULL, NULL, 1, '2015-08-24 17:37:08', 10001, '0000-00-00 00:00:00', NULL, NULL, 'oracle', 'oracle'),
	(10017, 10003, '192.168.203.128', '1521', 'orc1', NULL, 0, 1, 'vv', 'vv', NULL, NULL, NULL, 1, '2015-08-24 17:44:15', 10001, '0000-00-00 00:00:00', NULL, NULL, 'oracle', 'oracle'),
	(10018, 10004, '192.168.203.128', '1521', 'orc1', NULL, 0, 1, 'vv', 'vv', NULL, NULL, NULL, 1, '2015-08-24 18:01:39', 10001, '0000-00-00 00:00:00', NULL, NULL, 'oracle', 'oracle');
/*!40000 ALTER TABLE `T_DB_INSTANCES` ENABLE KEYS */;


-- 导出  表 config4oracle.T_DB_PLATS 结构
CREATE TABLE IF NOT EXISTS `T_DB_PLATS` (
  `plat_id` int(12) NOT NULL AUTO_INCREMENT,
  `plat_code` varchar(20) DEFAULT NULL,
  `plat_name` varchar(50) DEFAULT NULL,
  `plat_manager` varchar(50) DEFAULT NULL,
  `state` int(2) DEFAULT NULL,
  `create_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `creator` int(12) DEFAULT NULL,
  `last_update_date` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `modifier` int(12) DEFAULT NULL,
  `remark` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`plat_id`)
) ENGINE=InnoDB AUTO_INCREMENT=10006 DEFAULT CHARSET=utf8 COMMENT='平台配置表';

-- 正在导出表  config4oracle.T_DB_PLATS 的数据：~6 rows (大约)
DELETE FROM `T_DB_PLATS`;
/*!40000 ALTER TABLE `T_DB_PLATS` DISABLE KEYS */;
INSERT INTO `T_DB_PLATS` (`plat_id`, `plat_code`, `plat_name`, `plat_manager`, `state`, `create_date`, `creator`, `last_update_date`, `modifier`, `remark`) VALUES
	(10000, 'CESHI-001', '数据部', 'luozj', 1, '2015-08-21 14:14:33', 10000, '0000-00-00 00:00:00', NULL, NULL),
	(10001, 'CESHI-002', '研发一部', 'luozj', 1, '2015-08-21 14:14:33', 10000, '0000-00-00 00:00:00', NULL, NULL),
	(10002, 'CESHI-003', '研发二部', 'luozj', 1, '2015-08-21 14:14:33', 10000, '0000-00-00 00:00:00', NULL, NULL),
	(10003, 'CESHI-004', '研发三部', 'luozj', 1, '2015-08-21 14:14:33', 10000, '0000-00-00 00:00:00', NULL, NULL),
	(10004, 'CESHI-005', '云服务部', 'luozj', 1, '2015-08-21 14:14:33', 10000, '0000-00-00 00:00:00', NULL, NULL),
	(10005, 'CESHI-005', 'LITC', 'luozj', 1, '2015-08-21 14:14:33', 10000, '0000-00-00 00:00:00', NULL, NULL);
/*!40000 ALTER TABLE `T_DB_PLATS` ENABLE KEYS */;


-- 导出  表 config4oracle.T_DB_ROLES 结构
CREATE TABLE IF NOT EXISTS `T_DB_ROLES` (
  `role_id` int(12) NOT NULL AUTO_INCREMENT,
  `role_name_en` varchar(20) DEFAULT NULL,
  `role_name_cn` varchar(50) DEFAULT NULL,
  `app_id` int(12) DEFAULT NULL,
  `plat_id` int(12) DEFAULT NULL,
  `role_type` varchar(2) DEFAULT NULL COMMENT '角色所属类型 1）ROOT_DBA 2）PLAT_DBA 3）APP_DBA 4）COMMON_USER（暂不用）',
  `priority` varchar(2) DEFAULT NULL,
  `state` int(2) DEFAULT NULL,
  `create_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `creator` int(12) DEFAULT NULL,
  `last_update_date` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `modifier` int(12) DEFAULT NULL,
  `remark` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`role_id`)
) ENGINE=InnoDB AUTO_INCREMENT=10009 DEFAULT CHARSET=utf8 COMMENT='角色配置表';

-- 正在导出表  config4oracle.T_DB_ROLES 的数据：~4 rows (大约)
DELETE FROM `T_DB_ROLES`;
/*!40000 ALTER TABLE `T_DB_ROLES` DISABLE KEYS */;
INSERT INTO `T_DB_ROLES` (`role_id`, `role_name_en`, `role_name_cn`, `app_id`, `plat_id`, `role_type`, `priority`, `state`, `create_date`, `creator`, `last_update_date`, `modifier`, `remark`) VALUES
	(10000, 'root_dba_role', '根DBA', NULL, NULL, '1', '10', 1, '2015-08-21 14:18:48', 10000, '0000-00-00 00:00:00', NULL, NULL),
	(10001, 'test_app_dba', '测试库DBA', 10000, NULL, '3', '10', 1, '2015-08-21 14:45:58', 10000, '0000-00-00 00:00:00', NULL, NULL),
	(10002, 'test_app_dba_2', '测试库DBA2', NULL, 10001, '2', '10', 1, '2015-08-25 09:51:53', 10000, '0000-00-00 00:00:00', NULL, NULL),
	(10008, 'test_app_dba_3', '测试库DBA3', 10003, NULL, '3', '10', 1, '2015-08-26 12:08:23', 10000, '0000-00-00 00:00:00', NULL, NULL);
/*!40000 ALTER TABLE `T_DB_ROLES` ENABLE KEYS */;


-- 导出  表 config4oracle.T_DB_USERS 结构
CREATE TABLE IF NOT EXISTS `T_DB_USERS` (
  `user_id` int(12) NOT NULL AUTO_INCREMENT,
  `user_name_en` varchar(20) DEFAULT NULL,
  `user_name_ch` varchar(50) DEFAULT NULL,
  `password` varchar(50) DEFAULT NULL,
  `email` varchar(200) DEFAULT NULL,
  `state` int(2) DEFAULT NULL,
  `create_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `creator` int(12) DEFAULT NULL,
  `last_update_date` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `modifier` int(12) DEFAULT NULL,
  `remark` varchar(500) DEFAULT NULL,
  `dept_id` int(12) DEFAULT NULL,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=10008 DEFAULT CHARSET=utf8 COMMENT='用户配置表';

-- 正在导出表  config4oracle.T_DB_USERS 的数据：~3 rows (大约)
DELETE FROM `T_DB_USERS`;
/*!40000 ALTER TABLE `T_DB_USERS` DISABLE KEYS */;
INSERT INTO `T_DB_USERS` (`user_id`, `user_name_en`, `user_name_ch`, `password`, `email`, `state`, `create_date`, `creator`, `last_update_date`, `modifier`, `remark`, `dept_id`) VALUES
	(10000, 'root_dba', 'rootdba管理员', '05a671c66aefea124cc08b76ea6d30bb', NULL, 1, '2015-08-19 21:09:15', 10000, '0000-00-00 00:00:00', NULL, NULL, 10001),
	(10001, 'dba', 'dba管理员', '05a671c66aefea124cc08b76ea6d30bb', NULL, 1, '2015-08-21 14:43:13', 10000, '0000-00-00 00:00:00', NULL, NULL, 10000),
	(10007, 'test', 'testttt', 'eab42973d676d4de4bd8b9ceb2636b7b', 'asdf', 1, '2015-08-26 09:58:16', 10000, '0000-00-00 00:00:00', NULL, NULL, 10001);
/*!40000 ALTER TABLE `T_DB_USERS` ENABLE KEYS */;


-- 导出  表 config4oracle.T_USER_ROLE_REL 结构
CREATE TABLE IF NOT EXISTS `T_USER_ROLE_REL` (
  `t_id` int(12) NOT NULL AUTO_INCREMENT,
  `user_id` int(12) DEFAULT NULL,
  `role_id` int(12) DEFAULT NULL,
  `state` int(2) DEFAULT NULL,
  `create_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `creator` int(12) DEFAULT NULL,
  `last_update_date` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `modifier` int(12) DEFAULT NULL,
  `remark` varchar(500) DEFAULT NULL,
  `IS_DEFAULT` int(2) DEFAULT NULL,
  PRIMARY KEY (`t_id`)
) ENGINE=InnoDB AUTO_INCREMENT=10012 DEFAULT CHARSET=utf8 COMMENT='用户角色关系表';

-- 正在导出表  config4oracle.T_USER_ROLE_REL 的数据：~6 rows (大约)
DELETE FROM `T_USER_ROLE_REL`;
/*!40000 ALTER TABLE `T_USER_ROLE_REL` DISABLE KEYS */;
INSERT INTO `T_USER_ROLE_REL` (`t_id`, `user_id`, `role_id`, `state`, `create_date`, `creator`, `last_update_date`, `modifier`, `remark`, `IS_DEFAULT`) VALUES
	(10000, 10000, 10000, 1, '2015-08-21 14:15:40', 10000, '0000-00-00 00:00:00', NULL, NULL, 1),
	(10001, 10001, 10001, 1, '2015-08-21 14:45:43', 10000, '0000-00-00 00:00:00', NULL, NULL, 1),
	(10002, 10001, 10002, 1, '2015-08-25 09:23:37', 10000, '0000-00-00 00:00:00', NULL, NULL, 0),
	(10007, 10006, 10002, 1, '2015-08-26 09:57:13', 10000, '0000-00-00 00:00:00', NULL, NULL, 1),
	(10008, 10007, 10002, 1, '2015-08-26 09:58:16', 10000, '0000-00-00 00:00:00', NULL, NULL, 1),
	(10011, 10001, 10008, 1, '2015-08-26 20:55:31', 10000, '0000-00-00 00:00:00', NULL, NULL, 0);
/*!40000 ALTER TABLE `T_USER_ROLE_REL` ENABLE KEYS */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IF(@OLD_FOREIGN_KEY_CHECKS IS NULL, 1, @OLD_FOREIGN_KEY_CHECKS) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
