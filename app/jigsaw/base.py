from error import JigsawException
from config.mysql import Dbconfig
from tools.mysql import Mysql
import re

class Base(object):
    CONN = ""
    DOMAIN = "10.1.1.91"

    def __init__(self):
        if not self.CONN:
            self.CONN = self.conndb()
        

    def conndb(self):
        db = Dbconfig().option()
        conn = Mysql(
            host = db['host'],
            user = db['user'],
            password = db['password'],
            database = db['database'],
        )
        return conn


    def getjsonp(self, appid, start=0, end=0):
        result = "["

        if start and end:
            sql = "select value, timestamp from jigsaw_data where appid = '{appid}' and timestamp > {start} and timestamp < {end} order by timestamp".format(
                appid = appid,
                start = start,
                end = end,
            )
        else:
            sql = "select value, timestamp from jigsaw_data where appid = '{appid}' order by timestamp".format(
                appid = appid
            )
        
        for row in self.CONN.fetchall(sql):
            result += "[{timestamp}, {value}],".format(
                timestamp = int(row['timestamp']),
                value = row['value']
            )
        result = re.sub(",$", "", result)
        result += "]"
        return result

    def get(self, **config):
        if config.has_key('name'):
            sql = "select name from jigsaw_app where appid = '%s'" % config['name']
            return self.CONN.fetch(sql)['name']
        else:
            return ""
       

    def highstock(self, data, renderid, attr={}):
        """
            arguments:
                data   dict   { 'linename' : [1381312202000, 64701.0, 1381312262000, 63947.0] }
        """

        count = len(data)

        js = """
            <script type='text/javascript'>
            $(function() {{
                var seriesOptions = [],
                    yAxisOptions = [],
                    count = 0,
                    colors = Highcharts.getOptions().colors;
                Highcharts.setOptions({{
                    global : {{
                        useUTC : false
                    }}
                }}); 
        """


        color_index = 0
        for name, d in data.iteritems():
            if not name: continue
            js += """
            seriesOptions[{series_index}] = {{
                    name: '{name}',
                    data: {data},
                    yAxis: {y_index},
                    color: colors[{color_index}]
                }};
              count++;
              if (count == {count}) {{
                 createChart();
              }}
            """.format(
                series_index = color_index,
                data = d,
                y_index = color_index,
                count = count,
                color_index =  color_index,
                name = name,
            )
            color_index += 1


        
        js += """
 function createChart() {{
        var start = new Date();
        chart = new Highcharts.StockChart({{
            chart: {{
                zoomType: 'x ',
                renderTo: '{renderid}'
            }},

            yAxis: [
        """.format(
           renderid = renderid,
        )

        for i in range(count):
           if attr.has_key('opposite'):
               if attr['opposite'] == 'true':
                   if count-1 == i:
                       js += """
             {{
                lineWidth: 1,
                opposite: true,
             }},
                   """
                       continue

           js += """
            {{
               lineWidth: 1,
            }},
            """
        js = re.sub(",$", "", js)

        js += """
            ],
        """

        if attr.has_key('ctitle'):
            if attr['ctitle']:
                js += """
                    title:{
                        text: '%s'
                    },
                    scrollbar: {
                        enabled: true
                    },
                    navigator: {
                        enabled: true
                    },
                """ % attr['ctitle']
        selected = 1
        rangetime = ""
        if attr.has_key('rangetime'):
            if attr['rangetime']:
                if '|' in attr['rangetime']:
                    rangetime = attr['rangetime'].split('|')[0]
                else:
                    rangetime = attr['rangetime']

        if rangetime == '1h':
            selected = 0
        elif rangetime == '1d':
            selected = 1
        elif rangetime == '3d':
            selected = 2
        elif rangetime == '1w':
            selected = 3
        elif rangetime == '2w':
            selected = 4
        
            


        js += """

            legend: {{
                align: 'center',
                layout: 'horizontal',
                enabled: true,
                verticalAlign: 'bottom',
            }},

            rangeSelector: {{
                buttons: [{{
                    count: 1,
                    type: 'hour',
                    text: '1h'
                }}, {{
                    count: 1,
                    type: 'day',
                    text: '1d'
                }}, {{
                    count: 3,
                    type: 'day',
                    text: '3d'
                }}, {{
                    count: 1,
                    type: 'week',
                    text: '1w'
                }}, {{
                    count: 2,
                    type: 'week',
                    text: '2w'
                }}],
                inputEnabled: true,
                selected: {selected}
            }},
            tooltip: {{
                pointFormat: '<span>{{series.name}}</span>: <b>{{point.y}}</b>',
                valueDecimals: 2
            }},
            series: seriesOptions
        }});
    }}
}});

</script>
        """.format(
            selected = selected,
        )

        js = js.replace('"', '\"')
        js = js.replace('{{', '{')
        js = js.replace('}}', '}')
        #print js
        js = js.replace("\n", "")
        return js








    
