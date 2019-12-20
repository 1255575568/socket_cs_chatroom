import pymysql
import configparser
import time
import os
import datetime
from until.logger import Logger
# 读取配置文件
config = configparser.ConfigParser()
config.read('config/config.ini')
# 日志
base_dir = os.path.dirname(__file__)
path = os.path.join(base_dir, ('../' + config.get('log', 'path') + datetime.datetime.now().strftime('%Y-%m-%d') + '.log'))
log = Logger(path, level='info').logger


def get_time_id():
    now = time.time()
    int_now = int(now)
    ms = int((now - int_now) * 1000)
    time_id = time.strftime("%y%m%d%H%M%S", time.localtime(time.time())) + str(ms)
    return time_id


class Dao:
    def __init__(self, table_name):
        self.cur = self.conn.cursor()
        self.conn = pymysql.connect(user=config.get('mysql', 'user'), password=config.get(('mysql', 'password')),
                                    database="chatroom", charset="utf8")
        self.table_name = table_name

    def write_db(self, *data):
        sql = "INSERT INTO " + str(self.table_name) + " VALUES('" + get_time_id() + "'"
        for i in range(len(data)):
            if type(data[i]) == type("string"):
                sql += ",'" + data[i] + "'"
            else:
                sql += "," + str(data[i])
        sql += ")"
        try:
            self.cur.execute(sql.encode('utf-8'))
            self.conn.commit()
        except Exception as e:
            log.debug("writting  database error:%s" % e)
