#encoding=utf-8
from base import Base
from error import EchartsException
#encoding=utf-8
from base import Base
from error import EchartsException
import sys, re, types
reload(sys)
sys.setdefaultencoding('utf-8')


class Map(Base):

    def __init__(self, **configs):
        super(Base, self).__init__()
        self.configs = configs

    def get_seriesname(self, data):
        result = []
        for row in data:
            if type(row[1]) is types.StringType:
                result.append(row[0])
            else:
                result.append('None')
        return result

    def data_hashmap(self, data):
        result = "["
        flag = 1

        if type(data[1]) is types.StringType:
            data = data[1:]

        s = ""
        for index in data:
            if flag % 2:
                s += "{{name: '{name}', ".format(name=index)
            else:
                s += "value: {value}}},".format(value=index)
            result += s
            s = ""
            flag += 1

        result += "]"
        return result


    def data_hinge_hashmap(self, data):
        result = "["
        flag = 1

        if type(data[1]) is types.StringType:
            data = data[1:]


        s = ""
        for index in data:
            if flag % 2:
                s += "{{name: '{name}', ".format(name=index)
            else:
                s += "value: {value}}},".format(value=index)
            result += s
            s = ""
            flag += 1
        result += "]"
        return result


    def get_max(self, data):
        max = 0
        for row in data:
            for n in row:
                if type(n) is types.IntType:
                    if n > max:
                        max = n

        return max
    
    
    def create(self):
        if self.configs['type'] == 'map':
            return self.generate_map()
        elif self.configs['type'] == 'map_pie':
            return self.generate_map_pie()



    def generate_map(self):
        rows = eval(self.configs['data'])
        print rows
        
        series_name = self.get_seriesname(rows['data'])
        series_data = self.convert_list(series_name)
        max = self.get_max(rows['data'])


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
                        'echarts/chart/map'
                    ],
                    function(ec) {{
                        var myChart = ec.init(document.getElementById('{id}')); 
                        var option = {{
                        title : {{
                            text: '{title}',
                            x:'center'
                        }},
                        tooltip : {{
                            trigger: 'item'
                        }},

                        legend: {{
                            orient: 'vertical',
                            x:'left',
                            data: {series_data}
                        }},
                        dataRange: {{
                            min: 0,
                            max: {max},
                            text:['高','低'],           
                            calculable : true,
                            textStyle: {{
                                color: 'orange'
                            }}
                        }},
                        toolbox: {{
                            show : true,
                            orient : 'vertical',
                            x: 'right',
                            y: 'center',
                            feature : {{
                                mark : true,
                                dataView : {{readOnly: false}},
                                restore : true,
                                saveAsImage : true
                            }}
                        }},
                        series : [
        """.format(
            id = self.configs['id'],
            title = rows['title'],
            series_data = series_data,
            max = (max+100)/100*100
        )


        for index in range(len(series_name)):
            js += """
                        {{
                             name:'{sname}',
                             type: 'map',
                                    mapType: 'china',
                                    itemStyle:{{
                                        normal:{{label:{{show:true}}}},
                                        emphasis:{{label:{{show:true}}}}
                                    }},
                                    data: {data}
                        }},
                             
            """.format(
                sname = series_name[index],
                data = self.data_hashmap(rows['data'][index])
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







    def generate_map_pie(self):
        rows = eval(self.configs['data'])
        print rows
        
        series_name = self.get_seriesname(rows['data'])
        series_data = self.convert_list(series_name)
        max = self.get_max(rows['data'])

        hinge = []
        if rows.has_key('hinge'):
            for i in rows['hinge']:
                index = rows['data'][0].index(i)
                hinge.append(rows['data'][0][index])
                hinge.append(rows['data'][0][index+1])
        else:
            hinge = rows['data'][0]


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
                        'echarts/chart/pie',
                        'echarts/chart/map'
                    ],
                    function(ec) {{
                        var myChart = ec.init(document.getElementById('{id}')); 
                        var option = {{
                        title : {{
                            text: '{title}',
                            x:'center'
                        }},
                        tooltip : {{
                            trigger: 'item'
                        }},
                        legend: {{
                            x:'right',
                            data: {series_data}
                        }},
                        dataRange: {{
                            orient: 'horizontal',
                            min: 0,
                            max: {max},
                            text:['高','低'],           
                            splitNumber:0,
                            calculable : true,
                            textStyle: {{
                                color: 'orange'
                            }}
                        }},
                        toolbox: {{
                            show : true,
                            orient : 'vertical',
                            x: 'right',
                            y: 'center',
                            feature : {{
                                mark : true,
                                dataView : {{readOnly: false}},
                                saveAsImage : true
                            }}
                        }},
                        series : [
        """.format(
            id = self.configs['id'],
            title = rows['title'],
            series_data = series_data,
            max = (max+100)/100*100
        )


        for index in range(len(series_name)):
            js += """
                        {{
                             name:'{sname}',
                             type: 'map',
                                    mapType: 'china',
                                    mapLocation: {{
                                        x: 'left'
                                    }},
                                    selectedMode : 'multiple',
                                    itemStyle:{{
                                        normal:{{label:{{show:true}}}},
                                        emphasis:{{label:{{show:true}}}}
                                    }},
                                    data: {data}
                        }},
                             
            """.format(
                sname = series_name[index],
                data = self.data_hashmap(rows['data'][index])
            )


        js += """
            {{
                type:'pie',
                tooltip: {{
                    trigger: 'item',
                    formatter: '{{a}} <br/>{{b}} : {{c}} ({{d}}%)'
                }},
                center: [document.getElementById('{id}').offsetWidth - 250, 225],
                radius: [50, 120],
                data: {data}
                
            }}     
        """.format(
            id = self.configs['id'],
            data = self.data_hinge_hashmap(hinge)
        )




        js += """
                ],
                animation: false
            };
            var ecConfig = require('echarts/config');
            myChart.on(ecConfig.EVENT.MAP_SELECTED, function(param){
                var selected = param.selected;
                var mapSeries = option.series[0];
                var data = [];
                var legendData = [];
                var name;
                for (var p = 0, len = mapSeries.data.length; p < len; p++) {
                    name = mapSeries.data[p].name;
                    mapSeries.data[p].selected = selected[name];
                    if (selected[name]) {
                        data.push({
                            name: name,
                            value: mapSeries.data[p].value
                        });
                        legendData.push(name);
                    }
                }
                option.legend.data = legendData;
                option.series[1].data = data;
                myChart.setOption(option, true);
            });
             

                        myChart.setOption(option);

                        }
                       );
        </script>
        """


        #print js
        js = js.replace('"', '\"')
        js = js.replace("\n", "")
        return js 


      

      
