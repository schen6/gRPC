import os
import sys
import configparser

current_path = os.path.realpath(__file__)
root_path = os.path.dirname(os.path.dirname(current_path))
cfp = configparser.ConfigParser()
cfp.read(os.path.join(root_path, 'conf/web.conf'), encoding='utf-8')


class Config():
    def __init__(self):
        self.log_path = cfp.get('log', 'path')
        self.model_path = cfp.get('model', 'path')


if __name__ == '__main__':
    print(root_path)