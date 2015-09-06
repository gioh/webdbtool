#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project_name: my_dba_release
# @File_name: webservice.py
# @File_path: E:\开源程序\my_dba_release\app\tools\webservice.py
# @Author: 丁以然
# @Email:  dingyiran@szlanyou.com
# @Create_time:   2014-06-17 15:04:21
# @Last Modified by:   丁以然
# @Last Modified time: 2014-11-20 11:06:11


import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import urllib2

class Webservice:
    def wget(self, url):
        if not url.startswith('http://'):
            raise Exception('url error')
        else:
            data = ''
            req = urllib2.Request(url)
            try:
                fd = urllib2.urlopen(req)
            except urllib2.HTTPError, e:
                raise ValueError('HTTP ERROR: %s' % e)
            except urllib2.URLError, e:
                raise ValueError('URL ERROR: %s' % e)
            while 1:
                data_contents = fd.read(1024)
                if not len(data_contents):
                    break
                else:
                    data += data_contents
        return data

    def wget_head(self, url):
        if not url.startswith('http://'):
            raise Exception('url error')
        else:
            req = urllib2.Request(url)
            try:
                fd = urllib2.urlopen(req)
            except urllib2.HTTPError, e:
                raise ValueError('HTTP ERROR: %s' % e)
            except urllib2.URLError, e:
                raise ValueError('URL ERROR: %s' % e)
            info = fd.info()
            return info
        
                

