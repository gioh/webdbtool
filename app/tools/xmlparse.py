#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project_name: my_dba_release
# @File_name: xmlparse.py
# @File_path: E:\开源程序\my_dba_release\app\tools\xmlparse.py
# @Author: 丁以然
# @Email:  dingyiran@szlanyou.com
# @Create_time:   2014-06-17 15:04:21
# @Last Modified by:   丁以然
# @Last Modified time: 2014-11-20 11:05:55


import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from xml.dom import minidom

class XmlParse:
    def __init__(self, xmlfile):
        self.xmlfile = xmlfile

    def get_source_data(self):
        doc = minidom.parse(self.xmlfile)
        return doc.toxml('UTF-8')

    def get_attrvalue(self, node, attrname):
        return node.getAttribute(attrname) if node else ''

    def get_nodevalue(self, node, index = 0):
        return node.childNodes[index].nodeValue if node else ''

    def get_xmlnode(self, node,name):
        return node.getElementsByTagName(name) if node else []
        
    def get_parse_data(self, **config):
        doc = minidom.parse(self.xmlfile)
        root = doc.documentElement

        config.setdefault('parent_node', None)
        config.setdefault('attr', [])
        config.setdefault('node', [])

        
        if config['parent_node']:
            parent_nodes = XmlParse.get_xmlnode(self ,root,config['parent_node'])    #set parent node
            contents_list = []

            for node in parent_nodes:
                contents_dict = {}
                for attr in config['attr']:
                    attr_result = XmlParse.get_attrvalue(self, node,attr)
                    contents_dict[attr] = attr_result
                for sub_node in config['node']:
                    sub_node_result = XmlParse.get_xmlnode(self, node,sub_node)
                    sub_node_result = XmlParse.get_nodevalue(self, sub_node_result[0]).encode('utf-8','ignore')
                    contents_dict[sub_node] = sub_node_result
                contents_list.append(contents_dict)
        return contents_list
                
            





