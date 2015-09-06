#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 丁以然 dingyiran2000@qq.com
# @Date:   2014-11-19 19:08:01
# @Last Modified by:   丁以然
# @Last Modified time: 2014-11-20 17:27:07

from fabric.api import env
from fabric.api import cd
from fabric.api import run
from fabric.api import local
from fabric.api import get
from fabric.api import put,settings

# 连接单机用法

env.user = 'apps'
env.password = 'iv%fvd5mx42@w?9xvhp#852s'
#env.host_string = '192.168.30.242'
env.hosts = ['192.168.30.242','192.168.30.243']


#连接多个服务器用法
#env.hosts = ['apps@192.168.30.242:22']
#env.passwords = {'apps@192.168.30.242:22':'iv%fvd5mx42@w?9xvhp#852s'}

def test():
    for host in env.hosts:
        with settings(host_string=host):
            #put('/var/www/auto/apps/sh/tool/percona-xtrabackup-2.2.3-Linux-x86_64', '/home/apps',mirror_local_mode=True)
            run('ls -l;cat /etc/issue')
test()

#env.hosts = ['user1@host1:port1', 'user2@host2.port2']
#env.passwords = {'user1@host1:port1': 'password1', 'user2@host2.port2': 'password2'}

def copy():
    # make sure the directory is there!
    #run('mkdir -p /home/frodo/tmp')

    # our local 'testdirectory' - it may contain files or subdirectories ...
    put('/var/www/auto/apps/sh/tool/percona-xtrabackup-2.2.3-Linux-x86_64', '/home/apps/aaa')
    
def get_version():
    local('cat /etc/issue')
    run('ls -l;cat /etc/issue')
    #with cd('/root/'):
    #    put('/home/libaoyin/test.txt', 'test.txt', mode=0755)
    #    get('hello_world.txt')
    #run('ls')
#get_version()
    
#if __name__=='__main__':
    #copy()
#   get_version()


# from fabric.api import *

# # 使用远程命令的用户名
# env.user = 'appuser'
# # 执行命令的服务器
# env.hosts = ['server1.example.com', 'server2.example.com']

# def pack():
#     # 创建一个新的分发源，格式为 tar 压缩包
#     local('python setup.py sdist --formats=gztar', capture=False)

# def deploy():
#     # 定义分发版本的名称和版本号
#     dist = local('python setup.py --fullname', capture=True).strip()
#     # 把 tar 压缩包格式的源代码上传到服务器的临时文件夹
#     put('dist/%s.tar.gz' % dist, '/tmp/yourapplication.tar.gz')
#     # 创建一个用于解压缩的文件夹，并进入该文件夹
#     run('mkdir /tmp/yourapplication')
#     with cd('/tmp/yourapplication'):
#         run('tar xzf /tmp/yourapplication.tar.gz')
#         # 现在使用 virtual 环境的 Python 解释器来安装包
#         run('/var/www/yourapplication/env/bin/python setup.py install')
#     # 安装完成，删除文件夹
#     run('rm -rf /tmp/yourapplication /tmp/yourapplication.tar.gz')
#     # 最后 touch .wsgi 文件，让 mod_wsgi 触发应用重载
#     run('touch /var/www/yourapplication.wsgi')



# 另外一个样例
# from fabric.api import local, run, env, put
# import os, time
 
# # remote ssh credentials
# env.hosts = ['10.1.1.25']
# env.user = 'deploy'
# env.password = 'XXXXXXXX' #ssh password for user
# # or, specify path to server public key here:
# # env.key_filename = ''
 
# # specify path to files being deployed
# env.archive_source = '.'
 
# # archive name, arbitrary, and only for transport
# env.archive_name = 'release'
 
# # specify path to deploy root dir - you need to create this
# env.deploy_project_root = '/var/www/projectx/'
 
# # specify name of dir that will hold all deployed code
# env.deploy_release_dir = 'releases'
 
# # symlink name. Full path to deployed code is env.deploy_project_root + this
# env.deploy_current_dir = 'current'
 
# def update_local_copy():
#     # get latest / desired tag from your version control system
#     print('updating local copy...')
 
# def upload_archive():
#     # create archive from env.archive_source
#     print('creating archive...')
#     local('cd %s && zip -qr %s.zip -x=fabfile.py -x=fabfile.pyc *' \
#         % (env.archive_source, env.archive_name))
 
#     # create time named dir in deploy dir
#     print('uploading archive...')
#     deploy_timestring = time.strftime("%Y%m%d%H%M%S")
#     run('cd %s && mkdir %s' % (env.deploy_project_root + \
#         env.deploy_release_dir, deploy_timestring))
 
#     # extract code into dir
#     print('extracting code...')
#     env.deploy_full_path = env.deploy_project_root + \
#         env.deploy_release_dir + '/' + deploy_timestring
#     put(env.archive_name+'.zip', env.deploy_full_path)
#     run('cd %s && unzip -q %s.zip -d . && rm %s.zip' \
#         % (env.deploy_full_path, env.archive_name, env.archive_name))
 
# def before_symlink():
#     # code is uploaded, but not live. Perform final pre-deploy tasks here
#     print('before symlink tasks...')
 
# def make_symlink():
#     # delete existing symlink & replace with symlink to deploy_timestring dir
#     print('creating symlink to uploaded code...')
#     run('rm -f %s' % env.deploy_project_root + env.deploy_current_dir)
#     run('ln -s %s %s' % (env.deploy_full_path, env.deploy_project_root + \
#         env.deploy_current_dir))
 
# def after_symlink():
#     # code is live, perform any post-deploy tasks here
#     print('after symlink tasks...')
 
# def cleanup():
#     # remove any artifacts of the deploy process
#     print('cleanup...')
#     local('rm -rf %s.zip' % env.archive_name)
 
# def deploy():
#     update_local_copy()
#     upload_archive()
#     before_symlink()
#     make_symlink()
#     after_symlink()
#     cleanup()
#     print('deploy complete!')