#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project_name: my_dba_release
# @File_name: pyredis.py
# @File_path: E:\开源程序\my_dba_release\app\tools\pyredis.py
# @Author: 丁以然
# @Email:  dingyiran@szlanyou.com
# @Create_time:   2014-06-17 15:04:21
# @Last Modified by:   丁以然
# @Last Modified time: 2014-11-20 11:07:08


import sys, time
reload(sys)
sys.setdefaultencoding('utf-8')


import redis

class Pyredis(object):
    def __init__(self, **configs):
        """
        parameters:
            host    *
            db      *
            port
        """
        configs.setdefault('port', 6379)

        self.host  =  configs['host']
        self.db    =  configs['db']
        self.port  =  int(configs['port'])
        self.connect()

    def connect(self):
        self.conn = redis.Redis(self.host,db=self.db, socket_timeout=10)

    def fetch(self, key):
        return self.conn.mget(key)[0]

    def fetchall(self, keys=[]):
        return self.conn.mget(keys)

    def keys(self, key):
        return self.conn.keys(key)

    def flushdb(self):
        return self.conn.flushdb()

    def save(self, key):
        self.conn.save(key)
        return 1


#if __name__ == '__main__':
#    r = Pyredis(
#        host = '10.19.151.16',
#        db = '5'
#    )
#    print r.fetch('mars_pv_b2c')
#    print r.fetchall('mars_pv_b2c','mars_pv_mobile')
    

        
           
