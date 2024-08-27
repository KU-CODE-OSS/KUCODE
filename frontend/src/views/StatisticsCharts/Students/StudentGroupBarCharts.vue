<template>
  <div>
    <GChart
      type="ColumnChart"
      :data="chartData"
      :options="chartOptions"
    />
  </div>
</template>

<script>
import { defineComponent } from 'vue';
import { GChart } from 'vue-google-charts';

export default defineComponent({
  name: 'StudentGroupBarCharts',
  components: {
    GChart,
  },
  props: {
    data: {
      type: Array,
      required: true,
    },
    chartTitle: {
      type: String,
      default: 'Chart Title',
    },
    yAxisTitle: {
      type: String,
      default: 'Value',
    },
    dataKey: {
      type: String,
      required: true,
    },
    groupKey: {
      type: String,
      default: 'year',
    },
    titleFontSize: {
      type: Number,
      default: 16,
    },
    titleFontWeight: {
      type: String,
      default: 'bold',
    },
  },
  data() {
    return {
      chartData: [],
      chartOptions: {
        width: 550,
        height: 250,
        backgroundColor: {
          fill:'transparent'
        },
        chartArea: {
          left: 70,
          right: 70,
          top: 20,
        },
        fontSize: 12,
        // title: this.chartTitle,
        // titleTextStyle: {
        //   fontName: "sans-serif",
        //   fontSize: this.titleFontSize,
        //   fontWeight: this.titleFontWeight,
        //   bold: true,
        //   italic: false
        // },
        hAxis: {
          gridlines: { color: 'transparent' }, // x축 그리드 제거
          ticks: [], // 이후에 데이터에 있는 연도들로 설정
          baselineColor: '#FFEAEC',
          format: 'none',
        },
        vAxis: {
          // title: this.yAxisTitle,
          baselineColor: '#FFEAEC',
          viewWindow: { max: 100 },
          gridlines: { color: '#FFEAEC' },
          minorGridlines: {
            color: '#FFEAEC'
          },
        },
        legend: {
          position: 'bottom', // legend를 차트 아래로 위치
        },
        colors: ['#EB3E7C', '#FF5F87', '#FF85A3', '#FFADC1', '#FFD1DC'],
        animation: {
          startup: true,
          duration: 200,
        },
        bar: {
          groupWidth: 100,
          gap: 10,
        },
        annotations: {
          boxStyle: {
            // Color of the box outline.
            stroke: '#888',
            // Thickness of the box outline.
            strokeWidth: 1,
            // x-radius of the corner curvature.
            rx: 10,
            // y-radius of the corner curvature.
            ry: 10,
            // Attributes for linear gradient fill.
            gradient: {
              x1: '0%', y1: '0%',
              x2: '100%', y2: '100%',
              // If true, the boundary for x1,
              // y1, x2, and y2 is the box. If
              // false, it's the entire chart.
              useObjectBoundingBoxUnits: true
            }
          }
        }
      },
    };
  },
  watch: {
    data: {
      deep: true,
      handler(newVal) {
        if (newVal && newVal.length) {
          this.updateChartData(newVal);
        } else {
          // 데이터가 없을 경우 최근 연도로 기본 설정
          const recentYear = new Date().getFullYear();
          this.chartData = [['Group', ''], ['', 0]];
          this.chartOptions.hAxis.ticks = [recentYear.toString()];
          this.chartOptions.vAxis.viewWindow.max = 100; // 기본 Y축 범위
        }
      },
    },
  },
  methods: {
    updateChartData(data) {
      if (!data || data.length === 0) {
        // 데이터가 없을 경우 최근 연도로 기본 설정
        const recentYear = new Date().getFullYear();
        this.chartData = [['Group', ''], ['', 0]];
        this.chartOptions.hAxis.ticks = [recentYear.toString()];
        return;
      }

      let groups = [...new Set(data.map(item => {
        const groupValue = item[this.groupKey];
        return groupValue === '-1' ? '기타' : groupValue.toString(); // 모든 값을 문자열로 변환
      }))].sort((a, b) => {
        if (a === '기타') return 1; // '기타'는 마지막으로
        if (b === '기타') return -1;
        return b.localeCompare(a); // 문자열 비교로 내림차순 정렬
      });
      
      const courses = [...new Set(data.map(item => item.course_name))];

      const chartData = [['Group', ...courses]];
      let maxValue = 0;

      groups.forEach(group => {
        const row = [group];
        courses.forEach(courseName => {
          const course = data.find(item => {
            const itemGroup = item[this.groupKey] === '-1' ? '기타' : item[this.groupKey].toString();
            return itemGroup === group && item.course_name === courseName;
          });

          let value = 0;

          if (course) {
            const dataItem = course[this.dataKey];
            if (Array.isArray(dataItem)) {
              value = dataItem.reduce((a, b) => a + b, 0);
            } else if (typeof dataItem === 'object') {
              value = dataItem.sum;
            } else {
              value = dataItem;
            }
          }

          row.push(value);
          if (value > maxValue) {
            maxValue = value;
          }
        });
        chartData.push(row);
      });

      // 불필요한 축 값 제거
      if (groups.length === 1) {
        this.chartOptions.hAxis.textPosition = 'out';
        this.chartOptions.vAxis.textPosition = 'out';
      } else {
        this.chartOptions.hAxis.textPosition = 'out';
        this.chartOptions.vAxis.textPosition = 'out';
        this.chartOptions.hAxis.ticks = groups; // x축에 연도만 표시 (기타 포함)
      }

      this.chartOptions.vAxis.viewWindow.max = maxValue * 1;
      this.chartData = chartData;
    },
  },
  mounted() {
    if (this.data && this.data.length) {
      this.updateChartData(this.data);
    } else {
      // 데이터가 없을 경우 최근 연도로 기본 설정
      const recentYear = new Date().getFullYear();
      this.chartData = [['Group', ''], ['', 0]];
      this.chartOptions.hAxis.ticks = [recentYear.toString()];
    }
  },
});
</script>
