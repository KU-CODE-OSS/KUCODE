<template>
  <div class="container">
    <div class="navigation">
      <div class="menu">
        <router-link v-bind:to="'/info/course'" class="default-router plan-text" append>과목</router-link>
      </div>
      <div class="menu">
        <router-link v-bind:to="'/info/students'" class="default-router plan-text" append>학생</router-link>
      </div>
      <div class="menu">
        <div class="default-router plan-text current-tab">레포지토리</div>
      </div>
      <div class="search-box">
      <div class="form__group field">
        <input type="input" class="form-field" :value="searchField" />
        <label class="form__label">SEARCH</label>
      </div>
      </div>
    </div>
    <div class="navigation_underline"></div>
    <div class="contents-box">
      <div class="table">Table Content</div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'InformationRepos',
  data() {
    return {
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
  .search-box {
    min-height: 44px;
    margin-left: auto;
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

    #infoswitchrepos {
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
    #infoswitchrepos:checked + .switch_label .onf_btn {
        left: 70px;
        background: #fff;
        box-shadow: 1px 2px 3px #00000020;
    }
    #infoswitchrepos:checked + .switch_label .toggle-image-1 {
        & path {
            stroke: #E9D8D9;
        }
    }
    #infoswitchrepos:checked + .switch_label .toggle-image-2 {
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

.table,
.chart {
  margin: 20px 0;
  padding: 20px 0;
  border: 1px solid #dce2ed;
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
</style>
