#!/usr/bin/python
#!/usr/bin/python
#coding=utf-8
#!/usr/local/bin/python
#coding=utf-8

import re
import os
import sys
import time
import json
import MySQLdb
import logging



class WriteLog(object):

    def write(self,log_status,log_msg):
        logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s [%(levelname)s] %(message)s',
                datefmt='%Y-%m-%d %X',
                filename='/work/wuweijian/cloudmongodb/backup_mongodb/script/backup_general_log',
                filemode='a')

        if log_status == 'i':
                logging.info(log_msg)
        if log_status == 'e':
                logging.error(log_msg)


class DB_Initialize(object):

	def __init__(self,host,port,db):
		self.Log = WriteLog()
    		self.host = host
    		self.port = int(port)
    		self.database = db
		self.user = 'wcdb_admin'
    		self.pw = '2262acef336ce54a'
		
		_failed_times = 0
	 	
		while True:
     			try:
         			self.con_db = MySQLdb.connect(host=self.host,port=self.port,user=self.user,passwd=self.pw,db=self.database)
         			self.con_db.autocommit(1)
         			self.cursor = self.con_db.cursor()
     			except Exception as e:
         			_failed_times += 1
         			if _failed_times >= 3:
		             		print e
             				log_msg = "%s:%s %s" % (self.host,self.port,e)
             				self.Log.write('e',log_msg)
         			else:
             				continue
		
			break 	
	
	def backuptime_operation(self):
		
		try:
			self.cursor = self.con_db.cursor()
			self.cursor.execute("update db58_wcdb.tb_backup_mongodb_polling set execution_status=1 where execution_status=0")
			self.cursor.execute("select min(update_time) from  db58_wcdb.tb_backup_mongodb_polling")
			min_date=self.cursor.fetchone()
			self.cursor.execute('update db58_wcdb.tb_backup_mongodb_polling set execution_status=0 where update_time=%s',min_date)
			self.cursor.execute("update db58_wcdb.tb_backup_mongodb_polling set update_time=now() where execution_status=0")
			self.cursor.execute("select ipaddress from tb_backup_mongodb_polling where execution_status=0")
			update_ip=self.cursor.fetchone()
			self.cursor.execute("select max(available_size_G) from tb_backup_mongodb_storage where ipaddress=%s and statdate_time=CURDATE()",update_ip)
			available=self.cursor.fetchone()
			self.cursor.execute("select mount_directory from tb_backup_mongodb_storage where ipaddress='%s' and available_size_G=%s limit 1" %(update_ip[0], available[0]))
			max_directory=self.cursor.fetchone()
			self.cursor.execute("select ipaddress from tb_backup_mongodb_polling where execution_status=0")
			Store_ipaddress=self.cursor.fetchone()
			self.cursor.execute("update tb_backup_mongodb_client set store_ipaddress='%s',main_path='%s'" %(Store_ipaddress[0],max_directory[0]))

			self.con_db.commit()

	
		except MySQLdb.Error as err:
			log_msg='%s:%s > [%s] backuptime_operation  %s' %(self.host,self.port,self.database,err)
			self.Log.write('e',log_msg)


	def backupstrategy_operation(self):
		try:	
			localtime=time.localtime()
			nowtime=time.strftime("%w",localtime)			
			self.cursor.execute('select * from tb_backup_mongodb_client')
			sql_data=self.cursor.fetchall()
			for value in sql_data:
				id=value[0]
				ipaddress=value[1]
				port=value[3]			
				bak_switch=value[8]
				Weeks_backup_strategy=value[9]
        			if  nowtime in Weeks_backup_strategy  and Weeks_backup_strategy != '0':
					self.cursor.execute("update tb_backup_mongodb_client set bak_switch='ON' where id=%s " %id)
        			elif nowtime not in Weeks_backup_strategy :
                			self.cursor.execute("update tb_backup_mongodb_client set bak_switch='OFF' where id=%s " %id)
				elif Weeks_backup_strategy == '0':
					self.cursor.execute("update tb_backup_mongodb_client set bak_switch='OFF' where id=%s " %id)
				elif Weeks_backup_strategy == '0' and bak_switch != 'OFF' :
					value_status='%s:%s Weeks_backup_strategy The instance may be closed ,Please check ...' %(ipaddress,port)
					self.Log.write('i',value_status)

				elif bak_switch not in ('ON','OFF') :
					value_status='%s:%s  bak_switch Abnormal status value ,Please check ... ' %(ipaddress,port)
					self.Log.write('i',value_status)
			
			self.con_db.commit()

		except Exception as e:
			log_msg='%s backupstrategy_operation function Abnormal changes ....' %(e)
			self.Log.write('e',log_msg)



	def backupjson_operation(self):
		try:
			values={}
			va={}
			vb = self.cursor.execute("select * from tb_backup_mongodb_client where rsync_tag=0 and bak_switch='ON'")
			result=self.cursor.fetchall()
			for value in result:
				values['id']=value[0]
				host=value[1]
        			port=value[3]
				backup_directory=str(value[4]) + '/58mongodb/' + str(value[3]) 
				backup_version=value[5]
				backup_clean_up=value[6]
				va[values['id']] ={
					"host" : host,
					"port" : port,
					"backup_directory" : backup_directory,
					"backup_version" : backup_version,
					"backup_clean_up" : backup_clean_up
					}
			vc =  { "backup_list": va }
			with open('/work/wuweijian/cloudmongodb/backup_mongodb/group_vars/all.json','w') as file :
				json.dump(vc, file, indent=4, sort_keys=True)
	
			self.con_db.commit()	

		except Exception as e:
        		log_msg='%s backupjson_operation function Abnormal changes ....' %(e)
        		self.Log.write('e',log_msg)



	def  backuprsync_operation(self):
		try:
			sc=self.cursor.execute("select * from tb_backup_mongodb_client where rsync_tag=1 and bak_switch='ON'")
			result=self.cursor.fetchall()
			async_shell_dir=sys.path[0] + '/async_shell_backup'
			async_yml_dir=sys.path[0] + '/async_yml_backup'
			if not os.path.isdir(async_shell_dir):
				os.makedirs(async_shell_dir)
			elif not os.path.isdir(async_shell_dir):
				os.makedirs(async_yml_dir)
			for value in result:
				id=str(value[0])
				host=value[1]
				store_host=value[2]
				port=str(value[3])
				backup_directory=str(value[4]) + '/58mongodb/' + str(value[3])
				backup_version=value[5]
				backup_clean_up=value[6]
				backupfilename='mongodump_' +  id + '_backup.sh'
				ymlfilename='mongodump_' +  id + '_backup.yml'
				bf=open(sys.path[0] + '/async_shell_backup/' + backupfilename,'w')
				yf=open(sys.path[0] + '/async_yml_backup/' + ymlfilename,'w')
				if backup_version == '3.2':
					backupcontent ='''dt=`date +%%y%%m%%d%%H%%M%%S` \nbackupdir=%s/mongodb_backup \nbakdir=${backupdir}/mongoall_backup \nlogdir=%s/mongodb_log \n\nif [ ! -d '$bakdir' ];then \n     mkdir -p $bakdir  \nfi\nif [ ! -d '$logdir' ];then \n     mkdir -p $logdir\nfi\n\nmysql -uwcdb_admin -p2262acef336ce54a  -h 10.126.72.26 -P3261 -e  "insert into db58_wcdb.tb_backup_mongodb_statistic(objective_host,port,storage_machine,backup_mode,backup_tactics,backup_directory,backup_status,start_time,finish_time,statdate_time,before_compress,after_compress) values('%s',%s,'%s','mongodump','async_full','%s','Waiting',now(),'0000-00-00 00:00:00',curdate(),'Waiting','Waiting')"\nrm -rf ${bakdir} \n\n/opt/soft/%s/bin/mongodump -u$1 -p$2 --host=%s --port=%s --authenticationDatabase=admin --oplog  -o $bakdir --numParallelCollections=6 >>  $logdir/rsync_allbackup.log  \n\nif [ $? -ne 0 ]; then\n  mysql -uwcdb_admin -p2262acef336ce54a  -h 10.126.72.26 -P3261 -e  "update db58_wcdb.tb_backup_mongodb_statistic set backup_status='failure',finish_time=now() where objective_host='%s' and port=%s and statdate_time=curdate()  order by id desc limit 1 "  \n  echo $dt :: The backup ERROR ... >>  $logdir/rsync_allbackup.log\n  exit 1\nelse \n  backup01_size=`du -sh $bakdir | awk '{print $1}'`\n  echo `date '+%%y-%%m-%%d %%H:%%M:%%S'` :: The backup successful >>  $logdir/rsync_allbackup.log \nfi \ncd ${backupdir} ; tar -cv mongoall_backup  |  pigz -9 -p 16 -k > mongoall_${dt}_dump.tgz\nbackup02_size=`ls -lth ${backupdir}/mongoall_*_dump.tgz | head -1 | awk '{print $5}'` \nmysql -uwcdb_admin -p2262acef336ce54a  -h 10.126.72.26 -P3261 -e  "update db58_wcdb.tb_backup_mongodb_statistic set backup_status='successful',finish_time=now(),before_compress='$backup01_size',after_compress='$backup02_size'  where objective_host='%s' and port=%s and statdate_time=curdate()  order by id desc limit 1"\necho `date '+%%y-%%m-%%d %%H:%%M:%%S'` ::  Compression success   >>  $logdir/rsync_allbackup.log\nrm -rf ${bakdir}\nfind $backupdir -mtime +%s -name "*.tgz" -exec rm -rf {} \;''' %(backup_directory,backup_directory,host,port,store_host,backup_directory,backup_version,host,port,host,port,host,port,backup_clean_up)
				else:					
					backupcontent ='''dt=`date +%%y%%m%%d%%H%%M%%S` \nbackupdir=%s/mongodb_backup \nbakdir=${backupdir}/mongoall_backup \nlogdir=%s/mongodb_log \n\nif [ ! -d '$bakdir' ];then \n     mkdir -p $bakdir  \nfi\nif [ ! -d '$logdir' ];then \n     mkdir -p $logdir\nfi \n\nmysql -uwcdb_admin -p2262acef336ce54a  -h 10.126.72.26 -P3261 -e  "insert into db58_wcdb.tb_backup_mongodb_statistic(objective_host,port,storage_machine,backup_mode,backup_tactics,backup_directory,backup_status,start_time,finish_time,statdate_time,before_compress,after_compress) values('%s',%s,'%s','mongodump','async_full','%s','Waiting',now(),'0000-00-00 00:00:00',curdate(),'Waiting','Waiting')"\nrm -rf ${bakdir} \n\n/opt/soft/%s/bin/mongodump -u$1 -p$2 --host=%s --port=%s --authenticationDatabase=admin --oplog  -o $bakdir >>  $logdir/rsync_allbackup.log  \n\nif [ $? -ne 0 ]; then\n  mysql -uwcdb_admin -p2262acef336ce54a  -h 10.126.72.26 -P3261 -e  "update db58_wcdb.tb_backup_mongodb_statistic set backup_status='failure',finish_time=now() where objective_host='%s' and port=%s and statdate_time=curdate()  order by id desc limit 1 "  \n   echo `date '+%%y-%%m-%%d %%H:%%M:%%S'` :: The backup ERROR ... >>  $logdir/rsync_allbackup.log\n  exit 1\nelse \n  backup01_size=`du -sh $bakdir | awk '{print $1}'` \n  echo  `date '+%%y-%%m-%%d %%H:%%M:%%S'` :: The backup successful >>  $logdir/rsync_allbackup.log \nfi \ncd ${backupdir} ; tar -cv mongoall_backup  |  pigz -9 -p 16 -k > mongoall_${dt}_dump.tgz \nbackup02_size=`ls -lth ${backupdir}/mongoall_*_dump.tgz | head -1 | awk '{print $5}'`\nmysql -uwcdb_admin -p2262acef336ce54a  -h 10.126.72.26 -P3261 -e  "update db58_wcdb.tb_backup_mongodb_statistic set backup_status='successful',finish_time=now(),before_compress='$backup01_size',after_compress='$backup02_size'  where objective_host='%s' and port=%s and statdate_time=curdate()  order by id desc limit 1" \necho `date '+%%y-%%m-%%d %%H:%%M:%%S'` ::  Compression success   >>  $logdir/rsync_allbackup.log\nrm -rf ${bakdir}\nfind $backupdir -mtime +%s -name "*.tgz" -exec rm -rf {} \;''' %(backup_directory,backup_directory,host,port,store_host,backup_directory,backup_version,host,port,host,port,host,port,backup_clean_up) 
		
				ymlcontent = "--- \n- name: backup_ceshi \n  gather_facts: False \n  hosts: mongo_backup \n  serial: 24 \n  vars: \n     user: backup_user \n  vars_files: \n     - /work/wuweijian/cloudmongodb/backup_mongodb/files/external_vars.yml \n  tasks: \n     - name: mongobackup \n       script: %s {{user}} {{password}}" %(sys.path[0] + '/async_shell_backup/' + backupfilename)

				bf.write(backupcontent)
				yf.write(ymlcontent)
				bf.close()
				yf.close()
		
		except Exception as e:
		        log_msg='%s backuprsync_operation  function Abnormal changes ....' %(e)
        		self.Log.write('e',log_msg)




	def backupaddres_operation(self):
		try:
			status=self.cursor.execute('select *  from tb_backup_mongodb_polling')
			result=self.cursor.fetchall()
			f=open(sys.path[0] + '/backup_host','w')
			d=open('/work/wuweijian/cloudmongodb/backup_mongodb/inventory/backup_host','w')
			d.writelines('[backup_host]')
			d.close()
			d=open('/work/wuweijian/cloudmongodb/backup_mongodb/inventory/backup_host','a')
			for i in result:
				ipaddress=i[2]
				f.writelines(str(ipaddress)+"\n")
				d.writelines('\n' + str(ipaddress))
			f.close()
			d.close()

			self.con_db.close()
		
		except Exception as e:
        		log_msg='%s  backupaddres_operation  function Abnormal changes ....' %(e)
        		self.Log.write('e',log_msg)




if __name__ == '__main__':
	db=DB_Initialize('10.126.72.26','3261','db58_wcdb')
	backuptime=db.backuptime_operation()	
	backupstrategy=db.backupstrategy_operation()
	backupjson=db.backupjson_operation()	
	backuprsync=db.backuprsync_operation()
	backupaddres=db.backupaddres_operation()

