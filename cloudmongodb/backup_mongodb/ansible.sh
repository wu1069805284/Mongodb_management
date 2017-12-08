#!/bin/bash
## Note:Auto Login MySQL Server
##wuweijian
## Created by 
## 2016/12/10[Init]
##
## Change log
source /etc/profile
export LANG=en_US.UTF-8

ymldir=/work/wuweijian/cloudmongodb/backup_mongodb/script/async_yml_backup
shelldir=/work/wuweijian/cloudmongodb/backup_mongodb/script/async_shell_backup
ANSIBLE_PLAYBOOK=/usr/local/bin/ansible-playbook


for i in `ls $ymldir`
do
      async_log=`echo $i |awk -F '.' '{print $1}'`
      nohup ${ANSIBLE_PLAYBOOK} -i inventory.py $ymldir/$i > log/${async_log}.log &

done

${ANSIBLE_PLAYBOOK} -i inventory.py mongodump_all_backup.yml -e "db=all version=mongodump" >> log/mongodump_all_`date '+%Y-%m-%d'`_backup.log

rm -rf $ymldir/* ; rm -rf $shelldir/*
