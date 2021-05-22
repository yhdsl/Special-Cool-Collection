"""
**模块说明** \n
软件的底层数据库模块，已提供基本的数据检验 \n
**模块状态** \n
已完成
"""

import os
import sqlite3
from . import SCC_Exception
from . import SCC_Logs

# 日志记录器，负责写入具体的触发参数和异常帧
_logger = SCC_Logs.Logs(__name__).logger


class SQLGetStart:
    """
    返回指定数据库的connect对象或创建一个新的数据库 \n
    该类提供了一个安全获取connect对象的方法，以下所有类中均需要提供该方法返回的connect对象 \n
    下文connect对象简称con类

    *类参数* \n
    **db_adress: str** 指定的数据库地址
    **create_db=False: bool** 设置为True以便于创建一个新的空数据库，**若原数据库存在则将被删除**

    *类属性* \n
    **con -> sqlite3.Connect** 返回指定数据库的connect对象
    """

    def __init__(self, db_adress: str, create_db=False):
        self.con = self._get_con(db_adress, create_db=create_db)

    @staticmethod
    def _get_con(db_adress: str, create_db=False):
        """
        获取数据库的con对象

        :param db_adress: 指定的数据库地址
        :param create_db: 设置为True以允许创建一个空的数据库
        :return: sqlite3.Connect
        """
        if create_db:
            if os.path.exists(db_adress):
                try:
                    os.remove(db_adress)
                except PermissionError:
                    _logger.warning(f'数据库"{db_adress}"被另一个程序占用，已储存至临时数据库内')
                    db_adress = db_adress.rsplit('.', maxsplit=1)[0] + '_temp.db'
                else:
                    _logger.info(f'旧数据库"{db_adress}"已被删除')
        else:
            if not os.path.exists(db_adress):
                _logger.error(f'db_adress={db_adress}', stack_info=True)
                raise SCC_Exception.DBNotExistError
        _logger.debug(f'已与位于"{db_adress}"的数据库建立连接')
        return sqlite3.connect(db_adress)


class SQLDBUsefulMethod:
    """
    实现con类部分常用的方法 \n
    **注意在其他类做出改变后调用该类的con_safe_close方法，以防更改丢失**

    *类参数* \n
    **db_con: sqlite3.Connect** 数据库的con类

    *类方法* \n
    **con_safe_close()** con类的安全退出方法，现在如果con类未作出改变则不会提交 \n
    **con_get_cur() (sqlite3.cursor)** 获取cur类，更推荐直接使用con类的cursor方法
    """

    def __init__(self, db_con: sqlite3.Connection):
        self._con = db_con

    def con_safe_close(self):
        if self._con.in_transaction:
            _logger.info('数据库已提交')
            self._con.commit()
        _logger.debug('数据库已关闭')
        self._con.close()
        return

    def con_get_cur(self):
        return self._con.cursor()

    def _con_rollback(self):  # TODO(长期) 实现回滚操作
        """回滚操作"""
        self._con.rollback()
        return

    def _db_backup(self):  # TODO(长期) 实现数据库转移功能
        """数据库转移"""
        pass


class SQLTableMethod:
    """
    实现表(TABLE)的新建和删除，以及提供表名元组等常用功能

    *类参数* \n
    **db_con: sqlite3.Connect** 数据库的con类

    *类方法* \n
    **table_create(table_name: str, table_rules: str)** 创建指定名称和规则的表 \n
    **table_drop(table_name: str)** 删除指定名称的表 \n
    **table_tup() -> tup** 返回指定数据库中包含所有的表名的元组
    """

    def __init__(self, db_con: sqlite3.Connection):
        self._con = db_con

    def _table_exist_check(self, table_name: str, table_list_return=False):
        """
        检查表名是否存在，或返回表名列表

        :param table_name: 表名
        :param table_list_return: 设置为True以允许返回表名列表
        :return: bool或表名列表
        """
        cur = self._con.cursor()
        cur.execute("SELECT tbl_name FROM sqlite_master WHERE type = ?", ('table', ))
        table_list_unclear = cur.fetchall()
        table_list = []
        for i in table_list_unclear:
            table_list.append(i[0])
        if table_list_return:
            return table_list
        else:
            if table_name in table_list:
                return True
            else:
                return False

    def table_create(self, table_name: str, table_rules: str):
        table_check = self._table_exist_check(table_name)
        if table_check:
            _logger.error(f'table_name={table_name}', stack_info=True)
            raise SCC_Exception.TableCreateError
        else:  # 无法处理table_rules造成的sqlite3.OperationalError异常
            self._con.execute(f"CREATE TABLE {table_name} ({table_rules})")
            _logger.debug(f'已创建新表{table_name}，规则为{table_rules}')
        return

    def table_drop(self, table_name: str):
        table_check = self._table_exist_check(table_name)
        if table_check:
            self._con.execute(f"DROP TABLE {table_name}")
            _logger.debug(f'已删除表{table_name}')
        else:
            _logger.error(f'table_name={table_name}', stack_info=True)
            raise SCC_Exception.TableDropError
        return

    def table_tup(self):
        return tuple(self._table_exist_check(table_name='table_name', table_list_return=True))


class SQLColumnMethod:
    """
    实现数据列的增加，删除，修改，搜索

    *类参数* \n
    **db_con: sqlite3.Connect** 数据库的con类 \n
    **table_name: str** 表名 \n
    **where_user='True': str** 不带where前缀的where语句，默认为所有内容

    *类方法* \n
    数据的修改以column_tup为主，value_tup中多余的数据将被忽略 \n
    下文中where_tup为WHERE语句中占位符的传入数据元组
    **column_insert(column_tup: tuple, value_tup: tuple)** 增加数据 \n
    **column_delete(where_tup=None)** 删除数据 \n
    **column_update(column_tup: tuple, value_tup: tuple, where_tup=None)** 更新数据 \n
    **column_select(column_tup: tuple, fetch_number=0, where_tup=None) -> list** 返回指定数量的搜索结果，默认为全部
    """

    def __init__(self, db_con: sqlite3.Connection, table_name: str, where_user='True'):
        self._con = db_con
        self.table = table_name
        self.where = where_user
        self._table_check()

    def _table_check(self):
        """检查传入的表名是否存在"""
        table_tup = SQLTableMethod(self._con).table_tup()
        if self.table not in table_tup:
            _logger.error(f'table_name={self.table}', stack_info=True)
            raise SCC_Exception.ColunmError
        return

    def column_insert(self, column_tup: tuple, value_tup: tuple):
        if len(value_tup) < len(column_tup):
            _logger.error(f'column_tup={column_tup} value_tup={value_tup}', stack_info=True)
            raise SCC_Exception.ColunmValuesLessError
        column_add = ','.join(column_tup)
        value_add = '?,' * len(column_tup)
        self._con.execute(f"INSERT INTO {self.table} ({column_add}) VALUES ({value_add[:-1]})",
                          value_tup[:len(column_tup)])
        _logger.debug(f'已在表{self.table}中插入{column_tup}，值为{value_tup[:len(column_tup)]}')
        return

    def column_delete(self, where_tup=None):
        if not where_tup:
            where_tup = ()
        self._con.execute(f"DELETE FROM {self.table} WHERE {self.where}", where_tup)
        _logger.debug(f'已删除表{self.table}中的数据，过滤规则为{self.where}，补充内容为{where_tup}')
        return

    def column_update(self, column_tup: tuple, value_tup: tuple, where_tup=None):
        if not where_tup:
            where_tup = ()
        if len(value_tup) < len(column_tup):
            _logger.error(f'column_tup={column_tup} value_tup={value_tup}', stack_info=True)
            raise SCC_Exception.ColunmValuesLessError
        update_add = []
        for i in column_tup:
            update_add.append(f"{i} = ?")
        update_add = ','.join(update_add)
        self._con.execute(f"UPDATE {self.table} SET {update_add} WHERE {self.where}",
                          value_tup[:len(column_tup)] + where_tup)
        _logger.debug(f'已在{self.table}中将{column_tup}的数值更新为{value_tup[:len(column_tup)]}，'
                      f'过滤规则为{self.where}，补充内容为为{where_tup}')
        return

    def column_select(self, column_tup: tuple, fetch_number=0, where_tup=None):
        if not where_tup:
            where_tup = ()
        column_add = ','.join(column_tup)
        cur = SQLDBUsefulMethod(self._con).con_get_cur()
        cur.execute(f"SELECT {column_add} FROM {self.table} WHERE {self.where}", where_tup)
        if fetch_number <= 0:
            _logger.debug(f'搜索结果为{cur.fetchall()}')
            return cur.fetchall()
        else:
            _logger.debug(f'搜索结果为{cur.fetchmany(size=fetch_number)}')
            return cur.fetchmany(size=fetch_number)


class __SQLWhereMethod:
    """
    该类已被废弃，where语句由其他模块按需自行生成
    """

    def __init__(self, where_auto=False, where_user=''):
        self.where_return = self._where_get(where_auto=where_auto, where_user=where_user)

    @staticmethod
    def _where_create_one(where_id: int, where_tup: tuple, add_not=False):
        """
        构建单个where语句

        :param where_id: 指定的where语句类型
        :param where_tup: where语句可用参数
        :param add_not: 是否加入NOT
        :return: 不带where的完整语句部分
        """
        if where_id == 0:
            return f"BETWEEN {where_tup[0]} AND {where_tup[1]}"
        elif where_id == 1:
            if add_not:
                return f"{where_tup[0]} NOT IN {where_tup[1]}"
            else:
                return f"{where_tup[0]} IN {where_tup[1]}"
        elif where_id == 2:
            if add_not:
                return f"{where_tup[0]} NOT IS {where_tup[1]}"
            else:
                return f"{where_tup[0]} IS {where_tup[1]}"
        elif where_id == 3:
            return f"LIKE {where_tup[0]}"
        elif where_id == 4:
            return f"GLOB {where_tup[0]}"
        else:
            return " "

    @staticmethod
    def _where_create_all(where_one: tuple, where_and_or: tuple):
        where_fin = ''
        for i in where_one:
            if where_and_or[i]:
                i += ' and '
            else:
                i += ' or '
            where_fin += i
        return where_fin[:-1]

    @staticmethod
    def _where_get(where_auto, where_user):
        where_return = ''
        if not where_auto:
            where_return = where_user
        return where_return


if __name__ == '__main__':
    pass
