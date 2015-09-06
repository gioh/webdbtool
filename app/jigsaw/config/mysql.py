
class Dbconfig(object):

    def option(self):
        mysql = {
            'host'     : 'localhost',
            'user'     : 'dba',
            'password' : 'localdba',
            'database' : 'config'
        }
        return mysql
