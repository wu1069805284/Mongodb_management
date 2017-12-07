#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import absolute_import

CELERY_RESULT_BACKEND = 'redis://localhost:6001/0'
BROKER_URL = 'redis://localhost:6001'
CELERY_TASK_RESULT_EXPIRES = 18000  #celery任务结果有效期 
BROKER_TRANSPORT_OPTIONS  =  {  'visibility_timeout'  : 172800  }
CELERY_ENABLE_UTC = True
CELERY_TIMEZONE = 'Asia/Shanghai'
CELERY_ENABLE_UTC = True
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT=['json']
CELERYD_CONCURRENCY = 10


#CELERYD_TASK_SOFT_TIME_LIMIT = 7200
#CELERYD_TASK_TIME_LIMIT = 3600


