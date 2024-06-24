<template>
    <div ref="chart" style="width: 100%; height: 500px;"></div>
  </template>
  
  <script>
  import * as echarts from 'echarts';
  
  export default {
    name: 'chart_user',
    props: {
        totalCommitsByCourse: {
            type: Object,
            required: true
        },
        totalPRByCourse: {
            type: Object,
            required: true
        },
        totalIssueByCourse: {
            type: Object,
            required: true
        },
        totalRepoByCourse: {
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
  
          // totalCommitsByCourse, totalPRByCourse, totalIssueByCourse, totalRepoByCourse에서 데이터를 추출하여 차트에 사용
          const categories = Object.keys(this.totalCommitsByCourse);
          const commitData = categories.map(category => this.totalCommitsByCourse[category]);
          const prData = categories.map(category => this.totalPRByCourse[category]);
          const issueData = categories.map(category => this.totalIssueByCourse[category]);
          const repoData = categories.map(category => this.totalRepoByCourse[category]);
  
          const option = {
            tooltip: {
              trigger: 'axis',
              axisPointer: { type: 'shadow' }
            },
            legend: {
              data: ['Total Commits', 'Total PR', 'Total Issues', 'Total Repos']
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
                name: 'Total Commits',
                type: 'bar',
                barGap: 0,
                label: labelOption,
                emphasis: { focus: 'series' },
                data: commitData
              },
              {
                name: 'Total PR',
                type: 'bar',
                label: labelOption,
                emphasis: { focus: 'series' },
                data: prData
              },
              {
                name: 'Total Issues',
                type: 'bar',
                label: labelOption,
                emphasis: { focus: 'series' },
                data: issueData
              },
              {
                name: 'Total Repos',
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
  