import configparser
import os
from . import SCC_Localization as Lang
from . import SCC_Logs as Logs

# 配置文件地址
CODEBASE_CONGIG_ADDRESS = os.path.dirname(str(__file__).rsplit('\\', maxsplit=1)[0]) + r"\Config\CodeBase\Main.ini"
SOFTWARE_VERSION = ''  # 创建日志文件时需要先给出版本号，该值一般来说没有用处
__CODEBASE_SCC_LOGS = 'SCC_Logs'
__CODEBASE_SCC_Localization = 'SCC_Localization'


def __config_start(config_address: str, config_sections: str, config_name: str):
    """
    私有函数，用于可靠的从配置文件中读取自定义配置
    该函数仅应当在初始化时被调用，其旨在保证最大稳定性
    其他配置需求应调用该包中的配置模块来实现

    :param config_address: 配置文件地址
    :param config_sections: 配置的节名
    :param config_name: 配置的键
    :return: 返回一个列表，其第一个元素为布尔值，第二个元素为读取的配置值，不会进行类型转换
    """
    config_get = [False, '']
    configparser_get = configparser.ConfigParser(empty_lines_in_values=False)
    configparser_get.optionxform = lambda option: option
    if os.path.exists(config_address):
        configparser_get.read_file(open(config_address, encoding='utf8'))
        if configparser_get.has_option(config_sections, config_name):
            config_get[0] = True
            config_get[1] = configparser_get.get(config_sections, config_name)
    return config_get


# SCC_Localization模块配置初始化
if not os.path.exists(Lang.DEFAULT_TRUE_ADDRESS):  # 确保Localization文件夹存在
    os.mkdir(Lang.DEFAULT_TRUE_ADDRESS)
if __config_start(CODEBASE_CONGIG_ADDRESS, __CODEBASE_SCC_Localization, 'TRANSLATION_LANGUAGE')[0]:
    Logs.LOG_LEVEL = __config_start(CODEBASE_CONGIG_ADDRESS, __CODEBASE_SCC_Localization, 'TRANSLATION_LANGUAGE')[1]

# SCC_Logs模块配置初始化
if not os.path.exists(Logs.DEFAULT_TRUE_ADDRESS):  # 确保Logs文件夹存在
    os.mkdir(Logs.DEFAULT_TRUE_ADDRESS)
if __config_start(CODEBASE_CONGIG_ADDRESS, __CODEBASE_SCC_LOGS, 'MAX_LOGS_FILES')[0]:
    Logs.MAX_LOGS_FILES = int(__config_start(CODEBASE_CONGIG_ADDRESS, __CODEBASE_SCC_LOGS, 'MAX_LOGS_FILES')[1])
if __config_start(CODEBASE_CONGIG_ADDRESS, __CODEBASE_SCC_LOGS, 'LOG_LEVEL_STR')[0]:
    Logs.LOG_LEVEL = Logs.LOGS_LEVEL_DIR[__config_start(CODEBASE_CONGIG_ADDRESS,
                                                        __CODEBASE_SCC_LOGS, 'LOG_LEVEL_STR')[1]]
Logs.SOFTWARE_VERSION = SOFTWARE_VERSION

if __name__ == '__main__':
    pass
