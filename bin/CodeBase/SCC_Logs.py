"""
**模块说明** \n
软件的日志记录模块 \n
**模块状态** \n
已完成
"""

import logging
import os
import time

# 日志文件存储的绝对地址
DEFAULT_TRUE_ADDRESS = os.path.dirname(str(__file__).rsplit('\\', maxsplit=1)[0]) + r'\Logs'
# 最大日志文件数量，注意文件是从0开始计数的，默认为5，该值由配置文件优先提供
MAX_LOGS_FILES = 5
# 不带后缀名的日志文件名，注意该项更该后本模块可能无法正常工作
_DEFAULT_FILE_NAME = 'f"SCC_Logs{logs_int}"'
# 程序版本号，由启动模块赋值
SOFTWARE_VERSION = ''
# 日志初始化时的首行内容
_LOGS_FILE_FIRST_LINE = r'f"开始记录日志  当前时间{logs_time}  记录等级{logs_level}  SCC版本号 v{logs_version}\n"'
# 日志的时间格式
_LOGS_TIME_FORMAT = '%Y/%m/%d %I:%M:%S %p'
# 日志的内容格式
_LOGS_FORMATTER_FORMAT = r'[%(asctime)s] %(levelname)s %(name)s\%(module)s.%(funcName)s.%(lineno)d: %(message)s'
# 日志等级对应的字典，保证双向读取，其中OFF为关闭日志等级
LOGS_LEVEL_DIR = {logging.CRITICAL: 'CRITICAL',
                  logging.ERROR: 'ERROR',
                  logging.WARNING: 'WARNING',
                  logging.INFO: 'INFO',
                  logging.DEBUG: 'DEBUG',
                  logging.NOTSET: 'NOTSET',
                  100: 'OFF',
                  'CRITICAL': logging.CRITICAL,
                  'ERROR': logging.ERROR,
                  'WARNING': logging.WARNING,
                  'INFO': logging.INFO,
                  'DEBUG': logging.DEBUG,
                  'NOTSET': logging.NOTSET,
                  'OFF': 100}
# 日志等级，默认为INFO，该值由配置文件优先提供
LOG_LEVEL_INT = logging.INFO


class Logs:
    """
    实现日志记录的相关功能
    其中first_run参数仅由启动模块和调试时使用，用于建立一个新的日志文件

    *类参数* \n
    **module_name=__name__: str** 包名 \n
    **first_run=False: bool** 是否新建一个日志文件 \n

    *类属性* \n
    **logger -> logging.Logger** 日志记录器 \n
    """

    def __init__(self, module_name=__name__, first_run=False):
        if first_run:
            self._create_new_file()
        else:
            self.logger = self._get_log(module_name=module_name,
                                        file_address=rf'{DEFAULT_TRUE_ADDRESS}\{self._get_file_name()}.txt')

    @staticmethod
    def _get_file_name(get_int=False):
        """
        获取当前日志文件名称或返回日志数字特征值列表
        该方法尽量保证文件名称不是递增时仍然可以正常运行
        文件不存在时可能会触发异常

        :param get_int: 是否返回包含所有文件数字标识的列表，默认为False
        :return: 日志文件名称或特征值列表
        """
        file_list = os.listdir(DEFAULT_TRUE_ADDRESS)
        file_int_list = []
        file_name_test = eval(_DEFAULT_FILE_NAME, {'logs_int': 0})
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
            return eval(_DEFAULT_FILE_NAME, {'logs_int': logs_int})

    def _create_new_file(self):
        """
        创建一个新的日志文件，并向其写入初始化内容
        仅用于该模块的初始化进程
        """
        if not os.path.isdir(DEFAULT_TRUE_ADDRESS):  # 保证Logs文件夹存在
            os.mkdir(DEFAULT_TRUE_ADDRESS)
        file_int_list = self._get_file_name(get_int=True)
        if not file_int_list:  # 生成0号文件
            file_name = eval(_DEFAULT_FILE_NAME, {'logs_int': 0})
            file_open = open(rf"{DEFAULT_TRUE_ADDRESS}\{file_name}.txt", encoding='utf8', mode='x')
        else:
            if max(file_int_list) < MAX_LOGS_FILES - 1:  # 文件数量未达到上限
                file_name = eval(_DEFAULT_FILE_NAME, {'logs_int': max(file_int_list) + 1})
                file_open = open(rf"{DEFAULT_TRUE_ADDRESS}\{file_name}.txt", encoding='utf8', mode='x')
            else:
                remove_file_name = eval(_DEFAULT_FILE_NAME, {'logs_int': min(file_int_list)})
                os.remove(rf"{DEFAULT_TRUE_ADDRESS}\{remove_file_name}.txt")  # 移除超出上限的文件
                file_int_list.remove(min(file_int_list))
                for i in range(0, MAX_LOGS_FILES - 1):
                    file_old_name1 = rf"{DEFAULT_TRUE_ADDRESS}"
                    file_old_name2 = rf"\{eval(_DEFAULT_FILE_NAME, {'logs_int': file_int_list[i]})}.txt"
                    file_old_name = file_old_name1 + file_old_name2
                    file_new_name = rf"{DEFAULT_TRUE_ADDRESS}\{eval(_DEFAULT_FILE_NAME, {'logs_int': i})}.txt"
                    os.rename(file_old_name, file_new_name)
                file_name = eval(_DEFAULT_FILE_NAME, {'logs_int': MAX_LOGS_FILES - 1})
                file_open = open(rf"{DEFAULT_TRUE_ADDRESS}\{file_name}.txt", encoding='utf8', mode='x')
        file_open.write(eval(_LOGS_FILE_FIRST_LINE,
                             {'logs_time': time.strftime(_LOGS_TIME_FORMAT),
                              'logs_level': LOGS_LEVEL_DIR[LOG_LEVEL_INT],
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
        return logging.Formatter(_LOGS_FORMATTER_FORMAT, _LOGS_TIME_FORMAT)

    def _get_log(self, module_name: str, file_address: str):
        """
        返回记录器，并绑定相关的处理器和格式器

        :param module_name: 模块包名
        :param file_address: 日志文件地址
        :return:
        """
        logger = logging.getLogger(module_name)
        logger.setLevel(LOG_LEVEL_INT)
        logger_formatter = self._get_formatter()
        logger_handler = self._get_handler(file_address=file_address)
        logger_handler.setFormatter(logger_formatter)
        logger.addHandler(logger_handler)
        return logger


if __name__ == '__main__':
    pass
