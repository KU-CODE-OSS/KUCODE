<template>
  <v-chart :option="option" class="echarts" @legendselectchanged="toggleSeries" />
</template>

<style scoped>
.echarts {
  width: 600px; 
  height: 400px;
}
</style>

<script>
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
  components: {
    'v-chart': ECharts
  },
  data () {
    return {
      option : {
        title: {
            text: '연도별 개발 활동',
            textStyle: {
                fontSize: '20'
            },
            top: '20',
            left: 'center',
        },
        color: ['#E16785', '#67E1E0', '#E1E167', '#6767E1'],  // 각 데이터 시리즈의 색상
        backgroundColor: '#FFFBFB',
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        legend: {
          data: ['Commit', 'Issue', 'PR', 'Star'],
          selected: {
            'Commit': true,
            'Issue': true,
            'PR': true,
            'Star': true
          }
        },
        toolbox: {
          show: true,
          orient: 'vertical',
          left: 'right',
          top: 'center',
          feature: {
            mark: { show: true },
            dataView: { show: true, readOnly: false },
            magicType: { show: true, type: ['line', 'bar', 'stack'] },
            restore: { show: true },
            saveAsImage: { show: true }
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
            data: [], // 연도 데이터
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
            name: 'Commit',
            type: 'bar',
            barWidth: '15%',
            data: [], // 커밋 수 데이터
            emphasis: {
              itemStyle: {
                    borderRadius: [5, 5]
                },
                borderRadius: [5, 5, 0, 0]
            }
          },
          {
            name: 'Issue',
            type: 'bar',
            barWidth: '15%',
            data: [], // 이슈 수 데이터
            emphasis: {
              itemStyle: {
                    borderRadius: [5, 5]
                },
                borderRadius: [5, 5, 0, 0]
            }
          },
          {
            name: 'PR',
            type: 'bar',
            barWidth: '15%',
            data: [], // PR 수 데이터
            emphasis: {
              itemStyle: {
                    borderRadius: [5, 5]
                },
                borderRadius: [5, 5, 0, 0]
            }
          },
          {
            name: 'Star',
            type: 'bar',
            barWidth: '15%',
            data: [], // Star 수 데이터
            emphasis: {
              itemStyle: {
                    borderRadius: [5, 5]
                },
                borderRadius: [5, 5, 0, 0]
            }
          }
        ]
      }
    }
  },
  methods: {
    fetchCourseInfo() {
      // 임시 데이터
      const mockData = [
        { year: '2017', commit: 120, issue: 80, pr: 50, star: 200 },
        { year: '2018', commit: 132, issue: 90, pr: 70, star: 250 },
        { year: '2019', commit: 101, issue: 60, pr: 80, star: 300 },
        { year: '2020', commit: 134, issue: 110, pr: 90, star: 400 },
        { year: '2021', commit: 90, issue: 70, pr: 60, star: 350 }
      ];
      this.processData(mockData);
    },
    processData(data) {
      const years = data.map(item => item.year);
      const commits = data.map(item => item.commit);
      const issues = data.map(item => item.issue);
      const prs = data.map(item => item.pr);
      const stars = data.map(item => item.star);

      this.option.xAxis[0].data = years;
      this.option.series[0].data = commits;
      this.option.series[1].data = issues;
      this.option.series[2].data = prs;
      this.option.series[3].data = stars;
    },
    toggleSeries(params) {
      // params.selected 상태를 그대로 반영하여 옵션을 다시 설정
      this.option.legend.selected = params.selected;
      this.$refs.chartComponent.setOption(this.option, false);  // 현재 옵션을 업데이트
    }
  },
  mounted() {
    this.fetchCourseInfo();
  }
}
</script>
