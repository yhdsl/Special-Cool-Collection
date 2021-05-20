"""
**模块说明** 软件的日志记录模块

**模块状态** 开发中
"""

import logging
import os
import time

# 默认日志文件存储的相对地址
DEFAULT_FILE_ADDRESS = r'Logs'
# 最大日志文件数量，注意文件是从0开始计数的
MAX_LOGS_FILES = 5
# 不带后缀名的日志文件名，注意该项更该后本模块可能无法正常工作
DEFAULT_FILE_NAME = 'f"SCC_Logs{logs_int}"'
# 日志初始化时的首行内容
LOGS_FILE_FIRST_LINE = r'f"本日志于{logs_time}开始记录，记录等级为{logs_level}\n"'
# 日志的时间格式
LOGS_TIME_FORMAT = r'%Y/%m/%d %I:%M:%S %p'
# 日志等级
LOGS_LEVEL_DIR = {logging.CRITICAL: 'CRITICAL',
                  logging.ERROR: 'ERROR',
                  logging.WARNING: 'WARNING',
                  logging.INFO: 'INFO',
                  logging.DEBUG: 'DEBUG',
                  logging.NOTSET: 'NOTSET'}
# 默认选择的日志等级
DEFAULT_LOG_LEVEL = logging.INFO


class Logs:
    def __init__(self):
        pass

    @staticmethod
    def _get_file_name(get_int=False):
        """
        获取当前日志文件名称或返回日志数字特征值列表
        该方法尽量保证文件名称不是递增时仍然可以正常运行

        :param get_int: 是否返回包含所有文件数字标识的列表，默认为False
        :return: 日志文件名称或特征值列表
        """
        file_list = os.listdir(DEFAULT_FILE_ADDRESS)
        file_int_list = []
        file_name_test = eval(DEFAULT_FILE_NAME, {'logs_int': 0})
        file_int = len(file_name_test[:-1])  # 尝试获取文件名称的长度
        for i in file_list:
            file_int_list.append(int(i.rsplit('.')[0][file_int:]))  # 日志文件名称规则更改后可能会出现异常
        file_int_list.sort()  # 排序数组特征值列表
        if get_int:
            return file_int_list
        else:
            if not len(file_int_list):
                logs_int = 0
            else:
                logs_int = max(file_int_list)
            return eval(DEFAULT_FILE_NAME, {'logs_int': logs_int})

    def _make_new_file(self):
        """
        创建一个新的日志文件，并向其写入初始化内容
        仅用于该模块的初始化进程
        """
        file_int_list = self._get_file_name(get_int=True)
        if not os.path.isdir(DEFAULT_FILE_ADDRESS):  # 保证Logs文件夹存在
            os.mkdir(DEFAULT_FILE_ADDRESS)
        if not file_int_list:  # 生成0号文件
            file_name = eval(DEFAULT_FILE_NAME, {'logs_int': 0})
            file_open = open(rf"{DEFAULT_FILE_ADDRESS}\{file_name}.txt", encoding='utf8', mode='x')
        else:
            if max(file_int_list) < MAX_LOGS_FILES - 1:  # 文件数量未达到上限
                file_name = eval(DEFAULT_FILE_NAME, {'logs_int': max(file_int_list) + 1})
                file_open = open(rf"{DEFAULT_FILE_ADDRESS}\{file_name}.txt", encoding='utf8', mode='x')
            else:
                remove_file_name = eval(DEFAULT_FILE_NAME, {'logs_int': min(file_int_list)})
                os.remove(rf"{DEFAULT_FILE_ADDRESS}\{remove_file_name}.txt")  # 移除超出上限的文件
                file_int_list.remove(min(file_int_list))
                for i in range(0, MAX_LOGS_FILES - 1):
                    file_old_name1 = rf"{DEFAULT_FILE_ADDRESS}"
                    file_old_name2 = rf"\{eval(DEFAULT_FILE_NAME, {'logs_int': file_int_list[i]})}.txt"
                    file_old_name = file_old_name1 + file_old_name2
                    file_new_name = rf"{DEFAULT_FILE_ADDRESS}\{eval(DEFAULT_FILE_NAME, {'logs_int': i})}.txt"
                    os.rename(file_old_name, file_new_name)
                file_name = eval(DEFAULT_FILE_NAME, {'logs_int': MAX_LOGS_FILES - 1})
                file_open = open(rf"{DEFAULT_FILE_ADDRESS}\{file_name}.txt", encoding='utf8', mode='x')
        file_open.write(eval(LOGS_FILE_FIRST_LINE,
                             {'logs_time': time.strftime(LOGS_TIME_FORMAT),
                              'logs_level': LOGS_LEVEL_DIR[DEFAULT_LOG_LEVEL]}))
        file_open.close()
        return


if __name__ == '__main__':
    obj_test1 = Logs()
