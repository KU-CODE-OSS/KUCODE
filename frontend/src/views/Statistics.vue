<template>
  <div class="default-container">
    <div class="left-split">
      <div class="empty-box"></div>
      <div class="filter-box">
        <div class="filter-title-box">
          <div class="title">필터</div>
          <v-btn class="init" variant="outlined">초기화</v-btn>
        </div>
      </div>
    </div>
    <div class="right-split">
      <div class="title">
        {{titles}}
      </div>
      <router-view></router-view>
    </div>
  </div> 
</template>

<script>
export default {
  name: 'Statistics',
  data() {
    return {
      titles: '',
    };
  },
  mounted() {
    this.setTitles()
  },
  methods: {
    setTitles() {
      if(this.$route.name === "StatisticsCourse") {
        this.titles = '과목 통계'
      }
      else if(this.$route.name === "StatisticsStudent") {
        this.titles = '학생 통계'
      }
      else if(this.$route.name === "StatisticsRepos") {
        this.titles = '레포지토리 통계'
      }
    }
  },
  beforeMount() {
    if(this.$route.fullPath === "/statistics") {
      this.$router.replace('/statistics/course')
    }
  },
  watch: {
    $route(to, from) {
      if (to.path !== from.path) this.setTitles()
    },
  }
}
</script>

<style>
.default-container {
  /* position: relative; */
  display: flex;
  justify-content: flex-start;
  align-items: center;
  width: 100%;
  margin-top: 120px;
  height: 100vh;
  background: var(--White, #FCFCFC);
  overflow: hidden; /* Ensure no overflow issues */
}


.left-split {
  margin-left: 320px;
  width: 268px !important;
  min-width: 268px;
  height: 100vh;
  border-right: 2px solid;
  border-right-color: #DCE2ED;
  .empty-box {
    width: 100em;
    margin-bottom: 117px;
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
  height: 100vh;
  .title {
    font-size: 28px;
    font-weight: 700;
    margin-top: 57px;
    margin-left: 57px;
    height:33px;
    min-height: 33px;
    margin-bottom: 34px;
  }
}


</style>
