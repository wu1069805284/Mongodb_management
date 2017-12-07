#coding=utf-8
#!/usr/local/bin/python
import logging,sys

class WriteLog(object):

    def write(self,log_lev,log_msg):
        logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s [%(levelname)s] %(message)s',
                datefmt='%Y-%m-%d %X',
                filename=sys.path[0] + '/general.log',
#		filename='/work/wuweijian/inception/autosql/general.log',
                filemode='a')

        if log_lev == 'd':
            logging.debug(log_msg)
        elif log_lev == 'i':
            logging.info(log_msg)
        elif log_lev == 'w':
            logging.warning(log_msg)
        elif log_lev == 'e':
            logging.error(log_msg)
        elif log_lev == 'c':
            logging.critical(log_msg)

