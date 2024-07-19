<template>
  <v-card flat>
    <!-- <template v-slot:text>
      <v-col cols="5">
        <v-text-field class="search-container"
            v-model="search"
            label="Search"
            prepend-inner-icon="mdi-magnify"
            variant="outlined"
            hide-details
            single-line
        ></v-text-field>
      </v-col>
    </template> -->

    <v-data-table
      :headers="headers"
      :items="repo"
      :search="search"
      :loading="loading"
      align-items="center"
      fixed-header
      height="600px"
      class="text-center"
    ></v-data-table>
  </v-card>
</template>

<script>
  import axios from 'axios'

  export default {
    data() {
      return {
        loading: true,
        search: '',
        headers: [
          {
            align: 'center',
            key: 'name',
            sortable: false,
            title: '레포지토리', fixed: true, width: '20%'
          },
          { align: 'center', key: 'star_count', title: '스타 수', width: '10%' },
          { align: 'center', key: 'fork_count', title: '포크 수', width: '10%' },
          { align: 'center', key: 'commit_count', title: '커밋 수', width: '10%' },
          { align: 'center', key: 'pr_count', title: 'PR 수', width: '10%' },
          { align: 'center', key: 'total_issue_count', title: '이슈 수', width: '10%' },
          { align: 'center', key: 'language', title: '언어', fixed: true, width: '20%' },
          { align: 'center', key: 'contributors', title: '기여자 수', width: '10%' },
        ],
        repo: [],
      }
    },
    created() {
      this.fetchRepo()
    },
    methods: {
      async fetchRepo() {
        try {
          this.loading = true
          const response = await axios.get(
            'http://localhost/api/repo/repo_read_db'
          )
          this.processTotal(response.data)
          // console.log('Total Data:', response.data)
        } catch (error) {
          console.error('Error fetching data:', error)
        } finally {
          this.loading = false
        }
      },
      processTotal(data) {
        const repoInfo = {}

        data.forEach(repoItem => {
          // console.log('repo Item:', repoItem.name)
          repoInfo[repoItem.id] = {
            name: repoItem.name,
            star_count: repoItem.star_count,
            fork_count: repoItem.fork_count,
            commit_count: repoItem.commit_count,
            pr_count: repoItem.pr_count,
            total_issue_count: repoItem.total_issue_count,
            language: repoItem.language,
            contributors: repoItem.contributors,
          }
        })

        // console.log('repo Info:', repoInfo)
        this.repo = Object.values(repoInfo)
      },
    },
  }
</script>

<style scoped>
.search-container {
  justify-content: flex-end;
  margin-bottom: 10px;
  align-content: center;
}

.text-center th,
.text-center td {
  text-align: center !important;
}
</style>
