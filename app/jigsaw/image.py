from base import Base
from error import JigsawException
import httplib,re,time,types, random, os,urllib, urllib2

class Image(Base):
    Constr = ""
    Phantomjs_server = "127.0.0.1:3003"

    def __init__(self, **configs):
        # arguments:  appid
        super(Image, self).__init__()
        configs['appid'] = str(configs['appid'])
        self.configs = configs


    def create_stock_line(self, last_hour=24):
        self.Constr = 'StockChart'
        start, end = (int(time.time())-3600*last_hour)*1000, int(time.time())*1000
        #start = 1381312201000
        #end = 1381478914580
 
        appid = []
        if "|" in self.configs['appid']:
            appid = self.configs['appid'].split('|')
        else:
            appid.append(self.configs['appid'])
        for id in appid:
            json = self.getjsonp(id, start, end) 
            json_result = """
            {{
                legend: {{
                   align: 'center',
                   layout: 'horizontal',
                   enabled: true,
                   verticalAlign: 'top',
            }},
    	    series: [        
                {{  
                     name:'{name}',
                     data: {json}
                }},]}};
            """.format(
                name = self.get(name=self.configs['appid']),
                json = json.replace("\n","")
            )


            name = self.get(name=id).strip()
            #print id, name, json
            
            file_name = int(time.time()) + random.randint(0,99)

            json_file = open("/data/python/web/jigsaw/public/json/{name}.json".format(name=file_name), 'w' )
            json_file.write(json_result)
            json_file.close()

            commond = """
                 phantomjs /data/python/web/jigsaw/public/exporting-server/phantomjs/highcharts-convert.js -infile /data/python/web/jigsaw/public/json/{json_file}.json -outfile /data/python/web/jigsaw/public/img/{image_name}.png  -constr {type}
            """.format(
                json_file = file_name,
                image_name = file_name,
                type = self.Constr,
            )
            #print commond
            print os.popen(commond)
            return file_name
            
             




if __name__ == '__main__':
    i = Image(appid='2')
    i.create_stock_line(24)



