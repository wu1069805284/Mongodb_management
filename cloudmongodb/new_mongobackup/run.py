#!/usr/bin/python
#coding=utf-8
#!/usr/local/bin/python
#coding=utf-8

from MySQLHandler import MySQLHandler
from ansible_execute import ansible_backup
from host_backup import host_check
from datetime import datetime,timedelta
from LogHandler import WriteLog
from Celery_proj.tasks import *
import config_backup
import random,time

Log=WriteLog()


def string_toDatetime(string):
        date=datetime.now()
        ymd=str(date.year) + '-' + str(date.month) + '-' + str(date.day)
        nowtime=ymd + ' ' + string
        return datetime.strptime(nowtime, "%Y-%m-%d %H:%M:%S") - timedelta(hours=8)


def get_host(ip_list):
	list=[]
	for i in ip_list:
		list.append((i[0]))
	Random=random.choice(list)
	return Random


def global_scheduling(): 
#	bak_host_info=host_check()
#	bak_host_info.mysql_append()
	mongo_info=config_backup.mongo_user_info()
	mysql_info=config_backup.mysql_user_info()
	myconn=MySQLHandler(mysql_info[0],mysql_info[1],mysql_info[2],mysql_info[3])
	data=myconn.get_mysql_data("select * from cloud_mongodb.tb_backup_mongodb_client where bak_switch='ON'")
	mongo_user=mongo_info[0]
	mongo_pw=mongo_info[1]
	ip_list = myconn.get_mysql_data('select distinct store_ipaddress from cloud_mongodb.tb_backup_mongodb_client;')
	for value in data:
		new_client=get_host(ip_list)
		client_config = { 	
					'id'	      : value[0],	
					'client_host' : value[1],
			  		'backup_host' : new_client,
			  		'client_port' : value[3],
			  		'backup_version' : value[5],
			  		'backup_clean_up' : value[6],
			  		'bak_switch'  : value[7],
			  		'Weeks_strategy' : value[8],
					'backup_time' : value[9]
				}
		try:
			max_path=myconn.get_mysql_data("select max(available_size_G) from cloud_mongodb.backup_host_infomation where statdate_time=CURDATE() and ipaddress='%s' limit 1;"%(client_config['backup_host']))
			bak_path=myconn.get_mysql_data("select mount_directory from cloud_mongodb.backup_host_infomation where statdate_time=CURDATE() and ipaddress='%s' and available_size_G='%s' limit 1;"%(client_config['backup_host'],max_path[0][0]))
			myconn.execute_sql("update cloud_mongodb.tb_backup_mongodb_client set store_ipaddress='%s',main_path='%s' where id=%s"%(client_config['backup_host'],bak_path[0][0],client_config['id']))

		except Exception as err:
			Log.write('e',"mysql host update : {}".format(err))	

		localtime=time.localtime()
		nowtime=time.strftime("%w",localtime)
		if nowtime not in client_config['Weeks_strategy']:
			log_msg="%s:%s On the same day than in the backup cycle"%(client_config['client_host'],client_config['client_port'])
			Log.write('w',"global_scheduling {}".format(log_msg))
		else:
			tabletime=client_config['backup_time'].strip()
			nowtabletime=string_toDatetime(tabletime)	
			backup=ansible_bak.apply_async(args=[mongo_user,mongo_pw,client_config['client_host'],client_config['backup_host'],client_config['client_port'],bak_path[0][0],client_config['backup_version'],client_config['backup_clean_up']],eta=nowtabletime)
			if backup:
				if backup.status in {'PENDING','STARTED','SUCCESS'}:

					log_msg='%s:%s > %s Start state to normal'%(backup.status,client_config['client_host'],client_config['client_port'])
					Log.write('i',"Celery tasks {}".format(log_msg))
				else:
					log_msg='%s:%s > %s The start state is not normal'%(backup.status,client_config['client_host'],client_config['client_port'])
					Log.write('e',"Celery tasks {}".format(log_msg))





if __name__ == '__main__':
	global_scheduling()
