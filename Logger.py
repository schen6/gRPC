#coding:utf-8
import os
import datetime
import logging
import logging.config
import configparser

from conf.conf import Config

conf = Config()
file_path = conf.log_path


class log:
    def __init__(self, logger_name=None, over_write=False, to_file=True):
        '''

		:param over_write:
		:return:
		'''
        self.logger = logging.getLogger(name=logger_name)
        self.logger.handlers.clear()
        self.logger.setLevel(logging.DEBUG)
        # 终端Handler
        consoleHandler = logging.StreamHandler()
        consoleHandler.setLevel(logging.DEBUG)

        # 文件Handler
        #文件保存地址
        now_time = datetime.datetime.now().strftime('%Y-%m-%d')
        file_name = os.path.join(file_path, now_time + '.log')
        #文件保存格式，'a'为增加，'w'为覆盖
        if over_write:
            mode = 'w'
        else:
            mode = 'a'
        fileHandler = logging.FileHandler(file_name,
                                          mode=mode,
                                          encoding='UTF-8')
        fileHandler.setLevel(logging.NOTSET)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        consoleHandler.setFormatter(formatter)
        fileHandler.setFormatter(formatter)

        # 添加到Logger中
        self.logger.addHandler(consoleHandler)
        if to_file:
            self.logger.addHandler(fileHandler)


if __name__ == '__main__':
    log(to_file=False).logger.info('success')