<template>
  <div class="ranking-page">
    <div class="ranking-shell">
      <aside class="ranking-filter">
        <div class="filter-header">
          <p class="filter-label">랭킹 필터</p>
          <button class="reset-button" type="button" @click="resetFilters">초기화</button>
        </div>

        <label class="filter-field">
          <span>연도</span>
          <select v-model="selectedYear" :disabled="loading || years.length === 0">
            <option v-if="years.length === 0" value="" disabled>{{ loading ? '불러오는 중' : '연도 없음' }}</option>
            <option v-for="year in years" :key="year" :value="year">{{ year }}년</option>
          </select>
        </label>

        <label class="filter-field">
          <span>학기</span>
          <select v-model="selectedSemester" :disabled="loading || semesters.length === 0">
            <option v-if="semesters.length === 0" value="" disabled>{{ loading ? '불러오는 중' : '학기 없음' }}</option>
            <option v-for="semester in semesters" :key="semester" :value="semester">{{ semester }}학기</option>
          </select>
        </label>

        <label class="filter-field">
          <span>과목</span>
          <select v-model="selectedCourseKey" :disabled="loading || filteredCourses.length === 0">
            <option v-if="filteredCourses.length === 0" value="" disabled>{{ loading ? '불러오는 중' : '과목 없음' }}</option>
            <option v-for="course in filteredCourses" :key="course.key" :value="course.key">
              {{ course.course_id }} - {{ course.course_name }}
            </option>
          </select>
        </label>
      </aside>

      <main class="ranking-content">
        <section class="ranking-summary">
          <div>
            <p class="eyebrow">과목별 수상자</p>
            <h1>{{ selectedCourseTitle }}</h1>
            <p class="summary-meta">{{ summaryMeta }}</p>
          </div>
        </section>

        <section class="winner-strip" v-if="awardCandidates.length">
          <article
            v-for="student in awardCandidates"
            :key="student.student_id"
            class="winner-card"
            :class="`rank-${student.rank}`"
          >
            <div class="winner-rank">{{ student.rank }}위</div>
            <div>
              <strong>{{ student.name }}</strong>
              <span>{{ student.department }} · {{ student.student_id }}</span>
            </div>
            <p>{{ student.score }}점</p>
          </article>
        </section>

        <section class="ranking-table-card">
          <div class="table-top">
            <div>
              <h2>랭킹 목록</h2>
              <p>동점자는 이름 순으로 정렬됩니다.</p>
            </div>
            <div class="table-tools">
              <div class="search-box">
                <input v-model="searchKeyword" type="search" placeholder="이름, 학번, Github 검색" :disabled="loading || rows.length === 0" />
              </div>

              <div ref="tableSettings" class="table-settings" @keydown.esc.stop="closeTableSettings">
                <button
                  class="settings-button"
                  type="button"
                  :aria-expanded="tableSettingsOpen"
                  aria-controls="ranking-table-settings"
                  aria-haspopup="dialog"
                  :disabled="loading || rows.length === 0"
                  @click.stop="toggleTableSettings"
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                    <path d="M4 7H14M18 7H20M4 17H10M14 17H20M14 4V10M10 14V20" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                  </svg>
                  열/필터
                </button>

                <div
                  v-if="tableSettingsOpen"
                  id="ranking-table-settings"
                  class="settings-menu"
                  role="dialog"
                  aria-label="랭킹 목록 열 및 필터 설정"
                  @click.stop
                >
                  <div class="settings-header">
                    <div>
                      <strong>표 설정</strong>
                      <p>점수 열은 현재 위치에 고정됩니다.</p>
                    </div>
                    <button type="button" class="settings-reset" @click="resetTableSettings">전체 초기화</button>
                  </div>

                  <section class="settings-section" aria-labelledby="visible-columns-title">
                    <h3 id="visible-columns-title">표시할 열</h3>
                    <p class="column-order-help">목록의 위에서 아래 순서대로 표의 왼쪽에서 오른쪽에 표시됩니다.</p>
                    <div class="column-checklist">
                      <label v-for="column in columnOptions" :key="column.key" class="column-check">
                        <input
                          type="checkbox"
                          :checked="isColumnSelected(column.key)"
                          :disabled="column.key === 'score'"
                          @change="toggleColumn(column.key, $event.target.checked)"
                        />
                        <span>{{ column.label }}</span>
                        <span v-if="column.key === 'score'" class="column-lock">고정</span>
                      </label>
                    </div>
                  </section>

                  <section class="settings-section filter-settings" aria-labelledby="row-filters-title">
                    <div class="section-title-row">
                      <h3 id="row-filters-title">목록 필터</h3>
                      <button v-if="activeFilterCount" type="button" @click="resetRowFilters">필터 초기화</button>
                    </div>
                    <div class="filter-setting-grid">
                      <label>
                        <span>학과</span>
                        <select v-model="selectedDepartment">
                          <option value="">전체 학과</option>
                          <option v-for="department in departments" :key="department" :value="department">{{ department }}</option>
                        </select>
                      </label>
                      <label>
                        <span>재학 상태</span>
                        <select v-model="selectedEnrollment">
                          <option value="">전체 상태</option>
                          <option v-for="enrollment in enrollments" :key="enrollment" :value="enrollment">{{ enrollment }}</option>
                        </select>
                      </label>
                    </div>
                  </section>

                  <button type="button" class="settings-done" @click="closeTableSettings">완료</button>
                </div>
              </div>
            </div>
          </div>

          <div class="table-scroll">
            <table class="ranking-table">
              <thead>
                <tr>
                  <th v-for="column in displayColumns" :key="column.key" :class="columnClasses(column)">
                    {{ column.label }}
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="student in paginatedStudents" :key="student.student_id" :class="{ podium: student.rank <= 3 }">
                  <td v-for="column in displayColumns" :key="column.key" :class="columnClasses(column)">
                    <span v-if="column.key === 'rank'" class="rank-badge">{{ student.rank }}</span>
                    <a
                      v-else-if="column.key === 'github' && student.github"
                      :href="`https://github.com/${student.github}`"
                      target="_blank"
                      rel="noopener"
                    >
                      {{ student.github }}
                    </a>
                    <template v-else>{{ formatColumnValue(student, column) }}</template>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div v-if="visibleStudents.length === 0" class="empty-state">
            {{ emptyStateMessage }}
          </div>

          <div v-if="visibleStudents.length > 0" class="pagination-container">
            <div class="pagination-wrapper">
              <button class="page-nav" type="button" :disabled="firstPageDisabled" @click="goToPage(1)">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                  <path d="M15 18L9 12L15 6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M19 18L13 12L19 6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </button>
              <button class="page-nav" type="button" :disabled="prevPageDisabled" @click="goToPage(currentPage - 1)">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                  <path d="M15 18L9 12L15 6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </button>
              <button
                v-for="page in pagesToShow"
                :key="page"
                class="page-number"
                type="button"
                :class="{ active: page === currentPage }"
                @click="goToPage(page)"
              >
                {{ page }}
              </button>
              <button class="page-nav" type="button" :disabled="nextPageDisabled" @click="goToPage(currentPage + 1)">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                  <path d="M9 18L15 12L9 6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </button>
              <button class="page-nav" type="button" :disabled="lastPageDisabled" @click="goToPage(totalPages)">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                  <path d="M9 18L15 12L9 6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M5 18L11 12L5 6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </button>
            </div>
          </div>
        </section>
      </main>
    </div>
  </div>
</template>

<script>
import { getRankingStudentCourseInfo } from '@/api.js'

const DEFAULT_SCORE_METRIC = 'commits'
const TABLE_PREFERENCES_KEY = 'kucode-ranking-table-preferences'

const COLUMN_DEFINITIONS = {
  rank: { key: 'rank', label: '순위', type: 'number' },
  name: { key: 'name', label: '이름', type: 'text' },
  student_id: { key: 'student_id', label: '학번', type: 'text' },
  department: { key: 'department', label: '학과', type: 'text' },
  github: { key: 'github', label: 'Github', type: 'text' },
  enrollment: { key: 'enrollment', label: '재학 상태', type: 'text' },
  score: { key: 'score', label: '점수', type: 'number' },
  commits: { key: 'commits', label: 'Commits', type: 'number' },
  prs: { key: 'prs', label: 'PRs', type: 'number' },
  issues: { key: 'issues', label: 'Issues', type: 'number' },
  repos: { key: 'repos', label: 'Repos', type: 'number' },
  stars: { key: 'stars', label: 'Stars', type: 'number' },
  contributors: { key: 'contributors', label: 'Contributors', type: 'number' },
}

const COLUMN_KEYS = [
  'rank',
  'name',
  'student_id',
  'department',
  'github',
  'score',
  'enrollment',
  'commits',
  'prs',
  'issues',
  'repos',
  'stars',
  'contributors',
]
const DEFAULT_COLUMN_KEYS = ['rank', 'name', 'student_id', 'department', 'github', 'score', 'commits', 'prs', 'issues', 'repos']

export default {
  name: 'Ranking',
  data() {
    return {
      loading: false,
      loadError: '',
      selectedYear: '',
      selectedSemester: '',
      selectedCourseKey: '',
      searchKeyword: '',
      currentPage: 1,
      postsPerPage: 10,
      rows: [],
      tableSettingsOpen: false,
      selectedColumnKeys: [...DEFAULT_COLUMN_KEYS],
      selectedDepartment: '',
      selectedEnrollment: '',
    }
  },
  computed: {
    columnOptions() {
      return COLUMN_KEYS.map((key) => COLUMN_DEFINITIONS[key])
    },
    displayColumns() {
      return this.columnOptions.filter((column) => this.selectedColumnKeys.includes(column.key))
    },
    departments() {
      return [...new Set(this.rankedStudents.map((student) => student.department).filter(Boolean))]
        .sort((a, b) => a.localeCompare(b, 'ko'))
    },
    enrollments() {
      return [...new Set(this.rankedStudents.map((student) => student.enrollment).filter(Boolean))]
        .sort((a, b) => a.localeCompare(b, 'ko'))
    },
    activeFilterCount() {
      let count = 0
      if (this.selectedDepartment) count += 1
      if (this.selectedEnrollment) count += 1
      return count
    },
    years() {
      return [...new Set(this.rows.map((row) => row.year))].sort((a, b) => Number(b) - Number(a))
    },
    semesters() {
      return [...new Set(this.rows
        .filter((row) => row.year === this.selectedYear)
        .map((row) => row.semester))]
        .sort((a, b) => Number(b) - Number(a))
    },
    filteredCourses() {
      return this.rows
        .filter((row) => row.year === this.selectedYear && row.semester === this.selectedSemester)
        .map((row) => ({ ...row, key: this.toCourseKey(row) }))
    },
    selectedCourse() {
      return this.filteredCourses.find((course) => course.key === this.selectedCourseKey) || this.filteredCourses[0]
    },
    selectedCourseTitle() {
      if (this.loading) return '랭킹 데이터를 불러오는 중입니다'
      if (this.loadError) return '랭킹 데이터를 불러오지 못했습니다'
      if (!this.selectedCourse) return '랭킹 데이터가 없습니다'
      return `${this.selectedCourse.course_id} - ${this.selectedCourse.course_name}`
    },
    summaryMeta() {
      if (this.loading) return '학생별 과목 활동 데이터를 읽고 있습니다.'
      if (this.loadError) return this.loadError
      if (!this.selectedCourse) return '연도, 학기, 과목 데이터를 연결하면 랭킹이 표시됩니다.'
      return `${this.selectedYear}년 ${this.selectedSemester}학기 · ${this.selectedCourse.prof || '담당교수 미등록'}`
    },
    emptyStateMessage() {
      if (this.loading) return '랭킹 데이터를 불러오는 중입니다.'
      if (this.loadError) return this.loadError
      if (this.rows.length === 0) return '표시할 랭킹 데이터가 없습니다.'
      return '검색 또는 필터 결과가 없습니다.'
    },
    rankedStudents() {
      if (!this.selectedCourse) return []

      return this.selectedCourse.students
        .map((student) => ({
          ...student,
          score: this.calculateScore(student),
        }))
        .sort((a, b) => {
          if (b.score !== a.score) return b.score - a.score
          return a.name.localeCompare(b.name, 'ko')
        })
        .map((student, index) => ({
          ...student,
          rank: index + 1,
        }))
    },
    visibleStudents() {
      const keyword = this.searchKeyword.trim().toLowerCase()

      return this.rankedStudents.filter((student) => {
        const matchesKeyword = !keyword || [student.name, student.student_id, student.github, student.department, student.enrollment]
          .some((value) => String(value).toLowerCase().includes(keyword))
        const matchesDepartment = !this.selectedDepartment || student.department === this.selectedDepartment
        const matchesEnrollment = !this.selectedEnrollment || student.enrollment === this.selectedEnrollment

        return matchesKeyword && matchesDepartment && matchesEnrollment
      })
    },
    paginatedStudents() {
      const start = (this.currentPage - 1) * this.postsPerPage
      return this.visibleStudents.slice(start, start + this.postsPerPage)
    },
    totalPages() {
      return Math.max(1, Math.ceil(this.visibleStudents.length / this.postsPerPage))
    },
    pagesToShow() {
      const maxVisiblePages = 5
      const halfWindow = Math.floor(maxVisiblePages / 2)
      let start = Math.max(1, this.currentPage - halfWindow)
      let end = Math.min(this.totalPages, start + maxVisiblePages - 1)

      if (end - start + 1 < maxVisiblePages) {
        start = Math.max(1, end - maxVisiblePages + 1)
      }

      return Array.from({ length: end - start + 1 }, (_, index) => start + index)
    },
    firstPageDisabled() {
      return this.currentPage === 1
    },
    prevPageDisabled() {
      return this.currentPage === 1
    },
    nextPageDisabled() {
      return this.currentPage === this.totalPages
    },
    lastPageDisabled() {
      return this.currentPage === this.totalPages
    },
    awardCandidates() {
      return this.rankedStudents.slice(0, 3)
    },
  },
  watch: {
    selectedYear() {
      this.syncSelection()
    },
    selectedSemester() {
      this.syncSelection()
    },
    selectedCourseKey() {
      this.currentPage = 1
      this.searchKeyword = ''
      this.resetRowFilters()
    },
    searchKeyword() {
      this.currentPage = 1
    },
    selectedDepartment() {
      this.handleFilterChange()
    },
    selectedEnrollment() {
      this.handleFilterChange()
    },
  },
  created() {
    this.loadTablePreferences()
    this.fetchRankingRows()
  },
  mounted() {
    document.addEventListener('click', this.handleDocumentClick)
  },
  beforeUnmount() {
    document.removeEventListener('click', this.handleDocumentClick)
  },
  methods: {
    loadTablePreferences() {
      try {
        const preferences = JSON.parse(localStorage.getItem(TABLE_PREFERENCES_KEY))
        if (!preferences) return

        let selectedKeys = preferences.selectedColumnKeys
        if (!Array.isArray(selectedKeys) && Array.isArray(preferences.leadingColumnKeys) && Array.isArray(preferences.activityColumnKeys)) {
          selectedKeys = ['rank', ...preferences.leadingColumnKeys, 'score', ...preferences.activityColumnKeys]
        }

        if (Array.isArray(selectedKeys)) {
          const validKeys = COLUMN_KEYS.filter((key) => selectedKeys.includes(key) || key === 'score')
          this.selectedColumnKeys = validKeys.length ? validKeys : [...DEFAULT_COLUMN_KEYS]
        }
      } catch (error) {
        console.warn('Failed to load ranking table preferences:', error)
      }
    },
    saveTablePreferences() {
      try {
        localStorage.setItem(TABLE_PREFERENCES_KEY, JSON.stringify({
          selectedColumnKeys: this.selectedColumnKeys,
        }))
      } catch (error) {
        console.warn('Failed to save ranking table preferences:', error)
      }
    },
    toggleTableSettings() {
      this.tableSettingsOpen = !this.tableSettingsOpen
    },
    closeTableSettings() {
      this.tableSettingsOpen = false
    },
    handleDocumentClick(event) {
      if (this.tableSettingsOpen && !this.$refs.tableSettings?.contains(event.target)) {
        this.closeTableSettings()
      }
    },
    isColumnSelected(columnKey) {
      return this.selectedColumnKeys.includes(columnKey)
    },
    toggleColumn(columnKey, checked) {
      if (!COLUMN_KEYS.includes(columnKey) || columnKey === 'score') return

      const nextSelection = new Set(this.selectedColumnKeys)
      if (checked) {
        nextSelection.add(columnKey)
      } else {
        nextSelection.delete(columnKey)
      }
      nextSelection.add('score')
      this.selectedColumnKeys = COLUMN_KEYS.filter((key) => nextSelection.has(key))
      this.currentPage = 1
      this.saveTablePreferences()
    },
    resetRowFilters() {
      this.selectedDepartment = ''
      this.selectedEnrollment = ''
      this.currentPage = 1
    },
    resetTableSettings() {
      this.selectedColumnKeys = [...DEFAULT_COLUMN_KEYS]
      this.resetRowFilters()
      this.saveTablePreferences()
    },
    handleFilterChange() {
      this.currentPage = 1
    },
    columnClasses(column) {
      return {
        [`column-${column.key}`]: true,
        'numeric-column': column.type === 'number',
        'score-cell': column.key === 'score',
      }
    },
    formatColumnValue(student, column) {
      const value = student[column.key]
      if (value === null || value === undefined || value === '') return '-'
      return value
    },
    toCourseKey(course) {
      return `${course.year}-${course.semester}-${course.course_id}`
    },
    calculateScore(student) {
      return Number(student[DEFAULT_SCORE_METRIC] || 0)
    },
    async fetchRankingRows() {
      this.loading = true
      this.loadError = ''

      try {
        const response = await getRankingStudentCourseInfo()
        this.rows = this.buildRankingRows(response.data || [])
        this.applyInitialSelection()
      } catch (error) {
        console.error('Failed to fetch ranking data:', error)
        this.rows = []
        this.loadError = '랭킹 데이터를 불러오지 못했습니다.'
        this.applyInitialSelection()
      } finally {
        this.loading = false
      }
    },
    buildRankingRows(rawRows) {
      const courseMap = new Map()

      rawRows.forEach((row) => {
        const year = String(row.year || '').trim()
        const semester = String(row.semester || '').trim()
        const courseId = String(row.course_id || '').trim()
        const courseName = String(row.course_name || '').trim()

        if (!year || !semester || !courseId || !courseName || courseName === '기타') {
          return
        }

        const courseKey = `${year}-${semester}-${courseId}`
        if (!courseMap.has(courseKey)) {
          courseMap.set(courseKey, {
            year,
            semester,
            course_id: courseId,
            course_name: courseName,
            prof: row.prof || '',
            students: [],
          })
        }

        const course = courseMap.get(courseKey)
        const studentKey = String(row.id || row.github_id || row.name || '').trim()
        if (!studentKey) return

        let student = course.students.find((item) => item.student_key === studentKey)
        if (!student) {
          student = {
            student_key: studentKey,
            student_id: row.id || '',
            name: row.name || '',
            department: row.department || '',
            github: row.github_id || '',
            enrollment: row.enrollment || '',
            commits: 0,
            prs: 0,
            issues: 0,
            repos: 0,
            stars: 0,
            contributors: 0,
          }
          course.students.push(student)
        }

        student.commits += Number(row.commit || 0)
        student.prs += Number(row.pr || 0)
        student.issues += Number(row.issue || 0)
        student.repos += Number(row.num_repos || 0)
        student.stars += Number(row.star_count || 0)
        student.contributors += Number(row.total_contributors || 0)
      })

      return Array.from(courseMap.values())
        .map((course) => ({
          ...course,
          students: course.students.map(({ student_key, ...student }) => student),
        }))
        .sort((a, b) => {
          if (Number(b.year) !== Number(a.year)) return Number(b.year) - Number(a.year)
          if (Number(b.semester) !== Number(a.semester)) return Number(b.semester) - Number(a.semester)
          return `${a.course_name}${a.course_id}`.localeCompare(`${b.course_name}${b.course_id}`, 'ko', {
            numeric: true,
            sensitivity: 'base',
          })
        })
    },
    applyInitialSelection() {
      const firstCourse = this.rows[0]
      if (!firstCourse) {
        this.selectedYear = ''
        this.selectedSemester = ''
        this.selectedCourseKey = ''
        this.searchKeyword = ''
        this.currentPage = 1
        return
      }

      this.selectedYear = firstCourse.year
      this.selectedSemester = firstCourse.semester
      this.selectedCourseKey = this.toCourseKey(firstCourse)
      this.searchKeyword = ''
      this.currentPage = 1
    },
    syncSelection() {
      if (this.rows.length === 0) {
        this.selectedYear = ''
        this.selectedSemester = ''
        this.selectedCourseKey = ''
        this.searchKeyword = ''
        this.currentPage = 1
        return
      }

      if (!this.semesters.includes(this.selectedSemester)) {
        this.selectedSemester = this.semesters[0] || ''
      }

      const nextCourse = this.filteredCourses[0]
      this.selectedCourseKey = nextCourse ? nextCourse.key : ''
      this.searchKeyword = ''
      this.currentPage = 1
    },
    resetFilters() {
      const latest = this.rows[0]
      if (!latest) {
        this.selectedYear = ''
        this.selectedSemester = ''
        this.selectedCourseKey = ''
        this.searchKeyword = ''
        this.currentPage = 1
        return
      }

      this.selectedYear = latest.year
      this.selectedSemester = latest.semester
      this.selectedCourseKey = this.toCourseKey(latest)
      this.searchKeyword = ''
      this.currentPage = 1
    },
    goToPage(page) {
      this.currentPage = Math.min(Math.max(page, 1), this.totalPages)
    },
  },
}
</script>

<style scoped>
.ranking-page {
  min-height: 100vh;
  padding: 150px 0 80px;
  background: #fcfcfc;
}

.ranking-shell {
  display: grid;
  grid-template-columns: 300px minmax(0, 1fr);
  gap: 28px;
  width: min(1280px, calc(100% - 64px));
  margin: 0 auto;
}

.ranking-filter,
.ranking-table-card,
.ranking-summary,
.winner-card {
  border: 1px solid #dce2ed;
  background: #ffffff;
}

.ranking-filter {
  align-self: start;
  padding: 24px;
}

.filter-header,
.table-top,
.ranking-summary,
.winner-strip {
  display: flex;
}

.filter-header {
  align-items: center;
  justify-content: space-between;
  margin-bottom: 22px;
}

.filter-label,
.eyebrow {
  margin: 0;
  color: #910024;
  font-size: 14px;
  font-weight: 700;
}

.reset-button {
  height: 34px;
  padding: 0 14px;
  border: 1px solid #f5d6de;
  border-radius: 6px;
  background: #ffffff;
  color: #910024;
  font-weight: 700;
  cursor: pointer;
}

.filter-field {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 18px;
  color: #616161;
  font-size: 14px;
  font-weight: 700;
}

.filter-field select,
.search-box input,
.settings-menu select {
  height: 44px;
  border: 1px solid #dce2ed;
  border-radius: 6px;
  background: #fcfcfc;
  color: #262626;
  font-size: 15px;
}

.filter-field select {
  padding: 0 12px;
}

.ranking-content {
  min-width: 0;
}

.ranking-summary {
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding: 30px 34px;
}

.ranking-summary h1 {
  margin: 8px 0 10px;
  color: #262626;
  font-size: 30px;
  letter-spacing: 0;
}

.summary-meta {
  margin: 0;
  color: #616161;
  font-size: 15px;
}

.winner-card span,
.table-top p {
  display: block;
  color: #8a8a8a;
  font-size: 13px;
}

.winner-strip {
  gap: 14px;
  margin: 18px 0;
}

.winner-card {
  flex: 1;
  min-width: 0;
  padding: 18px 20px;
  border-radius: 6px;
}

.winner-card strong {
  display: block;
  margin-bottom: 5px;
  color: #262626;
  font-size: 18px;
}

.winner-card p {
  margin: 16px 0 0;
  color: #910024;
  font-size: 22px;
  font-weight: 800;
}

.winner-rank {
  width: fit-content;
  margin-bottom: 14px;
  padding: 5px 10px;
  border-radius: 999px;
  background: #910024;
  color: #ffffff;
  font-size: 13px;
  font-weight: 800;
}

.rank-2 .winner-rank {
  background: #616161;
}

.rank-3 .winner-rank {
  background: #b86d3c;
}

.ranking-table-card {
  padding: 26px 28px 30px;
}

.table-top {
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 22px;
}

.table-top h2 {
  margin: 0 0 6px;
  color: #262626;
  font-size: 22px;
  letter-spacing: 0;
}

.table-top p {
  margin: 0;
}

.table-tools {
  display: flex;
  align-items: center;
  gap: 10px;
}

.search-box {
  min-width: 0;
}

.search-box input {
  width: 260px;
  padding: 0 14px;
}

.table-settings {
  position: relative;
}

.settings-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  height: 44px;
  padding: 0 14px;
  border: 1px solid #dce2ed;
  border-radius: 6px;
  background: #ffffff;
  color: #616161;
  font-size: 14px;
  font-weight: 800;
  white-space: nowrap;
  cursor: pointer;
}

.settings-button:hover:not(:disabled),
.settings-button[aria-expanded="true"] {
  border-color: #910024;
  color: #910024;
}

.settings-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.settings-menu {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  z-index: 20;
  width: 430px;
  max-height: min(680px, calc(100vh - 190px));
  padding: 22px;
  overflow-y: auto;
  border: 1px solid #dce2ed;
  border-radius: 8px;
  background: #ffffff;
  box-shadow: 0 16px 40px rgba(38, 38, 38, 0.14);
  color: #262626;
}

.settings-header,
.section-title-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.settings-header strong {
  font-size: 18px;
}

.settings-header p {
  margin: 5px 0 0;
  color: #8a8a8a;
  font-size: 12px;
}

.settings-reset,
.section-title-row button {
  padding: 0;
  border: 0;
  background: transparent;
  color: #910024;
  font-size: 12px;
  font-weight: 800;
  white-space: nowrap;
  cursor: pointer;
}

.settings-section {
  margin-top: 20px;
  padding-top: 18px;
  border-top: 1px solid #eef1f5;
}

.settings-section h3 {
  margin: 0 0 12px;
  color: #616161;
  font-size: 13px;
}

.filter-setting-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.filter-setting-grid label {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.filter-setting-grid label > span {
  color: #8a8a8a;
  font-size: 12px;
  font-weight: 700;
}

.settings-menu select {
  width: 100%;
  padding: 0 10px;
  font-size: 14px;
}

.column-order-help {
  margin: -4px 0 10px;
  color: #8a8a8a;
  font-size: 12px;
  line-height: 1.5;
}

.column-checklist {
  border-top: 1px solid #eef1f5;
}

.column-check {
  display: flex;
  align-items: center;
  gap: 10px;
  min-height: 40px;
  padding: 0 4px;
  border-bottom: 1px solid #eef1f5;
  color: #262626;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
}

.column-check:hover {
  background: #fff8fa;
}

.column-check input {
  width: 17px;
  height: 17px;
  margin: 0;
  accent-color: #910024;
  cursor: pointer;
}

.column-check input:disabled {
  cursor: not-allowed;
}

.column-check:has(input:disabled) {
  cursor: default;
}

.column-lock {
  margin-left: auto;
  padding: 3px 8px;
  border-radius: 999px;
  background: #f8f1f3;
  color: #910024;
  font-size: 11px;
  font-weight: 800;
}

.settings-done {
  width: 100%;
  height: 42px;
  margin-top: 20px;
  border: 1px solid #910024;
  border-radius: 6px;
  background: #910024;
  color: #ffffff;
  font-size: 14px;
  font-weight: 800;
  cursor: pointer;
}

.table-scroll {
  overflow-x: auto;
}

.ranking-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}

.ranking-table th {
  height: 48px;
  border-top: 1px solid #dce2ed;
  border-bottom: 1px solid #dce2ed;
  color: #616161;
  font-size: 14px;
  font-weight: 800;
  text-align: left;
}

.ranking-table td {
  height: 54px;
  border-bottom: 1px solid #eef1f5;
  color: #262626;
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ranking-table th,
.ranking-table td {
  padding: 0 10px;
}

.ranking-table .column-rank {
  width: 58px;
  text-align: center;
}

.ranking-table .column-name {
  width: 90px;
}

.ranking-table .column-student_id {
  width: 112px;
}

.ranking-table .column-enrollment {
  width: 90px;
}

.ranking-table .numeric-column {
  text-align: right;
}

.ranking-table a {
  color: #910024;
  font-weight: 700;
  text-decoration: none;
}

.podium {
  background: #fff8fa;
}

.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #f8f1f3;
  color: #910024;
  font-weight: 800;
}

.score-cell {
  color: #910024;
  font-weight: 800;
}

.empty-state {
  padding: 40px 0 12px;
  color: #8a8a8a;
  text-align: center;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 28px;
}

.pagination-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-nav,
.page-number {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: 1px solid #dce2ed;
  border-radius: 6px;
  background: #ffffff;
  color: #616161;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: 0.2s ease;
}

.page-nav svg path {
  stroke: #616161;
}

.page-number.active,
.page-number:hover,
.page-nav:hover:not(:disabled) {
  border-color: #910024;
  background: #910024;
  color: #ffffff;
}

.page-nav:hover:not(:disabled) svg path {
  stroke: #ffffff;
}

.page-nav:disabled,
.page-number:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

@media (max-width: 1100px) {
  .ranking-shell {
    grid-template-columns: 1fr;
  }

  .ranking-summary,
  .table-top,
  .winner-strip {
    align-items: stretch;
    flex-direction: column;
  }

  .search-box input {
    width: 100%;
  }

  .table-tools {
    width: 100%;
  }

  .search-box {
    flex: 1;
  }

  .ranking-table {
    min-width: 920px;
  }
}

@media (max-width: 600px) {
  .ranking-page {
    padding-top: 120px;
  }

  .ranking-shell {
    width: min(100% - 28px, 1280px);
  }

  .ranking-table-card {
    padding: 22px 18px 26px;
  }

  .table-tools {
    align-items: stretch;
    flex-direction: column;
  }

  .settings-button {
    width: 100%;
  }

  .settings-menu {
    position: fixed;
    top: auto;
    right: 14px;
    bottom: 14px;
    left: 14px;
    width: auto;
    max-height: calc(100vh - 28px);
  }
}
</style>
