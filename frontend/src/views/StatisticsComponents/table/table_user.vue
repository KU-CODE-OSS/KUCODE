<template>
  <div>
    <!-- <v-row>
      <v-col cols="10"> </v-col>
      <v-col cols="0">
        <filters
          class="filter-container"
          :students="students"
          @update:filteredStudents="updateFilteredStudents"
        ></filters>
      </v-col>
      <v-col cols="2" align="right">
        <v-text-field
          v-model="search"
          label="Search"
          prepend-inner-icon="mdi-magnify"
          variant="outlined"
          hide-details
          single-line
        ></v-text-field>
      </v-col>
    </v-row>
      <v-tabs align-tabs="end" v-model="table_or_chart">
        <v-tab slim hide-slider color="blue" value="table">
            <v-icon size="x-large" icon="mdi-table"></v-icon>
            테이블
        </v-tab>
        <v-tab slim hide-slider color="blue" value="chart">
            <v-icon size="x-large" icon="mdi-chart-box"></v-icon>
            차트
        </v-tab>
      </v-tabs> -->
      <portal to="stat_table_user">
        <Filters
            class="filter-container"
            :students="students"
            @update:filteredStudents="updateFilteredStudents"
          ></Filters>
      </portal>

      <v-window v-model="table_or_chart">
        <v-window-item value="table">
          <v-data-table
            :group-by="groupBy"
            :headers="headers"
            :items="filteredStudentsBySearch"
            item-value="uniqueKey"
            :loading="loading"
            fixed-header
            height="600px"
          >
            <template v-slot:group-header="{ item, toggleGroup, isGroupOpen }">
              <tr :style="{ backgroundColor: isGroupOpen(item) ? '#f5f5f5' : '#ffffff' }">
                <td>
                  <v-btn
                    :icon="isGroupOpen(item) ? '$expand' : '$next'"
                    size="small"
                    variant="text"
                    @click="toggleGroup(item)"
                  ></v-btn>
                </td>
                <td>{{ groupInfo[item.value]?.name }}</td>
                <td>{{ groupInfo[item.value]?.department }}</td>
                <td>{{ groupInfo[item.value]?.id }}</td>
                <td>{{ groupInfo[item.value]?.enrollment }}</td>
                <td>{{ groupInfo[item.value]?.github_id }}</td>
                <td>{{ groupInfo[item.value]?.year }}</td>
                <td>{{ groupInfo[item.value]?.semester }}</td>
                <td>{{ groupInfo[item.value]?.course_name }}</td>
                <td>{{ groupInfo[item.value]?.commit }}</td>
                <td>{{ groupInfo[item.value]?.pr }}</td>
                <td>{{ groupInfo[item.value]?.issue }}</td>
                <td>{{ groupInfo[item.value]?.num_repos }}</td>
              </tr>
            </template>
            <template v-slot:item="{ item }">
              <tr>
                <td><!-- 그룹 --></td>                
                <td><!-- 이름 --></td>
                <td><!-- 학과 --></td>
                <td><!-- 학번 --></td>
                <td><!-- 재학상태 --></td>
                <td><!-- GitHub ID --></td>                
                <td>{{ item.year }}</td>
                <td>{{ item.semester }}</td>
                <td>{{ item.course_name }}</td>
                <td>{{ item.commit }}</td>
                <td>{{ item.pr }}</td>
                <td>{{ item.issue }}</td>
                <td>{{ item.num_repos }}</td>
              </tr>
            </template>
          </v-data-table>
        </v-window-item>
        <portal to="stat_chart_user">
        <!-- <v-window-item value="chart" class="chart_user"> -->
        <!-- ↓↓↓ 차트 컴포넌트 ↓↓↓ -->
            <v-lazy>
                <!-- <chart_user/> -->
                <chart_user
                  :totalCommitsByCourse="totalCommitsByCourse" 
                  :totalPRByCourse="totalPRByCourse"
                  :totalIssueByCourse="totalIssueByCourse"
                  :totalRepoByCourse="totalRepoByCourse"
                />

                <!-- <chart_user_example/>  -->
            </v-lazy>
        <!-- ↑↑↑ 차트 컴포넌트 ↑↑↑ -->
        <!-- </v-window-item> -->
      </portal>
      </v-window>
      
    <!-- </v-card> -->
  </div>
</template>

<script>
import axios from 'axios';
import Filters from './Filters.vue';
import chart_user from '../chart/chart_user.vue';
import chart_user_example from '../chart/chart_user_example.vue';
export default {
  components: {
    Filters,
    chart_user,
    chart_user_example
  },
  data() {
    return {
      table_or_chart: null,
      loading: true,
      search: '',
      groupBy: [
        {
          align: 'center',
          key: 'id',
          order: 'asc',
        },
      ],
      headers: [
        { align: 'center', title: '이름', key: 'name', width:'6%'},
        { align: 'center', title: '학과', key: 'department', width:'15%' },
        { align: 'center', title: '학번', key: 'id' },
        { align: 'center', title: '재학상태', key: 'enrollment' , width:'7%'},
        { align: 'center', title: 'GitHub ID', key: 'github_id', width:'10%' },
        { align: 'center', title: '연도', key: 'year' , width:'6%'},
        { align: 'center', title: '학기', key: 'semester', width:'5.5%' },
        { align: 'center', title: '과목명', key: 'course_name' , width:'15%'},
        { align: 'center', title: 'Commit 수', key: 'commit' },
        { align: 'center', title: 'PR 수', key: 'pr', width:'6%'},
        { align: 'center', title: 'Issue 수', key: 'issue', width:'7%' },
        { align: 'center', title: 'Repo 수', key: 'num_repos', width:'7%' },
      ],
      students: [],
      groupInfo: {},
      uniqueKeyCounter: 0,
      filteredStudents: [],
      totalCommitsByCourse: {}, // props로 넘겨줄 데이터
      totalPRByCourse: {} ,
      totalIssueByCourse: {},
      totalRepoByCourse: {},
    };
  },
  created() {
    this.fetchTotal();
    this.fetchCourse();
  },
  // props: {
  //   students: {
  //     type: Array,
  //     required: true
  //   }
  // },
  methods: {
    async fetchTotal() {
      try {
        this.loading = true;
        const response = await axios.get('http://localhost/api/account/student_read_total');
        this.processTotal(response.data);
        // console.log('Total Data:', response.data);
      } catch (error) {
        // console.error('Error fetching data:', error);
      } finally {
        this.loading = false;
      }
    },
    processTotal(data) {
      const groupInfo = {};
      // total 값들을 저장할 변수들. 아직 연도별, 학과별 등의 필터링을 적용 안 함.
      let total_commit_sum = 0; // total_commit 값을 합산할 변수
      let total_pr_sum = 0; // total_pr 값을 합산할 변수
      let total_issue_sum = 0; // total_issue 값을 합산할 변수
      let total_repos_sum = 0; // total_repos 값을 합산할 변수

      data.forEach(groupItem => {
        total_commit_sum += groupItem.total_commit; // total_commit 값을 더함
        total_pr_sum += groupItem.total_pr; // total_pr 값을 더함
        total_issue_sum += groupItem.total_issue; // total_issue 값을 더함
        total_repos_sum += groupItem.total_repos; // total_repos 값을 더함

        groupInfo[groupItem.id] = {
          name: groupItem.name,
          department: groupItem.department,
          id: groupItem.id,
          enrollment: groupItem.enrollment,
          github_id: groupItem.github_id,
          year: groupItem.year,
          semester: groupItem.semester,
          course_name: groupItem.course_name,
          commit: groupItem.total_commit,
          pr: groupItem.total_pr,
          issue: groupItem.total_issue,
          num_repos: groupItem.total_repos,
          students: [],
        };
      });

    //   console.log('Group Info:', groupInfo);
      this.groupInfo = groupInfo;
      
      this.total_commit_sum = total_commit_sum; // total_commit 값을 저장
      this.total_pr_sum = total_pr_sum; // total_pr 값을 저장
      this.total_issue_sum = total_issue_sum; // total_issue 값을 저장
      this.total_repos_sum = total_repos_sum; // total_repos 값을 저장

    //   console.log('Total Commit:', this.total_commit_sum);
    //   console.log('Total PR:', this.total_pr_sum);
    //   console.log('Total Issue:', this.total_issue_sum);
    //   console.log('Total Repos:', this.total_repos_sum);
    },
    async fetchCourse() {
      try {
        const response = await axios.get('http://localhost/api/account/student_read_course_info');
        this.processCourse(response.data);
        // console.log('Course Data:', response.data);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    },
    processCourse(data) {
      const students = [];

      const totalCommitsByCourse = {};
      const totalPRByCourse = {};
      const totalIssueByCourse = {};
      const totalRepoByCourse = {};

      data.forEach(student => {
        const uniqueKey = `item_${student.id}_${this.uniqueKeyCounter++}`;
        if (this.groupInfo[student.id]) {
          this.groupInfo[student.id].students.push({
            uniqueKey,
            ...student,
          });
        }
        students.push({
          uniqueKey,
          ...student,
        });
        // course_name별로 total_commit 계산
        if (!totalCommitsByCourse[student.course_name]) {
          totalCommitsByCourse[student.course_name] = 0;
        }
        totalCommitsByCourse[student.course_name] += student.commit;

        // course_name별로 total_pr 계산
        if (!totalPRByCourse[student.course_name]) {
          totalPRByCourse[student.course_name] = 0;
        }
        totalPRByCourse[student.course_name] += student.pr;

        // course_name별로 total_issue 계산
        if (!totalIssueByCourse[student.course_name]) {
          totalIssueByCourse[student.course_name] = 0;
        }
        totalIssueByCourse[student.course_name] += student.issue;

        // course_name별로 total_repo 계산
        if (!totalRepoByCourse[student.course_name]) {
          totalRepoByCourse[student.course_name] = 0;
        }
        totalRepoByCourse[student.course_name] += student.num_repos;

        // console.log(`Course: ${student.course_name}, Commit: ${student.commit}, PR: ${student.pr}, Issue: ${student.issue}, Repo: ${student.num_repos}`);
        // console.log(`Course: ${student.course_name}, Commit: ${student.commit}, Current Total: ${totalCommitsByCourse[student.course_name]}`);
      });

      // console.log('Updated Group Info:', this.groupInfo);
      // console.log('Students:', students);
      // console.log('Total Commits by Course:', totalCommitsByCourse);
      // console.log('Total PR by Course:', totalPRByCourse);
      // console.log('Total Issue by Course:', totalIssueByCourse);
      // console.log('Total Repo by Course:', totalRepoByCourse);

      this.students = students;
      this.filteredStudents = students; // Apply initial filter state
      this.totalCommitsByCourse = totalCommitsByCourse; // 저장
      this.totalPRByCourse = totalPRByCourse; // 저장
      this.totalIssueByCourse = totalIssueByCourse; // 저장
      this.totalRepoByCourse = totalRepoByCourse; // 저장

    },
    updateFilteredStudents(filtered) {
      this.filteredStudents = filtered;
      this.updateGroupTotals(filtered);
    },
    updateGroupTotals(filteredStudents) {
      const totals = {};

      filteredStudents.forEach(student => {
        if (!totals[student.id]) {
          totals[student.id] = {
            commit: 0,
            pr: 0,
            issue: 0,
            num_repos: 0,
          };
        }

        totals[student.id].commit += student.commit || 0;
        totals[student.id].pr += student.pr || 0;
        totals[student.id].issue += student.issue || 0;
        totals[student.id].num_repos += student.num_repos || 0;
      });

      Object.keys(this.groupInfo).forEach(key => {
        if (totals[key]) {
          this.groupInfo[key].commit = totals[key].commit;
          this.groupInfo[key].pr = totals[key].pr;
          this.groupInfo[key].issue = totals[key].issue;
          this.groupInfo[key].num_repos = totals[key].num_repos;
        } else {
          this.groupInfo[key].commit = 0;
          this.groupInfo[key].pr = 0;
          this.groupInfo[key].issue = 0;
          this.groupInfo[key].num_repos = 0;
        }
      });
    },
  },
  computed: {
    filteredStudentsBySearch() {
      const search = this.search.toLowerCase();
      return this.filteredStudents.filter(student => {
        const group = this.groupInfo[student.id] || {};
        return (
          (group.year && group.year.toString().includes(search)) ||
          (group.semester && group.semester.toString().includes(search)) ||
          (group.name && group.name.toLowerCase().includes(search)) ||
          (group.department && group.department.toLowerCase().includes(search)) ||
          (group.id && group.id.toLowerCase().includes(search)) ||
          (group.enrollment && group.enrollment.toLowerCase().includes(search)) ||
          (group.github_id && group.github_id.toLowerCase().includes(search)) ||
          (group.course_name && group.course_name.toLowerCase().includes(search)) ||
          (group.commit && group.commit.toString().includes(search)) ||
          (group.pr && group.pr.toString().includes(search)) ||
          (group.issue && group.issue.toString().includes(search)) ||
          (group.num_repos && group.num_repos.toString().includes(search)) ||
          student.name.toLowerCase().includes(search) ||
          student.course_name.toLowerCase().includes(search) ||
          student.year.toString().includes(search) ||
          student.semester.toString().includes(search) ||
          student.commit.toString().includes(search) ||
          student.pr.toString().includes(search) ||
          student.issue.toString().includes(search)
        );
      });
    },
  },
};
</script>

<style scoped>
.filter-container {
  /* margin-bottom: 10px; */
  
  /* align-content: center; */
}

.search-container > div {
  /* display: flex;
  justify-content: flex-end;
  margin-bottom: 0px; */
  flex-direction: row-reverse;
  align-items: right ;
  width : 200px !important;
}

.search-container .v-text-field {
  max-width: 300px;
}

.chart_user {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  margin-top: 60px;
  width: 100%;
  /* display: flex; */
}
</style>
  