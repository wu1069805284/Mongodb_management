#!/bin/bash
backup_dir=$1
clean_day=$2
current_date=`date "+%Y%m%d %X"`

#&& [ -n "$(echo ${clean_day}| sed -n "/^[0-9]\+$/p")" ]
if [  -d "${backup_dir}" ] && [  -n "$(echo $clean_day| sed -n "/^[0-9]\+$/p")" ]
then
	clean_log_dir="${backup_dir}/mongodb_log"
	find ${backup_dir:-'/tmp/'} -mtime +${clean_day:-'6'} -name "*.tgz" -exec rm -rf {} \;
	find ${clean_log_dir:-'/tmp/'} -mtime +20 -name "mongodump_all_*.log" -exec rm -rf {} \;
	echo " At current date ${current_date} :  Data has been clean up ${clean_day} days ago successful" >> $clean_log_dir/mongo_backup_clean.log
else
	echo "clean up input error" >> $clean_log_dir/mongo_backup_clean.log	
fi
