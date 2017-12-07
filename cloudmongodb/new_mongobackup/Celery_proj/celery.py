#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import absolute_import
from celery import Celery

Wrr = Celery('Celery_proj', include=['Celery_proj.tasks'])

Wrr.config_from_object('Celery_proj.config')

if __name__ == '__main__':
    Wrr.start()
