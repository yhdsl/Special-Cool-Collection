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
                     "note TEXT DEFAULT ''," \
                     "type TEXT DEFAULT 'str'"
# 配置允许的类型
DEFAULE_TYPE_TUP = ('str', 'int', 'float', 'bool')
# 视为TRUE的配置，大小写不敏感
DEFAULT_BOOL_TRUE = ('1', 'yes', 'true', 'on')
# 视为FALSE的配置，大小写不敏感
DEFAULT_BOOL_FALSE = ('0', 'no', 'false', 'off')

# 默认INI文件存储地址
DEFAULT_INI_ADDRESS = r'Configuration\\'


class _ConfigDB:
    """
    配置模块中关于DB数据库的操作方法

    *类参数* \n
    **db_name (str)** db数据库名称 \n
    **module_name='' (str)** 调用该类的模块名称，这将作为表名传入 \n
    **config_name='' (str)** 需要操作的配置名称，可通过类属性实现变化 \n
    **create_db=False (bool)** 设置为True以便于创建一个新的空数据库，**若原数据库存在将被删除**

    *类属性* \n
    **module (str)** 重写该属性以便于对不同的表进行操作 \n
    **config (str)** 重写该属性以便于对不同的配置进行操作

    *类方法* \n
    **table_create** 创建以模块命名的表\n
    **table_del** 删除以模块命名的表\n
    **table_name_tup** 返回所有模块元组 \n
    **config_name_tup (tup)** 返回该模块的所有配置名称\n
    **value_create(value: str, changeable=0, note='', db_type='')** 添加配置\n
    **value_del()** 删除配置\n
    **value_get()** 获取配置\n
    **value_updata(value='', changeable=-1, note='', db_type='')** 更新配置\n
    **db_close()** 提交所有的修改\n
    """

    def __init__(self, db_name: str, module_name='', config_name='', create_db=False):
        self._con = SCC_Database.SQLDBGetStart(DEFAULT_DB_ADDRESS + db_name, create_db=create_db).con
        self.module = module_name
        self.config = config_name

    def table_create(self):
        SCC_Database.SQLTableMethod(self._con).table_create(self.module, DEFAULT_TABLE_RULE)
        return

    def table_del(self):
        SCC_Database.SQLTableMethod(self._con).table_drop(self.module)
        return

    def table_name_tup(self):
        return SCC_Database.SQLTableMethod(self._con).table_tup()

    def config_name_tup(self):
        config_name = SCC_Database.SQLColumnMethod(self._con, self.module).column_select(('config',))
        config_name_list = []
        for i in config_name:
            config_name_list.append(i[0])
        return tuple(config_name_list)

    def changeable_name_tup(self):
        changeable_name = SCC_Database.SQLColumnMethod(self._con, self.module, where_user="changeable = ?"). \
            column_select(column_tup=("config",), where_tup=(1,))
        if not changeable_name:
            changeable_name_tup = ()
        else:
            changeable_name_list = []
            for i in changeable_name:
                changeable_name_list.append(i[0])
            changeable_name_tup = tuple(changeable_name_list)
        return changeable_name_tup

    def value_create(self, value: str, changeable=0, note='', db_type='str'):
        if changeable <= 0:
            changeable = 0
        else:
            changeable = 1
        if db_type not in DEFAULE_TYPE_TUP:
            db_type = 'str'
        if self.config not in self.config_name_tup():
            SCC_Database.SQLColumnMethod(self._con, self.module).column_insert((
                "config", "value", "changeable", "note", "type"), (self.config, value, changeable, note, db_type))
        else:
            raise SCC_Exception.ConfigDBAddError
        return

    def value_del(self):
        if self.config not in self.config_name_tup():
            raise SCC_Exception.ConfigDBDropError
        else:
            SCC_Database.SQLColumnMethod(self._con, self.module, where_user="config IS ?"). \
                column_delete(where_tup=(self.config,))
        return

    def value_get(self):
        if self.config not in self.config_name_tup():
            raise SCC_Exception.ConfigDBGetError
        else:
            value_get = SCC_Database.SQLColumnMethod(self._con, self.module, where_user="config IS ?"). \
                column_select(("config", "value", "changeable", "note", "type"), fetch_number=1,
                              where_tup=(self.config,))[0]
            value_get = list(value_get)
            value_get_str = value_get[1]
            if value_get[4] == DEFAULE_TYPE_TUP[0]:
                value_return = value_get_str
            elif value_get[4] == DEFAULE_TYPE_TUP[1]:
                value_return = int(value_get_str)
            elif value_get[4] == DEFAULE_TYPE_TUP[2]:
                value_return = float(value_get_str)
            elif value_get[4] == DEFAULE_TYPE_TUP[3]:
                if value_get[1].casefold() in DEFAULT_BOOL_TRUE:
                    value_return = True
                elif value_get[1].casefold() in DEFAULT_BOOL_FALSE:
                    value_return = False
                else:
                    raise SCC_Exception.ConfigDBBoolError
            else:
                value_return = value_get_str
            value_get[1] = value_return
        return tuple(value_get)

    def value_updata(self, value='', changeable=-1, note='', db_type=''):
        config_list = ["value", "changeable", "note", "type"]
        value_list = [value, changeable, note, db_type]
        if value == '':
            config_list.remove("value")
            value_list.remove(value)
        if changeable == -1:
            config_list.remove("changeable")
            value_list.remove(changeable)
        if note == '':
            config_list.remove("note")
            value_list.remove(note)
        if db_type == '':
            config_list.remove("type")
            value_list.remove(db_type)
        if len(config_list) == 0:
            return
        if self.config not in self.config_name_tup():
            raise SCC_Exception.ConfigDBDropError
        else:
            SCC_Database.SQLColumnMethod(self._con, self.module, where_user="config Is ?") \
                .column_update(tuple(config_list), tuple(value_list), where_tup=(self.config,))
        return

    def db_close(self):
        SCC_Database.SQLDBUsefulMethod(self._con).con_safe_close()
        return


class _ConfigINI:
    """
    配置模块中的ini文件管理部分，不包括ini注释管理部分

    *类参数* \n
    **module_name='' (str)** 调用模块名称， 这将作为节名，等效于表名 \n
    **config_name='' (str)** 配置名称

    *类属性* \n
    **module (str)** 同上 \n
    **config (str)** 同上

    *类方法* \n
    **configparser_read_file(ini_name: str)** 从指定名称文件中读取原有配置 \n
    **sections_name_tup (tup)** 返回所有节名元组 \n
    **config_name_tup (tup)** 返回指定节名的所有键值， 注意：其中也包括所有的注释 \n
    **sections_create** 创建节 \n
    **sections_del** 删除节 \n
    **config_create(value: str)** 创建包含指定数值的键 \n
    **config_updata(value: str)** 更新包含指定数值的键， 此方法与**config_create**等效 \n
    **config_del** 删除键 \n
    **config_get (str)** 返回键的数值 \n
    **config_getint (int)** 返回键转发为整数的数值 \n
    **config_getfloat (float)** 返回键转发为浮点数的数值 \n
    **config_getbool (bool)** 返回键转发为布尔指的数值 \n
    **ini_write(ini_name: str)** 将所有的更改写入指定文件，注意：此方法为覆写式写入
    """
    def __init__(self, module_name='', config_name=''):
        self._configparser = self._configparser_get()
        self.module = module_name
        self.config = config_name

    @staticmethod
    def _configparser_get():
        """
        :return: 返回经过处理的ConfigParser类，其值不可以包含多行，并且键值大小写敏感
        """
        configparser_get = configparser.ConfigParser(empty_lines_in_values=False)
        configparser_get.optionxform = lambda option: option
        return configparser_get

    def configparser_read_file(self, ini_name: str):
        self._configparser.read_file(open(DEFAULT_INI_ADDRESS + ini_name, encoding='utf8'))
        return

    def sections_name_tup(self):
        return tuple(self._configparser.sections())

    def config_name_tup(self):
        return tuple(self._configparser.options(self.module))

    def sections_create(self):
        self._configparser.add_section(self.module)
        return

    def sections_del(self):
        self._configparser.remove_section(self.module)
        return

    def config_create(self, value: str):
        self._configparser.set(self.module, self.config, value)
        return

    def config_updata(self, value: str):
        self.config_create(value)
        return

    def config_del(self):
        self._configparser.remove_option(self.module, self.config)
        return

    def config_get(self):
        return self._configparser.get(self.module, self.config)

    def config_getint(self):
        return self._configparser.getint(self.module, self.config)

    def config_getfloat(self):
        return self._configparser.getfloat(self.module, self.config)

    def config_getbool(self):
        return self._configparser.getboolean(self.module, self.config)

    def ini_write(self, ini_name: str):
        self._configparser.write(open(DEFAULT_INI_ADDRESS + ini_name, mode='w+', encoding='utf8'))
        return


if __name__ == '__main__':
    DEFAULT_INI_ADDRESS = r'D:\Programs\Programs\Working\Special-Cool-Collection\test\\'
    test_2 = _ConfigINI(module_name='Test1', config_name='one')
    test_2.configparser_read_file('test.ini')
    test_2.module = 'Jtest'
    test_2.config = 'one'
    test_3 = test_2.config_get()
    print(test_3)
    test_2.ini_write('test.ini')
