#encoding=utf-8
from base import Base
from error import EchartsException
import sys, re
reload(sys)
sys.setdefaultencoding('utf-8')

class Line(Base):
    def __init__(self, **configs):
        """
        arguments:
          id        render object
          type      line or column
          data      json string
        """
        super(Line, self).__init__()
        if configs.has_key('type'):
            if configs['type'] == 'column':
                configs['type'] = 'bar' 
        

        self.configs = configs


    def validation_key(self, data, k):
        if data.has_key(k):
            return data[k]
        else:
            return ""

    def create(self):
        rows = eval(self.configs['data'])
        print rows

        rows['title'] = self.validation_key(rows, 'title')

        name = self.convert_list(rows['name'])
        xaxis = self.convert_list(rows['xaxis'])


        datazoom = ""
        if rows.has_key('datazoom'):
            if rows['datazoom'] == 'true':
                datazoom = """
                dataZoom : {
                    show : true,
                    realtime : true,
                    start : 0,
                    end : 100
                },
                """

        js = r"""
<script>
require.config({{
    packages: [
        {{
            name: 'echarts',
            location: '/echarts/src',      
            main: 'echarts'
        }},
        {{
            name: 'zrender',
            location: '/zrender/src', 
            main: 'zrender'
        }}
    ]
}});

        require(
        [
            'echarts',
            'echarts/chart/bar',
            'echarts/chart/line'
        ],
        function(ec) {{
            var myChart = ec.init(document.getElementById('{id}'));
            var option = {{
                title : {{
                    text: '{title}',
                    x: 'left'
                }},
                tooltip : {{
                    trigger: 'axis',
                    backgroundColor: 'rgba(218,112,214,0.7)'
                }},
                legend: {{
                    data:{name}
                }},
                toolbox: {{
                    show : true,
                    feature : {{
                        mark : true,
                        dataZoom : true,
                        dataView : {{readOnly: false}},
                        magicType:['line', 'bar'],
                        restore : true,
                        saveAsImage : true
                    }}
                }},
                calculable : true,
                {datazoom}
                xAxis : [
                    {{
                        type : 'category',
                        data : {xaxis}
                    }}
                ],
                yAxis : [
                    {{
                        type : 'value',
                        splitArea : {{show : true}}
                    }}
                ],
           series : [

        """.format(
            id = self.configs['id'],
            name = name,
            xaxis = xaxis,
            title = rows['title'],
            datazoom = datazoom
        )


        for i in range(len(rows['name'])):
            if not rows.has_key('type'):
                #type = self.configs['type']
                type = self.configs['type']
            else:
                type = rows['type'][i]
            print self.configs['type']

            js += """
            {{
               name:'{name}',
               type:'{type}',
               data:{data}
            }},
            """.format(
                name = rows['name'][i],
                type = type, 
                data = rows['data'][i]
            )
        js += """
               ]
            };
            myChart.setOption(option);
          }
        );
        </script>
        """

        print js
        js = js.replace('"', '\"')
        js = js.replace("\n", "")
        return js
        

