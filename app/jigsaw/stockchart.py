from base import Base
from error import JigsawException
import httplib,re 

class Stockchart(Base):

    def __init__(self, **configs):
        #arguments :  width, height, appid 

        super(Stockchart, self).__init__()
        configs.setdefault('width', '0')
        configs.setdefault('height', '0')
        configs.setdefault('title', '')
        configs.setdefault('subtitle', '')
        #configs.setdefault('type', '')
        #if not configs.has_key('cid'):
        #    raise JigsawException("cid can not null!")
        self.configs = configs


    def create(self):
        if not self.configs['type']:
            return "type can not null"

        if self.configs['type'] == 'jigsaw-chart':
            if "|" not in self.configs['cid']:
                return self.create_line()
            else:
                return self.create_lines()
        elif self.configs['type'] == 'jigsaw-static_line':
            return self.create_static_line()
        elif self.configs['type'] == 'jigsaw-column':
            return self.create_static_column()
        elif self.configs['type'] == 'jigsaw-pie':
            return self.create_static_pie()
        else:
            return "%s is unknown" % self.configs['type']
        

    def create_lines(self):
        count = 0

        for id in self.configs['cid'].split('|'):
            id = id.strip()
            if not id: continue
            count += 1

        
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
        for id in self.configs['cid'].split('|'):
            id = id.strip()
            if not id: continue
            js += """
            $.getJSON('{json_url}', function(data) {{
            seriesOptions[{series_index}] =  {{
                name: '{name}' ,
                data: data,
                yAxis: {y_index},
                color: colors[{color_index}]

            }};
            count++;
            if (count == {count}) {{
                createChart();
            }}
        }});
            """.format(
                json_url = 'http://%s/getjsonp?appid=%s' % (self.DOMAIN, id),
                series_index = color_index,
                count = count, 
                y_index = color_index,
                color_index =  color_index,
                name = self.get(name=id),
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
           renderid = self.configs['id'],
        )


        for i in range(count):
            js += """
             {{
                lineWidth: 1,
             }},
             """.format(index=i)
        js = re.sub(",$", "", js)


        js += """
            ],

            legend: {{
                align: 'center',
                layout: 'horizontal',
                enabled: true,
                verticalAlign: 'top',
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
                selected: 1
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
        """

        #print js
        js = js.replace('"', '\"')
        js = js.replace('{{', '{')
        js = js.replace('}}', '}')
        return js.replace("\n", "")



    def create_line(self):
        
        js=r"""
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
        
            $.getJSON('{json_url}' , function(data) {{
                seriesOptions[0] = {{
                    name: '{name}' ,
                    data: data,
                }};
                count++;
                if (count == 1) {{
                    createChart();
                }}
            }});
        
    
    
        function createChart() {{
            var start = new Date();
            chart = new Highcharts.StockChart({{
                chart: {{
                    zoomType: 'x ',
                    renderTo: '{renderid}'
                }},
                legend: {{
                    align: 'center',
                    layout: 'horizontal',
                    enabled: true,
                    verticalAlign: 'top',
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
                    selected: 1
                }},
                yAxis: {{
                    plotLines: [{{
                        value: 0,
                        width: 2,
                        color: 'silver'
                    }}]
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
    json_url = 'http://%s/getjsonp?appid=%s' % (self.DOMAIN, self.configs['cid']),
    name = self.get(name=self.configs['cid']),
    renderid = self.configs['id']
)

        js = js.replace('"', '\"')
        return js.replace("\n", "")



    
    def create_static_line(self):
        data = ''
        index = 1
        self.configs['html_data'] = eval(self.configs['html_data'])
        for row in self.configs['html_data']['data']:
            row = str(row)
            if index == 1:
                data += '[['
            if index % 2:
                data += row + ','
            else:
                data += row + '],['
            index += 1
        data = re.sub(",\[$", "", data)
        data += ']'
        data = eval(data)
        print data
            


        js=r"""
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


        seriesOptions[0] = {{
                    name: '{name}',
                    data: {data},
                }};
        count++;
        createChart();

        function createChart() {{
            var start = new Date();
            chart = new Highcharts.StockChart({{
                chart: {{
                    zoomType: 'x ',
                    renderTo: '{id}'
                }},
                legend: {{
                    align: 'center',
                    layout: 'horizontal',
                    enabled: true,
                    verticalAlign: 'top',
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
                    selected: 1
                }},
                yAxis: {{
                    plotLines: [{{
                        value: 0,
                        width: 2,
                        color: 'silver'
                    }}]
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
    name = self.configs['html_data']['name'],
    data = data,
    id = self.configs['html_data']['id'],
)

        js = js.replace('"', '\"')
        return js.replace("\n", "")

        


#==================================  column  ================================================

    def create_static_column(self):

        self.configs['html_data'] = eval(self.configs['html_data'])
        count = len(self.configs['html_data']['name'])
        print self.configs['html_data']

        
        js=r"""
<script type='text/javascript'>

$(function () {{
        $('#{id}').highcharts({{
            chart: {{
                zoomType: 'x ',
                type: 'column'
            }},
            title: {{
                text: '{title}'
            }},
            subtitle: {{
                text: '{subtitle}'
            }},
            xAxis: {{
                categories: {x} 
            }},
            yAxis: {{
                min: 0,
                title: {{
                    text: 'Rainfall (mm)'
                }}
            }},
            tooltip: {{
                headerFormat: '<span>{{point.key}}</span><table>',
                pointFormat: '<tr><td>{{series.name}}: </td>' +
                    '<td><b>{{point.y:.1f}} mm</b></td></tr>',
                footerFormat: '</table>',
                shared: true,
                useHTML: true
            }},
            plotOptions: {{
                column: {{
                    pointPadding: 0.2,
                    borderWidth: 0
                }}
            }},
            series: [
""".format(
    id = self.configs['html_data']['id'],
    x = self.configs['html_data']['x'],
    title = self.configs['html_data']['title'],
    subtitle = self.configs['html_data']['subtitle'],
)

        for i in range(count):
            js += """
            {{
                name:'{name}',
                data:{data},
            }},
            """.format(
                name = self.configs['html_data']['name'][i],
                data = self.configs['html_data']['data'][i],
            )
        js += """
              ]
            });
           });
        </script>
        """


        js = js.replace('"', '\"')
        return js.replace("\n", "")


#============================================  pie  ===========================================

    def create_static_pie(self):
        self.configs['html_data'] = eval(self.configs['html_data'])
        print self.configs['html_data']

        js = r"""
        <script type='text/javascript'>
            $(function () {{
                var chart;
                $(document).ready(function () {{
                    $('#{id}').highcharts({{
                        chart: {{
                            zoomType: 'x ',
                            plotBackgroundColor: null,
                            plotBorderWidth: null,
                            plotShadow: false
                        }},
                        title: {{
                            text: '{title}'
                        }},
                        tooltip: {{
                    	    pointFormat: '{{series.name}}: <b></b>'
                        }},
                        plotOptions: {{
                            pie: {{
                                allowPointSelect: true,
                                cursor: 'pointer',
                                dataLabels: {{
                                    enabled: false
                                }},
                                showInLegend: true
                            }}
                        }},
                        series: [{{
                            type: 'pie',
                            name: 'description',
                            data: [
        """.format(
            id = self.configs['html_data']['id'],
            title = self.configs['html_data']['title'],
        )

        index = 0
        for row in self.configs['html_data']['data']:
            index += 1
            if index == 1:
                js += """
                            {{
                                name: '{key}',
                                y: {value},
                                sliced: true,
                                selected: true
                            }},
                """.format(
                    key = row[0],
                    value = row[1],
                )
                continue

            js += """
                                 ['{key}', {value}],
            """.format(
                key = row[0],
                value = row[1],
            )

        js = re.sub(",$", "", js)
        js += """
                                         ]
                                   }]
                               });
                           });
                       });
                   </script>
        """

        js = js.replace('"', '\"')
        return js.replace("\n", "")












       

