	
from pymongo import MongoClient
def mongoConn():
	try:
		URL="mongodb://localhost:2610/admin"
		client= MongoClient(URL)
		return(clinet)

	except Exception as e:
		print ("[Error] :%s"%(e))

if __name__ == '__main__':

	myclient = mongoConn()

	info = myclient.runcommand({"ping":1})

	print(info)
