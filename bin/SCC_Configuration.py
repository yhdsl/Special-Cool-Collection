"""
**模块说明** 软件的配置模块，目前提供两种配置管理 \n
**模块状态** 开发中
"""

import configparser
import SCC_Database
import SCC_Exception

# 默认DB文件存储地址
DEFAULT_DB_ADDRESS = r'Configuration\\DataBase\\'
# DB表格式
DEFAULT_TABLE_RULE = "config TEXT NOT NULL UNIQUE," \
                     "value TEXT NOT NULL," \
                     "changeable INTEGER DEFAULT 0," \
                     "note TEXT DEFAULT ''"


class _ConfigDB:
    """
    配置模块中关于DB数据库的操作方法

    *类参数* \n
    **db_name (str)** db数据库名称 \n
    **module_name (str)** 调用该类的模块名称，这将作为表名传入 \n
    **config_name='' (str)** 需要操作的配置名称 \n
    **create_db=False (bool)** 设置为True以便于创建一个新的空数据库，**若原数据库存在将被删除**

    *类属性* \n
    **config (str)** 重写该属性以便于对不同的配置进行操作

    *类方法* \n
    **table_create** 创建以模块命名的表\n
    **table_del** 删除以模块命名的表\n
    **config_name_tup (tup)** 返回该模块的所有配置名称\n
    **value_create(value: str, changeable=0, note='')** 添加配置\n
    **value_del()** 删除配置\n
    **value_get()** 获取配置\n
    **value_updata(value: str, changeable=-1, note='')** 更新配置\n
    **db_close()** 提交所有的修改\n
    """

    def __init__(self, db_name: str, module_name: str, config_name='', create_db=False):
        self._con = SCC_Database.SQLDBGetStart(DEFAULT_DB_ADDRESS + db_name, create_db=create_db).con
        self._table = module_name
        self.config = config_name

    def table_create(self):
        SCC_Database.SQLTableMethod(self._con).table_create(self._table, DEFAULT_TABLE_RULE)
        return

    def table_del(self):
        SCC_Database.SQLTableMethod(self._con).table_drop(self._table)
        return

    def config_name_tup(self):
        config_name = SCC_Database.SQLColumnMethod(self._con, self._table).column_select(('config',))
        config_name_list = []
        for i in config_name:
            config_name_list.append(i[0])
        return tuple(config_name_list)

    def value_create(self, value: str, changeable=0, note=''):
        if changeable <= 0:
            changeable = 0
        else:
            changeable = 1
        if self.config not in self.config_name_tup():
            SCC_Database.SQLColumnMethod(self._con, self._table).column_insert((
                "config", "value", "changeable", "note"), (self.config, value, changeable, note))
        else:
            raise SCC_Exception.ConfigDBAddError
        return

    def value_del(self):
        if self.config not in self.config_name_tup():
            raise SCC_Exception.ConfigDBDropError
        else:
            SCC_Database.SQLColumnMethod(self._con, self._table, where_user=f"config IS ?").\
                column_delete(where_tup=(self.config, ))
        return

    def value_get(self):
        if self.config not in self.config_name_tup():
            return ''
        else:
            return SCC_Database.SQLColumnMethod(self._con, self._table, where_user=f"config IS ?") \
                .column_select(("config", "value", "changeable", "note"), fetch_number=1, where_tup=(self.config, ))[0]

    def value_updata(self, value: str, changeable=-1, note=''):
        config_list = ["value", "changeable", "note"]
        value_list = [value, changeable, note]
        if changeable == -1:
            config_list.remove("changeable")
            value_list.remove(changeable)
        if note == '':
            config_list.remove("note")
            value_list.remove(note)
        if self.config not in self.config_name_tup():
            raise SCC_Exception.ConfigDBDropError
        else:
            SCC_Database.SQLColumnMethod(self._con, self._table, where_user=f"config Is ?") \
                .column_update(tuple(config_list), tuple(value_list), where_tup=(self.config, ))
        return

    def db_close(self):
        SCC_Database.SQLDBUsefulMethod(self._con).con_safe_close()
        return


if __name__ == '__main__':
    DEFAULT_DB_ADDRESS = r'D:\Programs\Programs\Working\Special-Cool-Collection\test\\'
    test_1 = _ConfigDB("main.db", 'test1')
    test_1.config = 'one'
    test_1.value_updata(value='a is not b')
    test_1.db_close()
