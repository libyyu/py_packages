# -*- coding: utf-8 -*-
import logging
import db
import sys, os

try:
    this_path = os.path.dirname(os.path.abspath(__file__))
except:
    this_path = os.path.dirname(os.path.abspath("__file__"))
root_path = os.path.abspath(os.path.join(this_path, os.path.pardir))
if root_path not in sys.path: sys.path.append(root_path)

from libs.convert import md5 as hashmd5

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
            out = self.query("SHOW DATABASES LIKE '%s';"% dbname)
            if isinstance(out, int):
                return out > 0
            elif isinstance(out, db.iterbetter):
                first = out.first()
                return not not out
            else:
                return False
        except:
            return False

    def has_table(self, tbname):
        try:
            if isinstance(self._db_module, db.SqliteDB):
                out = self.query("select count(*)  from sqlite_master where type='table' and name='%s'" % tbname)
                first = out.first()
                return first['count(*)'] == 1
            else:
                out = self.query("SHOW TABLES LIKE '%s';" %tbname)
            if isinstance(out, int):
                return out > 0
            elif isinstance(out, db.iterbetter):
                first = out.first()
                return not not out
            else:
                return False
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
    api = db.database(dbn='sqlite', db='fn2018', user='ldf', passwd='admin', host='localhost', charset='utf8', x='a')
    for x in api.query("select count(*)  from sqlite_master where type='table' and name='%s'" % "tb_user"):
        print (x)
    rows = api.query("select * from tb_user;").list()
    print (hasattr(rows, "__len__"), len(rows))
    print (rows[0])
    for x in rows:
        print(x)
    sql = '''
                CREATE TABLE IF NOT EXISTS `tb_user`
                   (id INTEGER PRIMARY KEY NOT NULL,
                   name           TEXT    NOT NULL,
                   password       INT     NOT NULL);
                '''
    result = api.query(sql)
    print (result)

    print (api.has_table("tb_user"))

    sql = "SELECT id FROM %s WHERE name='%s' AND password='%s' LIMIT 1;" % (
    'tb_user', 'admin', '21232f297a57a5a743894a0e4a801fc3')
    result = api.query(sql)
    if not result or result.first() is None:
        name = "admin"
        pw = "admin"
        pwd = hashmd5(pw).hexdigest()
        sql = 'INSERT INTO tb_user (name, password) VALUES($name, $pwd);'
        result = api.query(sql, vars=dict(name=name, pwd=pwd))
        print (result)
        sql = 'SELECT id FROM %s LIMIT 1;' % ('tb_user')
        result = api.query(sql)
        print (result, result.first())

def test_mysql():
    #api = DB(dbn='mysql', db='fn2018', user='root', passwd='199010', host='localhost', charset='utf8')
    api = db.database(dbn='mysql', db='fn2018', user='root', passwd='199010', host='localhost', charset='utf8')

    print (api.has_database('fn2018'))
    print (api.has_table("tb_user"))
    sql = '''
                CREATE TABLE IF NOT EXISTS `tb_user`
                   (id INTEGER PRIMARY KEY NOT NULL,
                   name           TEXT    NOT NULL,
                   password       INT     NOT NULL);
                '''
    result = api.query(sql)
    print (result)
    
    results = api.query("select * from %s where s_key=$key"%("tb_keyvalue"), dict(key='feng'))
    if results:
        for x in results:
            print (x)


def main():
    print ("test sqlite")
    test_sqlite()
    print ("test mysql")
    test_mysql()

if __name__ == '__main__':
    main()
