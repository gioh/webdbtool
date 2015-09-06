#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project_name: my_dba_release
# @File_name: fabric_remote_op.py
# @File_path: E:\开源程序\my_dba_release\app\tools\fabric_remote_op.py
# @Author: 丁以然
# @Email:  dingyiran@szlanyou.com
# @Create_time:   2014-11-19 19:08:01
# @Last Modified by:   丁以然
# @Last Modified time: 2014-11-21 17:30:29


from fabric.api import env
from fabric.api import cd
from fabric.api import run
from fabric.api import local
from fabric.api import get
from fabric.api import put,settings

#from .. import config

# 连接单机用法


#env.user = config.OS_USER

#env.password = config.OS_APPS_PASSWD

#env.host_string = '192.168.30.242'
#env.hosts = ['192.168.30.242','192.168.30.243']


#连接多个服务器用法
#env.hosts = ['apps@192.168.30.242:22']
#env.passwords = {'apps@192.168.30.242:22':'iv%fvd5mx42@w?9xvhp#852s'}
#env.hosts = ['user1@host1:port1', 'user2@host2.port2']
#env.passwords = {'user1@host1:port1': 'password1', 'user2@host2.port2': 'password2'}

def remote_cmd(v_hosts_list,v_os_user,v_os_passwd,v_cmd):
    env.user = v_os_user
    env.password = v_os_passwd
    env.hosts = v_hosts_list
    for host in env.hosts:
        with settings(host_string=host,warn_only=True):
            result = run(v_cmd)
            
            
            if result.return_code == 0: 

                pass

            else:

                print host,result

                #error

                return '执行失败, Server %s :%s' %(host,result)

    return ''  # success



def remote_copy(v_hosts_list,v_os_user,v_os_passwd,v_source_dir,v_target_dir):
    # make sure the directory is there!
    #run('mkdir -p /home/frodo/tmp')

    # our local 'testdirectory' - it may contain files or subdirectories ...
    # mirror_local_mode 保留原文件属性
    env.user = v_os_user
    env.password = v_os_passwd
    env.hosts = v_hosts_list
    for host in env.hosts:
        with settings(host_string=host):

            try:
                result = put(v_source_dir, v_target_dir,mirror_local_mode=True)

                print result

            except Exception, e:
                print host,e.message
            #except SystemExit:

                return '执行失败,Server %s Hit An Exception:%s' %(host,e.message)
            
           
    return ''
    
def get_version():
    local('cat /etc/issue')
    run('ls -l;cat /etc/issue')
    #with cd('/root/'):
    #    put('/home/libaoyin/test.txt', 'test.txt', mode=0755)
    #    get('hello_world.txt')
    #run('ls')
#get_version()
    
# Fabric怎么不使用fab命令来执行呢?
# 答案肯定是OK的了，可以使用execute来模拟fab命令直接在使用python代码执行任务，不需要在shell命令行下调用fab命令来执行任务代码如下:
# 1
# 2
# 3
# 4
# 5
# 6
# 7
# from fabric.api import run,env,execute
# env.hosts=["root@172.16.109.11"]
# env.password="server"
# def test():
#     run("ls -al")
# if __name__=="__main__":
#     execute(test)
#   
# 当run的时候，返回码不是0，仅仅警告，而不是abort退出  
# from fabric.api import settings

# with settings(warn_only=True):
#     result = run('pngout old.png new.png')
#        if result.return_code == 0: 
#           do something
#        elif result.return_code == 2: 
#           do something else 
#        else: #print error to user
#           print result
#           raise SystemExit()
#           

# 当执行的shell没有成功的话程序就好直接退出发生occur，那有什么办法可以捕获到错误呢
# vim fabfile.py
# from fabric.api import local, settings, abort
# from fabric.contrib.console import confirm
# def test():
#     with settings(warn_only=True):#setting设置变量,warn_only=True用于设置指定代码段如果出错的话就有abortd转为warnings状态(说白了就是在warn_only=True包含的代码快中 如果发生了错误原本是会直接终止的，现在变为不终止了变了警告)
#         result = local('ls al', capture=True) #执行了一个错误的shell命令,通过capture=True设置为可捕捉,
#                                               #通过failed属性或return_code来判断是否出错
#     if result.failed and not confirm("Tests failed. Continue anyway?"):
#     #confirm用来给用户一个提示的对话框，并给出yes/no让用户输入
#         abort("Aborting at user request.")
#     #abort是用于输出里面的信息并终止


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