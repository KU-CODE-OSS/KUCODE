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

        <v-btn @click="goToDashboard">이름미정</v-btn>
        <v-btn>정보관리</v-btn> 
        <v-btn @click="goToStatistic">통계분석</v-btn>
        <v-btn>커뮤니티</v-btn>
        <v-btn>공지사항</v-btn>


        <v-spacer></v-spacer>

        <v-responsive max-width="160">
          <v-text-field
            density="compact"
            label="Search"
            rounded="lg"
            variant="solo-filled"
            flat
            hide-details
            single-line
          ></v-text-field>
        </v-responsive>
      </v-container>
    </v-app-bar>

    <v-main class="bg-grey-lighten-3">
      <v-container>
        <v-row>
          <v-col cols="2">
            <v-sheet rounded="lg">
              <v-list rounded="lg">
                <div class="d-flex flex-row">
                  <v-tabs v-model="tab" color="primary" direction="vertical">
                    <v-tab
                      prepend-icon="mdi-account"
                      text="내 정보"
                      value="option-1"
                    ></v-tab>
                    <v-tab
                      prepend-icon="mdi-lock"
                      text="코스"
                      value="option-2"
                    ></v-tab>
                    <v-tab
                      prepend-icon="mdi-access-point"
                      text="전체 통계"
                      value="option-3"
                    ></v-tab>
                    <v-tab
                      prepend-icon="mdi-access-point"
                      text="Option 4"
                      value="option-4"
                    ></v-tab>
                    <v-tab
                      prepend-icon="mdi-access-point"
                      text="Option 5"
                      value="option-5"
                    ></v-tab>
                  </v-tabs>
                </div>

                <v-divider class="my-2"></v-divider>

                <v-list-item
                  color="grey-lighten-4"
                  title="Refresh"
                  link
                ></v-list-item>
              </v-list>
            </v-sheet>
          </v-col>

          <v-col>
            <v-sheet min-height="70vh" rounded="lg">
              <v-tabs-window v-model="tab">
                <v-tabs-window-item value="option-1">
                  <v-card flat>
                    <v-card-text>
                      <p>
                        Sed aliquam ultrices mauris. Donec posuere vulputate
                        arcu. Morbi ac felis. Etiam feugiat lorem non metus. Sed
                        a libero.
                      </p>

                      <p>
                        Nam ipsum risus, rutrum vitae, vestibulum eu, molestie
                        vel, lacus. Aenean tellus metus, bibendum sed, posuere
                        ac, mattis non, nunc. Aliquam lobortis. Aliquam
                        lobortis. Suspendisse non nisl sit amet velit hendrerit
                        rutrum.
                      </p>

                      <p class="mb-0">
                        Phasellus dolor. Fusce neque. Fusce fermentum odio nec
                        arcu. Pellentesque libero tortor, tincidunt et,
                        tincidunt eget, semper nec, quam. Phasellus blandit leo
                        ut odio.
                      </p>
                    </v-card-text>
                  </v-card>
                </v-tabs-window-item>

                <v-tabs-window-item value="option-2">
                  <div>
                    <v-container>
                      <v-row justify="center">
                        <!-- 중앙 정렬 -->
                        <v-col cols="12" md="6">
                          <!-- 중간 크기의 화면에서 6열 사용 -->
                          <v-tabs
                            v-model="tab2"
                            color="primary"
                            direction="vertical"
                          >
                            <v-tab
                              prepend-icon="mdi-account"
                              text="운영체제"
                            ></v-tab>
                            <v-tab
                              prepend-icon="mdi-lock"
                              text="컴퓨터 구조"
                            ></v-tab>
                            <v-tab
                              prepend-icon="mdi-access-point"
                              text="네트워크"
                            ></v-tab>
                            <v-tab
                              prepend-icon="mdi-access-point"
                              text="데이터 베이스"
                            ></v-tab>
                          </v-tabs>
                        </v-col>
                      </v-row>
                    </v-container>
                  </div>
                </v-tabs-window-item>

                <v-tabs-window-item value="option-3">
                  <v-card flat>
                    <v-card-text>
                      <p>
                        Fusce a quam. Phasellus nec sem in justo pellentesque
                        facilisis. Nam eget dui. Proin viverra, ligula sit amet
                        ultrices semper, ligula arcu tristique sapien, a
                        accumsan nisi mauris ac eros. In dui magna, posuere
                        eget, vestibulum et, tempor auctor, justo.
                      </p>

                      <p class="mb-0">
                        Cras sagittis. Phasellus nec sem in justo pellentesque
                        facilisis. Proin sapien ipsum, porta a, auctor quis,
                        euismod ut, mi. Donec quam felis, ultricies nec,
                        pellentesque eu, pretium quis, sem. Nam at tortor in
                        tellus interdum sagittis.
                      </p>
                    </v-card-text>
                  </v-card>
                </v-tabs-window-item>

                <v-tabs-window-item value="option-4">
                  <table-component />
                </v-tabs-window-item>

                <v-tabs-window-item value="option-5">
                  <v-card flat>
                    <v-card-text>
                      <p>
                        Fusce a quam. Phasellus nec sem in justo pellentesque
                        facilisis. Nam eget dui. Proin viverra, ligula sit amet
                        ultrices semper, ligula arcu tristique sapien, a
                        accumsan nisi mauris ac eros. In dui magna, posuere
                        eget, vestibulum et, tempor auctor, justo.
                      </p>

                      <p class="mb-0">
                        Cras sagittis. Phasellus nec sem in justo pellentesque
                        facilisis. Proin sapien ipsum, porta a, auctor quis,
                        euismod ut, mi. Donec quam felis, ultricies nec,
                        pellentesque eu, pretium quis, sem. Nam at tortor in
                        tellus interdum sagittis.
                      </p>
                    </v-card-text>
                  </v-card>
                </v-tabs-window-item>
              </v-tabs-window>
            </v-sheet>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup>
  import { ref } from 'vue'
  import TableComponent from './table.vue'

  const dialog = ref(false)
  const tab = ref('option-1')
  const links = ref(['정보관리', '통계분석', '커뮤니티', '공지사항']) 
  //<v-btn v-for="link in links" :key="link" text> {{ link }} </v-btn>
</script>

<script>
  export default {
    name: 'DashboardComponent',
    components: { TableComponent, // table.vue 컴포넌트를 등록
  },
    setup() {
      return { dialog, tab, links }
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
