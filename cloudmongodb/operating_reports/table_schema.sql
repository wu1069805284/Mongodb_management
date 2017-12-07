CREATE TABLE `rp_mongodb_dbstatistics` (
  `id` bigint(10) unsigned NOT NULL AUTO_INCREMENT,
  `iGId` varchar(50) NOT NULL COMMENT '实例所属集群组编号',
  `host` varchar(20) NOT NULL COMMENT '实例ip地址',
  `port` int(10) NOT NULL COMMENT '实例端口',
  `role` varchar(10) NOT NULL COMMENT '角色',
  `dbname` varchar(30) NOT NULL COMMENT '数据库名称',
  `dbsize` varchar(10) NOT NULL COMMENT '数据库大小，单位为G',
  `collections` int(5) NOT NULL COMMENT '当前数据库的集合数量',
  `objects` bigint(20) NOT NULL COMMENT '表示当前数据库所有collection总共有多少行数据,显示的数据是一个估计值',
  `avgObjSize` int(5) NOT NULL COMMENT '每行数据大小估值',
  `dataSize` bigint(20) NOT NULL COMMENT '表示当前数据库所有数据的总大小，不是指占有磁盘大小',
  `storageSize` bigint(20) NOT NULL COMMENT '表示当前数据库占有磁盘大小,加上预分配空间',
  `Indexnumber` int(10) NOT NULL COMMENT '索引表数据行数',
  `Indexsize` bigint(20) NOT NULL COMMENT '表示索引占有磁盘大小',
  `detailed_time` datetime NOT NULL COMMENT '当天写入的详细时间',
  `day_timedate` date NOT NULL COMMENT '当天写入的当天时间',
  PRIMARY KEY (`id`),
  KEY `Inx_hp` (`host`,`port`),
  KEY `Inx_igid` (`iGId`)
) ENGINE=InnoDB AUTO_INCREMENT=256316 DEFAULT CHARSET=utf8 COMMENT='mongodb库信息统计';

CREATE TABLE `rp_mongodb_globalstats` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `global_QPS` bigint(20) NOT NULL DEFAULT '0' COMMENT '今日总QPS[所有集群组]',
  `global_TPS` bigint(20) NOT NULL DEFAULT '0' COMMENT '今日总TPS[所有集群组]',
  `global_command` bigint(20) NOT NULL DEFAULT '0' COMMENT '今日总command query[所有集群组]',
  `global_Select` bigint(20) NOT NULL DEFAULT '0' COMMENT '今日总Select[所有集群组]',
  `global_Insert` bigint(20) NOT NULL DEFAULT '0' COMMENT '今日总Insert[所有集群组]',
  `global_Update` bigint(20) NOT NULL DEFAULT '0' COMMENT '今日总Upate[所有集群组]',
  `global_Delete` bigint(20) NOT NULL DEFAULT '0' COMMENT '今日总Delete[所有集群组]',
  `statDate` date DEFAULT NULL COMMENT '统计日期',
  `stateTime` datetime DEFAULT NULL COMMENT '统计时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_statDate` (`statDate`)
) ENGINE=InnoDB AUTO_INCREMENT=231 DEFAULT CHARSET=utf8 COMMENT='MySQL集群全局统计汇总表';

CREATE TABLE `rp_mongodb_instancestatistics` (
  `id` bigint(10) unsigned NOT NULL AUTO_INCREMENT,
  `iGId` varchar(50) NOT NULL COMMENT '实例所属集群组编号',
  `host` varchar(20) NOT NULL COMMENT '实例ip地址',
  `port` int(10) NOT NULL COMMENT '实例端口',
  `role` varchar(10) NOT NULL COMMENT '角色',
  `dbname` varchar(30) NOT NULL COMMENT '数据库名称',
  `dbsize` varchar(10) NOT NULL COMMENT '数据库大小，单位为G',
  `dbempty` varchar(10) NOT NULL COMMENT '检查所属db是否为空，状态值为True与False',
  `dbtonumber` int(10) NOT NULL DEFAULT '0' COMMENT '实实例中db的总数量',
  `dbtosize` int(10) NOT NULL DEFAULT '0' COMMENT '实例中db的总大小,单位为G',
  `detailed_time` datetime NOT NULL COMMENT '当天写入的详细时间',
  `day_timedate` date NOT NULL COMMENT '当天写入的当天时间',
  PRIMARY KEY (`id`),
  KEY `Inx_hp` (`host`,`port`),
  KEY `Inx_igid` (`iGId`)
) ENGINE=InnoDB AUTO_INCREMENT=281934 DEFAULT CHARSET=utf8 COMMENT='mongodb实例信息统计';

CREATE TABLE `rp_mongodb_statusstatistics` (
  `id` bigint(10) unsigned NOT NULL AUTO_INCREMENT,
  `iGId` varchar(50) NOT NULL COMMENT '实例所属集群组编号',
  `host` varchar(20) NOT NULL COMMENT '实例ip地址',
  `port` int(10) NOT NULL COMMENT '实例端口',
  `role` varchar(10) NOT NULL COMMENT '角色',
  `qtotal` bigint(10) NOT NULL COMMENT '单实例查询总量',
  `yqtotal` bigint(10) NOT NULL COMMENT '单实例昨日查询总量',
  `qday` bigint(10) NOT NULL COMMENT '当日产生的查询量',
  `utotal` bigint(10) NOT NULL COMMENT '单实例更新总量',
  `yutotal` bigint(10) NOT NULL COMMENT '单实例昨日更新总量',
  `uday` bigint(10) NOT NULL COMMENT '当日产生的更新量',
  `itotal` bigint(10) NOT NULL COMMENT '单实例插入总量',
  `yitotal` bigint(10) NOT NULL COMMENT '单实例昨日插入总量',
  `iday` bigint(10) NOT NULL COMMENT '当日产生的插入量',
  `dtotal` bigint(10) NOT NULL COMMENT '单实例删除总量',
  `ydtotal` bigint(10) NOT NULL COMMENT '单实例昨日插入总量',
  `dday` bigint(10) NOT NULL COMMENT '当日产生的删除量',
  `qcommand` bigint(20) NOT NULL DEFAULT '0' COMMENT '单实例command总量',
  `ycommand` bigint(20) NOT NULL DEFAULT '0' COMMENT '昨日单实例command总量',
  `daycommand` bigint(20) NOT NULL DEFAULT '0' COMMENT '当日单实例command总量',
  `total_qps_cluster` bigint(12) NOT NULL DEFAULT '0' COMMENT '对应的集群qps总量',
  `detailed_time` datetime NOT NULL COMMENT '当天写入的详细时间',
  `day_timedate` date NOT NULL COMMENT '当天写入的当天时间',
  PRIMARY KEY (`id`),
  KEY `Inx_hp` (`host`,`port`),
  KEY `Inx_igid` (`iGId`)
) ENGINE=InnoDB AUTO_INCREMENT=24948 DEFAULT CHARSET=utf8 COMMENT='流量统计表';

