"""
**模块说明** \n
软件的异常模块，包含所有自定义模块抛出的异常 \n
**模块状态** \n
随模块的开发更新异常
"""

from . import SCC_Localization as Lang
from . import SCC_Logs

# 日志记录器，仅记录异常文本，具体的触发参数和异常帧由各模块负责写入
_logger = SCC_Logs.Logs().logger

# 底层数据库异常部分
# SCC_Database


class DBNotExistError(Exception):
    """数据库不存在"""
    def __str__(self):
        lang = Lang.GetTranslation('SCC_Database', 'DBNotExistError').translation
        _logger.error(f'异常已触发 {lang} ，具体触发参数见上方内容')
        return lang


class TableCreateError(Exception):
    """表名已存在，无法新建"""
    def __str__(self):
        lang = Lang.GetTranslation('SCC_Database', 'TableCreateError').translation
        _logger.error(f'异常已触发 {lang} ，具体触发参数见上方内容')
        return lang


class TableDropError(Exception):
    """表名不存在，无法删除"""
    def __str__(self):
        lang = Lang.GetTranslation('SCC_Database', 'TableDropError').translation
        _logger.error(f'异常已触发 {lang} ，具体触发参数见上方内容')
        return lang


class ColunmError(Exception):
    """表名不存在，进行列操作"""
    def __str__(self):
        lang = Lang.GetTranslation('SCC_Database', 'ColunmError').translation
        _logger.error(f'异常已触发 {lang} ，具体触发参数见上方内容')
        return lang


class ColunmValuesLessError(Exception):
    """数据过少"""
    def __str__(self):
        lang = Lang.GetTranslation('SCC_Database', 'ColunmValuesLessError').translation
        _logger.error(f'异常已触发 {lang} ，具体触发参数见上方内容')
        return lang

# 配置库异常部分
# SCC_Configuration


class ConfigDBAddError(Exception):
    """DB中配置已存在"""
    def __str__(self):
        lang = Lang.GetTranslation('SCC_Configuration', 'ConfigDBAddError').translation
        _logger.error(f'异常已触发 {lang} ，具体触发参数见上方内容')
        return lang


class ConfigDBDropError(Exception):
    """DB中配置已存在"""
    def __str__(self):
        lang = Lang.GetTranslation('SCC_Configuration', 'ConfigDBDropError').translation
        _logger.error(f'异常已触发 {lang} ，具体触发参数见上方内容')
        return lang


class ConfigDBUpError(Exception):
    """DB中配置已存在"""
    def __str__(self):
        lang = Lang.GetTranslation('SCC_Configuration', 'ConfigDBUpError').translation
        _logger.error(f'异常已触发 {lang} ，具体触发参数见上方内容')
        return lang


class ConfigDBBoolError(Exception):
    """布尔值转换错误"""
    def __str__(self):
        lang = Lang.GetTranslation('SCC_Configuration', 'ConfigDBBoolError').translation
        _logger.error(f'异常已触发 {lang} ，具体触发参数见上方内容')
        return lang


class ConfigDBGetError(Exception):
    """DB中没有该配置名称"""
    def __str__(self):
        lang = Lang.GetTranslation('SCC_Configuration', 'ConfigDBGetError').translation
        _logger.error(f'异常已触发 {lang} ，具体触发参数见上方内容')
        return lang


class ConfigAddressError(Exception):
    """没有配置文件"""
    def __str__(self):
        lang = Lang.GetTranslation('SCC_Configuration', 'ConfigAddressError').translation
        _logger.error(f'异常已触发 {lang} ，具体触发参数见上方内容')
        return lang
