"""
**模块说明** 软件的异常模块，包含 大部分自定义模块抛出的异常 \n
**模块状态** 随模块的开发更新异常
"""

import SCC_Localization as Local


# 底层数据库异常部分
# SCC_Database


class DBNotExistError(Exception):
    """数据库不存在"""
    def __str__(self):
        return Local.GetTranslation('SCC_Database', 'DBNotExistError').translation


class TableCreateError(Exception):
    """表名已存在，无法新建"""
    def __str__(self):
        return Local.GetTranslation('SCC_Database', 'TableCreateError').translation


class TableDropError(Exception):
    """表名不存在，无法删除"""
    def __str__(self):
        return Local.GetTranslation('SCC_Database', 'TableDropError').translation


class ColunmError(Exception):
    """表名不存在，进行列操作"""
    def __str__(self):
        return Local.GetTranslation('SCC_Database', 'ColunmError').translation


class ColunmValuesLessError(Exception):
    """数据过少"""
    def __str__(self):
        return Local.GetTranslation('SCC_Database', 'ColunmValuesLessError').translation

# 配置库异常部分
# SCC_Configuration


class ConfigDBAddError(Exception):
    """DB中配置已存在"""
    def __str__(self):
        return Local.GetTranslation('SCC_Configuration', 'ConfigDBAddError').translation


class ConfigDBDropError(Exception):
    """DB中配置已存在"""
    def __str__(self):
        return Local.GetTranslation('SCC_Configuration', 'ConfigDBDropError').translation


class ConfigDBUpError(Exception):
    """DB中配置已存在"""
    def __str__(self):
        return Local.GetTranslation('SCC_Configuration', 'ConfigDBUpError').translation


class ConfigDBBoolError(Exception):
    """布尔值转换错误"""
    def __str__(self):
        return Local.GetTranslation('SCC_Configuration', 'ConfigDBBoolError').translation


class ConfigDBGetError(Exception):
    """DB中没有该配置名称"""
    def __str__(self):
        return Local.GetTranslation('SCC_Configuration', 'ConfigDBGetError').translation
