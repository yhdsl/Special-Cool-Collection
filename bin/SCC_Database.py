"""
**模块说明** 软件的底层数据库模块，已提供基本的数据检验 \n
**模块状态** 开发中
"""

import os
import sqlite3
import SCC_Exception


class SQLDBGetStart:
    """
    返回指定数据库的connect对象或创建一个新的数据库

    *类参数* \n
    **db_adress (str)** 指定的数据库地址
    **create_db (bool -> False)** 设置为True以允许创建一个 新的空数据库

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
        数据库的con对象获取方法

        :param db_adress: 指定的数据库地址
        :param create_db: 设置为True以允许创建一个空的数据库
        :return: sqlite3.connect
        """
        if (not create_db) and (not os.path.exists(db_adress)):
            raise SCC_Exception.DBNotExistError
        return sqlite3.connect(db_adress)


class SQLDBUsefulMethod:
    """
    提供con常用的部分方法

    *类属性* \n
    **db_con** 数据库的con类

    *类方法* \n
    **con_safe_close** con安全退出 \n
    **con_exit_check** con提交检查 \n
    **con_get_cur** 获取cur类
    """

    def __init__(self, db_con):
        self._con = db_con

    def con_safe_close(self):
        self._con.commit()
        self._con.close()
        return

    def con_exit_check(self):
        if self._con.in_transaction:
            self._con.commit()
        return

    def con_get_cur(self):
        return self._con.cursor()

    def con_back(self):
        """回滚操作"""
        pass

    def db_backup(self):
        """数据库备份"""
        pass


class SQLTableMethod:
    """
    提供表的新建和删除方法，以及提供所有表名的列表

    *类属性* \n
    **db_con** 数据库的con类

    *类方法* \n
    **table_create(table_name: str, table_rules: str)** 创建指定规则的表 \n
    **table_drop(table_name: str)** 删除指定的表 \n
    **table_list** 返回数据库所有的表名
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
        table_list = cur.fetchall()
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
        else:
            self._con.execute(f"CREATE TABLE {table_name} ({table_rules})")
        return

    def table_drop(self, table_name: str):
        table_check = self._table_exist_check(table_name)
        if table_check:
            self._con.execute(f"DROP TABLE {table_name}")
        else:
            raise SCC_Exception.TableDropError
        return

    def table_list(self):
        table_list_tup = self._table_exist_check(table_name='table_name', table_list_return=True)
        table_list = []
        for i in table_list_tup:
            table_list.append(i[0])
        return table_list


class SQLColumnMethod:
    def __init__(self, db_con, table_name, where_user='True'):
        self._con = db_con
        self.table = table_name
        self.where = where_user
        self._table_check()

    def _table_check(self):
        table_list = SQLTableMethod(self._con).table_list()
        if self.table not in table_list:
            raise SCC_Exception.ColunmError
        return

    def column_insert(self, column_tup: tuple, value_tup: tuple):
        column_add = ','.join(column_tup)
        value_add = ','.join(value_tup[: len(column_tup) + 1])
        self._con.execute(f"INSERT INTO {self.table} ({column_add}) VALUES ({value_add})")
        return

    def column_delete(self):
        self._con.execute(f"DELETE FROM {self.table} WHERE {self.where}")
        return

    def column_update(self, column_tup: tuple, value_tup: tuple):
        update_add = []
        for i in column_tup:
            update_add.append(f"{i} = {value_tup[column_tup.index(i)]}")
        update_add = ','.join(update_add)
        self._con.execute(f"UPDATE {self.table} SET {update_add} WHERE {self.where}")
        return

    def column_select(self, column_tup: tuple, fetch_number=0):
        column_add = ','.join(column_tup)
        cur = SQLDBUsefulMethod(self._con).con_get_cur()
        cur.execute(f"SELECT {column_add} FROM {self.table} WHERE {self.where}")
        if not fetch_number:
            return cur.fetchall()
        else:
            return cur.fetchmany(size=fetch_number)


class SQLWhereMethod:
    """
    目前该方法不完善
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
    test_address = r"D:\Programs\Programs\Working\Special-Cool-Collection\test\Juzi_database.db"
    test_1 = SQLDBGetStart(test_address).con
    test_2 = SQLColumnMethod(test_1, 'Juzidata_old', where_user='True')
    test_2.column_delete()
    SQLDBUsefulMethod(test_1).con_safe_close()
