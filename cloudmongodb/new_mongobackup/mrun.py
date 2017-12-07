#!/usr/bin/python
from ansible_execute import ansible_backup
from MySQLHandler import MySQLHandler
from Celery_proj.tasks import *
from time import sleep
import multiprocessing
import config_backup
import logging,sys


class WriteLog(object):

    def write(self,log_lev,log_msg):
        logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s [%(levelname)s] %(message)s',
                datefmt='%Y-%m-%d %X',
                filename=sys.path[0] + '/Manual_backup.log',
                filemode='a')

        if log_lev == 'e':
            logging.error(log_msg)
        elif log_lev == 'i':
            logging.info(log_msg)
        elif log_lev == 'w':
            logging.warning(log_msg)



class Producer(multiprocessing.Process):
    def __init__(self, queue):
        multiprocessing.Process.__init__(self)
        self.queue = queue
	self.Log=WriteLog()
	self.mysql_info=config_backup.mysql_user_info()
	self.conn=MySQLHandler(self.mysql_info[0],self.mysql_info[1],self.mysql_info[2],self.mysql_info[3])
       

    def get_mysql(self):
	get_info = self.conn.get_mysql_data('select id,manual_bak_switch from cloud_mongodb.tb_backup_mongodb_client;') 
	id_list = []
	for info in get_info:
		if info[1] == 'ON':
			wid=int(info[0])
			id_list.append((wid))
	
	return id_list


 
    def run(self):
        while True:
  	    	uid=self.get_mysql()
		if uid == []:
			uid='NULL'
            	self.queue.put(uid)
#	    	print	self.queue.qsize()
#            print multiprocessing.current_process().name + str(os.getpid()) + ' produced one product, the no of queue now is: %d' %self.queue.qsize()
            	sleep(2)
        
        
class Consumer(multiprocessing.Process):
    def __init__(self, queue):
        multiprocessing.Process.__init__(self)
        self.queue = queue
	self.Log=WriteLog()
	self.mysql_info=config_backup.mysql_user_info()
	self.mongo_info=config_backup.mongo_user_info()
	self.conn=MySQLHandler(self.mysql_info[0],self.mysql_info[1],self.mysql_info[2],self.mysql_info[3])


    def exc_mysql(self,id):

	try:
    		for igid in id:
#			value=int(igid)
			info=self.conn.get_mysql_data('select * from cloud_mongodb.tb_backup_mongodb_client where id=%s;'%(igid))
			backup=ansible_bak.apply_async(args=[self.mongo_info[0],self.mongo_info[1],info[0][1],info[0][2],info[0][3],info[0][4],info[0][5],info[0][6]])
			self.conn.get_mysql_data("update cloud_mongodb.tb_backup_mongodb_client set manual_bak_switch='OFF' where id=%s;"%(igid))
			if backup.status not in {'PENDING','STARTED','SUCCESS'}:
				log_msg='%s:%s Manual backup abnormal'
				self.Log.write('e'," exc_mysql {}".format(log_msg))

	except Exception as err:
                self.Log.write('e'," exc_mysql {}".format(err.message))



        
    def run(self):
        while True:
            d = self.queue.get(1)
            if d != None:
		if d != 'NULL':
			self.exc_mysql(d)
			for list in d:
				log_msg="Id for %s task is performed"%(list)
				self.Log.write('i'," run get {}".format(log_msg))
	    	else:
			log_msg='There is no task into the queue'
			self.Log.write('i'," run get {}".format(log_msg))

#		print type(d),d
#                print multiprocessing.current_process().name + str(os.getpid()) + ' consumed  %s, the no of queue now is: %d' %(d,self.queue.qsize())
                sleep(2)
                continue
            else:
                break
                
#create queue
queue = multiprocessing.Queue(40)
       
if __name__ == "__main__":
    processed = []
    for i in range(1):
        processed.append(Producer(queue))
        processed.append(Consumer(queue))
        
    for i in range(len(processed)):
        processed[i].start()
    
    for i in range(len(processed)):
        processed[i].join()  
