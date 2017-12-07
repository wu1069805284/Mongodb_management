#!/usr/bin/python
#coding=utf-8
#!/usr/local/bin/python
#coding=utf-8

import os
import sys
import time
import logging
import MySQLdb
from pymongo import MongoClient



class WriteLog(object):
    def write(self,log_status,log_msg):
        logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s [%(levelname)s] %(message)s',
                datefmt='%Y-%m-%d %X',
                filename=sys.path[0] + '/general_mongodb.log',
                filemode='a')
	
	if log_status == 'i':
        	logging.info(log_msg)
	if log_status == 'e':
        	logging.error(log_msg)        



class Mysql_Change(object):
	def  __init__(self):	
		self.Log = WriteLog()
		self.host = '10.126.72.26'
		self.port = 3261 
		self.user = 'wcdb_admin'
		self.pw = '2262acef336ce54a'
		self.database = 'db58_wcdb'
		_failed_times = 0

		while True:
     			try:
         			self.con_db = MySQLdb.connect(host=self.host,port=self.port,user=self.user,passwd=self.pw,db=self.database)
         			self.con_db.autocommit(1)
         			self.cursor = self.con_db.cursor()
     			except Exception as e:
         			_failed_times += 1
         			if _failed_times >= 3:
		             		print e
             				log_msg = "%s:%s %s" % (self.host,self.port,e)
             				self.Log.write('e',log_msg)
         			else:
             				continue
		
			break

	def mongo_export(self):
		try:
			sql="select inip,port,iRole,iGId,isOnLine from dbms_mongo_instanceinfo where iRole in ('Primary','Secondary') and port not in (7111,7112)"	
			self.cursor.execute(sql)
			data=self.cursor.fetchall()
			return data	
		
		except MySQLdb.Error as err:
			log_msg="mongo_export function ERROR ==>> %s" %(err)
			self.Log.write('e',log_msg)
			print err.args[1]	
			return 0	



	def instantiate_import(self,data):

		try:
			self.cursor.execute("select count(*) from rp_mongodb_instancestatistics where day_timedate = CURDATE()")
			today=self.cursor.fetchone()

			if today >= 1 :
        			self.cursor.execute("delete from rp_mongodb_instancestatistics where day_timedate  = CURDATE()")
			for value  in  data:
				if not value[4]:
					print value[1],value[2]
				self.cursor.execute("insert into rp_mongodb_instancestatistics (iGId,host,port,role,dbname,dbsize,dbempty,detailed_time,day_timedate) values ('%s','%s',%s,'%s','%s','%s','%s',now(),CURDATE())" %(value[0],value[1],value[2],value[3],value[4],value[5],value[6]))

		except BaseException as e:
				log_msg = " instantiate_import : %s"%(e)
				self.Log.write('e',log_msg)


	def Instant_operate(self,host,port):

		try:
			Instant_info=self.cursor.execute("select count(*) from rp_mongodb_instancestatistics where host='%s' and port=%d and day_timedate  = CURDATE()" %(host,port))
			info=self.cursor.fetchone()
			if info[0] != 0:
				self.cursor.execute("select count(dbname) ,sum(dbsize)  from rp_mongodb_instancestatistics where host='%s' and port=%d and day_timedate = CURDATE()" %(host,port) )
				data=self.cursor.fetchone()
				a=int(data[0]) - 1
				b=int(data[1])
				self.cursor.execute("update rp_mongodb_instancestatistics set dbtonumber=%s , dbtosize=%s where host='%s' and port=%d " %(a,b,host,port))


                except Exception as e:
                                log_msg = " Instant_operate : %s"%(e)
                                self.Log.write('e',log_msg)




	def DBInformation_import(self,data):

		try:
			sql="insert into rp_mongodb_dbstatistics (iGId,host,port,role,dbname,dbsize,collections,objects,avgObjSize,dataSize,storageSize,Indexnumber,Indexsize,detailed_time,day_timedate) values ('%s','%s',%s,'%s','%s','%s',%s,%s,%s,%s,%s,%s,%s,now(),CURDATE())"
			
			self.cursor.execute("select count(*) from rp_mongodb_dbstatistics where day_timedate = CURDATE()")
                        today=self.cursor.fetchone()
			if today >= 1 :
                                self.cursor.execute("delete from rp_mongodb_dbstatistics where day_timedate  = CURDATE()")
			for value in data:
				dbname=value[4]
				if dbname not in {'local'}:
					collections=value[7]
					objects=value[8]
					avgObjSize=round(float(value[9])/1024/1024/1024,2)
					dataSize=round(float(value[10])/1024/1024/1024,2)
					storageSize=round(float(value[11])/1024/1024/1024,2)
					index_number=value[12]
					Index_size=round(float(value[13])/1024/1024/1024,2)
					self.cursor.execute(sql %(value[0],value[1],value[2],value[3],value[4],value[5],collections,objects,avgObjSize,dataSize,storageSize,index_number,Index_size)) 


		except Exception as e:
			log_msg = " DBInformation_import : %s"%(e)
			self.Log.write('e',log_msg)




        def QPSinformation_import(self,data,vdata):
		try:

			sql01="select count(*) from rp_mongodb_statusstatistics where day_timedate = CURDATE()"

			sql02="insert into rp_mongodb_statusstatistics (iGId,host,port,role,qtotal,yqtotal,qday,utotal,yutotal,uday,itotal,yitotal,iday,dtotal,ydtotal,dday,qcommand,ycommand,daycommand,detailed_time,day_timedate) values (%s,%s,%s,%s,%s,0,0,%s,0,0,%s,0,0,%s,0,0,%s,0,0,now(),CURDATE())"

			sql03="update rp_mongodb_statusstatistics  set yqtotal=%s,yutotal=%s,yitotal=%s,ydtotal=%s,ycommand=%s where host=%s and port=%s and day_timedate=CURDATE()"

			sql04="select * from rp_mongodb_statusstatistics where day_timedate=CURDATE()"

			sql05="update rp_mongodb_statusstatistics set qday=%s,uday=%s,iday=%s,dday=%s,daycommand=%s where host='%s' and port=%s and day_timedate=CURDATE()"

			self.cursor.execute(sql01)
			today=self.cursor.fetchone()			
			if today >= 1 :
				self.cursor.execute("delete from rp_mongodb_statusstatistics where day_timedate = CURDATE()")
				self.cursor.execute("delete from rp_mongodb_globalstats where statDate = CURDATE()")
				self.cursor.execute("delete from rp_mongodb_dbstatistics where day_timedate = CURDATE()")
				self.cursor.execute("delete from rp_mongodb_instancestatistics where  day_timedate = CURDATE()")
			for nv in data:
				if nv[0]:
					self.cursor.execute(sql02,nv)	
			for ov in vdata:
				if ov[5]:
					self.cursor.execute(sql03,ov)
			self.cursor.execute(sql04)
			qps=self.cursor.fetchall()
			for value in qps:
				host=str(value[2])
				port=int(value[3])
				if int(value[5]) < int(value[6]) or int(value[8]) < int(value[9]) or int(value[11]) < int(value[12]) or int(value[14]) < int(value[15]) or int(value[17]) < int(value[18]):
					query=int(value[5])
					update=int(value[8])
					insert=int(value[11])
					delete=int(value[14])
					ctotal=int(value[17])
					log_msg="%s:%s Instance is not normal, may be a restart "%(host,port)
					self.Log.write('i',log_msg) 
					self.cursor.execute(sql05 %(query,update,insert,delete,ctotal,host,port))
				else:
					query=int(value[5])  -  int(value[6])
					update=int(value[8]) - int(value[9])
					insert=int(value[11]) - int(value[12])
					delete=int(value[14]) - int(value[15])
					ctotal=int(value[17]) - int(value[18])
					self.cursor.execute(sql05 %(query,update,insert,delete,ctotal,host,port))
			

		except Exception as e:
				log_msg = " QPSinformation_import : %s"%(e)
				self.Log.write('e',log_msg)



	def QPS_today(self):
		try:
			sql="select qtotal,utotal,itotal,dtotal,qcommand,host,port from rp_mongodb_statusstatistics where to_days(now()) - to_days(day_timedate) = 1 "	
			self.cursor.execute(sql)
			today=self.cursor.fetchall()	
			return (today)			

		except Exception as e:
				log_msg = " QPS_today : %s"%(e)
				self.Log.write('e',log_msg)


	def QPS_summary(self):
		try:
			self.cursor.execute("select iGId,sum(qday)+sum(daycommand) from rp_mongodb_statusstatistics where day_timedate = CURDATE() group by iGId")
			data=self.cursor.fetchall()
			for value in data:
				igid=str(value[0])
				tcqps=int(value[1])
				self.cursor.execute("update rp_mongodb_statusstatistics set total_qps_cluster=%s where day_timedate = CURDATE() and iGId='%s'" %(tcqps,igid))
			self.cursor.execute("insert into rp_mongodb_globalstats(global_QPS,global_TPS,global_command,global_Select,global_Insert,global_Update,global_Delete,statDate,stateTime) (select sum(daycommand)+sum(qday)+sum(uday)+sum(iday)+sum(dday),sum(uday)+sum(iday)+sum(dday),sum(daycommand),sum(qday),sum(uday),sum(iday),sum(dday),CURDATE(),now() from rp_mongodb_statusstatistics where day_timedate=CURDATE());")

		except Exception as e:
			log_msg = " QPS_summary : %s"%(e)
                        self.Log.write('e',log_msg)



	def close_connection(self):
		self.con_db.close()


class mongo(object):

	def __init__(self):
		self.Log = WriteLog()
		self.user="monitor"
		self.password='B033562027D95A0F17'

	def mongoconn(self,host,port,db='admin'):
		try:
			URL="mongodb://%s:%s@%s:%s/%s" %(self.user,self.password,host,port,db)
			mongoconn = MongoClient(URL)
			#conn = mongoconn.admin.authenticate(self.user,self.password)
			return(mongoconn)

		except Exception as e:
			log_msg = " mongoconn Error : %s"%(e)
			self.Log.write('e',log_msg)
		

	def Instance(self,host,port,role,IGid):

		try:
			instanceinfo=[]
			Statusinfo = self.mongoconn(host,port).admin.command("listDatabases") 
			DBtotalsize = Statusinfo['databases']
			for value in DBtotalsize:
				aname = value['name']
				if aname not in {'admin'} :
					dbname = str(value['name'])
					dbsize = str(round(float(value['sizeOnDisk'])/1024/1024/1024,2))
					empty = str(value['empty'])
					dbconninfo=self.mongoconn(host,port)[dbname].command("dbStats")
					collections=int(dbconninfo['collections'])
					objects=int(dbconninfo['objects'])
					avgObjSize=int(dbconninfo['avgObjSize'])
					dataSize=int(dbconninfo['dataSize'])
					storageSize=int(dbconninfo['storageSize'])
					indexes=int(dbconninfo['indexes'])
					indexSize=int(dbconninfo['indexSize'])
					instanceinfo.append((IGid,host,port,role,dbname,dbsize,empty,collections,objects,avgObjSize,dataSize,storageSize,indexes,indexSize))	

			return(instanceinfo)			

		except Exception as e:
			log_msg = "%s:%s Instance information get  Error : %s" %(host,port,e)
			self.Log.write('e',log_msg)

	
#	def storage_table(self,host,port):
#		try:
			
#		except Exception as e:
#			log_msg = " storage_table information get  Error : %s"%(e)
#			self.Log.write(log_msg)


	def qps(self,host,port,role,IGid):
		try:		
			Statusinfo = self.mongoconn(host,port).admin.command("serverStatus")
			qpsstatus = Statusinfo['opcounters']
			qtotal = qpsstatus['query']
			utotal = qpsstatus['update']
			itotal = qpsstatus['insert']
			dtotal = qpsstatus['delete']
			ctotal = qpsstatus['command']
			return(IGid,host,port,role,qtotal,utotal,itotal,dtotal,ctotal)

		except Exception as e:
			log_msg = "%s:%s qps information get  Error : %s" %(host,port,e)
			self.Log.write('e',log_msg)



if __name__ == '__main__':
	data = []
	vdata = []
	Instancedata = []
	mysql_client=Mysql_Change()
	mongodb=mongo()
	Log=WriteLog()

	for value in  mysql_client.mongo_export():
		mongo_host=str(value[0])
		mongo_port=int(value[1])
		mongo_role=str(value[2])
		mongo_IGid=str(value[3])
		mongo_isOnLine=value[4]
		if mongo_isOnLine != 1:
			continue
		else:
			mongodb_qpsinfo=mongodb.qps(mongo_host,mongo_port,mongo_role,mongo_IGid)	
			mongodb_Instance=mongodb.Instance(mongo_host,mongo_port,mongo_role,mongo_IGid)
			if mongodb_qpsinfo is None:
				continue
			else:
				data.append((mongodb_qpsinfo))
			
			if mongodb_Instance is None:
				continue
			else:
				for value in mongodb_Instance:
					Instancedata.append((value))
			log_msg="(%s:%s:%s:%s) Access to information to complete" %(mongo_IGid,mongo_role,mongo_host,mongo_port)
			Log.write('i',log_msg)				

	todata=mysql_client.QPS_today()
	mysql_client.QPSinformation_import(data,todata)
	mysql_client.instantiate_import(Instancedata)
	mysql_client.DBInformation_import(Instancedata)	
	mysql_client.QPS_summary()

	for dvalue in mysql_client.mongo_export():
		mongo_host=str(dvalue[0])
		mongo_port=int(dvalue[1])
		mysql_client.Instant_operate(mongo_host,mongo_port)
		
	mysql_client.close_connection()
