"""
**模块说明** 软件的配置模块，目前提供两种配置管理 \n
**模块状态** 开发中
"""

import configparser
import SCC_Database
import SCC_Exception

DEFAULT_DB_ADDRESS = r'Configuration\\DataBase\\'


class ConfigDB:
    def __init__(self, db_name, module_name, config_name=''):
        self._con = SCC_Database.SQLDBGetStart(DEFAULT_DB_ADDRESS + db_name).con
        self._table = module_name
        self._config = config_name
        self._table_rule = 'config TEXT, value TEXT'

    def table_create(self):
        SCC_Database.SQLTableMethod(self._con).table_create(self._table, self._table_rule)
        return

    def table_drop(self):
        SCC_Database.SQLTableMethod(self._con).table_drop(self._table)
        return

    def _config_name_list(self):
        config_name = SCC_Database.SQLColumnMethod(self._con, self._table).column_select(('config', ))
        config_name_list = []
        for i in config_name:
            config_name_list.append(i[0])
        return config_name_list

    def value_add(self, value):
        if self._config not in self._config_name_list():
            SCC_Database.SQLColumnMethod(self._con, self._table).column_insert((self._config, ), (value, ))
        else:
            raise SCC_Exception.ConfigDBAddError
        return

    def value_drop(self):
        if self._config not in self._config_name_list():
            raise SCC_Exception.ConfigDBDropError
        else:
            SCC_Database.SQLColumnMethod(self._con, self._table, where_user=f"config={self._config}").column_delete()
        return

    def value_get(self):
        if self._config not in self._config_name_list():
            return ''
        else:
            return SCC_Database.SQLColumnMethod(self._con, self._table, where_user=f"config={self._config}")\
                .column_select(('value', ), fetch_number=1)[0]

    def value_updata(self, value):
        if self._config not in self._config_name_list():
            raise SCC_Exception.ConfigDBDropError
        else:
            SCC_Database.SQLColumnMethod(self._con, self._table, where_user=f"config={self._config}")\
                .column_update(('value', ), (value, ))
        return
