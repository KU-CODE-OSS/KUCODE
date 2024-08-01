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
            text: '학번별 평균 Commit 수',
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
            name: 'Average Commit',
            type: 'bar',
            barWidth: '50%',
            data: [],
            emphasis: {
              itemStyle: {
                borderRadius: [5, 5, 0, 0]
              }
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
      const idCommitMap = data.reduce((acc, course) => {
        const id = course.id.slice(2, 4); // 학번의 3,4번째 자리 추출
        if (!acc[id]) {
          acc[id] = { sum: 0, count: 0 };
        }
        acc[id].sum += course.commit;
        acc[id].count += 1;
        return acc;
      }, {});

      const ids = Object.keys(idCommitMap).sort();
      const avgCommits = ids.map(id => (idCommitMap[id].sum / idCommitMap[id].count).toFixed(2));

      this.option.xAxis[0].data = ids;
      this.option.series[0].data = avgCommits;
    }
  },
  mounted() {
    this.fetchCourseInfo();
  },
};
</script>
