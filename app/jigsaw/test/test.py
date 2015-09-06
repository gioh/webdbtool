import sys
sys.path.insert(0, '../../')


from jigsaw.stockchart import Stockchart

charts = Stockchart(
    width = 200,
    heigth = 400,
    appid = 1
)

print charts.create()
