#!/usr/bin/python
import argparse              
try:                         
    import json              
except ImportError:          
    import simplejson as json
import sys,time,MySQLdb



def getList():
    sql='select ipaddress from tb_backup_mongodb_polling where execution_status=0; '
    try:
        conn=MySQLdb.connect(user='wcdb_admin',passwd='2262acef336ce54a',host='10.126.72.26',db='db58_wcdb',port=3261)
        cur=conn.cursor()
        cur.execute(sql)
        result=cur.fetchall()
#	for value in result:
#		print json.dumps(value)
	print json.dumps({"mongo_backup":{                   
        			"hosts": result[0],
        			"vars":{"mongodb_backup":27017,"pass":666 } } } )
        cur.close()
        conn.close()

    except:
        print "Mysql Connect to Error"



def getVars(host):
    sql='select ipaddress from tb_backup_mongodb_polling ;'
    try:
	conn=MySQLdb.connect(user='wcdb_admin',passwd='2262acef336ce54a',host='10.126.72.26',db='db58_wcdb',port=3261)	
	cur=conn.cursor()
	cur.execute(sql)
	result=cur.fetchall()
	print json.dumps({"mongo_backup":{
                                "hosts": result[0:],
                                "vars":{"http_port":8888,"max_clients":789} } })
	cur.close()
	conn.close()

    except:
	print "Mysql Connect to Error"

if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument('--list',action='store_true',dest='list',help='get all hosts')
	parser.add_argument('--host',action='store',dest='host',help='get all hosts')
        args = parser.parse_args()
    
        if args.list:
            getList()
    
        if args.host:
            getVars(args.host)
