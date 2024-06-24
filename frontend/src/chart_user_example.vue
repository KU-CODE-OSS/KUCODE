<template>
  <div ref="chart" style="width: 100%; height: 500px;"></div>
</template>

<script>
import * as echarts from 'echarts';

export default {
  name: 'MyChart',
  props: {
    averageCommitsByCourse: {
      type: Object,
      required: true
    },
    averagePRByCourse: {
      type: Object,
      required: true
    },
    averageIssueByCourse: {
      type: Object,
      required: true
    },
    averageRepoByCourse: {
      type: Object,
      required: true
    }
  },
  mounted() {
    this.initChart();
  },
  methods: {
    initChart() {
      if (this.$refs.chart) {
        const chart = echarts.init(this.$refs.chart);
        const posList = [
          'left', 'right', 'top', 'bottom', 'inside', 'insideTop', 'insideLeft', 'insideRight', 'insideBottom',
          'insideTopLeft', 'insideTopRight', 'insideBottomLeft', 'insideBottomRight'
        ];
        const app = {};
        app.configParameters = {
          rotate: { min: -90, max: 90 },
          align: { options: { left: 'left', center: 'center', right: 'right' } },
          verticalAlign: { options: { top: 'top', middle: 'middle', bottom: 'bottom' } },
          position: {
            options: posList.reduce(function (map, pos) {
              map[pos] = pos;
              return map;
            }, {})
          },
          distance: { min: 0, max: 100 }
        };
        app.config = {
          rotate: 90,
          align: 'left',
          verticalAlign: 'middle',
          position: 'insideBottom',
          distance: 15,
          onChange: function () {
            const labelOption = {
              rotate: app.config.rotate,
              align: app.config.align,
              verticalAlign: app.config.verticalAlign,
              position: app.config.position,
              distance: app.config.distance
            };
            chart.setOption({
              series: [
                { label: labelOption },
                { label: labelOption },
                { label: labelOption },
                { label: labelOption }
              ]
            });
          }
        };
        const labelOption = {
          show: true,
          position: app.config.position,
          distance: app.config.distance,
          align: app.config.align,
          verticalAlign: app.config.verticalAlign,
          rotate: app.config.rotate,
          formatter: '{c}  {name|{a}}',
          fontSize: 16,
          rich: { name: {} }
        };

        // averageCommitsByCourse, averagePRByCourse, averageIssueByCourse, averageRepoByCourse에서 데이터를 추출하여 차트에 사용
        const categories = Object.keys(this.averageCommitsByCourse);
        const commitData = categories.map(category => this.averageCommitsByCourse[category]);
        const prData = categories.map(category => this.averagePRByCourse[category]);
        const issueData = categories.map(category => this.averageIssueByCourse[category]);
        const repoData = categories.map(category => this.averageRepoByCourse[category]);

        const option = {
          tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'shadow' }
          },
          legend: {
            data: ['Average Commits', 'Average PR', 'Average Issues', 'Average Repos']
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
          xAxis: [
            {
              type: 'category',
              axisTick: { show: false },
              data: categories
            }
          ],
          yAxis: [
            {
              type: 'value'
            }
          ],
          series: [
            {
              name: 'Average Commits',
              type: 'bar',
              barGap: 0,
              label: labelOption,
              emphasis: { focus: 'series' },
              data: commitData
            },
            {
              name: 'Average PR',
              type: 'bar',
              label: labelOption,
              emphasis: { focus: 'series' },
              data: prData
            },
            {
              name: 'Average Issues',
              type: 'bar',
              label: labelOption,
              emphasis: { focus: 'series' },
              data: issueData
            },
            {
              name: 'Average Repos',
              type: 'bar',
              label: labelOption,
              emphasis: { focus: 'series' },
              data: repoData
            }
          ]
        };
        chart.setOption(option);

        window.addEventListener('resize', () => {
          if (chart) {
            chart.resize();
          }
        });
      } else {
        console.error('Chart DOM element not found.');
      }
    }
  }
};
</script>

<style scoped>
</style>
