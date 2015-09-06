#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project_name: my_dba_release
# @File_name: mysql.py
# @File_path: E:\开源程序\my_dba_release\app\tools\mysql.py
# @Author: 丁以然
# @Email:  dingyiran@szlanyou.com
# @Create_time:   2014-06-17 15:04:21
# @Last Modified by:   丁以然
# @Last Modified time: 2014-11-20 11:08:25


import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class Mysql:
    def __init__(self, **config):
        config.setdefault('host', 'localhost')
        self.host     = config['host']
        self.user     = config['user']
        self.password = config['password']
        self.database = config['database']
        Mysql.connect(self)
    
    def connect(self):
        import MySQLdb
        import MySQLdb.cursors
        conn = MySQLdb.connect(
            host=self.host,
            user=self.user,
            passwd=self.password,
            db=self.database,
            compress = 1,
            cursorclass = MySQLdb.cursors.DictCursor,
            charset='utf8'
        )
        cursor = conn.cursor()
        cursor.execute("SET NAMES 'utf8'")
        cursor.execute("SET CHARACTER_SET_CLIENT=utf8")
        cursor.execute("SET CHARACTER_SET_RESULTS=utf8")
        self.cursor = cursor

    def fetchall(self, sql):
        count = self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        return rows

    def fetch(self, sql):
        count = self.cursor.execute(sql)
        row = self.cursor.fetchone()
        return row

    def save(self, sql):
        self.cursor.execute(sql)
        self.cursor.execute("commit")

    def truncate(self, table):
        sql = "truncate table %s" % table
        self.cursor.execute(sql)
        self.cursor.execute("commit")

    def close(self):
        self.cursor.close()

    def __del__(self):
        self.close()




