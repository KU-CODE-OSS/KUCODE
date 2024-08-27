<template>
    <v-chart :option="option"/>
</template>

<style>

.echarts {
  width: 280px;
  height: 280px;
}
</style>

<script>
// import Vue from 'vue'
import ECharts from 'vue-echarts'
import 'echarts-gl'
import { use } from "echarts/core";


import { LineChart, BarChart, ScatterChart, EffectScatterChart } from 'echarts/charts'
import { GridComponent, TitleComponent, TooltipComponent, LegendComponent, DataZoomComponent, ToolboxComponent } from 'echarts/components'
import { UniversalTransition } from 'echarts/features'
import { CanvasRenderer } from 'echarts/renderers'
use([
    CanvasRenderer,
    TitleComponent,
    LineChart,
    BarChart,
    ScatterChart,
    GridComponent,
    TooltipComponent,
    EffectScatterChart,
    UniversalTransition,
    LegendComponent,
    DataZoomComponent,
    ToolboxComponent,
  ])

export default {
  name: 'BarChart1',
  props: ["data"],
  components: {
    'v-chart': ECharts
  },
  data () {
    return {
      option : {
        title: {
            text: '연도별 Score',
            textStyle: {
                fontSize: '20'
            },
            top: '20',
            left: '10%',
        },
        color: '#E16785',
        backgroundColor: '#FFFBFB',
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        grid: {
          left: '10%',
          right: '10%',
          bottom: '40',
          top: '100',
          containLabel: true,
        },
        xAxis: [
          {
            type: 'category',
            data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            axisLabel: {
                fontWeight: '700'
            },
            axisTick: {
              alignWithLabel: true,
              lineStyle: {
                color: '#FFC093'
              }
            },
          }
        ],
        yAxis: [
          {
            type: 'value',
            splitLine: {
                lineStyle: {
                    color: [
                        '#FFC093'
                    ]
                }
            },
            axisLabel: {
                fontWeight: '700'
            },
          }
        ],
        series: [
          {
            name: 'Direct',
            type: 'bar',
            barWidth: '50%',
            data: [10, 52, 200, 334, 390, 330, 220],
            itemStyle: {
                emphasis: {
                    barBorderRadius: [5, 5]
                },
                normal: {
                    barBorderRadius: [5, 5, 0, 0]
                }
            }
          }
        ]
      }
    }
  }
}
</script>