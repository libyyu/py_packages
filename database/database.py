# -*- coding: utf-8 -*-
import logging
from . import db

class DB(object):
    """docstring for DB"""
    def __init__(self, **params):
        super(DB, self).__init__()
        self._db_module = db.database(**params)
        self._dbname = params.pop('db')
        if isinstance(self._db_module, db.SqliteDB):
            self.db_type = "sqlite"

    def has_database(self, dbname):
        if isinstance(self._db_module, db.SqliteDB):
            return dbname == self._dbname
        try:
            result = self.query("SHOW DATABASES LIKE %s"% dbname)
            return result == 1
        except:
            return False

    def has_table(self, tbname):
        try:
            if isinstance(self._db_module, db.SqliteDB):
                out = self.query("select count(*)  from sqlite_master where type='table' and name='%s'" % tbname)
                first = out.first()
                return first['count(*)'] == 1
            else:
                out = self.query("SHOW TABLES LIKE %s" %tbname)
            if isinstance(out, int):
                return out > 0
            elif isinstance(out, db.iterbetter):
                first = out.first()
                return not not out
            else:
                return False
        except Exception as e:
            raise e
            return False
    def has_field(self, tabname, fieldname):
        try:
            if isinstance(self._db_module, db.SqliteDB):
                out = self.query("select * from sqlite_master where name='%s' and sql like '%s'" % (tabname, "%"+fieldname+"%"))
                first = out.first()
                return first is not None
            else:
                raise Exception("database not implemention")
        except Exception as e:
            raise e

    def query(self, sql, processed=False, _test=False, **vars):
        try:
            if vars is None: vars = {}
            return self._db_module.query(sql, vars=vars, processed=processed, _test=_test)
        except Exception as e:
            logging.error("Error query on '%s' for %s", self._dbname, str(db.reparam(sql, vars or {})))
            raise e

    def execute_sql(self, sql, **vars):
        try:
            cursor = self._db_module._db_cursor()
            if vars is None: vars = {}
            sql_query = db.reparam(sql, vars)
            result = self._db_module._db_execute(cursor, sql_query)
            return result
        except Exception as e:
            logging.error("Error execute on '%s' for %s",  self._dbname, str(db.reparam(sql, vars or {})))
            raise e

    def commit(self):
        self._db_module.ctx.commit()

    def __getattr__(self, key):
        try:
            return getattr(self._db_module, key)
        except:
            return None

    def __getitem__(self, key):
        try:
            return getattr(self._db_module, key)
        except:
            return None


def test_sqlite():
    api = DB(dbn='sqlite', db='fn2018', user='ldf', passwd='admin', host='localhost', charset='utf8', x='a')
    print (api['query'], api.query)

    print (api.has_database('fn2018'))
    print (api.has_table("tb_user"))
    sql = '''
                CREATE TABLE IF NOT EXISTS `tb_user`
                   (id INTEGER PRIMARY KEY NOT NULL,
                   name           TEXT    NOT NULL,
                   password       INT     NOT NULL);
                '''
    result = api.execute_sql(sql)
    print (result)
    api.commit()

    print (api.has_table("tb_user"))

    sql = "SELECT id FROM %s WHERE name='%s' AND password='%s' LIMIT 1;" % (
    'tb_user', 'admin', '21232f297a57a5a743894a0e4a801fc3')
    result = api.query(sql)
    print (result, result.first())
    if result.first() is None:
        from hashlib import md5
        name = "admin"
        pw = "admin"
        pwd = md5(pw).hexdigest()
        sql = 'INSERT INTO tb_user (name, password) VALUES($name, $pwd);'
        result = api.execute_sql(sql, name=name, pwd=pwd)
        print (result, result.rowcount)
        api.commit()
        sql = 'SELECT id FROM %s LIMIT 1;' % ('tb_user')
        result = api.query(sql)
        print (result, result.first())

def test_my():
    pass

def main():
    test_sqlite()
    test_my()

if __name__ == '__main__':
    main()
