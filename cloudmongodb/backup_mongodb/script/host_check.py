#!/usr/bin/python
import ansible.runner
import sys,os,json,MySQLdb
from threading import Thread



def get_hostinfo(ip):
	data = []
	results = ansible.runner.Runner(
				module_name='setup',
#				module_args='filter=ansible_mounts',
				pattern='backup_host',
				forks=10
		)
	datastructure = results.run()
#	host_data=json.dumps(host,indent=4,sort_keys=True)	
	sn = datastructure['contacted'][ip]['ansible_facts']['ansible_product_serial']
	sysinfo = datastructure['contacted'][ip]['ansible_facts']['ansible_system']
	cpu = datastructure['contacted'][ip]['ansible_facts']['ansible_processor'][1]
	cpu = ''.join(cpu.split())
	mem = datastructure['contacted'][ip]['ansible_facts']['ansible_memtotal_mb']
	disk = datastructure['contacted'][ip]['ansible_facts']['ansible_devices']['sda']['size']

	partition_information=datastructure['contacted'][ip]['ansible_facts']['ansible_mounts']

	for key in  partition_information:
		partition=key['device'] 
		mount_disk=key['mount']
		Available_size=key['size_available']
		total_size=key['size_total']
		hostname_pub = datastructure['contacted'][ip]['ansible_facts']['ansible_nodename']
		ipadd_in = datastructure['contacted'][ip]['ansible_facts']['ansible_all_ipv4_addresses'][0]
		data.append((hostname_pub,ipadd_in,partition,mount_disk,total_size,Available_size))
	return  data




def operation_db(data):


	try:
		conn=MySQLdb.connect(user='wcdb_admin',passwd='2262acef336ce54a',host='10.126.72.26',db='db58_wcdb',port=3261)
		cur=conn.cursor()
		

		sql='''
		insert into tb_backup_mongodb_storage(hostname,ipaddress,partition,mount_directory,total_size_G,available_size_G,add_time,statdate_time) values (%s,%s,%s,%s,%s/1024/1024/1024,%s/1024/1024/1024,now(),CURDATE());
		'''
		
		
		for value in data:
			cur.execute(sql,value)
		
		cur.execute("delete from tb_backup_mongodb_storage where statdate_time=CURDATE() and mount_directory in ('/','/boot','/opt')")

		conn.commit()
		cur.close()   


	except MySQLdb.Error ,e:
		print	"Error %d:%s" % (e.args[0], e.args[1])
		try:  
    			sqlError =  "Error %d:%s" % (e.args[0], e.args[1])  
		except IndexError:  
    			print "MySQL Error:%s" % str(e) 


def thead_save(i):

	data = get_hostinfo(i)
	operation_db(data)


def delete():
	try:
        	conn=MySQLdb.connect(user='wcdb_admin',passwd='2262acef336ce54a',host='10.126.72.26',db='db58_wcdb',port=3261)
        	cur=conn.cursor()
		cur.execute("delete from tb_backup_mongodb_storage where statdate_time=CURDATE() ")

        	conn.commit()
        	cur.close()
		
	except MySQLdb.Error as e:
		print e


if __name__ == '__main__':
    delete()
    threads = []
#    fi = open('/data1/github/cloudmongodb/ansible/backup_ceshi/script/backup_host','r')

    fi = open(sys.path[0] + '/backup_host','r')
    fline = fi.readlines()
    fi.close()


    for i in fline:
	i = i.strip()
	threads.append(Thread(target=thead_save,args=(i,)))


    for thread in threads:
	thread.start()
       
    for thread in threads:
	thread.join()


