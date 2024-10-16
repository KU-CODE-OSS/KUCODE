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
  name: 'StudentGroupBoxCharts',
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
      default: 'course_name',
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
          fill: 'transparent',
        },
        chartArea: {
          left: 70,
          right: 70,
          top: 20,
        },
        fontSize: 12,
        hAxis: {
          gridlines: { color: 'transparent' }, // x축 그리드 제거
          baselineColor: '#FFEAEC',
          format: 'none',
        },
        vAxis: {
          // title: this.yAxisTitle,
          gridlines: { color: '#FFEAEC' },
          minorGridlines: {
            color: '#FFEAEC'
          },
        },
        legend: {
          position: 'bottom', // legend를 차트 아래로 위치
          fillOpacity: '0.5',
        },
        seriesType: 'bars',
        intervals: {
          style: 'boxes',
          boxWidth: '1',
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
      // 차트 데이터를 헤더 행으로 초기화
      const chartData = [['Year']];
      
      const courses = [...new Set(data.map(item => item[this.groupKey]))];

      // 각 과목에 대해 과목 이름과 5개의 interval 역할을 위한 열을 추가
      courses.forEach(course => {
        chartData[0].push(
          course,
          { id: 'min', role: 'interval' }, // Min
          { id: 'q1', role: 'interval' }, // Q1
          { id: 'median', role: 'interval' }, // Median
          { id: 'q3', role: 'interval' }, // Q3
          { id: 'max', role: 'interval' }, // Max
        );
      });

      const yearGroups = {};
      data.forEach(item => {
        let year = item[this.yearKey].toString();
        if (year === '-1') {
          year = '기타';
        }
        if (!yearGroups[year]) {
          yearGroups[year] = { year };
          courses.forEach(course => {
            yearGroups[year][course] = [null, null, null, null, null]; 
          });
        }
        const stats = item[this.dataKey];
        // 해당 연도 그룹 내 특정 과목에 대해 값 할당
        yearGroups[year][item[this.groupKey]] = [
          0,  // start init point로 시작은 0이어야 함.
          stats.min, 
          stats.q1,
          stats.median,
          stats.q3, 
          stats.max
        ];
      });

      // 차트 데이터 행 채우기
      for (const year in yearGroups) {
        const row = [year];
        courses.forEach(course => {
          // 각 과목 항목에 5개의 요소(min, q1, median, q3, max)가 있는지 확인
          const courseData = yearGroups[year][course];
          if (courseData.length === 5) {
            courseData.unshift(0)
          }
          row.push(...courseData);
        });
        // 행의 열 수가 올바른지 확인
        if (row.length !== chartData[0].length) {
          console.error(`연도 ${year}에 대한 행에 ${row.length}개의 열이 있으며, ${chartData[0].length}개가 필요함`);
          // 누락된 열을 null로 채우기
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
