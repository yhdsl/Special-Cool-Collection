"""
**模块说明** 软件的底层数据库模块，已提供基本的数据检验 \n
**模块状态** 测试中
"""

import os
import sqlite3
import SCC_Exception


class SQLDBGetStart:
    """
    返回指定数据库的connect对象或创建一个新的数据库 \n
    该类提供了一个安全获取con对象的方法，以下所有类中均需要提供该方法返回的con对象

    *类参数* \n
    **db_adress (str)** 指定的数据库地址
    **create_db=False (bool)** 设置为True以便于创建一个新的空数据库，**若原数据库存在将被删除**

    *类属性* \n
    **.con (sqlite3.connect)** 返回指定数据库的connect对象

    *类异常* \n
    **SCC_Exception.DBNotExistError** 数据库不存在
    """

    def __init__(self, db_adress: str, create_db=False):
        self.con = self._get_con(db_adress, create_db=create_db)

    @staticmethod
    def _get_con(db_adress: str, create_db=False):
        """
        获取数据库的con对象

        :param db_adress: 指定的数据库地址
        :param create_db: 设置为True以允许创建一个空的数据库
        :return: sqlite3.connect
        """
        if create_db:
            if os.path.exists(db_adress):
                os.remove(db_adress)
        else:
            if not os.path.exists(db_adress):
                raise SCC_Exception.DBNotExistError
        return sqlite3.connect(db_adress)


class SQLDBUsefulMethod:
    """
    实现con类部分常用的方法 \n
    **注意在做出改变后调用该类的con_safe_close方法**

    *类属性* \n
    **db_con (sqlite3.connect)** 数据库的con类

    *类方法* \n
    **con_safe_close** con安全退出，现在如果con未作出改变则不会调用commit \n
    **con_get_cur (sqlite3.cursor)** 获取cur类，更推荐直接使用con的cur方法
    """

    def __init__(self, db_con):
        self._con = db_con

    def con_safe_close(self):
        if self._con.in_transaction:
            self._con.commit()
        self._con.close()
        return

    def con_get_cur(self):
        return self._con.cursor()

    def _con_rollback(self):  # TODO(长期) 实现回滚操作
        """回滚操作，目前回滚无法实现"""
        self._con.rollback()
        return

    def db_backup(self):  # TODO(长期) 实现数据库备份功能
        """数据库备份"""
        pass


class SQLTableMethod:
    """
    实现表的新建和删除，以及提供表名元组

    *类属性* \n
    **db_con (sqlite3.connect)** 数据库的con类

    *类方法* \n
    **table_create(table_name: str, table_rules: str)** 创建指定规则的表 \n
    **table_drop(table_name: str)** 删除指定的表 \n
    **table_tup (tup)** 返回指定数据库中所有的表名元组
    """

    def __init__(self, db_con):
        self._con = db_con

    def _table_exist_check(self, table_name: str, table_list_return=False):
        """
        表名检查

        :param table_name: 表名
        :param table_list_return: 设置为True以允许返回表名列表
        :return: Bool或表名列表
        """
        cur = SQLDBUsefulMethod(self._con).con_get_cur()
        cur.execute("SELECT tbl_name FROM sqlite_master WHERE type = 'table'")
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
            raise SCC_Exception.TableCreateError
        else:  # 未处理table_rules造成的sqlite3.OperationalError异常
            self._con.execute(f"CREATE TABLE {table_name} ({table_rules})")
        return

    def table_drop(self, table_name: str):
        table_check = self._table_exist_check(table_name)
        if table_check:
            self._con.execute(f"DROP TABLE {table_name}")
        else:
            raise SCC_Exception.TableDropError
        return

    def table_tup(self):
        return tuple(self._table_exist_check(table_name='table_name', table_list_return=True))


class SQLColumnMethod:
    """
    实现数据列的增加，删除，修改，搜索

    *类属性* \n
    **db_con (sqlite3.connect)** 数据库的con类 \n
    **table_name (str)** 表名 \n
    **where_user='True' (str)** 不带where前缀的where语句，默认为所有内容

    *类方法* \n
    数据的修改以column_tup为主，value_tup中多余的数据将被忽略 \n
    **column_insert(column_tup: tuple, value_tup: tuple)** 增加数据 \n
    **column_delete** 删除数据 \n
    **column_update(column_tup: tuple, value_tup: tuple)** 更新数据 \n
    **column_select(column_tup: tuple, fetch_number=0) (list)** 返回指定数量的搜索结果，默认为全部

    *类异常* \n
    **SCC_Exception.ColunmError** 表名不存在
    **SCC_Exception.ColunmValuesLessError** 提供的数据过少
    """

    def __init__(self, db_con, table_name: str, where_user='True'):
        self._con = db_con
        self.table = table_name
        self.where = where_user
        self._table_check()

    def _table_check(self):
        """检查传入的表名是否存在"""
        table_tup = SQLTableMethod(self._con).table_tup()
        if self.table not in table_tup:
            raise SCC_Exception.ColunmError
        return

    def column_insert(self, column_tup: tuple, value_tup: tuple):
        if len(value_tup) < len(column_tup):
            raise SCC_Exception.ColunmValuesLessError
        column_add = ','.join(column_tup)
        value_add = '?,' * len(column_tup)
        self._con.execute(f"INSERT INTO {self.table} ({column_add}) VALUES ({value_add[:-1]})",
                          value_tup[:len(column_tup)])
        return

    def column_delete(self):
        self._con.execute(f"DELETE FROM {self.table} WHERE {self.where}")
        return

    def column_update(self, column_tup: tuple, value_tup: tuple):
        if len(value_tup) < len(column_tup):
            raise SCC_Exception.ColunmValuesLessError
        update_add = []
        for i in column_tup:
            update_add.append(f"{i} = ?")
        update_add = ','.join(update_add)
        self._con.execute(f"UPDATE {self.table} SET {update_add} WHERE {self.where}", value_tup[:len(column_tup)])
        return

    def column_select(self, column_tup: tuple, fetch_number=0):
        column_add = ','.join(column_tup)
        cur = SQLDBUsefulMethod(self._con).con_get_cur()
        cur.execute(f"SELECT {column_add} FROM {self.table} WHERE {self.where}")
        if fetch_number <= 0:
            return cur.fetchall()
        else:
            return cur.fetchmany(size=fetch_number)


class _SQLWhereMethod:  # TODO(中期) 确定WHERE语句的规则
    """
    目前该方法不完善，数据需要使用占位符传入
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
    test_address = r"D:\Programs\Programs\Working\Special-Cool-Collection\test\test.db"
    test_1 = SQLDBGetStart(test_address, create_db=False).con
    test_2 = SQLDBUsefulMethod(test_1)
    test_3 = SQLTableMethod(test_1)
    test_4 = SQLColumnMethod(test_1, 'test1')
    # test_4.column_insert(('name1', 'name2'), ('a', ))
    # test_4.column_delete()
    # test_4.column_update(('name1', 'name2'), ('2', ))
    print(test_4.column_select(('name1', 'name2'), 1))
    test_2.con_safe_close()
