<template>
  <v-app id="inspire">
    <v-app-bar flat>
      <v-container class="mx-auto d-flex align-center justify-center">
        <v-avatar>
          <v-img
            alt="John"
            src="https://cdn.vuetifyjs.com/images/john.jpg"
          ></v-img>
        </v-avatar>

        <v-btn @click="goToDashboard" prepend-icon="mdi-home">홈</v-btn>
        <v-btn prepend-icon="mdi-information">정보관리</v-btn> 
        <v-btn @click="goToStatistic" prepend-icon="mdi-chart-bar">통계분석</v-btn>
        <v-btn prepend-icon="mdi-account-group">커뮤니티</v-btn>
        <v-btn prepend-icon="mdi-bulletin-board">공지사항</v-btn> 

        <v-spacer></v-spacer>

        <v-responsive max-width="160">
          <!-- <v-text-field
            density="compact"
            label="Search"
            rounded="lg"
            variant="solo-filled"
            flat
            hide-details
            single-line
          ></v-text-field> -->
        </v-responsive>
      </v-container>
    </v-app-bar>

    <v-main class="bg-grey-lighten-3">
      <!-- <div class="sidebar_filter_box">
        <img src="./assets/hana.png" alt="Filter Image" style="max-width: 100%; max-height: 100%;">
        하나은행 01089146793907 정현승
      </div> -->
      <div>
      <v-container>
        <v-row>
          <v-col>
            <v-sheet min-height="70vh" rounded="lg">
              <v-tabs-window v-model="table_tab">
                <!-- 절대 위치로 v-tab 추가 -->
                <v-tabs v-model="table_tab" class="absolute-tab row_bar">
                  <v-tab class="row_bar" value="subject" prepend-icon="mdi-book-open-variant-outline">전공과목</v-tab>
                  <v-tab class="user_font" value="user" prepend-icon="mdi-account-multiple">사용자</v-tab>
                  <v-tab value="repository" prepend-icon="mdi-source-repository-multiple">레포지토리</v-tab>
                </v-tabs>
                <v-tabs-window-item value="subject"> <table-major-component/> </v-tabs-window-item>
                <v-tabs-window-item value="user"> <table-user-component/> </v-tabs-window-item>
                <v-tabs-window-item value="repository"> <table-repo-component/> </v-tabs-window-item>
              </v-tabs-window>
            </v-sheet>
          </v-col>
        </v-row>
      </v-container>
    </div>
    </v-main>
  </v-app>
</template>

<script setup>
import { ref } from 'vue'
import TableMajorComponent from './table_major.vue'
import TableUserComponent from './table_user.vue'
import TableRepoComponent from './table_repo.vue'

const dialog = ref(false)
const table_tab = ref('subject')
</script>

<script>
export default {
  name: 'DashboardComponent',
  components: {
    TableMajorComponent,
    TableUserComponent,
    TableRepoComponent,
  },
  data() {
    return {
      tab1: null, // 첫 번째 탭 그룹의 v-model,
      tab2: null, // 두 번째 탭 그룹의 v-model,
      headers: [
        { text: 'StudentID', value: 'StudentID' },
        { text: 'StudentNM', value: 'StudentNM' },
        { text: 'Department', value: 'Department' },
        { text: 'DoubleMajor', value: 'DoubleMajor' },
        { text: 'StudentNumber', value: 'StudentNumber' },
        { text: 'College', value: 'College' },
        { text: 'Primary_Email', value: 'Primary_Email' },
        { text: 'EnrollmentStatus', value: 'EnrollmentStatus' },
        { text: 'Follower_cnt', value: 'Follower_cnt' },
        { text: 'Following_cnt', value: 'Following_cnt' },
        { text: 'Public_repos_cnt', value: 'Public_repos_cnt' },
        {
          text: 'Github_profile_createDate',
          value: 'Github_profile_createDate',
        },
        {
          text: 'Github_profile_updateDate',
          value: 'Github_profile_updateDate',
        },
        { text: 'Actions', value: 'actions', sortable: false },
      ],
      items: [
        // 예제 데이터
      ],
      editedIndex: -1,
      editedItem: {
        // 초기화된 항목 데이터
      },
      defaultItem: {
        // 기본 항목 데이터
      },
      // search: '',
      // years: ['2024', '2023', '2022', '2021'],
      // selectedYears: [],
    }
  },
  computed: {
    formTitle() {
      return this.editedIndex === -1 ? 'New Item' : 'Edit Item'
    },
  },
  methods: {
    editItem(item) {
      this.editedIndex = this.items.indexOf(item)
      this.editedItem = Object.assign({}, item)
      this.dialog = true
    },
    deleteItem(item) {
      const index = this.items.indexOf(item)
      if (confirm('Are you sure you want to delete this item?')) {
        this.items.splice(index, 1)
      }
    },
    close() {
      this.dialog = false
      setTimeout(() => {
        this.editedItem = Object.assign({}, this.defaultItem)
        this.editedIndex = -1
      }, 300)
    },
    save() {
      if (this.editedIndex > -1) {
        Object.assign(this.items[this.editedIndex], this.editedItem)
      } else {
        this.items.push(this.editedItem)
      }
      this.close()
    },
    reset() {
      this.items = []
      this.initialize()
    },
    initialize() {
      // 초기 데이터를 추가하는 부분입니다.
    },
    goToStatistic() {
    this.$router.push('/dashboard/stats');
    },
    goToDashboard() {
    this.$router.push('/dashboard');
    },
  },
}
</script>

<style>
/* 절대 위치 스타일 */
.absolute-tab {
  position: absolute;
  top: 0;
  left: 0;
  z-index: 1000; /* 필요에 따라 z-index 조정 */
  background-color: white; /* 필요에 따라 배경색 조정 */
}
.sidebar_filter_box {
  float: left;
  width: 150px;
  height: 520px;
  border-radius: 3px; 
  background-color: #008485;
  padding: 16px;
  margin-left: 60px;
  margin-top: 16px;
  margin-right: 32px;
}
.row_bar {
  color: black;
  .v-btn__prepend{
    color: blue;
  }
}
.row_bar > .v-slide-group__container > .v-slide-group__content > button:hover{
  .v-btn__content{
    color: red;
  }
}

.user_font {
  .v-btn__content{
    font-weight: bold;
  }
}

.bg-grey-lighten-3{
  padding-top: 16px !important;
}
</style>