<template>
  <div class="container" :class="{cursorblock: pannelLoading === true}">
    <div class="navigation">
      <div class="menu">
        <router-link v-bind:to="'/statistics/students'" class="default-router plan-text" append>전체</router-link>
      </div>
      <div class="menu">
        <div class="default-router plan-text current-tab">과목별</div>
      </div>
      <div class="menu">
        <router-link v-bind:to="'/statistics/department'" class="default-router plan-text" append>학과별</router-link>
      </div>
      <div class="toggle-box" @click.self.prevent="toggle">
        <div class="wrapper">
          <input type="checkbox" id="switchcourse" v-model="showTable">
          <label for="switchcourse" class="switch_label">
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
        <div v-if="!showTable" class="table">
          <div class="course-title">{{title}}</div>
          <div class="all-table">
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
                      <td :title="item.course_id">{{ item.course_id_for_stats }}</td>
                      <td :title="item.students">{{item.students}}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            <div class="sub-table-right">
              <div class="title">학생별 Repos</div>
              <div class="sub-table">
                <table>
                  <thead class="table-header-wrapper">
                    <th>합계</th>
                    <th>최솟값</th>
                    <th>최댓값</th>
                    <th>평균</th>
                  </thead>
                  <tbody class="table-body-wrapper">
                    <tr v-for="(item, index) in posts" :key="item[0]">
                      <td :title="item.students">{{item.num_repos_stats.sum}}</td>
                      <td :title="item.students">{{item.num_repos_stats.min}}</td>
                      <td :title="item.students">{{item.num_repos_stats.max}}</td>
                      <td :title="item.students">{{item.num_repos_stats.mean}}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            <!-- 줄 바뀜 -->
            <div class="sub-table-left">
              <div class="title">학생별 Commits</div>
              <div class="sub-table">
                <table>
                  <thead class="table-header-wrapper">
                    <th>합계</th>
                    <th>최솟값</th>
                    <th>최댓값</th>
                    <th>평균</th>
                  </thead>
                  <tbody class="table-body-wrapper">
                    <tr v-for="(item, index) in posts" :key="item[0]">
                      <td :title="item.students">{{item.commit_stats.sum}}</td>
                      <td :title="item.students">{{item.commit_stats.min}}</td>
                      <td :title="item.students">{{item.commit_stats.max}}</td>
                      <td :title="item.students">{{item.commit_stats.mean}}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            <div class="sub-table-right">
              <div class="title">학생별 Issues</div>
              <div class="sub-table">
                <table>
                  <thead class="table-header-wrapper">
                    <th>합계</th>
                    <th>최솟값</th>
                    <th>최댓값</th>
                    <th>평균</th>
                  </thead>
                  <tbody class="table-body-wrapper">
                    <tr v-for="(item, index) in posts" :key="item[0]">
                      <td :title="item.students">{{item.issue_stats.sum}}</td>
                      <td :title="item.students">{{item.issue_stats.min}}</td>
                      <td :title="item.students">{{item.issue_stats.max}}</td>
                      <td :title="item.students">{{item.issue_stats.mean}}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            <!-- 줄 바뀜 -->
            <div class="sub-table-left">
              <div class="title">학생별 PRs</div>
              <div class="sub-table">
                <table>
                  <thead class="table-header-wrapper">
                    <th>합계</th>
                    <th>최솟값</th>
                    <th>최댓값</th>
                    <th>평균</th>
                  </thead>
                  <tbody class="table-body-wrapper">
                    <tr v-for="(item, index) in posts" :key="item[0]">
                      <td :title="item.students">{{item.pr_stats.sum}}</td>
                      <td :title="item.students">{{item.pr_stats.min}}</td>
                      <td :title="item.students">{{item.pr_stats.max}}</td>
                      <td :title="item.students">{{item.pr_stats.mean}}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            <div class="sub-table-right">
              <div class="title">학생별 Stars</div>
              <div class="sub-table">
                <table>
                  <thead class="table-header-wrapper">
                    <th>합계</th>
                    <th>최솟값</th>
                    <th>최댓값</th>
                    <th>평균</th>
                  </thead>
                  <tbody class="table-body-wrapper">
                    <tr v-for="(item, index) in posts" :key="item[0]">
                      <td :title="item.students">{{item.stars_stats.sum}}</td>
                      <td :title="item.students">{{item.stars_stats.min}}</td>
                      <td :title="item.students">{{item.stars_stats.max}}</td>
                      <td :title="item.students">{{item.stars_stats.mean}}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="chart">
          <div class="year-chart-container">
            <div class="title">연도별 데이터</div>
          </div>
          <div class="category-chart-container">
            <div class="title">카테고리별 상세 데이터</div>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StatisticsCourse',
  props: ["course"],
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
      title: '',
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
      return length
    },
    allStudentToggleButton() {
      this.subToggleButton = false
      this.$router.replace({ path: this.$route.path, query: { type: 'all' } });
    },
    eachStudentToggleButton() {
      this.subToggleButton = true
      this.$router.replace({ path: this.$route.path, query: { type: 'each' } });
    },
    renamedTitle() {
      console.log(this.posts)
      if(this.posts.length === 0) {
        this.title = '과목을 선택하세요.'
      }
      else if(this.posts[0].course_name === '기타') {
        this.title = '기타'
      } else {
        this.title = this.posts[0].course_name + ' (' + this.posts[0].course_id + ')'
      }
    },
  },
  mounted() {
    this.posts = this.course
    this.renamedTitle()
  },
  watch: {
    course(to, from) {
      const vm = this
      this.posts = vm.course
      this.renamedTitle()
    },
  }
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
      margin: 30px 0 20px 0;
      padding-bottom: 20px;
      /* border: 1px solid #dce2ed; */
      border-radius: 4px;
      height: 100%;

      .course-title {
        color: var(--Black, #262626);
        font-family: Pretendard;
        font-size: 20px;
        font-style: normal;
        font-weight: 700;
        height: 24px;
        line-height: 24px;
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
            position : sticky;
            display:block;
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
            position : sticky;
            display:block;
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
      height: 44px;
      text-align: center;
      margin: 0 auto;
      position: relative;
    }

    #switchcourse {
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
        .img1, .img2 {
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
    #switchcourse:checked + .switch_label .onf_btn {
        left: 70px;
        background: #fff;
        box-shadow: 1px 2px 3px #00000020;
    }
    #switchcourse:checked + .switch_label .toggle-image-1 {
        & path {
            stroke: #E9D8D9;
        }
    }
    #switchcourse:checked + .switch_label .toggle-image-2 {
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
  .table-header-wrapper{
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

.chart {
  margin: 20px 0;
  padding: 20px 0;
  /* border: 1px solid #dce2ed; */
  border-radius: 4px;
  height: 100%;
  .year-chart-container {
  
    
  }
  .category-chart-container {

  }
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
