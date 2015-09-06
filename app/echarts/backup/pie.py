#encoding=utf-8
from base import Base
from error import EchartsException
#encoding=utf-8
from base import Base
from error import EchartsException
import sys, re
reload(sys)
sys.setdefaultencoding('utf-8')


class Pie(Base):
    def __init__(self, **configs):
        """
            arguments: 
                
        """

        super(Pie, self).__init__()

        self.configs = configs


    def create(self):
        rows = eval(self.configs['data'])
        print rows

        name = []
        for k in rows['data']:
            name.append(k['name'])

        name = self.convert_list(name)

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
                        'echarts/chart/pie'
                    ],
                    function(ec) {{
                        var myChart = ec.init(document.getElementById('{id}')); 
                        var option = {{
                            title : {{
                                text: '{title}',
                                subtext: '',
                                x:'center'
                            }},
                            tooltip : {{
                                trigger: 'item',
                            }},
                            legend: {{
                                orient : 'vertical',
                                x : 'left',
                                data: {name}
                            }},
                            toolbox: {{
                                show : true,
                                feature : {{
                                    mark : true,
                                    dataView : {{readOnly: false}},
                                    restore : true,
                                    saveAsImage : true
                                }}
                            }},
                            calculable : true,
""".format(
    id = self.configs['id'],    
    title = rows['title'],
    name = name
)

        data = "["
        for row in rows['data']:
            data += "{{'value':{value}, 'name':'{name}'}},".format(value=row['value'], name=row['name'])
        data += "]"       


        js += """
                            series : [
                                {{
                                    type:'pie',
                                    radius : [0, 110],
                                    center: ['50%',225],
                                    data:{data}
                                }}
                            ]
                        }};
                        myChart.setOption(option);
                        }}
                       );
          </script>
        """.format(
            data = data
        )
 


        #print js
        js = js.replace('"', '\"')
        js = js.replace("\n", "")
        return js
        
