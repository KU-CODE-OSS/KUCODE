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
import { getCourseStudentInfo } from '@/api.js';

export default defineComponent({
  name: 'CourseGroupStudentBarCharts',
  components: {
    GChart,
  },
  props: {
    courseId: {
      type: String,
      required: true,
    },
    chartTitle: {
      type: String,
      default: 'Student Count by Department',
    },
    yAxisTitle: {
      type: String,
      default: 'Number of Students',
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
        },
        vAxis: {
          baselineColor: '#FFEAEC',
          gridlines: { color: '#FFEAEC' },
          minorGridlines: { color: '#FFEAEC' },
          minValue: 0,  // 최소값을 0으로 설정
        },
        bar: {
          // groupWidth: 100,
          // gap: 10,
        },
        legend: {
          position: 'bottom',
          fillOpacity: '0.5',
        },
        colors: ['#EB3E7C', '#FFD1DC', '#FF5F87', '#FFADC1', '#FF85A3'],
        animation: {
          startup: true,
          duration: 200,
        },
      },
    };
  },
  methods: {
    async updateChartData() {
      try {
        getCourseStudentInfo().then(res => {
          const allCourseData = res.data;
          const courseData = allCourseData.find(course => course.course_id === this.courseId);

          if (courseData) {
            const chartData = [['Year', ...Object.keys(courseData.department_count)]];

            // 데이터를 연도별로 정리
            const row = [courseData.year.toString()];

            Object.values(courseData.department_count).forEach(count => {
              row.push(count || 0);  // 데이터가 없을 경우 0으로 대체
            });

            chartData.push(row);
            console.log('row', row);
            this.chartData = chartData;
          } else {
            this.chartData = [['Year']];
          }
        });
      } catch (error) {
        console.error('Error fetching course info:', error);
      }
    },
  },
  watch: {
    courseId: {
      immediate: true,
      handler(newVal) {
        if (newVal) {
          console.log('newval is ', newVal);
          this.updateChartData();
        }
      },
    },
  },
  mounted() {
    if (this.courseId) {
      this.updateChartData();
    }
  },
});
</script>

<style scoped>
/* 스타일을 여기에 추가할 수 있습니다 */
</style>
