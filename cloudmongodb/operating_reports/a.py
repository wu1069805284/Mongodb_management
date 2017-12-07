from pymongo import MongoClient




class mongo(object):

        def __init__(self):
                self.user="admin"
                self.password=123456

        def mongoconn(self,host,port,db='admin'):
		URL="mongodb://%s:%s@%s:%s/%s" %(self.user,self.password,host,port,db)
		mongoconn = MongoClient(URL)
		#conn = mongoconn.admin.authenticate(self.user,self.password)
		return(mongoconn)

	def data_info(self,host,port):
		#self.mongoconn(host,port).admin.authenticate(self.user,self.password)
		Statusinfo = self.mongoconn(host,port).admin.command("serverStatus")
		qpsstatus = Statusinfo['opcounters']
		qtotal = qpsstatus['query']
		print qtotal		

if __name__ == '__main__':
	conn = mongo()
	#conn.mongoconn('localhost',3200)
	conn.data_info('localhost',3200)







