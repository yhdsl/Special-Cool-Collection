"""
**模块说明** 软件的日志记录模块

**模块状态** DEBUG
"""

import logging
import os
import time


def _get_true_address(flie_name: str):
    """
    返回Logs文件夹的绝对地址

    :param flie_name: Logs文件夹名称
    :return: Logs文件夹的绝对地址
    """
    module_address = os.getcwd()
    return os.path.dirname(module_address) + "\\" + flie_name


# 默认日志文件夹的名称
DEFAULT_ADDRESS_NAME = r'Logs'
# 日志文件存储的绝对地址
DEFAULT_TRUE_ADDRESS = _get_true_address(DEFAULT_ADDRESS_NAME)
# 最大日志文件数量，注意文件是从0开始计数的，默认为5
MAX_LOGS_FILES = 5
# 不带后缀名的日志文件名，注意该项更该后本模块可能无法正常工作
DEFAULT_FILE_NAME = 'f"SCC_Logs{logs_int}"'
# 程序版本号，由__init__文件初始化时修改
SOFTWARE_VERSION = ''
# 日志初始化时的首行内容
LOGS_FILE_FIRST_LINE = r'f"开始记录日志 当前时间{logs_time} 记录等级{logs_level} SCC版本号v{logs_version}\n"'
# 日志的时间格式
LOGS_TIME_FORMAT = '%Y/%m/%d %I:%M:%S %p'
# 日志的内容格式
LOGS_FORMATTER_FORMAT = '[%(asctime)s] %(levelname)s %(name)s/%(module)s.%(funcName)s.%(lineno)d: %(message)s'
# 日志等级对应的字典
LOGS_LEVEL_DIR = {logging.CRITICAL: 'CRITICAL',
                  logging.ERROR: 'ERROR',
                  logging.WARNING: 'WARNING',
                  logging.INFO: 'INFO',
                  logging.DEBUG: 'DEBUG',
                  logging.NOTSET: 'NOTSET'}
# 日志等级，默认为INFO
LOG_LEVEL = logging.INFO


class Logs:
    """
    用于日志记录

    *类参数* \n
    **module_name=__name__ (str)** 包名 \n
    **run_first=False (bool)** 是否新建一个日志文件 \n

    *类属性* \n
    **logger (logging.Logger)** 日志记录器 \n
    """

    def __init__(self, module_name=__name__, run_first=False):
        if run_first:
            self._make_new_file()
        self.logger = self._get_log(module_name=module_name,
                                    file_address=rf'{DEFAULT_TRUE_ADDRESS}\{self._get_file_name()}.txt')

    @staticmethod
    def _get_file_name(get_int=False):
        """
        获取当前日志文件名称或返回日志数字特征值列表
        该方法尽量保证文件名称不是递增时仍然可以正常运行

        :param get_int: 是否返回包含所有文件数字标识的列表，默认为False
        :return: 日志文件名称或特征值列表
        """
        file_list = os.listdir(DEFAULT_TRUE_ADDRESS)
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
        if not os.path.isdir(DEFAULT_TRUE_ADDRESS):  # 保证Logs文件夹存在
            os.mkdir(DEFAULT_TRUE_ADDRESS)
        file_int_list = self._get_file_name(get_int=True)
        if not file_int_list:  # 生成0号文件
            file_name = eval(DEFAULT_FILE_NAME, {'logs_int': 0})
            file_open = open(rf"{DEFAULT_TRUE_ADDRESS}\{file_name}.txt", encoding='utf8', mode='x')
        else:
            if max(file_int_list) < MAX_LOGS_FILES - 1:  # 文件数量未达到上限
                file_name = eval(DEFAULT_FILE_NAME, {'logs_int': max(file_int_list) + 1})
                file_open = open(rf"{DEFAULT_TRUE_ADDRESS}\{file_name}.txt", encoding='utf8', mode='x')
            else:
                remove_file_name = eval(DEFAULT_FILE_NAME, {'logs_int': min(file_int_list)})
                os.remove(rf"{DEFAULT_TRUE_ADDRESS}\{remove_file_name}.txt")  # 移除超出上限的文件
                file_int_list.remove(min(file_int_list))
                for i in range(0, MAX_LOGS_FILES - 1):
                    file_old_name1 = rf"{DEFAULT_TRUE_ADDRESS}"
                    file_old_name2 = rf"\{eval(DEFAULT_FILE_NAME, {'logs_int': file_int_list[i]})}.txt"
                    file_old_name = file_old_name1 + file_old_name2
                    file_new_name = rf"{DEFAULT_TRUE_ADDRESS}\{eval(DEFAULT_FILE_NAME, {'logs_int': i})}.txt"
                    os.rename(file_old_name, file_new_name)
                file_name = eval(DEFAULT_FILE_NAME, {'logs_int': MAX_LOGS_FILES - 1})
                file_open = open(rf"{DEFAULT_TRUE_ADDRESS}\{file_name}.txt", encoding='utf8', mode='x')
        file_open.write(eval(LOGS_FILE_FIRST_LINE,
                             {'logs_time': time.strftime(LOGS_TIME_FORMAT),
                              'logs_level': LOGS_LEVEL_DIR[LOG_LEVEL],
                              'logs_version': SOFTWARE_VERSION}))
        file_open.close()
        return

    @staticmethod
    def _get_handler(file_address: str):
        """
        返回日志处理器，向指定文件尾端增添内容

        :param file_address: 日志文件地址
        :return: 处理器
        """
        return logging.FileHandler(file_address, mode='a+', encoding='utf8')

    @staticmethod
    def _get_formatter():
        """

        :return: 格式器
        """
        return logging.Formatter(LOGS_FORMATTER_FORMAT, LOGS_TIME_FORMAT)

    def _get_log(self, module_name: str, file_address: str, ):
        """
        返回记录器，并绑定处理器和格式器

        :param module_name: 模块包名
        :param file_address: 日志文件地址
        :return:
        """
        logger = logging.getLogger(module_name)
        logger.setLevel(LOG_LEVEL)
        logger_formatter = self._get_formatter()
        logger_handler = self._get_handler(file_address=file_address)
        logger_handler.setFormatter(logger_formatter)
        logger.addHandler(logger_handler)
        return logger


if __name__ == '__main__':
    pass
