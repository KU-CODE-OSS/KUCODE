<template>
    <v-chart :option="option" class="echarts"/>
</template>

<style scoped>
.echarts {
  width: 330px;
  height: 330px;
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

import { getCourseInfo } from '@/api.js'

export default {
  name: 'BarChart1',
  components: {
    'v-chart': ECharts
  },
  data () {
    return {
      option : {
        title: {
            text: '연도별 총 commit 수',
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
            data: [],
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
            name: 'Total Commit',
            type: 'bar',
            barWidth: '50%',
            data: [],
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
    async fetchCourseInfo() {
      try {
        const response = await getCourseInfo();
        const data = response.data; // 데이터가 response.data에 있다고 가정
        this.processData(data);
      } catch (error) {
        console.error("Error fetching course info:", error);
      }
    },
    processData(data) {
      const yearCommitMap = data.reduce((acc, course) => {
        const year = course.year;
        if (!year) return acc;
        if (!acc[year]) {
          acc[year] = 0;
        }
        acc[year] += course.commit;
        return acc;
      }, {});

      const years = Object.keys(yearCommitMap).sort();
      const commits = years.map(year => yearCommitMap[year]);

      this.option.xAxis[0].data = years;
      this.option.series[0].data = commits;
    }
  },
  mounted() {
    this.fetchCourseInfo();
  },
};
</script>
