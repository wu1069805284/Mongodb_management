#!/usr/bin/python
from ConfigParser import SafeConfigParser


parser = SafeConfigParser()
parser.read('config_backup.cfg')

def mysql_user_info():
	user = parser.get('admin','user')
	host = parser.get('admin','host')
	port = parser.getint('admin','port')
	password = parser.get('admin','password')
	return(user,host,port,password)


def mongo_user_info():
	user = parser.get('mongo_client','user')	
	password = parser.get('mongo_client','password')
	return(user,password)


	
