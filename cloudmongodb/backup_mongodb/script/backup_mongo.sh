#!/bin/bash
dt=`date +%Y%m%d%H%M`
ydt=`date +%Y%m%d -d '1 days ago'`



function mongodump_help(){
        echo  "sh $0 -u admin -p admin  -h localhost -P 3001  -d ceshi_wuweijian   -v mongodump -V mongodump -a db -l directory" 
        echo  "sh $0 -u admin -p admin -h localhost -P 3001  -v mongodump -V mongodump  -a all -l directory"
}


if [ $# -lt 14  ];then
       mongodump_help
       break       
fi


while getopts u:p:h:l:P:d:v:V:a:c: OPTION
do
	case $OPTION in
		u)user=$OPTARG
                ;;
		p)password=$OPTARG
		;;
		h)hostname=$OPTARG
		;;
		l)business=$OPTARG
			if [ ! -d "${business}" ];then
				mkdir -p ${business}
				echo "business  Directory not  exists,Has already been created"
			fi			
			mongodb_dir=${business}/mongodb_backup
                        mongoall_dir=${mongodb_dir}/mongoall_backup

		;;
		P)port=$OPTARG
			if ! [ -n "$(echo $port| sed -n "/^[0-9]\+$/p")" ]
			then 
                                echo -e "\033[31mYou must have a right action: number port ! \033[0m"
				exit 1
                        fi
		;;
		d)database=$OPTARG
		;;
		v)mold=$OPTARG
			if [ "$mold" != "mongodump" ] && [ "$mold" != "mongo_scp" ] && [ -z $mold ] 
			then 
				echo -e "\033[31mYou must have a right action: mongodump ! \033[0m"
			fi
		;;
		V)version_size=$OPTARG
			if [ -z $version_size ]
			then
				version_size="mongodump"
			fi
		;;
		a)action=$OPTARG
			if [ $action != 'all' ] &&  [ $action != 'db'  ] 
			then
				echo -e "\033[31mYou must have a right action: all/db ! \033[0m"
				break
			fi
		;;
		c)concurrency=$OPTARG
                ;;
		?)
		echo -e "\033[31m `date` Please check  -[ u:p:h:l:P:d:v:V:a:c ] [value] \033[0m"
		;;
	esac
done




function mongodump_backup(){
	mongo_logdir="${business}/mongodb_log"
	status_logfile="$mongo_logdir/mongodump_backup_status.log"

        if [ ! -d "$mongo_logdir" ];then
            
		mkdir -p $mongo_logdir
      	fi


	if [ "$action" == "all" ] && [ -z $database ] && [ -n $hostname ] && [ -n $port ] && [ -n $database ] && [ -n $Target_Directory ] ;then

		if [ ! -d "$mongoall_dir" ];then

        		mkdir -p $mongoall_dir
		fi

		logfile="$mongo_logdir/mongodump_all_${dt}.log"
		echo  "StartTime: `date '+%Y-%m-%d %H:%M:%S'` mongodump full backup ..." >> $status_logfile 2>&1
		
		store_host=`mysql -uwcdb_admin -p2262acef336ce54a  -h 10.126.72.26 -P3261 -BNe  "select ipaddress from db58_wcdb.tb_backup_mongodb_polling where execution_status=0;"`		

		mysql -uwcdb_admin -p2262acef336ce54a  -h 10.126.72.26 -P3261 -e  "insert into db58_wcdb.tb_backup_mongodb_statistic(objective_host,port,storage_machine,backup_mode,backup_tactics,backup_directory,backup_status,start_time,finish_time,statdate_time,before_compress,after_compress) values('${hostname}',${port},'${store_host}','${mold}','${action}','${business}','Waiting',now(),'0000-00-00 00:00:00',curdate(),'Waiting','Waiting')"

		rm -rf ${mongoall_dir} >> $logfile 2>&1

		${version_size} -u${user} -p${password} --host=${hostname} --port=${port} ${concurrency} --oplog  --authenticationDatabase=admin -o ${mongoall_dir} > $logfile 2>&1 


		if [ $? -ne 0 ]; then
			status='failure'
			mysql -uwcdb_admin -p2262acef336ce54a  -h 10.126.72.26 -P3261 -e  "update db58_wcdb.tb_backup_mongodb_statistic set backup_status='$status',finish_time=now()  where objective_host='$hostname' and port='$port' and statdate_time=curdate()  order by id desc limit 1 "
			echo -e "\033[31m At time: `date "+%Y-%m-%d %H:%M:%S"` : mongodump is Error. You confirm the backup db '-a $action' \033[0m"
			echo  "At `date '+%Y-%m-%d %H:%M:%S'` mongodump full backup ERROR ..." >> $status_logfile 2>&1
			exit 1
		else
			backup01_size=`du -sh ${mongoall_dir} | awk '{print $1}'`
			status='successful'
		fi
		
		echo  "At time: `date '+%Y-%m-%d %H:%M:%S'`  mongodump full backup succeed....." >> $logfile 2>&1
		echo  "EndTime: `date '+%Y-%m-%d %H:%M:%S'`  Host ${hostname} port ${port} nodes has been backed up to ${mongoall_dir} success " >> $status_logfile 2>&1
		cd ${mongodb_dir}
                tar -cv mongoall_backup  |  pigz -9 -p 16 -k > mongoall_${dt}_dump.tgz  2>&1
		backup02_size=`ls -lth ${mongodb_dir}/mongoall_*_dump.tgz | head -1 | awk '{print $5}'`
                rm -rf ${mongoall_dir} >> $logfile 2>&1	
		echo  "At time: `date '+%Y-%m-%d %H:%M:%S'`  mongodump full backup compress succeed....." >> $logfile 2>&1	

	elif [ "$action" == "db" ] && [ -n $database ]  && [ -n $hostname ] && [ -n $port ] && [ -n $database ] && [ -n $Target_Directory ];then
		if [ ! -d "$mongodb_dir" ];then
        		mkdir -p $mongodb_dir
		fi
	
		logfile="$mongo_logdir/mongodump_db_${dt}.log"
		echo  "StartTime: `date '+%Y-%m-%d %H:%M:%S'` mongodump DB backup ..." >> $status_logfile
		${version_size} -u${user} -p${password} --host=${hostname} --port=${port} -d${database} ${concurrency}  --authenticationDatabase=admin -o ${mongodb_dir} > $logfile 2>&1 

		if [ $? -ne 0 ]; then
			status='failure'
                        echo -e "\033[31m At time: `date "+%Y-%m-%d %H:%M:%S"` : mongodump is Error. You confirm the backup db '-a $action' \033[0m"
			echo  "At `date '+%Y-%m-%d %H:%M:%S'` mongodump DB backup ERROR ..." >> $status_logfile 2>&1
			exit 1
		else
			status='successful'
                fi

		echo  "At time: `date '+%Y-%m-%d %H:%M:%S'`  mongodump DB backup succeed....." >> $logfile 2>&1
		echo  "EndTime: `date '+%Y-%m-%d %H:%M:%S'`  mongodump DB backup Host ${hostname} port ${port} nodes has been backed up to ${mongoall_dir} success " >> $status_logfile 2>&1
		cd ${mongodb_dir}
                tar cf - ${mongodb_dir}  | pigz -6 -p 20 > ${database}_${dt}_dbdump.tgz  2>&1
                rm -rf ${mongodb_dir}/${database} >> $logfile 2>&1
		echo  "At time: `date '+%Y-%m-%d %H:%M:%S'`  mongodump DB backup compress succeed....." >> $logfile 2>&1
	else 
		echo -e  "\033[31m Error:Please check user or host or port or database or Target_Directory or backup -a >> db/all \033[0m"
		break
		
	fi

}


function mongo_authlog(){
	
	mysql -uwcdb_admin -p2262acef336ce54a  -h 10.126.72.26 -P3261 -e  "update db58_wcdb.tb_backup_mongodb_statistic set backup_status='$status',finish_time=now(),before_compress='$backup01_size',after_compress='$backup02_size'  where objective_host='$hostname' and port='$port' and statdate_time=curdate()  order by id desc limit 1"

}




function mongodump_scp(){

if [ -e $mongodb_dir/*_${dt}_db.tar.gz ] && [ "$action" == "db" ] 
then
	if [ -z $user  ] || [ -z $hostname  ] || [ -z $business  ]
	then
		echo -e "\033[31mPlease check -u:-h:-l \033[0m"
		break
	fi
	scp    $mongodb_dir/*_db.tar.gz $user@$hostname:$business
	if [ $? -ne 0 ]; then
		 echo -e "\033[31m Scp abnormal  \033[0m" 
	         break
	fi
	rm -rf $mongodb_dir/*_${dt}_db.tar.gz
		
elif [ -e $mongoall_dir/*_${dt}_all.tar.gz ] && [ "$action" == "all" ]
then
	if [ -z $user  ] || [ -z $hostname  ] || [ -z $business  ]
        then
                echo -e "\033[31mPlease check -u:-h:-l \033[0m"
                break
        fi
	scp $mongoall_dir/*_${dt}_all.tar.gz $user@$hostname:$business 
	if [ $? -ne 0 ]; then
                 echo -e "\033[31m Scp abnormal  \033[0m" 
                 break 
        fi
	rm -rf $mongoall_dir/*_${dt}_all.tar.gz
else
                echo "NO there is ${dt}  new files or unspecified DB"
fi

}




if [ "$mold" == "mongodump" ];then
	mongodump_backup
	mongo_authlog
fi

