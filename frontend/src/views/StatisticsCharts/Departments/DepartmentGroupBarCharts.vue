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
    name: 'DepartmentGroupBarCharts',
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
            fill: 'transparent'
          },
          chartArea: {
            left: 70,
            right: 70,
            top: 20,
          },
          fontSize: 12,
          hAxis: {
            gridlines: { color: 'transparent' },
            ticks: [],
            baselineColor: '#FFEAEC',
            format: 'none',
          },
          vAxis: {
            baselineColor: '#FFEAEC',
            viewWindow: { max: 100 },
            gridlines: { color: '#FFEAEC' },
            minorGridlines: {
              color: '#FFEAEC'
            },
          },
          legend: {
            position: 'bottom',
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
              stroke: '#888',
              strokeWidth: 1,
              rx: 10,
              ry: 10,
              gradient: {
                x1: '0%', y1: '0%',
                x2: '100%', y2: '100%',
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
            const recentYear = new Date().getFullYear();
            this.chartData = [['Group', ''], ['', 0]];
            this.chartOptions.hAxis.ticks = [recentYear.toString()];
            this.chartOptions.vAxis.viewWindow.max = 100;
          }
        },
      },
    },
    methods: {
        updateChartData(data) {
    if (!data || data.length === 0) {
      const recentYear = new Date().getFullYear();
      this.chartData = [['Group', ''], ['', 0]];
      this.chartOptions.hAxis.ticks = [recentYear.toString()];
      return;
    }

    // 연도 키를 추출하고 '-1'을 '기타'로 변환하여 정렬
    const yearsSet = new Set();
    data.forEach(item => {
      Object.keys(item.departmentByYear).forEach(year => {
        const formattedYear = year === '-1' ? '기타' : year;
        yearsSet.add(formattedYear);
      });
    });
    const years = Array.from(yearsSet).sort((a, b) => {
      if (a === '기타') return 1;
      if (b === '기타') return -1;
      return a - b;
    });

    // 부서 이름들을 추출
    const departments = data.map(item => item.department);

    const chartData = [['Year', ...departments]];
    let maxValue = 0;

    years.forEach(year => {
      const row = [year];
      departments.forEach(department => {
        const departmentData = data.find(item => item.department === department);
        let value = 0;

        if (departmentData) {
          const originalYearKey = year === '기타' ? '-1' : year;
          const yearData = departmentData.departmentByYear[originalYearKey];

          if (yearData) {
            const keys = this.dataKey.split('.');
            let nestedValue = yearData;
            for (const key of keys) {
              if (nestedValue[key] !== undefined) {
                nestedValue = nestedValue[key];
              } else {
                nestedValue = 0;
                break;
              }
            }
            value = nestedValue;
          }
        }

        row.push(value);
        if (value > maxValue) {
          maxValue = value;
        }
      });
      chartData.push(row);
    });

    this.chartOptions.hAxis.ticks = years;
    this.chartOptions.vAxis.viewWindow.max = maxValue * 1.1 || 100;
    this.chartData = chartData;
  },
    },
    mounted() {
      if (this.data && this.data.length) {
        this.updateChartData(this.data);
      } else {
        const recentYear = new Date().getFullYear();
        this.chartData = [['Group', ''], ['', 0]];
        this.chartOptions.hAxis.ticks = [recentYear.toString()];
      }
    },
  });
  </script>
  