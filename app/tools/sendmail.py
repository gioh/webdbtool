#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project_name: my_dba_release
# @File_name: sendmail.py
# @File_path: E:\开源程序\my_dba_release\app\tools\sendmail.py
# @Author: 丁以然
# @Email:  dingyiran@szlanyou.com
# @Create_time:   2014-06-17 15:04:21
# @Last Modified by:   丁以然
# @Last Modified time: 2014-11-20 11:06:23


import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class Sendmail:
    def __init__(self, **config):
        config.setdefault('mail_from', 'nezha@vipshop.com')
        config.setdefault('user', 'nezha')
        config.setdefault('passwd', 'NzVipshop@12345!')

        self.mail_from       = config['mail_from']
        self.user            = config['user']
        self.passwd          = config['passwd']

    def send_mail(self, **config):
        # config['mail_to']
        # config['mail_cc']   None
        # config['mail_bcc']  None
        # config['subject']
        # config['msg']
        # config['coding']    utf-8
        # config['server']    mail.pptv.com
        # config['port']      587

        config.setdefault('mail_cc', None)
        config.setdefault('mail_bcc', None)
        config.setdefault('coding', 'utf-8')
        config.setdefault('server', 'smtp.vipshop.com')
        config.setdefault('port', 25)


        import smtplib
        from email.MIMEText import MIMEText
        msg = MIMEText(config['msg'],'html', _charset=config['coding'])
        msg.set_charset(config['coding'])
        msg['From']=self.mail_from
        msg['Subject']=config['subject']
        if isinstance(config['mail_to'],list):
            msg['To']=','.join(config['mail_to'])
        else:
            msg['To']=config['mail_to']
        if isinstance(config['mail_cc'],list):
            msg['Cc']=','.join(config['mail_cc'])
        else:
            msg['Cc']=config['mail_cc']
        if isinstance(config['mail_bcc'],list):
            msg['Bcc']=','.join(config['mail_bcc'])
        else:
            msg['Bcc']=config['mail_bcc']


        server = smtplib.SMTP()
        server.connect(config['server'], config['port'])
        server.login(self.user, self.passwd)
        server.sendmail(self.mail_from, config['mail_to'], msg.as_string())
        server.quit()

