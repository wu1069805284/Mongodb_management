#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import absolute_import
import sys
sys.path.append("/work/wuweijian/cloudmongodb/new_mongobackup")
from ansible_execute import ansible_backup
from Celery_proj.celery import Wrr
from time import sleep




@Wrr.task
def ansible_bak(mu,mp,chost,bhost,cport,path,version,clean):
	mongobak=ansible_backup(mu,mp,chost,bhost,cport,path,version,clean)
	return mongobak.ansible_backup()

@Wrr.task
def add(x, y,ignore_result=True):
    sleep(15)
    return x + y

@Wrr.task(bind=True)
def test_mes(self):
	for i in xrange(1, 11):
		time.sleep(0.1)
		self.update_state(state="PROGRESS", meta={'p': i*10})
	return 'finish'
