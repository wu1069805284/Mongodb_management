#!/usr/bin/python
from config_backup import mysql_user_info
from MySQLHandler import MySQLHandler
from LogHandler import WriteLog 
from ansible import runner
import json,sys


class ansible_backup(object):
	
	def __init__(self,mu,mp,ch,bh,cp,mpath,bv,bu):
		self.Log=WriteLog()
		self.mongo_user=mu
		self.mongo_pw=mp
		self.c_host=ch
		self.c_port=cp
		self.backup_host=bh
		self.bak_dir=mpath+'/58mongodb_backup'
		self.version=bv
		self.clean_day=int(bu)

	def ansible_initialize(self):

		dt = runner.Runner(
			  module_name='script',
			  module_args='script/mongo_backup.sh -d %s -h %s -P %s -v %s -c %d -m path_init' %(self.bak_dir,self.c_host,self.c_port,self.version,self.clean_day),
			  pattern='%s'%(self.backup_host),
		 	  forks=10
			)
			
		results = dt.run()
		json_data=json.dumps(results,indent=4)

		if results is None:
			return(json_data)
			sys.exit(1)

		for (hostname, result) in results['contacted'].items():
			if not 'failed' in result:
				if result['stdout'] == '':
					result['stdout'] = 'OK'
				log_msg="%s:%s >>> %s" % (hostname,self.c_port,result['stdout'])
				self.Log.write('i',"ansible_initialize {}".format(log_msg))
			elif 'failed' in result and result['stdout'] != '':
				log_msg="%s:%s >> %s > %s" % (hostname,self.c_port,result['stdout'],result['stderr'])
				self.Log.write('e',"ansible_initialize {}".format(log_msg))
		return(log_msg)


	def ansible_backup(self):

		self.ansible_initialize()

		dt = runner.Runner(
                          module_name='script',
                          module_args='script/mongo_backup.sh -u %s -p %s -h %s -P %s -b %s -d %s -v %s -c %s -m backup_start' %(self.mongo_user,self.mongo_pw,self.c_host,self.c_port,self.backup_host,self.bak_dir,self.version,self.clean_day),
                          pattern='%s'%(self.backup_host),
                          forks=10
                        )

                results = dt.run()
		json_data=json.dumps(results,indent=4)

                if results is None:
			return(json_data)
			sys.exit(1)

		for (hostname, result) in results['contacted'].items():
                        if not 'failed' in result:
                                if result['stdout'] == '':
                                        result['stdout'] = 'OK'
                                log_msg="%s:%s >>> %s" % (hostname,self.c_port,result['stdout'])
                                self.Log.write('i',"ansible_backup {}".format(log_msg))
                        elif 'failed' in result and result['stdout'] != '': 
                                log_msg="%s:%s >> %s > %s" % (hostname,self.c_port,result['stdout'],result['stderr'])
                                self.Log.write('e',"ansible_backup {}".format(log_msg))

		return(log_msg)
