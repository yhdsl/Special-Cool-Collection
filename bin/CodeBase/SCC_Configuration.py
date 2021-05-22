"""
**模块说明** \n
软件的配置模块，目前提供两种配置管理 \n
**模块状态** \n
开发中
"""

import configparser
import re
import os
from . import SCC_Database
from . import SCC_Exception
from . import SCC_Logs

# 配置文件夹地址，未在初始化进程中进行检查
_CONFIG_ADDRESS = os.path.dirname(str(__file__).rsplit('\\', maxsplit=1)[0]) + r"\Config"
# 默认DB表格式
# config为配置名称，不可为空不可重复
# value为配置内容，不可为空
# changeable为该配置是否可由INI文件覆盖，默认为0
# comment为该配置的说明内容
# type为配置内容的格式，默认为str
_DEFAULT_TABLE_RULE = "config TEXT NOT NULL UNIQUE," \
                      "value TEXT NOT NULL," \
                      "changeable INTEGER DEFAULT 0," \
                      "comment TEXT DEFAULT ''," \
                      "type TEXT DEFAULT 'str'"
# 配置允许的类型
_DEFAULE_TYPE_TUP = ('str', 'int', 'float', 'bool')
# 视为TRUE的配置，大小写不敏感
_DEFAULT_BOOL_TRUE = ('1', 'yes', 'true', 'on')
# 视为FALSE的配置，大小写不敏感
_DEFAULT_BOOL_FALSE = ('0', 'no', 'false', 'off')
# 日志记录器，负责写入具体的触发参数和异常帧
_logger = SCC_Logs.Logs(__name__).logger


class _ConfigDB:
    """
    配置模块中关于DB数据库的操作方法 \n
    一般来说配置模块仅使用该类的读取功能，其他功能仅在生成DB数据库时调用

    *类参数* \n
    **db_name: str** DB数据库的名称 \n
    **module_name='': str** 调用该类的模块名称，这将作为表名传入 \n
    **config_name='': str** 需要操作的配置名称，可通过类属性实现变化 \n
    **create_db=False: bool** 设置为True以便于创建一个新的空数据库，**若原数据库存在将被删除**

    *类属性* \n
    **module -> str** 重写该属性以便于对不同的表进行操作 \n
    **config -> str** 重写该属性以便于对不同的配置进行操作

    *类方法* \n
    **table_create()** 创建以模块命名的表 \n
    **table_del()** 删除以模块命名的表 \n
    **table_name_tup() -> tup** 返回包含该数据库的所有表名的元组 \n
    **config_name_tup() -> tup** 返回包含该模块的所有配置名称的元组 \n
    **changeable_name_tup() -> tup** 返回包含该模块的所有允许更改配置名称的元组 \n
    **value_create(value: str, changeable=0, comment='', db_type='')** 添加配置 \n
    **value_del()** 删除配置 \n
    **value_get() -> tuple** 获取配置 \n
    **value_updata(value='', changeable=-1, comment='', db_type='')** 更新配置 \n
    **db_close()** 提交所有的修改
    """

    def __init__(self, db_name: str, module_name='', config_name='', create_db=False):
        self._con = SCC_Database.SQLGetStart(_CONFIG_ADDRESS + rf'\{db_name}.db', create_db=create_db).con
        self.module = module_name
        self.config = config_name

    def table_create(self):
        SCC_Database.SQLTableMethod(self._con).table_create(self.module, _DEFAULT_TABLE_RULE)
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

    def value_create(self, value: str, changeable=0, comment='', db_type='str'):
        if changeable <= 0:
            changeable = 0
        else:
            changeable = 1
        if db_type not in _DEFAULE_TYPE_TUP:
            db_type = 'str'
        if self.config not in self.config_name_tup():
            SCC_Database.SQLColumnMethod(self._con, self.module).column_insert((
                "config", "value", "changeable", "comment", "type"),
                (self.config, value, changeable, comment, db_type))
        else:
            _logger.error(f'config={self.config} config_name_tup={self.config_name_tup()}', stack_info=True)
            raise SCC_Exception.ConfigDBAddError
        return

    def value_del(self):
        if self.config not in self.config_name_tup():
            _logger.error(f'config={self.config} config_name_tup={self.config_name_tup()}', stack_info=True)
            raise SCC_Exception.ConfigDBDropError
        else:
            SCC_Database.SQLColumnMethod(self._con, self.module, where_user="config IS ?"). \
                column_delete(where_tup=(self.config,))
        return

    def value_get(self):
        if self.config not in self.config_name_tup():
            _logger.error(f'config={self.config} config_name_tup={self.config_name_tup()}', stack_info=True)
            raise SCC_Exception.ConfigDBGetError
        else:
            value_get = SCC_Database.SQLColumnMethod(self._con, self.module, where_user="config IS ?"). \
                column_select(("config", "value", "changeable", "comment", "type"), fetch_number=1,
                              where_tup=(self.config,))[0]
            value_get: list = list(value_get)
            value_get_str = value_get[1]
            if value_get[4] == _DEFAULE_TYPE_TUP[0]:
                value_return = value_get_str
            elif value_get[4] == _DEFAULE_TYPE_TUP[1]:
                value_return = int(value_get_str)
            elif value_get[4] == _DEFAULE_TYPE_TUP[2]:
                value_return = float(value_get_str)
            elif value_get[4] == _DEFAULE_TYPE_TUP[3]:
                if value_get[1].casefold() in _DEFAULT_BOOL_TRUE:
                    value_return = True
                elif value_get[1].casefold() in _DEFAULT_BOOL_FALSE:
                    value_return = False
                else:
                    _logger.error(f'value_get={value_get}', stack_info=True)
                    raise SCC_Exception.ConfigDBBoolError
            else:
                value_return = value_get_str
            value_get[1] = value_return
        return tuple(value_get)

    def value_updata(self, value='', changeable=-1, comment='', db_type=''):
        config_list = ["value", "changeable", "comment", "type"]
        value_list = [value, changeable, comment, db_type]
        if value == '':
            config_list.remove("value")
            value_list.remove(value)
        if changeable == -1:
            config_list.remove("changeable")
            value_list.remove(changeable)
        if comment == '':
            config_list.remove("comment")
            value_list.remove(comment)
        if db_type == '':
            config_list.remove("type")
            value_list.remove(db_type)
        if len(config_list) == 0:
            return
        if self.config not in self.config_name_tup():
            _logger.error(f'config={self.config} config_name_tup={self.config_name_tup()}', stack_info=True)
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
    配置模块中的ini文件管理部分，不包括ini注释部分 \n
    配置模块的主要部分

    *类参数* \n
    **module_name='': str** 调用模块名称，这将作为节名传入 \n
    **config_name='': str** 配置名称

    *类属性* \n
    **module -> str** 同上 \n
    **config -> str** 同上

    *类方法* \n
    **configparser_read_file(ini_name: str)** 从指定名称文件中读取原有配置到私有变量中 \n
    **sections_name_tup() -> tup** 返回包含所有节名的元组 \n
    **config_name_tup() -> tup** 返回包含指定节名的所有键值的元组，注意：其中也包括所有的注释 \n
    **sections_create()** 创建节 \n
    **sections_del()** 删除节 \n
    **config_create(value: str)** 创建包含指定数值的键 \n
    **config_updata(value: str)** 更新包含指定数值的键，注意此方法与**config_create()**等效 \n
    **config_del()** 删除键 \n
    **config_get() -> str** 返回键的值 \n
    **config_getint() -> int** 返回键的值转化为整数的数值 \n
    **config_getfloat() -> float** 返回键的值转化为浮点数的数值 \n
    **config_getbool() -> bool** 返回键的值转化为布尔值的数值 \n
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
        """注意这里的ini_name包含了包的结构"""
        self._configparser.read_file(open(_CONFIG_ADDRESS + rf'\{ini_name}.ini', encoding='utf8'))
        return

    def sections_name_tup(self):
        return tuple(self._configparser.sections())

    def config_name_tup(self):
        return tuple(self._configparser.options(self.module))

    def sections_create(self):
        self._configparser.add_section(self.module)
        _logger.debug(f'已创建指定的节{self.module}')
        return

    def sections_del(self):
        self._configparser.remove_section(self.module)
        _logger.debug(f'已删除指定的节{self.module}')
        return

    def config_create(self, value: str):
        self._configparser.set(self.module, self.config, value)
        _logger.debug(f'已在{self.module}创建指定的配置{self.config}，值为{value}')
        return

    def config_updata(self, value: str):
        self.config_create(value)
        return

    def config_del(self):
        self._configparser.remove_option(self.module, self.config)
        _logger.debug(f'已在{self.module}删除指定的配置{self.config}')
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
        """注意这里的ini_name包含了包的结构"""
        self._configparser.write(open(_CONFIG_ADDRESS + rf'\{ini_name}.ini', mode='w+', encoding='utf8'))
        _logger.debug(f'已向{_CONFIG_ADDRESS}{ini_name}.ini中写入配置')
        return


class _ConfigINIComment:
    """
    *类参数* \n
    **ini_name: str** ini文件名称

    *类属性* \n
    **comment_tag -> tup** 注释标识

    *类方法* \n
    **comment_title_updata(comment: str)** 在INI文件的开头加上指定的注释内容 \n
    **comment_sections_updata(module_name: str, config_name: str, comment: str)** 在指定的节的键前添加注释 \n
    **file_write()** 将修改后的结果覆写入指定文件
    """

    def __init__(self, ini_name: str):
        self._ini_name = ini_name
        self.comment_tag = ('; ', '# ')
        self._file = self._ini_read()

    def _ini_read(self):
        """
        :return: 指定文件的内容列表
        """
        return open(_CONFIG_ADDRESS + rf'\{self._ini_name}.ini', encoding='utf8').readlines()

    def _file_updata(self, file: list):
        """
        将私有属性_file的内容更新为传入的file
        """
        self._file = file
        return

    def comment_title_updata(self, comment: str):
        first_sections = 0
        for file in self._file:
            if re.search(r'\[.+]', file):
                first_sections = self._file.index(file)
                break
        self._file_updata([comment] + self._file[first_sections:])
        return

    def _file_index_get(self, module_sign: int, config_name: str):
        """
        返回指定config在文件列表中的索引值

        :param module_sign: module索引值
        :param config_name: 配置名称
        :return: config在文件列表中的索引值
        """
        config_sign = 0
        for n in self._file[module_sign:]:
            if re.fullmatch(rf'{config_name} = .+\n', n):
                config_sign = self._file.index(n)
                break
        return config_sign

    def comment_sections_updata(self, module_name: str, config_name: str, comment: str):
        config_obj = _ConfigINI(module_name=module_name)
        config_obj.configparser_read_file(self._ini_name)
        config_tup = config_obj.config_name_tup()
        module_sign = self._file.index(f'[{module_name}]\n')
        if config_tup[0] == config_name:
            start_sign = module_sign
        else:
            start_sign = self._file_index_get(module_sign, config_tup[config_tup.index(config_name) - 1])
        end_sign = self._file_index_get(module_sign, config_name)
        self._file_updata(self._file[:start_sign + 1] + [comment] + self._file[end_sign:])
        return

    def file_write(self):
        open(_CONFIG_ADDRESS + rf'\{self._ini_name}.ini', mode='w', encoding='utf8').write(''.join(self._file))
        return


class Config:
    def __init__(self, package_name: str, file_name='Main', value_default='NULL'):
        self._file_address = rf'{package_name}\{file_name}'
        self.value_default = value_default
        self.module = ''
        self.config = ''
        self.value = ''
        self.title_comment = ''

    def file_updata(self):
        ini_true_address = rf'{_CONFIG_ADDRESS}\{self._file_address}.ini'
        if os.path.exists(ini_true_address):
            os.remove(ini_true_address)
            _logger.warning(f'位于{ini_true_address}的INI文件已存在，已删除原INI文件')
        open(ini_true_address, mode='x', encoding='utf8').close()
        if os.path.exists(rf'{_CONFIG_ADDRESS}\{self._file_address}.db'):
            db_open = _ConfigDB(db_name=self._file_address, module_name=self.module, config_name=self.config)
            ini_open = _ConfigINI()
            db_module_tup = db_open.table_name_tup()
            ini_comment_list = [self.title_comment]
            for db_module in db_module_tup:
                db_open.module = db_module
                ini_open.module = db_module
                ini_open.sections_create()
                db_config_changeable_tup = db_open.changeable_name_tup()
                for db_config in db_config_changeable_tup:
                    db_open.config = db_config
                    db_value = db_open.value_get()
                    ini_open.config_create(db_value[1])
                    ini_comment_list.append((db_module, db_config, db_value[3]))
            ini_open.ini_write(self._file_address)
            ini_comment_open = _ConfigINIComment(self._file_address)
            ini_comment_open.comment_title_updata(self.title_comment)
            for comment_tup in ini_comment_list[1:]:
                ini_comment_open.comment_sections_updata(comment_tup[0], comment_tup[1], comment_tup[2])
            ini_comment_open.file_write()
        return


if __name__ == '__main__':
    pass
