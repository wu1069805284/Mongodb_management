import os,sys,json,MySQLdb

def dbtime_polling():
	conn=MySQLdb.connect(user='root',passwd='backup',host='127.0.0.1',db='cloud_mongodb',port=3302)
        cur=conn.cursor()
	sc=cur.execute("select * from backup_client_infomation where tag=1")
	result=cur.fetchall()
	for value in result:
		id=str(value[0])
		host=value[1]
		port=str(value[2])
		backup_directory=str(value[3]) + '/58mongodb/' + str(value[2])
		backup_version=value[4]
		backup_clean_up=value[5]
		backupfilename=backup_version + '_' + id + '_backup.sh'
		ymlfilename=backup_version + '_' + id + '_backup.yml'
		bf=open(sys.path[0] + '/async_shell_backup/' + backupfilename,'w')
		yf=open(sys.path[0] + '/async_yml_backup/' + ymlfilename,'w')
		
		backupcontent =  '''dt=`date +%%y%%m%%d%%H%%M` \nbackupdir=%s/mongodb_backup \nbakdir=${backupdir}/mongoall_backup \nlogdir=%s/mongodb_log \n\nif [ ! -d '$bakdir' ];then \n     mkdir -p $bakdir  \nfi \n\n/opt/soft/%s/bin/mongodump -u$1 -p$2 --host=%s --port=%s --authenticationDatabase=admin -o $bakdir >> $logdir/rsync_allbackup_$dt.log  \n\nif [ $? -ne 0 ]; then\n   mysql -udba -pbackup  -h 10.1.180.12 -P3302 -e  "insert into cloud_mongodb.backup_status_log(objective_host,port,backup_mode,backup_tactics,backup_directory,backup_status,create_time,statdate_time) values('%s','%s','mongodump','async_full','%s','failure',now(),curdate())"   \n   exit 1\nelse \n   mysql -udba -pbackup  -h 10.1.180.12 -P3302 -e  "insert into cloud_mongodb.backup_status_log(objective_host,port,backup_mode,backup_tactics,backup_directory,backup_status,create_time,statdate_time) values('%s','%s','mongodump','async_full','%s','successful',now(),curdate())"   \nfi \ncd ${backupdir} ; tar -cv mongoall_backup  |  pigz -9 -p 12 -k > mongoall_${dt}_dump.tgz;rm -rf ${bakdir}''' %(backup_directory,backup_directory,backup_version,host,port,host,port,backup_directory,host,port,backup_directory)
		
		ymlcontent = "--- \n- name: backup_ceshi \n  gather_facts: False \n  hosts: mongo_backup \n  serial: 24 \n  vars: \n     user: backup_user \n  vars_files: \n     - /data1/github/cloudmongodb/ansible/backup_ceshi/files/external_vars.yml \n  tasks: \n     - name: mongobackup \n       script: %s {{user}} {{password}}" %(sys.path[0] + '/async_shell_backup/' + backupfilename)

		bf.write(backupcontent)
		yf.write(ymlcontent)
		bf.close()
		yf.close()

		print  sys.path[0] + '/async_shell_backup/' + backupfilename
		print sys.path[0] + '/async_yml_backup/' + ymlfilename


if __name__ == '__main__':
	dbtime_polling()
