<template>
  <div>
    <GChart
      type="LineChart"
      :data="chartData"
      :options="chartOptions"
    />
  </div>
</template>

<script>
import { defineComponent } from 'vue';
import { GChart } from 'vue-google-charts';

export default defineComponent({
  name: 'CourseGroupLineCharts',
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
      default: 'Statistics Over Years',
    },
    yAxisTitle: {
      type: String,
      default: 'Value',
    },
    dataKey: {
      type: String,
      required: true,
    },
    yearKey: {
      type: String,
      default: 'year',
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
        hAxis: {
          // title: 'Year',
          gridlines: { color: 'transparent' },
          baselineColor: '#FFEAEC',
        },
        vAxis: {
          baselineColor: '#FFEAEC',
          gridlines: { color: '#FFEAEC' },
          minorGridlines: { color: '#FFEAEC' },
        },
        legend: {
          position: 'bottom',
          fillOpacity: '0.5',
        },
        colors: ['#EB3E7C', '#FFD1DC', '#FF5F87', '#FFADC1'],
        animation: {
          startup: true,
          duration: 200,
        },
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
          this.chartData = [['Year', 'Max', 'Min', 'Mean', 'StdDev']];
        }
      },
    },
  },
  methods: {
    updateChartData(data) {
      // 차트 데이터를 헤더 행으로 초기화
      const chartData = [['Year', 'Max', 'Min', 'Mean', 'StdDev']];

      // 연도별 데이터 그룹화
      const yearGroups = {};
      data.forEach(item => {
        let year = item[this.yearKey].toString();
        if (year === '-1') {
          year = '기타';
        }
        if (!yearGroups[year]) {
          yearGroups[year] = { year };
        }
        const stats = item[this.dataKey];
        yearGroups[year] = [stats.max, stats.min, parseFloat(stats.mean), parseFloat(stats.stdDev)];
      });

      // 차트 데이터 행 채우기
      for (const year in yearGroups) {
        const row = [year, ...yearGroups[year]];
        chartData.push(row);
      }

      this.chartData = chartData;
    },
  },
  mounted() {
    if (this.data && this.data.length) {
      this.updateChartData(this.data);
    } else {
      this.chartData = [['Year', 'Max', 'Min', 'Mean', 'StdDev']];
    }
  },
});
</script>

<style scoped>
/* 스타일을 여기에 추가할 수 있습니다 */
</style>
