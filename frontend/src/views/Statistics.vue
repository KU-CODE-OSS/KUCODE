<template>
  <div class="default-container">
    <div class="left-split">
      <div class="empty-box"></div>
      <div class="filter-box">
        <div class="filter-title-box">
          <div>
            <div style="display: inline-block" class="title">필터</div>
            <div style="display: inline-block; padding-left: 50%">
              <v-btn class="init" variant="outlined">초기화</v-btn>
            </div>
            <portal-target name="stat_table_major">
            </portal-target> 
            <portal-target name="stat_table_user">
            </portal-target> 
          </div>
        </div>
      </div>
    </div>
    <div class="right-split">
      <div class="title">{{titles}}</div>
      <router-view></router-view>
    </div>
  </div>
</template>

<script>
  // import Filters from './StatisticsComponents/table/Filters.vue'
  import TableUser from './StatisticsComponents/table/table_user.vue'
  import TableMajor from './StatisticsComponents/table/table_major.vue'

  export default {
    name: 'Statistics',
    components: {
      // Filters,
      TableUser,
      TableMajor,
    },
    data() {
      return {
        titles: '',
        // students: [],
        // search: '',
        // filteredStudents: [],
      }
    },
    mounted() {
      this.setTitles()
    },
    methods: {
      // updateFilteredStudents(filteredStudents) {
      //   this.filteredStudents = filteredStudents
      // },
      setTitles() {
        if (this.$route.name === 'StatisticsCourse') {
          this.titles = '과목 통계'
        } else if (this.$route.name === 'StatisticsStudent') {
          this.titles = '학생 통계'
        } else if (this.$route.name === 'StatisticsRepos') {
          this.titles = '레포지토리 통계'
        }
      },
    },
    beforeMount() {
      if (this.$route.fullPath === '/statistics') {
        this.$router.replace('/statistics/course')
      }
    },
    watch: {
      $route(to, from) {
        if (to.path !== from.path) this.setTitles()
      },
    },
  }
</script>

<style>
  .default-container {
    display: flex;
    width: 100vw;
    height: calc(100rem - 100px);
    background: var(--White, #fcfcfc);
    overflow: hidden; /* Ensure no overflow issues */
  }
  .default-container {
    display: flex;
    width: 100vw;
    height: calc(100rem - 100px);
    background: var(--White, #fcfcfc);
    overflow: hidden; /* Ensure no overflow issues */
  }

  .left-split {
    margin-left: 220px;
    width: 300px !important;
    min-width: 300px;
    height: 100em;
    border-right: 2px solid;
    border-right-color: #dce2ed;
    .empty-box {
      width: 100em;
      margin-bottom: 166px;
    }
    .filter-box {
      height: 100%;
      .filter-title-box {
        height: 40px;
        display: flex;
        flex-wrap: nowrap;
        .title {
          font-size: 22px;
          font-weight: 600;
        }
        .init {
          margin-left: auto;
          margin-right: 15px;
          background-color: white;
          /* &:hover {
          background-color: #862633;
          opacity: 0.2;
        } */
          .v-btn__content {
            font-weight: 600 !important;
            color: #862633 !important;
          }
          &.v-btn--variant-outlined {
            border-color: #862633;
            border-radius: 12px !important;
            border-width: 2px;
          }
        }
      }
    }
  }

  .right-split {
    width: 100%;
    margin-right: 320px;
    .title {
      font-size: 28px;
      font-weight: 700;
      margin-top: 57px;
      margin-left: 57px;
      min-height: 45px;
      margin-bottom: 64px;
    }
  }
</style>
