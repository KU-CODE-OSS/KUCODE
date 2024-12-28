
<template>
  <div class="container" :class="{ cursorblock: pannelLoading === true }">
    <div class="navigation">
      <div class="menu">
        <div class="default-router plan-text current-tab">전체</div>
      </div>
      <div class="menu">
        <router-link v-bind:to="'/statistics/course'" class="default-router plan-text" append>과목별</router-link>
      </div>
      <div class="menu">
        <router-link v-bind:to="'/statistics/department'" class="default-router plan-text" append>학과별</router-link>
      </div>
      <div class="export-and-toggle">
        <button class="export-button" @click="exportToExcel">
          내보내기
        </button>
        <div class="toggle-box" @click.self.prevent="toggle">
          <div class="wrapper">
            <input type="checkbox" id="switchstudent" v-model="showTable">
            <label for="switchstudent" class="switch_label">
              <span class="onf_btn"></span>
              <div class="toggle_img">
                <div class="img1">
                  <svg class="toggle-image-1" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <g id="Huge-icon">
                      <path id="Vector"
                        d="M10 6H16M10 14H16M10 10H22M10 18H22M3 10H5C5.55228 10 6 9.55228 6 9V7C6 6.44772 5.55228 6 5 6H3C2.44772 6 2 6.44772 2 7V9C2 9.55228 2.44772 10 3 10ZM3 18H5C5.55228 18 6 17.5523 6 17V15C6 14.4477 5.55228 14 5 14H3C2.44772 14 2 14.4477 2 15V17C2 17.5523 2.44772 18 3 18Z"
                        stroke-width="1.5" stroke-linecap="round" />
                    </g>
                  </svg>
                </div>
                <div class="img2">
                  <svg class="toggle-image-2" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none">
                    <path
                      d="M8 14L9.08225 12.1963C9.72077 11.132 11.2247 11.0309 12 12C12.7753 12.9691 14.2792 12.8679 14.9178 11.8037L16 10M12 18V22M4 6H20C21.1046 6 22 5.10457 22 4C22 2.89543 21.1046 2 20 2H4C2.89543 2 2 2.89543 2 4C2 5.10457 2.89543 6 4 6ZM3 6H21V16C21 17.1046 20.1046 18 19 18H5C3.89543 18 3 17.1046 3 16V6Z"
                      stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
                  </svg>
                </div>
              </div>
            </label>
          </div>
        </div>
      </div>
    </div>
    <div class="navigation_underline"></div>
    <div class="contents-box">
      <div class="student-sub-toggle">
        <div class="all dragblock" :class="[this.subToggleButton ? 'all-unclick' : 'all-click']"
          @click="allStudentToggleButton">전체 학생</div>
        <div class="each dragblock" :class="[this.subToggleButton ? 'each-click' : 'each-unclick']"
          @click="eachStudentToggleButton">학생별</div>
      </div>
      <transition name="slide-fade" mode="out-in">
        <div v-if="!showTable" class="table">
          <transition name="slide-fade" mode="out-in">
            <div v-if="!subToggleButton" class="all-table">
              <div class="sub-table-left">
                <div class="title">활동 학생 수</div>
                <div class="sub-table">
                  <table>
                    <thead class="table-header-wrapper">
                      <th>학수번호</th>
                      <th>합계</th>
                    </thead>
                    <tbody class="table-body-wrapper">
                      <tr v-for="(item, index) in posts" :key="item[0]">
                        <td :title="item.course_id">{{ item.course_id}}</td>
                        <td :title="item.students">{{ item.students }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
              <div class="sub-table-right">
                <div class="title">Total Repos</div>
                <div class="sub-table">
                  <table>
                    <thead class="table-header-wrapper">
                      <th>학수번호</th>
                      <th>합계</th>
                    </thead>
                    <tbody class="table-body-wrapper">
                      <tr v-for="(item, index) in posts" :key="item[0]">
                        <td :title="item.course_id">{{ item.course_id }}</td>
                        <td :title="item.students">{{ item.num_repos }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
              <!-- 줄 바뀜 -->
              <div class="sub-table-left">
                <div class="title">Total Commits</div>
                <div class="sub-table">
                  <table>
                    <thead class="table-header-wrapper">
                      <th>학수번호</th>
                      <th>합계</th>
                    </thead>
                    <tbody class="table-body-wrapper">
                      <tr v-for="(item, index) in posts" :key="item[0]">
                        <td :title="item.course_id">{{ item.course_id }}</td>
                        <td :title="item.commit">{{ item.commit }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
              <div class="sub-table-right">
                <div class="title">Total Issues</div>
                <div class="sub-table">
                  <table>
                    <thead class="table-header-wrapper">
                      <th>학수번호</th>
                      <th>합계</th>
                    </thead>
                    <tbody class="table-body-wrapper">
                      <tr v-for="(item, index) in posts" :key="item[0]">
                        <td :title="item.course_id">{{ item.course_id }}</td>
                        <td :title="item.issue">{{ item.issue }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
              <!-- 줄 바뀜 -->
              <div class="sub-table-left">
                <div class="title">Total PRs</div>
                <div class="sub-table">
                  <table>
                    <thead class="table-header-wrapper">
                      <th>학수번호</th>
                      <th>합계</th>
                    </thead>
                    <tbody class="table-body-wrapper">
                      <tr v-for="(item, index) in posts" :key="item[0]">
                        <td :title="item.course_id">{{ item.course_id }}</td>
                        <td :title="item.pr">{{ item.pr }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
              <div class="sub-table-right">
                <div class="title">Total Stars</div>
                <div class="sub-table">
                  <table>
                    <thead class="table-header-wrapper">
                      <th>학수번호</th>
                      <th>합계</th>
                    </thead>
                    <tbody class="table-body-wrapper">
                      <tr v-for="(item, index) in posts" :key="item[0]">
                        <td :title="item.course_id">{{ item.course_id }}</td>
                        <td :title="item.issue">{{ item.issue }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
            <!-- 학생별 시작 -->
            <div v-else class="each-table">
              <div class="sub-table-left">
                <div class="title">학생별 Repos</div>
                <div class="sub-table">
                  <table>
                    <thead class="table-header-wrapper">
                      <th width="203px">학수번호</th>
                      <th width="58px">25%</th>
                      <th width="58px">50%</th>
                      <th width="58px">75%</th>
                      <th width="58px">최대</th>
                      <th width="87px">평균</th>
                      <th width="87px">표준편차</th>
                    </thead>
                    <tbody class="table-body-wrapper">
                      <tr v-for="(item, index) in posts" :key="item[0]">
                        <td width="203px" :title="item.course_id">{{ item.course_id }}</td>
                        <td width="58px" :title="item.num_repos_q1">{{ item.num_repos_q1 }}</td>
                        <td width="58px" :title="item.num_repos_q2">{{ item.num_repos_q2 }}</td>
                        <td width="58px" :title="item.num_repos_q3">{{ item.num_repos_q3 }}</td>
                        <td width="58px" :title="item.num_repos_max">{{ item.num_repos_max }}</td>
                        <td width="87px" :title="item.num_repos_mean">{{ item.num_repos_mean }}</td>
                        <td width="87px" :title="item.num_repos_std">{{ item.num_repos_std }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
              <div class="sub-table-right">
                <div class="title">학생별 Commits</div>
                <div class="sub-table">
                  <table>
                    <thead class="table-header-wrapper">
                      <th width="203px">학수번호</th>
                      <th width="58px">25%</th>
                      <th width="58px">50%</th>
                      <th width="58px">75%</th>
                      <th width="58px">최대</th>
                      <th width="87px">평균</th>
                      <th width="87px">표준편차</th>
                    </thead>
                    <tbody class="table-body-wrapper">
                      <tr v-for="(item, index) in posts" :key="item[0]">
                        <td width="203px" :title="item.course_id">{{ item.course_id }}</td>
                        <td width="58px" :title="item.commit_q1">{{ item.commit_q1 }}</td>
                        <td width="58px" :title="item.commit_q2">{{ item.commit_q2 }}</td>
                        <td width="58px" :title="item.commit_q3">{{ item.commit_q3 }}</td>
                        <td width="58px" :title="item.commit_max">{{ item.commit_max }}</td>
                        <td width="87px" :title="item.commit_mean">{{ item.commit_mean }}</td>
                        <td width="87px" :title="item.commit_std">{{ item.commit_std }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
              <!-- 줄 바뀜 -->
              <div class="sub-table-left">
                <div class="title">학생별 Issues</div>
                <div class="sub-table">
                  <table>
                    <thead class="table-header-wrapper">
                      <th width="203px">학수번호</th>
                      <th width="58px">25%</th>
                      <th width="58px">50%</th>
                      <th width="58px">75%</th>
                      <th width="58px">최대</th>
                      <th width="87px">평균</th>
                      <th width="87px">표준편차</th>
                    </thead>
                    <tbody class="table-body-wrapper">
                      <tr v-for="(item, index) in posts" :key="item[0]">
                        <td width="203px" :title="item.course_id">{{ item.course_id }}</td>
                        <td width="58px" :title="item.issue_q1">{{ item.issue_q1 }}</td>
                        <td width="58px" :title="item.issue_q2">{{ item.issue_q2 }}</td>
                        <td width="58px" :title="item.issue_q3">{{ item.issue_q3 }}</td>
                        <td width="58px" :title="item.issue_max">{{ item.issue_max }}</td>
                        <td width="87px" :title="item.issue_mean">{{ item.issue_mean }}</td>
                        <td width="87px" :title="item.issue_std">{{ item.issue_std }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
              <div class="sub-table-right">
                <div class="title">학생별 PRs</div>
                <div class="sub-table">
                  <table>
                    <thead class="table-header-wrapper">
                      <th width="203px">학수번호</th>
                      <th width="58px">25%</th>
                      <th width="58px">50%</th>
                      <th width="58px">75%</th>
                      <th width="58px">최대</th>
                      <th width="87px">평균</th>
                      <th width="87px">표준편차</th>
                    </thead>
                    <tbody class="table-body-wrapper">
                      <tr v-for="(item, index) in posts" :key="item[0]">
                        <td width="203px" :title="item.course_id">{{ item.course_id }}</td>
                        <td width="58px" :title="item.pr_q1">{{ item.pr_q1 }}</td>
                        <td width="58px" :title="item.pr_q2">{{ item.pr_q2 }}</td>
                        <td width="58px" :title="item.pr_q3">{{ item.pr_q3 }}</td>
                        <td width="58px" :title="item.pr_max">{{ item.pr_max }}</td>
                        <td width="87px" :title="item.pr_mean">{{ item.pr_mean }}</td>
                        <td width="87px" :title="item.pr_std">{{ item.pr_std }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
              <!-- 줄 바뀜 -->
              <div class="sub-table-left">
                <div class="title">학생별 Stars</div>
                <div class="sub-table">
                  <table>
                    <thead class="table-header-wrapper">
                      <th width="203px">학수번호</th>
                      <th width="58px">25%</th>
                      <th width="58px">50%</th>
                      <th width="58px">75%</th>
                      <th width="58px">최대</th>
                      <th width="87px">평균</th>
                      <th width="87px">표준편차</th>
                    </thead>
                    <tbody class="table-body-wrapper">
                      <tr v-for="(item, index) in posts" :key="item[0]">
                        <td width="203px" :title="item.course_id">{{ item.course_id }}</td>
                        <td width="58px" :title="item.star_q1">{{ item.star_q1 }}</td>
                        <td width="58px" :title="item.star_q2">{{ item.star_q2 }}</td>
                        <td width="58px" :title="item.star_q3">{{ item.star_q3 }}</td>
                        <td width="58px" :title="item.star_max">{{ item.star_max }}</td>
                        <td width="87px" :title="item.star_mean">{{ item.star_mean }}</td>
                        <td width="87px" :title="item.star_std">{{ item.star_std }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </transition>
        </div>
        <div v-else class="chart">
          <transition name="slide-fade" mode="out-in">
            <div v-if="!subToggleButton">
              <div class="horizontal-chart-container">
                <div class="left-container">
                  <div class="chart-title">
                    활동 학생 수
                  </div>
                  <!-- 학생 수 차트 -->
                  <StudentGroupBarCharts class="charts" :data="posts" chartTitle="Number of Students by Year"
                    yAxisTitle="학생 수" dataKey="students" />
                </div>
                <div class="right-container">
                  <div class="chart-title">
                    Total Repos
                  </div>
                  <!-- Repos 차트 -->
                  <StudentGroupBarCharts :data="posts" chartTitle="Number of Repos by Year" yAxisTitle="Repos 수"
                    dataKey="num_repos" />
                </div>
              </div>
              <div class="horizontal-chart-container">
                <div class="left-container">
                  <div class="chart-title">
                    Total Commits
                  </div>
                  <!-- Commits 차트 -->
                  <StudentGroupBarCharts :data="posts" chartTitle="Number of Commits by Year" yAxisTitle="Commits 수"
                    dataKey="commit" />
                </div>
                <div class="right-container">
                  <div class="chart-title">
                    Total Issues
                  </div>
                  <!-- Issues 차트 -->
                  <StudentGroupBarCharts :data="posts" chartTitle="Number of Issues by Year" yAxisTitle="Issues 수"
                    dataKey="issue" />
                </div>
              </div>
              <div class="horizontal-chart-container">
                <div class="left-container">
                  <div class="chart-title">
                    Total PRs
                  </div>
                  <!-- PRs 차트 -->
                  <StudentGroupBarCharts :data="posts" chartTitle="Number of PRs by Year" yAxisTitle="PR 수"
                    dataKey="pr" />
                </div>
                <div class="right-container">
                  <div class="chart-title">
                    Total Stars
                  </div>
                  <!-- Stars 차트 -->
                  <StudentGroupBarCharts :data="posts" chartTitle="Number of Stars by Year" yAxisTitle="Star 수"
                    dataKey="stars" />
                </div>
              </div>
            </div>
            <div v-else>
              <div class="horizontal-chart-container">
                <div class="left-container">
                  <div class="chart-title">
                    Total Repos
                  </div>
                  <!-- Repos 차트 -->
                  <StudentGroupBoxCharts :data="posts" chartTitle="Number of Repos by Year" yAxisTitle="Repos 수"
                    dataKey="num_repos_stats" />
                </div>
                <div class="right-container">
                  <div class="chart-title">
                    Total Commits
                  </div>
                  <!-- Commits 차트 -->
                  <StudentGroupBoxCharts :data="posts" chartTitle="Number of Commits by Year" yAxisTitle="Commits 수"
                    dataKey="commit_stats" />
                </div>
              </div>
              <div class="horizontal-chart-container">
                <div class="left-container">
                  <div class="chart-title">
                    Total Issues
                  </div>
                  <!-- Issues 차트 -->
                  <StudentGroupBoxCharts :data="posts" chartTitle="Number of Issues by Year" yAxisTitle="Issues 수"
                    dataKey="issue_stats" />
                </div>
                <div class="right-container">
                  <div class="chart-title">
                    Total PRs
                  </div>
                  <!-- PRs 차트 -->
                  <StudentGroupBoxCharts :data="posts" chartTitle="Number of PRs by Year" yAxisTitle="PR 수"
                    dataKey="pr_stats" />
                </div>
              </div>
              <div class="horizontal-chart-container">
                <div class="left-container">
                  <div class="chart-title">
                    Total Stars
                  </div>
                  <!-- Stars 차트 -->
                  <StudentGroupBoxCharts :data="posts" chartTitle="Number of Stars by Year" yAxisTitle="Star 수"
                    dataKey="stars_stats" />
                </div>
              </div>
            </div>
          </transition>
        </div>
      </transition>
    </div>
  </div>
</template>

<script>
import StudentGroupBarCharts from '@/views/StatisticsCharts/Students/StudentGroupBarCharts.vue';
import StudentGroupBoxCharts from '@/views/StatisticsCharts/Students/StudentGroupBoxCharts.vue';
import * as XLSX from 'xlsx';

export default {
  name: 'StatisticsStudent',
  props: ["course"],
  components: {
    StudentGroupBarCharts,
    StudentGroupBoxCharts,
  },
  data() {
    return {
      showOverlay: false,
      showTable: false,
      searchField: '',
      selectedFile: null,
      pannelLoading: false,
      posts: [],
      currentPage: 1,
      postsPerPage: 10,
      header: [['개설학기', '9%'],
      ['과목명', '14%'],
      ['학수번호', '11%'],
      ['지도교수', '11%'],
      ['수강생', '11%'],
      ['Commit', '11%'],
      ['PR', '11%'],
      ['Issue', '11%'],
      ['Repos', '11%']],
      importItem: {
        course_id: '',
        year: '',
        semester: '',
        course_name: '',
        prof: '',
        ta: '',
      },
      ValidationItem: {
        course_id: '',
        year: '',
        semester: '',
        course_name: '',
        prof: '',
        ta: '',
        file: '',
      },
      selectedFileName: '',
      subToggleButton: false,
    };
  },
  computed: {
    totalPages() {
      return Math.ceil(this.posts.length / this.postsPerPage)
    },
  },
  methods: {
    toggle() {
      this.showTable = !this.showTable;
    },
    tablewidth(length) {
      return length;
    },
    allStudentToggleButton() {
      this.subToggleButton = false;
      this.$router.replace({ path: this.$route.path, query: { type: 'all' } });
    },
    eachStudentToggleButton() {
      this.subToggleButton = true;
      this.$router.replace({ path: this.$route.path, query: { type: 'each' } });
    },
    exportToExcel() {
      // 현재 표시된 데이터 가져오기 (필터가 이미 적용된 this.posts 사용)
      const dataToExport = this.getExportData();

      const worksheet = XLSX.utils.json_to_sheet(dataToExport);
      const workbook = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(workbook, worksheet, 'Sheet1');
      const excelBuffer = XLSX.write(workbook, { type: 'array', bookType: 'xlsx' });
      const data = new Blob([excelBuffer], { type: 'application/octet-stream' });

      // 파일 다운로드 링크 생성
      const url = window.URL.createObjectURL(data);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'student_data.xlsx'; // 다운로드 파일명 설정
      link.click();
      window.URL.revokeObjectURL(url);
    },
    getExportData() {
      // 현재 표시된 데이터(this.posts)를 엑셀에 적합한 형식으로 변환

      return this.posts.map(item => {
        let rowData = {
          '학수번호': item.course_id,
          '과목명': item.course_name
        };

        if (!this.showTable) {
          // 테이블이 표시되는 경우
          if (!this.subToggleButton) {
            // '전체 학생' 탭
            rowData['활동 학생 수'] = item.students;
            rowData['Total Repos'] = item.num_repos;
            rowData['Total Commits'] = item.commit,
            rowData['Total Issues'] = item.issue,
            rowData['Total PRs'] = item.pr,
            rowData['Total Stars'] = item.star,
            rowData['KPI Repos'] = item.num_repos ? ((item.num_repos / item.students) * 100).toFixed(2) + '%' : '0%';
            rowData['KPI Commits'] = item.commit ? ((item.commit / item.students) * 100).toFixed(2) + '%' : '0%';
            rowData['KPI contributors'] = item.contributors ? ((item.contributors / item.students) * 100).toFixed(2) + '%' : '0%';

          } else {
            // '학생별' 탭
            // Repos 통계 데이터 추가
            rowData['Repos 25%'] = item.num_repos_q1;
            rowData['Repos 50%'] = item.num_repos_q2;
            rowData['Repos 75%'] = item.num_repos_q3;
            rowData['Repos 최대'] = item.num_repos_max;
            rowData['Repos 평균'] = item.num_repos_mean;
            rowData['Repos 표준편차'] = item.num_repos_std;

            // Commits 통계 데이터 추가
            rowData['Commits 25%'] = item.commit_q1;
            rowData['Commits 50%'] = item.commit_q2;
            rowData['Commits 75%'] = item.commit_q3;
            rowData['Commits 최대'] = item.commit_max;
            rowData['Commits 평균'] = item.commit_mean;
            rowData['Commits 표준편차'] = item.commit_std;

            // Issues 통계 데이터 추가
            rowData['Issues 25%'] = item.issue_q1;
            rowData['Issues 50%'] = item.issue_q2;
            rowData['Issues 75%'] = item.issue_q3;
            rowData['Issues 최대'] = item.issue_max;
            rowData['Issues 평균'] = item.issue_mean;
            rowData['Issues 표준편차'] = item.issue_std;

            // PRs 통계 데이터 추가
            rowData['PRs 25%'] = item.pr_q1;
            rowData['PRs 50%'] = item.pr_q2;
            rowData['PRs 75%'] = item.pr_q3;
            rowData['PRs 최대'] = item.pr_max;
            rowData['PRs 평균'] = item.pr_mean;
            rowData['PRs 표준편차'] = item.pr_std;

            // Stars 통계 데이터 추가
            rowData['Stars 25%'] = item.star_q1;
            rowData['Stars 50%'] = item.star_q2;
            rowData['Stars 75%'] = item.star_q3;
            rowData['Stars 최대'] = item.star_max;
            rowData['Stars 평균'] = item.star_mean;
            rowData['Stars 표준편차'] = item.star_std;
          }
        } else {
          // 차트가 표시되는 경우
          // 필요에 따라 rowData를 구성하거나, 차트 데이터를 내보내기 원치 않으면 무시할 수 있습니다.
        }

        return rowData;
      });
    },
  },
  mounted() {
    this.posts = this.course;
  },
  watch: {
    course(to, from) {
      this.posts = this.course;
    },
  },
};

</script>

<style scoped>
.cursorblock {
  pointer-events: none;
}

.container {
  max-width: 1600px;

  .navigation {
    min-height: 41px;
    padding-left: 56px;
    padding-right: 56px;
    /* margin-left: 56px; */
    display: flex;
    align-items: center;

    .menu {
      width: 101px;
      margin-right: 30px !important;
      font-size: 18px;
      align-items: center;
      text-align: center;

      .plan-text {
        margin: 0 auto;
        line-height: 41px;
      }

      .current-tab {
        color: #862633 !important;
        border-bottom: solid 4px #862633;
      }
    }
  }

  .contents-box {
    padding: 0 56px;

    .student-sub-toggle {
      padding-top: 20px;
      width: 200px;
      height: 40px;
      display: inline-flex;

      .all,
      .each {
        width: 100px;
        height: 40px;
        text-align: center;
        line-height: 40px;
        border-radius: 30px;
        background: #FFEAEC;
        color: var(--Primary_medium, #CB385C);
        font-family: Pretendard;
        font-size: 16px;
        font-style: normal;
        font-weight: 600;
        cursor: pointer;
      }

      .all-unclick {
        background: #FFF;
        color: #CDCDCD;
      }

      .all-click {
        background: #FFEAEC;
        color: var(--Primary_medium, #CB385C);
      }

      .each-unclick {
        background: #FFF;
        color: #CDCDCD;
      }

      .each-click {
        background: #FFEAEC;
        color: var(--Primary_medium, #CB385C);
      }
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

    .table {
      margin: 0 0 20px 0;
      padding-bottom: 20px;
      /* border: 1px solid #dce2ed; */
      border-radius: 4px;
      height: 100%;

      .student-sub-toggle {
        width: 200px;
        height: 40px;
        display: inline-flex;

        .all,
        .each {
          width: 100px;
          height: 40px;
          text-align: center;
          line-height: 40px;
          border-radius: 30px;
          background: #FFEAEC;
          color: var(--Primary_medium, #CB385C);
          font-family: Pretendard;
          font-size: 16px;
          font-style: normal;
          font-weight: 600;
          cursor: pointer;
        }

        .all-unclick {
          background: #FFF;
          color: #CDCDCD;
        }

        .all-click {
          background: #FFEAEC;
          color: var(--Primary_medium, #CB385C);
        }

        .each-unclick {
          background: #FFF;
          color: #CDCDCD;
        }

        .each-click {
          background: #FFEAEC;
          color: var(--Primary_medium, #CB385C);
        }
      }

      .all-table,
      .each-table {
        /* margin-top: 40px; */
      }

      .all-table {
        display: flex;
        flex-flow: wrap;
        height: 900px;
        justify-content: space-between;
        align-content: flex-start;

        & .title {
          color: var(--Black, #262626);
          font-family: Pretendard;
          font-size: 18px;
          font-weight: 700;
          margin: 0 0 15px 15px;
        }

        .sub-table-left {
          margin-top: 40px;
          width: 540px;
          height: 270px;
          min-height: 270px;
          background: var(--Primary_background, #FFF);
        }

        .sub-table-middle {
          width: 320px;
          background: var(--Primary_background, #FFF);
        }

        .sub-table-right {
          margin-top: 40px;
          width: 540px;
          height: 270px;
          min-height: 270px;
          background: var(--Primary_background, #FFF);
        }

        & .sub-table {
          width: 100%;

          & table {
            width: 100%;
            border-collapse: collapse;
          }

          & .table-header-wrapper {
            border-top: 1px solid #FFEAEC;
            border-bottom: 1px solid #FFEAEC;
            background-color: #FFFBFB;
            border-collapse: collapse;
            position: sticky;
            display: block;
            inset-block-start: 0;

          }

          & .table-body-wrapper {
            display: block;
            max-height: 154px;
            width: 100%;
            overflow-y: auto;
          }

          & th {
            vertical-align: middle;
            width: 270px;
            text-align: center;
            height: 43px;
            color: #CB385C;
            line-height: 43px;

            font-size: 16px;
            font-weight: 600;
          }

          & tr {
            height: 50px;
            width: 270px;
            vertical-align: middle;
            text-align: center;

            border-top: 1px solid #FFEAEC;
            border-bottom: 1px solid #FFEAEC;

            & td {
              width: 270px;
              font-size: 16px;
              font-weight: 500;
              line-height: 50px;
            }
          }
        }
      }

      .each-table {
        display: flex;
        flex-flow: wrap;
        height: 900px;
        justify-content: space-between;
        align-content: flex-start;

        & .title {
          color: var(--Black, #262626);
          font-family: Pretendard;
          font-size: 18px;
          font-weight: 700;
          margin: 0 0 15px 15px;
        }

        .sub-table-left {
          margin-top: 40px;
          width: 580px;
          height: 270px;
          min-height: 270px;
          background: var(--Primary_background, #FFF);
        }

        .sub-table-middle {
          width: 320px;
          background: var(--Primary_background, #FFF);
        }

        .sub-table-right {
          margin-top: 40px;
          width: 580px;
          height: 270px;
          min-height: 270px;
          background: var(--Primary_background, #FFF);
        }

        .sub-table {
          width: inherit;

          & table {
            width: 100%;
            border-collapse: collapse;
          }

          & .table-header-wrapper {
            border-top: 1px solid #FFEAEC;
            border-bottom: 1px solid #FFEAEC;
            background-color: #FFFBFB;
            border-collapse: collapse;
            position: sticky;
            display: block;
            inset-block-start: 0;

          }

          & .table-body-wrapper {
            display: block;
            max-height: 154px;
            width: inherit;
            overflow-y: auto;
          }

          & th {
            vertical-align: middle;
            /* width: 270px; */
            text-align: center;
            height: 43px;
            color: #CB385C;
            line-height: 43px;

            font-size: 16px;
            font-weight: 600;
          }

          & tr {
            height: 50px;
            width: inherit;
            vertical-align: middle;
            text-align: center;

            border-top: 1px solid #FFEAEC;
            border-bottom: 1px solid #FFEAEC;

            & td {
              /* width: 270px; */
              font-size: 15px;
              font-weight: 500;
              line-height: 50px;
            }
          }
        }
      }
    }
  }

  .toggle-box {
    align-self: flex-end;
    margin-left: auto;

    .wrapper {
      width: 150px;
      height: 58px;
      text-align: center;
      margin: 0 auto;
      position: relative;
    }

    #switchstudent {
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

      & svg {
        width: 29px;
        height: 29px;
      }

      .img1,
      .img2 {
        .toggle-image-1 {
          & path {
            transition: 0.2s;
            stroke: #CB385C;
          }
        }

        .toggle-image-2 {
          & path {
            transition: 0.2s;
            stroke: #E9D8D9;
          }
        }

      }

      .img1 {
        margin-right: auto;
      }
    }

    #switchstudent:checked+.switch_label .onf_btn {
      left: 70px;
      background: #fff;
      box-shadow: 1px 2px 3px #00000020;
    }

    #switchstudent:checked+.switch_label .toggle-image-1 {
      & path {
        stroke: #E9D8D9;
      }
    }

    #switchstudent:checked+.switch_label .toggle-image-2 {
      & path {
        stroke: #CB385C;
      }
    }
  }
}

.navigation_underline {
  border-bottom: solid 2px #dce2ed;
  width: calc(1920px - 586px) !important;
}

.table-over {
  border-collapse: collapse;
  width: 100%;
  font-size: 16px;

  .table-header-wrapper {
    border-top: solid 1px #F9D2D6;
    border-bottom: solid 1px #F9D2D6;
  }

  .table-header {
    color: var(--Primary_normal, #910024);
    font-weight: 600;
    height: 43px;
    vertical-align: middle;
  }

  .table-row {
    height: 70px;
    border-bottom: solid 1px #DCE2ED;
    text-align: center;
    text-overflow: ellipsis;
    overflow: hidden;
    white-space: nowrap;
  }
}

.export-and-toggle {
  display: flex;
  align-items: center;
  margin-left: auto;

  .export-button {
    margin-right: 10px;
    padding: 8px 16px;
    background-color: #CB385C;
    color: #FFF;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
    font-weight: 600;
  }

  .export-button:hover {
    background-color: #a82e4a;
  }
}


.chart {
  margin: 20px 0;
  padding: 20px 0;
  /* border: 1px solid #dce2ed; */
  border-radius: 4px;
  height: 100%;

  & .horizontal-chart-container {
    display: flex;
    flex-flow: wrap;
    justify-content: space-between;
    align-content: flex-start;

    .left-container,
    .right-container {
      margin-bottom: 20px;
      background: var(--Primary_background, #FFFBFB);
      border-radius: 20px;

      .chart-title {
        margin-top: 10px;
        position: static;
        color: var(--Black, #262626);
        font-family: Pretendard;
        font-size: 18px;
        font-style: normal;
        font-weight: 700;
        margin-left: 40px;
      }

      .charts {
        position: static;
      }
    }
  }

  .category-chart-container {}

  & .title {
    font-size: 22px;
    font-weight: 700;
  }
}

.dragblock {
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-use-select: none;
  user-select: none;
}
</style>