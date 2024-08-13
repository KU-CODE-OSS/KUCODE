<template>
  <div class="container">
    <div class="navigation">
      <div class="menu">
        <router-link v-bind:to="'/statistics/course'" class="default-router plan-text" append>과목</router-link>
      </div>
      <div class="menu">
        <div class="default-router plan-text current-tab">학생</div>
      </div>
      <div class="menu">
        <router-link v-bind:to="'/statistics/repos'" class="default-router plan-text" append>레포지토리</router-link>
      </div>
      <div class="search-box">
      <div class="form__group field">
        <input type="input" class="form-field" :value="searchField" />
        <label class="form__label">SEARCH</label>
      </div>
      </div>
      <div class="toggle-box" @click.self.prevent="toggle">
        <div class="wrapper">
          <input type="checkbox" id="switch" v-model="showTable">
          <label for="switch" class="switch_label">
            <span class="onf_btn"></span>
            <div class="toggle_img">
                <div class="img1">
                    <svg class="toggle-image-1" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <g id="Huge-icon">
                            <path id="Vector" d="M10 6H16M10 14H16M10 10H22M10 18H22M3 10H5C5.55228 10 6 9.55228 6 9V7C6 6.44772 5.55228 6 5 6H3C2.44772 6 2 6.44772 2 7V9C2 9.55228 2.44772 10 3 10ZM3 18H5C5.55228 18 6 17.5523 6 17V15C6 14.4477 5.55228 14 5 14H3C2.44772 14 2 14.4477 2 15V17C2 17.5523 2.44772 18 3 18Z"  stroke-width="1.5" stroke-linecap="round"/>
                        </g>
                    </svg>
                </div>
                <div class="img2">
                    <svg class="toggle-image-2" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none">
                        <path d="M8 14L9.08225 12.1963C9.72077 11.132 11.2247 11.0309 12 12C12.7753 12.9691 14.2792 12.8679 14.9178 11.8037L16 10M12 18V22M4 6H20C21.1046 6 22 5.10457 22 4C22 2.89543 21.1046 2 20 2H4C2.89543 2 2 2.89543 2 4C2 5.10457 2.89543 6 4 6ZM3 6H21V16C21 17.1046 20.1046 18 19 18H5C3.89543 18 3 17.1046 3 16V6Z" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
            </div>
          </label>
        </div>
      </div>
    </div>
    <div class="navigation_underline"></div>
    <div class="contents-box">
      <transition name="slide-fade" mode="out-in">
        <div v-if="!showTable" class="table"> <IdCommitAvg/></div>
        <div v-else class="chart">
          <div class="year-chart-container">
            <div class="chart-title">연도별 데이터</div>
            <div class="charts">
              <div class="chart-container">
                <YearCommit/>
              </div>
              <div class="chart-container">
                <YearAll/>
              </div>
              <div class="chart-container">
                <YearPr/>
              </div>
              <div class="chart-container">
                <DepartCommit/>
              </div>
              <div class="chart-container">
                <IdCommit/>
              </div>
            </div>
          </div>
          <div class="category-chart-container">
            <div class="chart-title">카테고리별 상세 데이터</div>
          </div>
        </div>
      </transition>
    </div>
    <!-- portal-target을 여기로 이동 -->
    <!-- <portal-target name="stat_chart_user"></portal-target> -->
  </div>
</template>

<script>
import BarChart1 from '../StudentCharts/BarCharts1.vue';
import BarChart2 from '../StudentCharts/BarCharts2.vue';
import BarChart3 from '../StudentCharts/BarCharts3.vue';
import BarChart4 from '../StudentCharts/BarCharts4.vue';
import chart_user from './chart/chart_user.vue';
import TableUser from './table/table_user.vue';
import YearCommit from './chart/year_commit.vue';
import YearIssue from './chart/year_issue.vue';
import YearPr from './chart/year_pr.vue';
import DepartCommit from './chart/depart_commit.vue';
import IdCommit from './chart/id_commit.vue';
import IdCommitAvg from './chart/id_commit_avg.vue';
import YearAll from './chart/x-year_y-all_.vue';


export default {
  name: 'StatisticsStudent',
  components: {
    BarChart1,
    BarChart2,
    BarChart3,
    BarChart4,
    TableUser,
    chart_user,
    YearCommit,
    YearIssue,
    YearPr,
    DepartCommit,
    IdCommit,
    IdCommitAvg,
    YearAll,


  },
  data() {
    return {
      option: {
        textStyle: {
          fontFamily: 'Inter, "Helvetica Neue", Arial, sans-serif',
        },
        title: {
          text: 'Traffic Sources',
          left: 'center',
        },
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b} : {c} ({d}%)',
        },
        legend: {
          orient: 'vertical',
          left: 'left',
          data: [
            'Direct',
            'Email',
            'Ad Networks',
            'Video Ads',
            'Search Engines',
          ],
        },
        series: [
          {
            name: 'Traffic Sources',
            type: 'pie',
            radius: '55%',
            center: ['50%', '60%'],
            data: [
              { value: 335, name: 'Direct' },
              { value: 310, name: 'Email' },
              { value: 234, name: 'Ad Networks' },
              { value: 135, name: 'Video Ads' },
              { value: 1548, name: 'Search Engines' },
            ],
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)',
              },
            },
          },
        ],
      },
      showTable: false,
      searchField: '',
    };
  },
  methods: {
    toggle() {
      this.showTable = !this.showTable;
    },
  },
};
</script>

<style scoped>
.container {
  max-width: 1600px;
}

.navigation {
  min-height: 41px;
  padding-left: 56px;
  padding-right: 56px;
  display: flex;
  align-items: center;
}

.menu {
  width: 101px;
  margin-right: 30px !important;
  font-size: 18px;
  align-items: center;
  text-align: center;
}

.plan-text {
  margin: 0 auto;
  line-height: 41px;
}

.current-tab {
  color: #862633 !important;
  border-bottom: solid 4px #862633;
}

.contents-box {
  padding: 0 56px;
}

.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.2s cubic-bezier(1, 0.5, 0.8, 1);
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateX(50px);
  opacity: 0;
}

.search-box {
  min-height: 44px;
  margin-left: auto;
  align-self: flex-end;
  padding-bottom: 4px;
  margin-right: 26px;
}

.form__group {
  position: relative;
  width: 100%;
}

.form-field {
  font-family: inherit;
  width: 230px;
  height: 40px;
  border: 0;
  border-bottom: 2px solid #9b9b9b;
  outline: 0;
  color: #86263300;
  padding: 1px 0;
  background: transparent;
  transition: border-bottom 0.2s ease-in-out;
  transition: border-image 0.2s ease-in-out;
  font-size: 1.1rem;
}

.form-field::placeholder {
  color: transparent;
}

.form-field:placeholder-shown ~ .form__label {
  font-size: 1.0rem;
  cursor: text;
}

.form__label {
  position: absolute;
  top: 5px;
  display: block;
  transition: 0.2s;
  color: #9b9b9b;
  font-size: 1.3rem;
  pointer-events: none;
}

.form-field:focus ~ .form__label {
  position: absolute;
  top: -25px;
  display: block;
  transition: 0.2s;
  font-size: 1rem;
  color: #CB385C;
  font-weight: 700;
}

.form-field:focus {
  padding-bottom: 6px;
  font-weight: 700;
  border-width: 3px;
  border-image: linear-gradient(to right, #CB385C, #FFF4F5);
  transition: opacity 1s;
  border-image-slice: 1;
  color: #862633;
}

.form-field:focus::before, .form-field:focus::after {
  transition: 0.2s ease-in-out;
}

/* reset input */
.form-field:required,
.form-field:invalid {
  box-shadow: none;
}

.toggle-box .wrapper {
  width: 150px;
  height: 44px;
  text-align: center;
  margin: 0 auto;
  position: relative;
}

#switch {
  display: none;
}

.switch_label {
  position: relative;
  cursor: pointer;
  display: inline-block;
  width: 150px;
  height: 41px;
  background: #ffe2e5;
  border-radius: 20px;
  transition: 0.4s;
}

.onf_btn {
  position: absolute;
  top: 4px;
  left: 3px;
  width: 75px;
  height: 33px;
  border-radius: 20px;
  background: white;
  transition: 0.2s;
  box-shadow: 1px 2px 3px #00000020;
}

.toggle_img {
  position: absolute;
  line-height: 41px;
  height: 41px;
  width: 150px;
  display: flex;
  justify-content: flex-start;
  vertical-align: middle;
  padding: 6px 26px;
}

.toggle_img svg {
  width: 29px;
  height: 29px;
}

.toggle_img .img1 .toggle-image-1 path,
.toggle_img .img2 .toggle-image-2 path {
  transition: 0.2s;
}

.toggle_img .img1 .toggle-image-1 path {
  stroke: #CB385C;
}

.toggle_img .img2 .toggle-image-2 path {
  stroke: #E9D8D9;
}

.img1 {
  margin-right: auto;
}

#switch:checked + .switch_label .onf_btn {
  left: 70px;
  background: #fff;
  box-shadow: 1px 2px 3px #00000020;
}

#switch:checked + .switch_label .toggle-image-1 path {
  stroke: #E9D8D9;
}

#switch:checked + .switch_label .toggle-image-2 path {
  stroke: #CB385C;
}

.navigation_underline {
  border-bottom: solid 2px #dce2ed;
  width: calc(1600px + 320px) !important;
}

.table,
.chart {
  margin: 20px 0;
  padding: 20px 0;
  border: 1px solid #dce2ed;
  border-radius: 4px;
  height: 100%;
}

.chart .year-chart-container {}

.chart .category-chart-container {
  margin-top: 60px;
}

.chart .chart-title {
  font-size: 22px;
  font-weight: 700;
  margin: 0 0 30px 0;
}

.chart .charts {
  display: flex;
  min-height: 300px;
  justify-content: space-between;
}

.chart .chart-container {
  width: 330px;
}
</style>
