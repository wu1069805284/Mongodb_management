#!/usr/bin/python
#!/usr/bin/python
#coding=utf-8
#!/usr/local/bin/python
#coding=utf-8

import os,sys
import subprocess
import linecache
from MySQLHandler import MySQLHandler as mysql_conn
from pymongo import MongoClient


def mysql_export():
	try:
		conn = mysql_conn('127.0.0.1',3302)	
		info = conn.get_mysql_data("select * from cloud_mongodb.rp_mongodb_dbstatistics where day_timedate='2017-03-08'")
		return(info)
	
	except Exception as e:
		print e


def mongo_import():
	try:
		command = '''/opt/soft/mongodb3210/bin/mongo %s:%s/%s --eval "db.getCollectionInfos()" ''' %('localhost','2600','wuweijian')
		tablelist = subprocess.check_call(command,shell=True)
		a = linecache.getline(tablelist,2)
		#a=str(tablelist).split("[")[1].split("]")[0]
		print a

	except Exception as e:
		print e

if __name__ == '__main__':
#	mysql_export()
	mongo_import()

