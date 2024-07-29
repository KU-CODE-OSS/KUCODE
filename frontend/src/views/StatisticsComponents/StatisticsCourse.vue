<template>
  <div class="container">
    <div class="import-overlay" v-show="this.showOverlay" v-on:click="changeOverlay">
      <div class="pannel-container" @click.stop>
        <div class="pannel-top">
          <div class="text">Import Course</div>
          <div class="exit-svg" v-on:click="changeOverlay">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path fill-rule="evenodd" clip-rule="evenodd" d="M11.9498 13.364C12.3403 13.7545 12.9734 13.7545 13.364 13.364C13.7545 12.9734 13.7545 12.3403 13.364 11.9497L8.41424 7.00002L13.364 2.05031C13.7545 1.65978 13.7545 1.02662 13.364 0.636092C12.9734 0.245567 12.3403 0.245567 11.9497 0.636092L7.00003 5.5858L2.05026 0.636033C1.65973 0.245508 1.02657 0.245509 0.636045 0.636033C0.24552 1.02656 0.24552 1.65972 0.636045 2.05025L5.58582 7.00002L0.636033 11.9498C0.245508 12.3403 0.245509 12.9735 0.636033 13.364C1.02656 13.7545 1.65972 13.7545 2.05025 13.364L7.00003 8.41423L11.9498 13.364Z" fill="#262626"/>
            </svg>
          </div>
        </div>
      </div>
    </div>
    <div class="navigation">
      <div class="menu">
        <div class="default-router plan-text current-tab">과목</div>
      </div>
      <div class="menu">
        <router-link v-bind:to="'/statistics/students'" class="default-router plan-text" append>학생</router-link>
      </div>
      <div class="menu">
        <router-link v-bind:to="'/statistics/repos'" class="default-router plan-text" append>레포지토리</router-link>
      </div>
      <div class="import-btn">
        <div class="import-btn-svg">
          <svg id="svg-icon" xmlns="http://www.w3.org/2000/svg" width="20" height="18" viewBox="0 0 20 18" fill="none">
            <path d="M4.75 0.25C2.12665 0.25 0 2.37665 0 5V13C0 15.6234 2.12665 17.75 4.75 17.75H12C14.6234 17.75 16.75 15.6234 16.75 13C16.75 12.5858 16.4142 12.25 16 12.25C15.5858 12.25 15.25 12.5858 15.25 13C15.25 14.7949 13.7949 16.25 12 16.25H7.46412C8.26157 15.4003 8.75 14.2572 8.75 13V5C8.75 3.74279 8.26157 2.59965 7.46412 1.75H12C13.7949 1.75 15.25 3.20507 15.25 5C15.25 5.41421 15.5858 5.75 16 5.75C16.4142 5.75 16.75 5.41421 16.75 5C16.75 2.37665 14.6234 0.25 12 0.25H4.75Z" fill="#CB385C"/>
            <path d="M13.5302 6.46967C13.8231 6.76256 13.8231 7.23744 13.5302 7.53033L12.8105 8.25L19.2499 8.25C19.6641 8.25 19.9999 8.58579 19.9999 9C19.9999 9.41421 19.6641 9.75 19.2499 9.75L12.8105 9.75L13.5302 10.4697C13.8231 10.7626 13.8231 11.2374 13.5302 11.5303C13.2373 11.8232 12.7624 11.8232 12.4695 11.5303L11.1766 10.2374C10.4932 9.55402 10.4932 8.44598 11.1766 7.76256L12.4695 6.46967C12.7624 6.17678 13.2373 6.17678 13.5302 6.46967Z" fill="#CB385C"/>
          </svg>
          <div class="import-btn-svg-text" v-on:click="changeOverlay">Import</div>
        </div>
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
        <div v-if="!showTable" class="table">
          <table class="table-over" style="table-layout: fixed"> 
            <thead class="table-header-wrapper"><th class="table-header" v-for="item in header" v-bind:style="{width: tablewidth(item[1])}">{{item[0]}}</th></thead>
            <tbody>
              <tr v-for="item in posts" class="table-row">
                <!-- {{item}} -->
                <td>{{item.yearandsemester}}</td>
                <td>{{item.course_name}}</td>
                <td>{{item.course_id}}</td>
                <td>{{item.prof}}</td>
                <td>{{item.students}}</td>
                <td>{{item.commit}}</td>
                <td>{{item.pr}}</td>
                <td>{{item.issue}}</td>
                <td>{{item.num_repos}}</td>
              </tr>
            </tbody>
          </table>
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
import {getCourseInfo} from '@/api.js'
export default {
  name: 'StatisticsCourse',
  props: ["postss"],
  data() {
    return {
      showOverlay: false,
      showTable: false,
      searchField: '',
      posts: [],
      currentPage: 1,
      postsPerPage: 10,
      header : [['개설학기', '9%'], 
                ['과목명', '14%'], 
                ['학수번호', '11%'], 
                ['지도교수', '11%'], 
                ['수강생', '11%'],
                ['Commit', '11%'], 
                ['PR', '11%'], 
                ['Issue', '11%'], 
                ['Repos', '11%']]
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
    changeOverlay() {
      this.showOverlay = !this.showOverlay
    },
    tablewidth(length) {
      return length
    },
  },
  mounted() {
    this.posts = this.postss
  },
  watch: {
    postss(to, from) {
      const vm = this
      this.posts = vm.postss
    },
  }
};
</script>

<style scoped>
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
  }
  .import-btn {
    margin-left: auto;
    min-height: 34px;
    min-width: 117px;
    margin-right: 60px;
    /* padding-top:5px;
    padding-bottom: 5px; */
    padding: 5px 18px;
    
    border-radius: 10px;
    border: 1px solid var(--Primary_medium, #CB385C);
    background: #fff4f5;
    cursor: pointer;
    &:hover {
      background: #ffe9eb;
    }
    .import-btn-svg {
      display: flex;
      align-items: center;
      /* background-color: red; */
      height: 24px;
      #svg-icon {
        /* margin: 0 auto; */
        display: block;
      }
      .import-btn-svg-text {
        display: block;
        margin-left: 8px;
        font-size: 16px;
        font-style: normal;
        font-weight: 500;
        line-height: normal;
        color: var(--Primary_medium, #CB385C);
      }
    }
  }
  .search-box {
    min-height: 44px;
    margin-left: 0;
    align-self: flex-end;
    padding-bottom: 4px;
    margin-right: 26px;

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
      transition: border-bottom 0.2s ease-in-out;;
      transition: border-image 0.2s ease-in-out;
      font-size: 1.1rem;
      &::placeholder {
        color: transparent;
      }
    
      &:placeholder-shown ~ .form__label {
        font-size: 18px;
        cursor: text;
      }
    }
    
    .form__label {
      position: absolute;
      top: 5px;
      display: block;
      transition: 0.2s;
      color: #9b9b9b;
      font-size: 1.1rem;
      pointer-events: none;
    }
    
    .form-field:focus {
      ~ .form__label {
        position: absolute;
        top: -25px;
        display: block;
        transition: 0.2s;
        font-size: 1rem;
        color: #CB385C;
        font-weight: 700;
      }
      padding-bottom: 6px;
      font-weight: 700;
      border-width: 3px;
      border-image: linear-gradient(to right, #CB385C, #FFF4F5);
      transition: opacity 1s;
      border-image-slice: 1;
      color: #862633;
    }
    .form-field:focus::before, .form-field:focus::after{
        transition: 0.2s ease-in-out;
    }
    /* reset input */
    .form-field {
      &:required,
      &:invalid {
        box-shadow: none;
      }
    }

  }

  .toggle-box {
    .wrapper {
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
    #switch:checked + .switch_label .onf_btn {
        left: 70px;
        background: #fff;
        box-shadow: 1px 2px 3px #00000020;
    }
    #switch:checked + .switch_label .toggle-image-1 {
        & path {
            stroke: #E9D8D9;
        }
    }
    #switch:checked + .switch_label .toggle-image-2 {
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

.table,
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

.import-overlay {
  position: fixed;
  height: 100vh;
  display: -webkit-box;
  display: -webkit-flex;
  display: -ms-flexbox;
  display: flex;
  -webkit-box-align: center;
  -webkit-align-items: center;
  -ms-flex-align: center;
  align-items: center;
  top: 0;
  left: 0;
  height: 100vh;
  width: 100vw;
  background: rgba(0, 0, 0, 0.41);
  z-index: 1000;
  .pannel-container {
    margin: 0 auto;
    width: 710px;
    height: 550px;
    flex-shrink: 0;
    border-radius: 10px;
    background: #FFF;

    .pannel-top {
      height: 74px;
      .text {
        display: block;
        height: 24px;
        line-height: 24px;
        font-size: 20px;
        font-style: normal;
        font-weight: 600;
        margin-left: 50px;
        margin-top: 30px;
        float: left;

      }
      .exit-svg {
        display: block;
        margin-left: auto;
        margin-top: 26px;
        margin-right: 50px;
        float: right;
        width: 32px;
        height: 32px;
        line-height: 32px;
        z-index: 1002;
        cursor: pointer;
      }
    }
  }
}
</style>
