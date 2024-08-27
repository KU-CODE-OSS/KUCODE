<template>
  <div>
    <GChart
      type="ComboChart"
      :data="chartData"
      :options="chartOptions"
    />
  </div>
</template>

<script>
import { defineComponent } from 'vue';
import { GChart } from 'vue-google-charts';

export default defineComponent({
  name: 'DepartmentGroupBoxCharts',
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
      default: 'Box Plot Chart',
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
      default: 'department',
    },
  },
  data() {
    return {
      chartData: [],
      chartOptions: {
        width: 550,
        height: 250,
        backgroundColor: {
          fill: 'transparent',
        },
        chartArea: {
          left: 70,
          right: 70,
          top: 20,
        },
        fontSize: 12,
        hAxis: {
          gridlines: { color: 'transparent' },
          baselineColor: '#FFEAEC',
          format: 'none',
        },
        vAxis: {
          gridlines: { color: '#FFEAEC' },
          minorGridlines: {
            color: '#FFEAEC'
          },
        },
        legend: {
          position: 'bottom',
          fillOpacity: '0.5',
        },
        seriesType: 'bars',
        intervals: {
          style: 'boxes',
          boxWidth: '1.0',
          fillOpacity: '0.7',
        },
        interval: {
          median: {
            style: 'bar',
            fillOpacity: 0,
            color: 'blue',
          }
        },
        animation: {
          startup: true,
          duration: 200,
        },
        series: {
          0: {
            type: 'bars',
          },
        },
        colors: ['#EB3E7C', '#FFD1DC', '#FF5F87', '#FFADC1', '#FF85A3'],
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
          this.chartData = [['Year', { role: 'annotation' }]];
        }
      },
    },
  },
  methods: {
    updateChartData(data) {
      const chartData = [['Year']];

      const departments = [...new Set(data.map(item => item[this.groupKey]))];

      departments.forEach(department => {
        chartData[0].push(
          department,
          { id: 'min', role: 'interval' }, // Min
          { id: 'q1', role: 'interval' }, // Q1
          { id: 'median', role: 'interval' }, // Median
          { id: 'q3', role: 'interval' }, // Q3
          { id: 'max', role: 'interval' }, // Max
        );
      });

      const yearGroups = {};
      data.forEach(item => {
        for (let [year, stats] of Object.entries(item.departmentByYear)) {
          year = year === '-1' ? '기타' : year.toString();
          if (!yearGroups[year]) {
            yearGroups[year] = { year };
            departments.forEach(department => {
              yearGroups[year][department] = [null, null, null, null, null];
            });
          }

          const nestedStats = stats[this.dataKey]; // stats에서 dataKey (예: num_repos_stats)를 가져옴

          if (nestedStats) {
            yearGroups[year][item[this.groupKey]] = [
              0,  // start init point로 시작은 0이어야 함.
              nestedStats.min,
              nestedStats.q1,
              nestedStats.median,
              nestedStats.q3,
              nestedStats.max,
            ];
          }
        }
      });

      for (const year in yearGroups) {
        const row = [year];
        departments.forEach(department => {
          const courseData = yearGroups[year][department];
          if (courseData.length === 5) {
            courseData.unshift(0)
          }
          row.push(...courseData);
        });
        if (row.length !== chartData[0].length) {
          while (row.length < chartData[0].length) {
            row.push(null);
          }
        }
        console.log(row)
        chartData.push(row);
      }

      this.chartData = chartData;
    },
  },
  mounted() {
    if (this.data && this.data.length) {
      this.updateChartData(this.data);
    } else {
      this.chartData = [['Year']];
    }
  },
});
</script>
