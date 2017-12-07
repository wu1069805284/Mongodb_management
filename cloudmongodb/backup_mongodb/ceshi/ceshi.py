#!/bin/env python
#-*- encoding=utf8 -*-
import os,sys,json,MySQLdb
#print "__file__=%s" % __file__
#print "os.path.realpath(__file__)=%s" % os.path.realpath(__file__)
#print "os.path.dirname(os.path.realpath(__file__))=%s" % os.path.dirname(os.path.realpath(__file__))
#print "os.path.abspath(__file__)=%s" % os.path.abspath(__file__)
#print "os.getcwd()=%s" % os.getcwd()
#print "sys.path[0]=%s" % sys.path[0]
#print "sys.argv[0]=%s" % sys.argv[0]
#print os.path.abspath(os.path.join(os.path.dirname("__file__"),os.path.pardir))


conn=MySQLdb.connect(user='root',passwd='backup',host='127.0.0.1',db='cloud_mongodb',port=3302)
cur=conn.cursor()
sql='select * from backup_client_infomation'
sql01='select max(available_size_G) from backup_host_infomation where ipaddress=%s and statdate_time=CURRENT_DATE ;'
sql02='select mount_directory from backup_host_infomation where ipaddress="%s" and available_size_G=%s limit 1;'
cur.execute("select ipaddress from backup_mongo_status where execution_status=0;")
update_ip=cur.fetchone()
cur.execute(sql01,update_ip)
available=cur.fetchone()
cur.execute(sql02 %(update_ip[0], available[0]))
min_directory=cur.fetchone()
cur.execute('update backup_client_infomation set main_path="%s" ;' %min_directory[0])
cur.execute(sql)
result=cur.fetchall()
for value in result:
	backup_directory=str(value[3]) + '/' + str(value[2])
	cur.execute('')
#print update_ip[0],available[0]
#result=cur.fetchall()
#for value in result:
conn.cckup_directoryommit()
cur.close()
