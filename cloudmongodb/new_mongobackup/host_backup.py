#!/usr/bin/python
from config_backup import mysql_user_info
from MySQLHandler import MySQLHandler
from LogHandler import WriteLog 
from ansible import runner
import json

class host_check(object):
	
	def __init__(self):
		self.Log=WriteLog()
		self.mysql_info=mysql_user_info()
		self.muser=self.mysql_info[0]
		self.mhost=self.mysql_info[1]
		self.mport=self.mysql_info[2]
		self.mpw=self.mysql_info[3]
		self.conn=MySQLHandler(self.muser,self.mhost,self.mport,self.mpw)

	def get_hostinfo(self):
		data = []
		get_info = self.conn.get_mysql_data('select ipaddress from cloud_mongodb.backup_mongo_status;')
		for host in get_info:
			ip=host[0]
			if ip:
				results = runner.Runner(
						module_name='setup',
#						module_args='filter=ansible_mounts',
						pattern='%s'%(ip),
						forks=10
						)
				dt = results.run()
				pt=dt['contacted'][ip]['ansible_facts']['ansible_mounts']
				for key in pt:
					partition=key['device']
					mount_disk=key['mount']
					Available_size=key['size_available']
					total_size=key['size_total']
					hostname_pub = dt['contacted'][ip]['ansible_facts']['ansible_nodename']
					ipadd_in = dt['contacted'][ip]['ansible_facts']['ansible_all_ipv4_addresses'][0]
					if mount_disk not in {'/','/boot','/dev/shm','/opt'}:
						data.append((hostname_pub,ipadd_in,partition,mount_disk,total_size,Available_size))
		return data				


	def ansible_script(self):
		
		get_host_info = self.conn.get_mysql_data('select ipaddress from cloud_mongodb.backup_mongo_status;')

		for host in get_host_info:
			ip = host[0]
			results = runner.Runner(
                                                module_name='script',
                                                module_args='/work/wuweijian/cloudmongodb/new_mongobackup/ceshi.sh',
                                                pattern='%s'%(ip),
                                                forks=10
                                                )
			dt = results.run()
		return dt

	def mysql_append(self):

		try:
			sql='''
                insert into cloud_mongodb.backup_host_infomation(hostname,ipaddress,partition,mount_directory,total_size_G,available_size_G,add_time,statdate_time) values ('%s','%s','%s','%s',%s/1024/1024/1024,%s/1024/1024/1024,now(),CURDATE());
                '''
			self.conn.execute_sql("delete from cloud_mongodb.backup_host_infomation where statdate_time=CURDATE()")

			for sql_info in self.get_hostinfo():
				if sql_info:
					info=sql %(sql_info)
					self.conn.execute_sql(info)
			


		except Exception as err:
			self.Log.write('e',"mysql_append {}".format(err))


