# -----CodeBase包 初始化进程-----
# 本模块负责实现自定义配置的自动载入功能
# 启动模块负责实现
# 1.启动该初始化进程
# 2.向日志模块传入程序版本号
# 3.生成新的日志文件并初始化日志记录器
# 4.复检配置的可用性，并写入日志
# 5.检查日志等级，如果为OFF则删除新建立的日志文件
# -----CodeBase包 说明-----
# SCC_Configuration 实现配置文件的相关功能
# SCC_Database 实现底层数据库的相关功能
# SCC_Exception 包含所有的自定义异常
# SCC_Localization 提供语言选择功能，已在此模块中导入
# SCC_Logs 提供日志记录功能，已在此模块中导入
# SCC_Scrapy 开发中
# SCC_Subprocess 开发中

import configparser
import os
from . import SCC_Localization as Lang
from . import SCC_Logs as Logs

# 配置文件地址
__CODEBASE_CONGIG_ADDRESS = os.path.dirname(str(__file__).rsplit('\\', maxsplit=1)[0]) + r'\Config\CodeBase\Main.ini'
# 已在初始化导入的模块名称
__CODEBASE_SCC_LOGS = 'SCC_Logs'
__CODEBASE_SCC_Localization = 'SCC_Localization'


def _config_check(config_address: str, config_sections: str, config_name: str):
    """
    用于从配置文件中读取自定义配置 \n
    该函数仅应当在初始化和启动模块自检时被调用，其旨在保证最大的稳定性 \n
    其他配置需求应调用CodeBase包中的配置模块来实现

    :param config_address: 配置文件地址
    :param config_sections: 配置的节名
    :param config_name: 配置的键值
    :return: 返回一个列表，其第一个元素为布尔值，表明配置是否存在；第二个元素为读取的配置值，并且不会进行类型转换，默认为 ''
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


# SCC_Localization模块 配置初始化
if not os.path.exists(Lang.DEFAULT_TRUE_ADDRESS):
    os.mkdir(Lang.DEFAULT_TRUE_ADDRESS)  # 确保Localization文件夹存在
if _config_check(__CODEBASE_CONGIG_ADDRESS, __CODEBASE_SCC_Localization, 'TRANSLATION_LANGUAGE')[0]:
    Logs.LOG_LEVEL = _config_check(__CODEBASE_CONGIG_ADDRESS, __CODEBASE_SCC_Localization, 'TRANSLATION_LANGUAGE')[1]

# SCC_Logs模块 配置初始化
if not os.path.exists(Logs.DEFAULT_TRUE_ADDRESS):
    os.mkdir(Logs.DEFAULT_TRUE_ADDRESS)  # 确保Logs文件夹存在
if _config_check(__CODEBASE_CONGIG_ADDRESS, __CODEBASE_SCC_LOGS, 'MAX_LOGS_FILES')[0]:
    Logs.MAX_LOGS_FILES = int(_config_check(__CODEBASE_CONGIG_ADDRESS, __CODEBASE_SCC_LOGS, 'MAX_LOGS_FILES')[1])
if _config_check(__CODEBASE_CONGIG_ADDRESS, __CODEBASE_SCC_LOGS, 'LOG_LEVEL_STR')[0]:
    Logs.LOG_LEVEL = Logs.LOGS_LEVEL_DIR[_config_check(__CODEBASE_CONGIG_ADDRESS,
                                                       __CODEBASE_SCC_LOGS, 'LOG_LEVEL_STR')[1]]
