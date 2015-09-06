#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project_name: my_dba_release
# @File_name: project.py
# @File_path: E:\开源程序\my_dba_release\app\jigsaw\project.py
# @Author: 丁以然
# @Email:  dingyiran@szlanyou.com
# @Create_time:   2015-01-26 18:51:27
# @Last Modified by:   丁以然
# @Last Modified time: 2015-03-25 10:57:50
from base import Base
from error import JigsawException
import ConfigParser, time, re
from tools.mysql import Mysql

class Project(Base):
    Config_path = '/home/apps/my_prog/my_dba_release/app/config/highstock'   

    def __init__(self, **configs):
        """
            argument:
              name
              cid
              id
              attr   dictionary
        """
        super(Project, self).__init__()
        self.configs = configs

    def create_stock(self):
        if self.configs['name'].lower() == 'telescope':
            return self.stock_telescope()


    def stock_telescope(self):
        cf = ConfigParser.ConfigParser()
        cf.read("%s/%s.ini" % (self.Config_path, self.configs['name'])  )  
        host = cf.get("db", "host") 
        port = cf.get("db", "port") 
        user = cf.get("db", "user") 
        password = cf.get("db", "pass") 
        database = cf.get("db", "database") 
        
        conn = Mysql(
            host = host,
            user = user,
            password = password,
            database = database, 
        )

        cid = []        
        if "|" in self.configs['cid']:
            for i in self.configs['cid'].split('|'):
                cid.append(i.strip())
        else:
            cid.append(self.configs['cid'])
        print cid

        now = int(time.time())

        result = {}
        for appid in cid:
            sql_title = "select title from h_appmap where appid = '%s' limit 1" % appid
            appmap_row = conn.fetch(sql_title)
            if not appmap_row['title']: appmap_row['title'] = appid
            line = appmap_row['title']
            print line
            result[line] = []
            rangetime = 1209600

            if self.configs['attr'].has_key('rangetime'):
                if self.configs['attr']['rangetime'] and '|' in self.configs['attr']['rangetime']:
                    rangetime = self.configs['attr']['rangetime'].split('|')[1]
                    times = re.search("^([0-9]+)([a-z|A-Z]+)", rangetime)
                    n, m = int(times.group(1)), times.group(2) 
                    if m == 'h':
                        m = 3600
                    elif m == 'd':
                        m = 86400
                    elif m == 'w':
                        m = 604800
                    rangetime = n*m
            print rangetime                    

            sql_data = "select timestamp, value from h_data where appid = '%s' and timestamp > %d order by timestamp" % (appid, now-rangetime)
            data_rows = conn.fetchall(sql_data)
            for row in data_rows:
                result[line].append([int(row['timestamp']*1000), int(row['value'])]) 

            #print result

        
        return self.highstock(result, self.configs['id'], self.configs['attr'])

       # return self.highstock({'line1' : [[1381312202000, 1.0], [1381312262000, 5.0]], 'line2' : [[1381312202000, 2.0], [1381312262000, 4.0]]}, "telescope")
                                            

        


        


            
        




    

        

if __name__ == '__main__':
    p = Project(
        name="telescope",
        cid="992|993"         
    )
    print p.create_stock()


