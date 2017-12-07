#!/bin/bash
day_date=`date "+%Y%m%d"`
current_date=`date "+%Y%m%d%H%M%S"`
mysql_user='dba_admin'
mysql_pw='ganji@admin'
mysql_host='10.9.196.59'
mysql_port='3302'
mysql_db='cloud_mongodb'


while getopts u:p:h:P:b:d:v:c:m: OPTION
do
	case $OPTION in
		u)client_user=$OPTARG
		;;
		p)client_pw=$OPTARG
		;;
		h)client_host=$OPTARG
                ;;
		P)client_port=$OPTARG
		;;
		b)backup_host=$OPTARG
		;;
		d)backup_dir=$OPTARG
		;;
		v)version=$OPTARG
		;;
		c)cleanup=$OPTARG
		;;
		m)mode=$OPTARG
		;;
		?)
		;;
	esac
done


instance_dir=${backup_dir}/${day_date}/${client_port}_${client_host}
bakdir=${instance_dir}/mongodb_backup
log_dir=${instance_dir}/mongodb_log


function initialize(){
	STATUS_LOG=${log_dir}/${version}_mongodump_backup_status.log

	if ! [ -d ${instance_dir} ]
	then
		mkdir -p {$bakdir,$log_dir} 
	fi

	if [  -d "${bakdir}" ] && [  -n "$(echo $cleanup| sed -n "/^[0-9]\+$/p")" ]
	then
		find ${bakdir:-'/tmp/'} -mtime +${cleanup:-'6'} -name "*.tgz" -exec rm -rf {} \;
		find ${log_dir:-'/tmp/'} -mtime +${cleanup:-'6'} -name "*.log" -exec rm -rf {} \;
		echo "[`date "+%Y-%m-%d %H:%M:%S"`] Data has been clean up ${cleanup} days ago successful" >> ${STATUS_LOG}
	else
		echo "[`date "+%Y-%m-%d %H:%M:%S"`] Clean up ${cleanup} days input error" >> ${STATUS_LOG}	
	fi
	
}




function mongodb_backup(){
	MONGODUMP=/opt/soft/${version}/bin/mongodump
	BACKUP_NAME=mongodump_${current_date}
	BACKUP_DIR=${bakdir}/${BACKUP_NAME}
	STATUS_LOG=${log_dir}/${version}_mongodump_backup_status.log
	BACKUP_LOG=${log_dir}/${version}_mongodump_${current_date}_backup.log
	echo "[`date "+%Y-%m-%d %H:%M:%S"`] start mongodump full backup ... " >> ${STATUS_LOG}
	if ! [ -d ${BACKUP_DIR} ]
	then
		mkdir -p ${BACKUP_DIR}
	fi
	mysql -u${mysql_user} -p${mysql_pw}  -h${mysql_host} -P${mysql_port} -e  "insert into cloud_mongodb.tb_backup_mongodb_statistic(objective_host,port,storage_machine,backup_mode,backup_directory,backup_status,start_time,finish_time,statdate_time,before_compress,after_compress) values('${client_host}',${client_port},'${backup_host}','full_mongodump','${instance_dir}','Waiting',now(),'0000-00-00 00:00:00',curdate(),'Waiting','Waiting')"
	$MONGODUMP  -u${client_user} -p${client_pw} --host=${client_host} --port=${client_port} --oplog --authenticationDatabase=admin -o ${BACKUP_DIR} >> ${BACKUP_LOG} 2>&1
	if [ $? -ne 0 ]	
	then
		status='failure'
		echo  "[`date "+%Y-%m-%d %H:%M:%S"`] stop mongodump full backup ${status} " >> ${STATUS_LOG}
		mysql -u${mysql_user} -p${mysql_pw}  -h${mysql_host} -P${mysql_port} -e  "update cloud_mongodb.tb_backup_mongodb_statistic set backup_status='${status}',finish_time=now(),before_compress='${S_size}' where objective_host='${client_host}' and port=${client_port} and statdate_time=curdate() limit 1"
		exit 1
	else
		S_size=`du -sh ${BACKUP_DIR} |awk '{print $1}'`
		if  [ -z $S_size  ]; then
			S_size='0'
		fi
		status='successful'
		echo  "[`date "+%Y-%m-%d %H:%M:%S"`] stop mongodump full backup ${status} " >> ${STATUS_LOG}
		mysql -u${mysql_user} -p${mysql_pw}  -h${mysql_host} -P${mysql_port} -e  "update cloud_mongodb.tb_backup_mongodb_statistic set backup_status='${status}',finish_time=now(),before_compress='${S_size}' where objective_host='${client_host}' and port=${client_port} and statdate_time=curdate() limit 1"
	fi
	echo  "[`date "+%Y-%m-%d %H:%M:%S"`] To compress ${client_host}:${client_port} the backup file " >> ${STATUS_LOG}	
	cd ${bakdir}
	{ tar -cv ${BACKUP_NAME}  |  pigz -6 -p 16 -k > mongoall_${current_date}_dump.tgz; } 2>>${STATUS_LOG} 
	if [ $? -ne 0 ]
	then
		mysql -u${mysql_user} -p${mysql_pw}  -h${mysql_host} -P${mysql_port} -e  "update cloud_mongodb.tb_backup_mongodb_statistic set after_compress='failure' where objective_host='${client_host}' and port=${client_port} and statdate_time=curdate() limit 1"
		echo "[`date "+%Y-%m-%d %H:%M:%S"`] To compress ${client_host}:${client_port} the backup file failure " >> ${STATUS_LOG}
	else
		E_size=`ls -lth mongoall_*_dump.tgz | head -1 | awk '{print $5}'`
		mysql -u${mysql_user} -p${mysql_pw}  -h${mysql_host} -P${mysql_port} -e  "update cloud_mongodb.tb_backup_mongodb_statistic set after_compress='${E_size}' where objective_host='${client_host}' and port=${client_port} and statdate_time=curdate() limit 1"
		echo "[`date "+%Y-%m-%d %H:%M:%S"`] To compress ${client_host}:${client_port} the backup file successful " >> ${STATUS_LOG}
		rm -rf ${BACKUP_DIR}
	fi

}


if [ $mode == 'path_init' ]
then
	initialize

elif [ $mode == 'backup_start' ]
then
	mongodb_backup		
fi


