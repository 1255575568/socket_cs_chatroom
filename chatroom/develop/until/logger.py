import logging
from logging import handlers
import configparser
import os
import datetime
# 读取配置文件
config = configparser.ConfigParser()
config.read('config/config.ini')

class Logger(object):
    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'crit': logging.CRITICAL
    }  # 日志级别关系映射

    def __init__(self, level='info', when='D', backCount=3,
                 # fmt='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'):
                 fmt='%(asctime)s - %(levelname)s: %(message)s'):
        base_dir = os.path.dirname(__file__)
        path = os.path.join(base_dir,
                            '../'+(config.get('log', 'path') + datetime.datetime.now().strftime('%Y-%m-%d') + '.log'))
        if not os.path.exists(path):
            fd = open(path, mode="w", encoding="utf-8")
            fd.close()
        self.logger = logging.getLogger(path)
        format_str = logging.Formatter(fmt)  # 设置日志格式
        self.logger.setLevel(self.level_relations.get(level))  # 设置日志级别
        sh = logging.StreamHandler()  # 往屏幕上输出
        sh.setFormatter(format_str)  # 设置屏幕上显示的格式
        th = handlers.TimedRotatingFileHandler(filename=path, when=when, backupCount=backCount,
                                               encoding='utf-8')  # 往文件里写入#指定间隔时间自动生成文件的处理器
        # 实例化TimedRotatingFileHandler
        # interval是时间间隔，backupCount是备份文件的个数，如果超过这个个数，就会自动删除，when是间隔的时间单位，单位有以下几种：
        # S 秒
        # M 分
        # H 小时、
        # D 天、
        # W 每星期（interval==0时代表星期一）
        # midnight 每天凌晨
        th.setFormatter(format_str)  # 设置文件里写入的格式
        self.logger.addHandler(sh)  # 把对象加到logger里
        self.logger.addHandler(th)