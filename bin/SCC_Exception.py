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
