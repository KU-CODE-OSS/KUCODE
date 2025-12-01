<template>
  <div class="e-portfolio">
    <!-- Edit/Save Button -->
      <div class="save-section">
        <button class="pdf-export-btn" @click="openPdfExportModal">
          PDF 내보내기
        </button>
        <button class="save-btn" @click="isEditingProfile ? saveProfile() : toggleEditMode()">
          {{ isEditingProfile ? '저장' : '편집' }}
        </button>
      </div>
      
    <!-- Main Content -->
    <main class="main-content">
      <!-- Profile Section -->
      <section class="profile-section">
        <div class="profile-card">
          <!-- Profile Picture and Info Layout -->
          <div class="profile-header">
            <div class="profile-picture-placeholder"></div>
            <div class="profile-info">
              <h2 class="profile-name">{{ user.name || 'N/A' }} 님</h2>
              <div class="profile-details">
                <div class="detail-item">
                  <i class="icon-location"></i>
                  <div class="detail-content">
                    <span>{{ user.university || '' }} {{ user.department || '' }}</span>
                  </div>
                </div>
                <div class="detail-item">
                  <i class="icon-github"></i>
                  <a 
                    v-if="user.github_id"
                    :href="`https://github.com/${user.github_id}`" 
                    target="_blank" 
                    class="github-link"
                  >
                    {{ user.github_id }}
                  </a>
                  <span v-else class="github-link">GitHub ID 없음</span>
                </div>
                <div class="detail-item">
                  <i class="icon-mail"></i>
                  <span>{{ user.email || 'N/A' }}</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 나의 소개 Section - EDITABLE -->
          <div class="profile-intro">
            <div class="intro-header">
              <i class="icon-message"></i>
              <span>나의 소개</span>
            </div>
            <textarea 
              v-model="user.introduction"
              class="intro-input"
              placeholder="자신을 소개해 주세요..."
              rows="8"
              maxlength="150"
              :disabled="!isEditingProfile"
            ></textarea>
            <div class="intro-counter">
              {{ user.introduction.length }}/150
            </div>
          </div>
        </div>

        <!-- Right Column Container -->
        <div class="right-column">
          <!-- Combined Tech Stack and Skills Section -->
          <div class="combined-tech-skills-card">
            <!-- Tech Stack Section -->
            <div class="tech-stack-section">
              <!-- Horizontal Layout Container -->
              <div class="tech-stack-content">
                <!-- Left Section: Main Languages -->
                <div class="main-languages-section">
                  <h4 class="tech-column-title">주요 사용 언어</h4>
                  
                  <!-- Chart and Legend Container -->
                  <div class="chart-and-legend">
                    <div class="chart-container">
                      <!-- Chart.js Donut Chart -->
                      <canvas ref="techStackChart" width="120" height="120"></canvas>
                    </div>
                    <div class="chart-legend">
                      <div 
                        v-for="(lang, index) in convertTechStackDataForChart()" 
                        :key="lang.name"
                        class="legend-item"
                      >
                        <div 
                          class="legend-color" 
                          :style="{ background: lang.color }"
                        ></div>
                        <span>{{ lang.name }} ({{ lang.percentage }}%)</span>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Vertical Divider -->
                <div class="vertical-divider"></div>

                <!-- Right Section: Tech Stack -->
                <div class="tech-stack-dropdown-section">
                  <h4 class="tech-column-title">주요 기술 스택</h4>
                  <div class="tech-dropdowns">
                    <div 
                      v-for="(dropdown, index) in techStackDropdowns" 
                      :key="index"
                      class="tech-dropdown-container"
                    >
                      <div 
                        class="tech-dropdown"
                        :class="{ 'dropdown-open': dropdown.isOpen, 'dropdown-disabled': !isEditingProfile }"
                        @click.stop="isEditingProfile ? toggleDropdown(index) : null"
                      >
                        <div class="dropdown-selected">
                          <i :class="getIconClass(dropdown.selected)"></i>
                          <span>{{ dropdown.selected || '선택하세요' }}</span>
                          <i class="icon-arrow-down" :class="{ 'rotated': dropdown.isOpen }"></i>
                        </div>
                        <div v-if="dropdown.isOpen" class="dropdown-options">
                          <div 
                            v-for="option in dropdown.options" 
                            :key="option"
                            class="dropdown-option"
                            @click.stop="selectOption(index, option)"
                          >
                            <i :class="getIconClass(option)"></i>
                            <span>{{ option }}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Skills Section -->
            <div class="skills-section">
              <div class="skills-stats-container">
                <div class="skills-stats">
                  <div class="stat-item">
                    <div class="stat-content">
                      <div class="stat-title">추가 / 삭제 커밋 라인 수</div>
                      <div class="stat-value">{{ stats.commitLines.added.toLocaleString() }} / {{ stats.commitLines.deleted.toLocaleString() }}</div>
                    </div>
                  </div>
                  <div class="stat-item">
                    <div class="stat-content">
                      <div class="stat-title">이슈 생성 / 닫은 수</div>
                      <div class="stat-value">{{ stats.issues.created }} / {{ stats.issues.closed }}</div>
                    </div>
                  </div>
                  <div class="stat-item">
                    <div class="stat-content">
                      <div class="stat-title">PR 생성 수</div>
                      <div class="stat-value">{{ stats.pullRequests }}개</div>
                    </div>
                  </div>
                  <div class="stat-item">
                    <div class="stat-content">
                      <div class="stat-title">오픈소스 프로젝트</div>
                      <div class="stat-value">{{ stats.openSourceContributions }}개</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Activity Section -->
      <section class="activity-section">
        <!-- Activity Section Header -->
        <div class="activity-section-header">
          <div class="activity-header-content">
            <i class="icon-activity"></i>
            <h2 class="activity-title">개발 활동 패턴</h2>
          </div>
        </div>
        
        <div class="activity-charts">
          <!-- Activity Trends Chart -->
            <div class="chart-card">
              <div class="chart-header">
                <h3 class="chart-title-text">활동 추이 (최근 6개월)</h3>
              <!-- <div class="chart-toggle">
                <span 
                  :class="{ 'toggle-active': activityViewMode === 'monthly', 'toggle-inactive': activityViewMode !== 'monthly' }"
                  @click="switchActivityViewMode('monthly')"
                >
                  월간
                </span>
                <span 
                  :class="{ 'toggle-active': activityViewMode === 'weekly', 'toggle-inactive': activityViewMode !== 'weekly' }"
                  @click="switchActivityViewMode('weekly')"
                >
                  주간
                </span>
              </div> -->
            </div>
            <p class="chart-description">최근 대규모의 커밋량 변동이 많았습니다</p>
            
            <!-- Chart Legend -->
            <div class="chart-legend-horizontal">
              <div class="legend-item">
                <div class="legend-dot" style="background: #C16179;"></div>
                <span>커밋 횟수</span>
              </div>
              <div class="legend-item">
                <div class="legend-dot" style="background: #FF176A;"></div>
                <span>코드 생산량</span>
              </div>
              <!-- <div class="legend-item">
                <div class="legend-dot" style="background: #FF90AB;"></div>
                <span>Stars</span>
              </div> -->
            </div>

            <!-- Activity Line Chart -->
            <div class="activity-chart-container">
              <canvas ref="activityChart" width="525" height="180"></canvas>
            </div>
          </div>

          <!-- Project Team Size Chart -->
            <div class="chart-card">
              <div class="chart-header">
                <h3 class="chart-title-text">팀 프로젝트 비율</h3>
              </div>
            <p class="chart-description">{{ teamSizeDescription }}</p>
            
            <!-- Bar Chart Area -->
            <div class="team-size-chart-container">
              <canvas ref="teamSizeChart" width="525" height="200"></canvas>
            </div>
          </div>
        </div>

        <!-- Activity Time Pattern -->
          <div class="time-pattern-card">
            <div class="section-header">
              <h3 class="chart-title-text">활동 시간대 ()</h3>
            </div>
          
          <!-- 히트맵 컴포넌트 -->
          <EProfileHeatmap :heatmapData="heatmapData" />
        </div>
      </section>

      <!-- Projects Section -->
      <section class="projects-section">
        <div class="section-header">
          <i class="icon-archive"></i>
          <h3 class="chart-title-text projects-title">나의 프로젝트</h3>
        </div>
        
        <!-- Projects Table -->
        <div class="projects-table">
          <div class="table-header">
            <span class="sortable-header" @click="sortByColumn('category')">
              Category
              <i :class="getSortIcon('category')"></i>
            </span>
            <span class="sortable-header" @click="sortByColumn('name')">
              Repository
              <i :class="getSortIcon('name')"></i>
            </span>
            <span class="sortable-header" @click="sortByColumn('type')">
              Owner
              <i :class="getSortIcon('type')"></i>
            </span>
            <span class="sortable-header" @click="sortByColumn('commit_count')">
              Commits
              <i :class="getSortIcon('commit_count')"></i>
            </span>
            <span class="sortable-header" @click="sortByColumn('pr_count')">
              PRs
              <i :class="getSortIcon('pr_count')"></i>
            </span>
            <span class="sortable-header" @click="sortByColumn('total_issue_count')">
              Issues
              <i :class="getSortIcon('total_issue_count')"></i>
            </span>
            <span class="sortable-header" @click="sortByColumn('star_count')">
              Stars
              <i :class="getSortIcon('star_count')"></i>
            </span>
            <span class="sortable-header" @click="sortByColumn('fork_count')">
              Forks
              <i :class="getSortIcon('fork_count')"></i>
            </span>
            <span>Language</span>
            <span class="sortable-header" @click="sortByColumn('contributors_count')">
              Contributors
              <i :class="getSortIcon('contributors_count')"></i>
            </span>
          </div>
          
          <!-- Replace the static table rows with dynamic data -->
          <div class="table-row" v-for="repo in paginatedRepositoriesData" :key="repo.id">
          <div 
            class="category-column"
            :class="{ 
              'autonomous': !repo.is_course, 
              'course': repo.is_course 
            }"
          >
            <div class="category-type">
              {{ repo.is_course ? '전공역량' : '자율활동' }}
            </div>
            <!-- Show dropdown only for autonomous projects (is_course: false) -->
            <div 
              v-if="!repo.is_course"
              class="category-dropdown"
              :class="{ 
                'dropdown-open': categoryDropdownOpen[repo.id],
                'dropdown-up': shouldDropUp(repo.id),
                'dropdown-disabled': !isEditingProfile
              }"
              @click.stop="isEditingProfile ? toggleCategoryDropdown(repo.id) : null"
              :ref="`categoryDropdown_${repo.id}`"
            >
              <div class="category-dropdown-selected">
                <span>{{ repo.category || 'N/A' }}</span>
                <i class="icon-arrow-down" :class="{ 'rotated': categoryDropdownOpen[repo.id] }"></i>
              </div>
              <div 
                v-if="categoryDropdownOpen[repo.id] && isEditingProfile" 
                class="category-dropdown-options"
                :class="{ 'options-up': shouldDropUp(repo.id) }"
              >
                <div 
                  v-for="option in categoryOptions" 
                  :key="option"
                  class="category-dropdown-option"
                  @click.stop="selectCategoryOption(repo.id, option)"
                >
                  {{ option }}
                </div>
              </div>
            </div>
            <!-- Show static value for course projects (is_course: true) -->
            <div v-else class="category-static">
              {{ repo.category || 'N/A' }}
            </div>
          </div>
          <span 
            :title="repo.name || 'N/A'" 
            class="repo-name-clickable"
            @click="openRepoModal(repo)"
          >{{ repo.name || 'N/A' }}</span>
          <span>{{ getRepoType(repo) }}</span>
          <span>{{ getRepoCommits(repo)?.toLocaleString() || '0' }}</span>
          <span>{{ getRepoPRs(repo)?.toLocaleString() || '0' }}</span>
          <span>{{ getRepoIssues(repo)?.toLocaleString() || '0' }}</span>
          <span>{{ repo.star_count?.toLocaleString() || '0' }}</span>
          <span>{{ repo.fork_count?.toLocaleString() || '0' }}</span>
          <span :title="repo.language || 'N/A'">{{ repo.language || 'N/A' }}</span>
          <span>{{ repo.contributors_count?.toLocaleString() || '0' }}</span>
        </div>

          <!-- Loading state -->
          <div v-if="repositoriesLoading" class="table-row">
            <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: #616161;">
              프로젝트 데이터를 불러오는 중...
            </div>
          </div>

          <!-- Error state -->
          <div v-if="repositoriesError && !repositoriesLoading" class="table-row">
            <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: #CB385C;">
              프로젝트 데이터를 불러오는데 실패했습니다.
            </div>
          </div>

          <!-- Empty state -->
          <div v-if="!repositoriesLoading && !repositoriesError && repositoriesData.length === 0" class="table-row">
            <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: #616161;">
              등록된 프로젝트가 없습니다.
            </div>
          </div>
        </div>

        <!-- Pagination Controls -->
        <div class="pagination-section" v-if="totalPages > 1">
          <div class="pagination-info">
            {{ paginationInfo.start }}-{{ paginationInfo.end }} / {{ paginationInfo.total }}개 프로젝트
          </div>

          <div class="pagination-controls">
            <button
              class="pagination-btn"
              :class="{ 'disabled': currentPage === 1 }"
              @click="goToPage(1)"
              :disabled="currentPage === 1"
            >
              첫 페이지
            </button>

            <button
              class="pagination-btn"
              :class="{ 'disabled': currentPage === 1 }"
              @click="goToPage(currentPage - 1)"
              :disabled="currentPage === 1"
            >
              이전
            </button>

            <div class="page-numbers">
              <button
                v-for="page in visiblePages"
                :key="page"
                class="page-number"
                :class="{ 'active': page === currentPage }"
                @click="goToPage(page)"
              >
                {{ page }}
              </button>
            </div>

            <button
              class="pagination-btn"
              :class="{ 'disabled': currentPage === totalPages }"
              @click="goToPage(currentPage + 1)"
              :disabled="currentPage === totalPages"
            >
              다음
            </button>

            <button
              class="pagination-btn"
              :class="{ 'disabled': currentPage === totalPages }"
              @click="goToPage(totalPages)"
              :disabled="currentPage === totalPages"
            >
              마지막 페이지
            </button>
          </div>
        </div>
      </section>

    </main>

    <!-- PDF 내보내기 모달 -->
    <div v-if="showPdfExportModal" class="modal-overlay" @click.self="closePdfExportModal">
      <div class="pdf-export-modal">
        <div class="modal-header">
          <h3>PDF 내보내기</h3>
          <button class="close-btn" @click="closePdfExportModal">×</button>
        </div>
        <div class="modal-body">
          <p class="modal-description">프로필 요약 정보와 함께 내보낼 프로젝트를 선택하세요.</p>

          <div class="search-section">
            <input
              v-model="pdfExportSearchQuery"
              type="text"
              placeholder="프로젝트 검색..."
              class="search-input"
            />
          </div>

          <div class="select-actions">
            <button @click="selectAllRepos" class="action-btn">전체 선택</button>
            <button @click="clearAllRepos" class="action-btn">선택 해제</button>
          </div>

          <div class="repo-list">
            <div
              v-for="repo in filteredReposForPdf"
              :key="repo.id"
              class="repo-checkbox-item"
            >
              <label>
                <input
                  type="checkbox"
                  :value="repo.id"
                  v-model="selectedReposForPdf"
                />
                <span>{{ repo.name }}</span>
              </label>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="closePdfExportModal" class="cancel-btn">취소</button>
          <button @click="exportToPdf" class="confirm-btn" :disabled="pdfExporting">
            {{ pdfExporting ? '내보내는 중...' : 'PDF 다운로드' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 프로젝트 상세 모달 -->
    <RepoDetailModal
      :show="showRepoModal"
      :repo="selectedRepo"
      @close="closeRepoModal"
    />
  </div>
</template>

<script>
import { Chart, registerables } from 'chart.js'
import html2canvas from 'html2canvas'
import { jsPDF } from 'jspdf'
import EProfileHeatmap from './EProfileComponents/EProfileHeatmap.vue'
import RepoDetailModal from './EProfileComponents/RepoDetailModal.vue'
import { getEProfileHeatmap, updateStudentIntroduction, updateStudentTechnologyStack } from '@/api.js'
import { processActivityData, processAddedLinesData, estimateCommitLines } from './EProfileComponents/chartUtils/chartUtils.js'
import { auth } from '../services/firebase'

// Register Chart.js components
Chart.register(...registerables)

export default {
  name: 'EPortfolioDashboard',
  components: {
    EProfileHeatmap,
    RepoDetailModal
  },
  data() {
    return {
      user: {
        name: '최다영',
        university: '고려대학교',
        department: '컴퓨터학과',
        email: 'joyyoj1@korea.ac.kr',
        github_id: '',
        introduction: ''
      },
      techStack: {
        languages: [],
        frameworks: []
      },
      stats: {
        commitLines: { added: 0, deleted: 0 },
        issues: { created: 0, closed: 0 },
        pullRequests: 0,
        openSourceContributions: 0
      },
      // Tech Stack Chart Data
      techStackData: [],
      // 히트맵 데이터
      heatmapData: {},
      // 모달 관련 데이터
      showRepoModal: false,
      selectedRepo: null,
      techStackChart: null,
      // Activity Chart Data - NEW ADDITIONS
      activityChart: null,
      activityViewMode: 'monthly', // 'monthly' or 'weekly'
      // Sample activity data - replace with actual API data
      activityData: {
        monthly: {
          labels: [],
          commits: [],
          commitLines: []
        },
        weekly: {
          labels: [],
          commits: [],
          commitLines: []
        }
        
        // monthly: {
        //   labels: ['5월', '6월', '7월', '8월', '10월', '11월'],
        //   repos: [3, 35, 45, 55, 40, 30],
        //   commits: [40, 55, 75, 70, 65, 50],
        //   stars: [0, 0, 0, 0, 0, 0]
        // },
        // weekly: {
        //   labels: ['1주차', '2주차', '3주차', '4주차', '5주차', '6주차'],
        //   repos: [8, 12, 15, 18, 14, 10],
        //   commits: [20, 28, 35, 32, 30, 25],
        //   stars: [0, 0, 0, 0, 0, 0]
        // }
      },
      // Add to your data() return object:
      teamSizeChart: null,
      teamSizeData: {
        labels: [],
        data: []
      },
      allTechOptions: ['Python', 'JavaScript', 'TypeScript', 'Java', 'C++', 'C#', 'Go', 'Rust', 
      'Swift', 'Kotlin', 'React', 'Vue.js', 'Angular', 'Svelte', 'Django', 
      'Flask', 'Express.js', 'Spring Boot', 'PostgreSQL', 'MySQL', 'MongoDB', 
      'Redis', 'Docker', 'Kubernetes', 'AWS', 'Google Cloud', 'Azure'],
      techStackDropdowns: [
        {
          selected: '',
          isOpen: false,
          options: []
        },
        {
          selected: '',
          isOpen: false,
          options: []
        },
        {
          selected: '',
          isOpen: false,
          options: []
        },
        {
          selected: '',
          isOpen: false,
          options: []
        },
        {
          selected: '',
          isOpen: false,
          options: []
        }
      ],
      repositoriesData: [],
      repositoriesLoading: false,
      repositoriesError: null,
      // Sorting state
      sortBy: '',
      sortDirection: 'asc', // 'asc' or 'desc'
      // githubId: "YeoJune", // 임시 테스트용 GitHub 아이디 - TODO: 실제 로그인된 사용자 ID로 변경 필요
      student_uuid: auth.currentUser.uid,
      // Category dropdown state
      categoryDropdownOpen: {},
      categoryOptions: [
        '자료구조',
        '알고리즘',
        '컴퓨터구조',
        '운영체제',
        '데이터베이스',
        '네트워크',
        '인공지능',
        '컴파일러',
        '소프트웨어공학',
        '클라우드컴퓨팅',
        '운영체제실습',
        '네트워크실습',
        '프로그래밍언어론',
        '분산시스템',
        '컴퓨터그래픽스',
        '사이버보안'
      ],
      // Pagination properties
      currentPage: 1,
      itemsPerPage: 10,
      // Edit mode state
      isEditingProfile: false,
      // PDF Export properties
      showPdfExportModal: false,
      pdfExportSearchQuery: '',
      selectedReposForPdf: [],
      pdfExporting: false
    }
  },
  computed: {
    teamSizeDescription() {
      if (!this.teamSizeData || !this.teamSizeData.data || this.teamSizeData.data.length === 0) {
        return '프로젝트 데이터가 없습니다'
      }
      
      // 가장 높은 값을 가진 인덱스 찾기
      const maxIndex = this.teamSizeData.data.indexOf(Math.max(...this.teamSizeData.data))
      const maxValue = this.teamSizeData.data[maxIndex]
      const maxLabel = this.teamSizeData.labels[maxIndex]
      
      // 총합 계산
      const total = this.teamSizeData.data.reduce((sum, val) => sum + val, 0)
      const percentage = Math.round((maxValue / total) * 100)
      
      return `${maxLabel} 프로젝트 비율이 가장 높습니다 (${percentage}%)`
    },

    sortedRepositoriesData() {
      if (!this.sortBy) {
        return this.repositoriesData
      }

      const sorted = [...this.repositoriesData].sort((a, b) => {
        let aVal = a[this.sortBy]
        let bVal = b[this.sortBy]

        // Handle different data types
        if (this.sortBy === 'category') {
          // Sort category: course projects first, then autonomous
          aVal = a.is_course ? 0 : 1
          bVal = b.is_course ? 0 : 1
        } else if (this.sortBy === 'name') {
          // String comparison for repository names
          aVal = (aVal || '').toString().toLowerCase()
          bVal = (bVal || '').toString().toLowerCase()
        } else if (this.sortBy === 'type') {
          // Sort type: Owner (displayed as '-') first, then Contributor (owner_github_id) alphabetically
          const aType = this.getRepoType(a)
          const bType = this.getRepoType(b)
          
          // Owner는 '-'로 표시되므로 가장 앞에 정렬 (priority 0)
          // Contributor는 owner_github_id로 정렬 (priority 1, value는 lowercase)
          // N/A는 마지막 (priority 2)
          let aPriority, bPriority, aValue, bValue
          
          if (aType === '-') {
            aPriority = 0
            aValue = ''
          } else if (aType === 'N/A') {
            aPriority = 2
            aValue = ''
          } else {
            aPriority = 1
            aValue = aType.toLowerCase()
          }
          
          if (bType === '-') {
            bPriority = 0
            bValue = ''
          } else if (bType === 'N/A') {
            bPriority = 2
            bValue = ''
          } else {
            bPriority = 1
            bValue = bType.toLowerCase()
          }
          
          // priority로 먼저 정렬, 같은 priority면 value로 정렬
          if (aPriority !== bPriority) {
            aVal = aPriority
            bVal = bPriority
          } else {
            aVal = aValue
            bVal = bValue
          }
        } else if (this.sortBy === 'commit_count') {
          // Use calculated commit count
          aVal = this.getRepoCommits(a)
          bVal = this.getRepoCommits(b)
        } else if (this.sortBy === 'pr_count') {
          // Use calculated PR count
          aVal = this.getRepoPRs(a)
          bVal = this.getRepoPRs(b)
        } else if (this.sortBy === 'total_issue_count') {
          // Use calculated issue count
          aVal = this.getRepoIssues(a)
          bVal = this.getRepoIssues(b)
        } else if (['star_count', 'fork_count', 'contributors_count'].includes(this.sortBy)) {
          // Numeric comparison for other fields
          aVal = parseInt(aVal) || 0
          bVal = parseInt(bVal) || 0
        }

        if (this.sortDirection === 'asc') {
          return aVal > bVal ? 1 : aVal < bVal ? -1 : 0
        } else {
          return aVal < bVal ? 1 : aVal > bVal ? -1 : 0
        }
      })

      return sorted
    },

    // Pagination computed properties
    totalPages() {
      return Math.ceil(this.sortedRepositoriesData.length / this.itemsPerPage)
    },

    paginatedRepositoriesData() {
      const start = (this.currentPage - 1) * this.itemsPerPage
      const end = start + this.itemsPerPage
      return this.sortedRepositoriesData.slice(start, end)
    },

    paginationInfo() {
      const start = (this.currentPage - 1) * this.itemsPerPage + 1
      const end = Math.min(this.currentPage * this.itemsPerPage, this.sortedRepositoriesData.length)
      const total = this.sortedRepositoriesData.length
      return { start, end, total }
    },

    visiblePages() {
      const maxVisible = 5
      const totalPages = this.totalPages
      const currentPage = this.currentPage

      if (totalPages <= maxVisible) {
        return Array.from({ length: totalPages }, (_, i) => i + 1)
      }

      const start = Math.max(1, currentPage - Math.floor(maxVisible / 2))
      const end = Math.min(totalPages, start + maxVisible - 1)
      const adjustedStart = Math.max(1, end - maxVisible + 1)

      return Array.from({ length: end - adjustedStart + 1 }, (_, i) => adjustedStart + i)
    },

    filteredReposForPdf() {
      if (!this.pdfExportSearchQuery) {
        return this.repositoriesData
      }
      const query = this.pdfExportSearchQuery.toLowerCase()
      return this.repositoriesData.filter(repo =>
        repo.name.toLowerCase().includes(query)
      )
    }
  },
  async mounted() {
    this.techStackDropdowns.forEach(dropdown => {
      dropdown.options = this.allTechOptions
    })
    
    await this.loadActivityChart()
    await this.loadHeatmapData()

    this.createTechStackChart()
    setTimeout(() => {
      this.createActivityChart()
    }, 50)
    this.createTeamSizeChart()

    // Use arrow function to maintain 'this' context
    this.closeAllDropdowns = (event) => {
      if (!event.target.closest('.tech-dropdown')) {
        this.techStackDropdowns.forEach(dropdown => {
          dropdown.isOpen = false
        })
      }
      
      if (!event.target.closest('.category-dropdown')) {
        this.closeCategoryDropdowns()
      }
    }
    
    document.addEventListener('click', this.closeAllDropdowns)
  },
  beforeUnmount() {
    if (this.techStackChart) {
      this.techStackChart.destroy()
    }
    if (this.activityChart) {
      this.activityChart.destroy()
    }
    if (this.teamSizeChart) {
      this.teamSizeChart.destroy()
    }

    document.removeEventListener('click', this.closeAllDropdowns)
  },
  methods: {
    // 편집 모드 토글
    toggleEditMode() {
      this.isEditingProfile = true
    },
    // 저장 버튼 클릭 핸들러
    async saveProfile() {
      try {
        await this.saveProfileChanges()
        this.isEditingProfile = false
        alert('저장 완료')
      } catch (error) {
        console.error('저장 실패:', error)
        alert('저장에 실패했습니다. 다시 시도해주세요.')
      }
    },
    // 모달 관련 메서드
    openRepoModal(repo) {
      this.selectedRepo = repo
      this.showRepoModal = true
    },
    closeRepoModal() {
      this.showRepoModal = false
      this.selectedRepo = null
    },
    // PDF Export 모달 관련 메서드
    openPdfExportModal() {
      this.showPdfExportModal = true
    },
    closePdfExportModal() {
      this.showPdfExportModal = false
      this.pdfExportSearchQuery = ''
      this.selectedReposForPdf = []
    },
    selectAllRepos() {
      this.selectedReposForPdf = this.filteredReposForPdf.map(repo => repo.id)
    },
    clearAllRepos() {
      this.selectedReposForPdf = []
    },
    async exportToPdf() {
      this.pdfExporting = true

      // Close the modal first so it doesn't appear in the PDF
      const modalWasOpen = this.showPdfExportModal
      this.showPdfExportModal = false

      try {
        // TODO: PLACEHOLDER_API_CALL('/repo/export_profile_pdf')
        // Expected payload: { uuid: this.student_uuid, repo_ids: this.selectedReposForPdf }

        // For now, use client-side PDF generation (html2canvas + jsPDF)
        // This is temporary until backend PDF rendering is implemented

        // Wait for modal to close and DOM to update
        await new Promise(resolve => setTimeout(resolve, 200))

        // Get the main content area (everything except modals and buttons)
        const mainContent = document.querySelector('.main-content')
        if (!mainContent) {
          throw new Error('Main content not found')
        }

        // Hide buttons and edit controls temporarily
        const saveSection = document.querySelector('.save-section')
        const originalDisplay = saveSection ? saveSection.style.display : ''
        if (saveSection) saveSection.style.display = 'none'

        // Filter repos based on selection if any are selected
        const originalRepos = [...this.repositoriesData]
        if (this.selectedReposForPdf.length > 0) {
          this.repositoriesData = this.repositoriesData.filter(repo =>
            this.selectedReposForPdf.includes(repo.id)
          )
          // Wait for Vue to re-render
          await this.$nextTick()
          await new Promise(resolve => setTimeout(resolve, 300))
        }

        // Capture the main content with html2canvas
        const canvas = await html2canvas(mainContent, {
          scale: 2,
          useCORS: true,
          logging: false,
          allowTaint: true,
          backgroundColor: '#ffffff',
          width: mainContent.scrollWidth,
          height: mainContent.scrollHeight,
          windowWidth: mainContent.scrollWidth,
          windowHeight: mainContent.scrollHeight
        })

        // Restore repos if filtered
        if (this.selectedReposForPdf.length > 0) {
          this.repositoriesData = originalRepos
          await this.$nextTick()
        }

        // Restore button visibility
        if (saveSection) saveSection.style.display = originalDisplay

        // Create PDF
        const imgData = canvas.toDataURL('image/png')
        const pdf = new jsPDF({
          orientation: 'portrait',
          unit: 'mm',
          format: 'a4'
        })

        const imgWidth = 210 // A4 width in mm
        const pageHeight = 297 // A4 height in mm
        const imgHeight = (canvas.height * imgWidth) / canvas.width
        let heightLeft = imgHeight
        let position = 0

        // Add first page
        pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
        heightLeft -= pageHeight

        // Add additional pages if content is longer than one page
        while (heightLeft >= 0) {
          position = heightLeft - imgHeight
          pdf.addPage()
          pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
          heightLeft -= pageHeight
        }

        // Download PDF
        const fileName = this.selectedReposForPdf.length > 0
          ? `${this.user.name}_EProfile_선택된프로젝트.pdf`
          : `${this.user.name}_EProfile.pdf`
        pdf.save(fileName)

        alert('PDF 내보내기 완료!')
      } catch (error) {
        console.error('PDF export error:', error)
        alert('PDF 내보내기에 실패했습니다. 다시 시도해주세요.')
      } finally {
        this.pdfExporting = false
        if (modalWasOpen) {
          this.showPdfExportModal = true
        }
      }
    },
    createTechStackChart() {
      const ctx = this.$refs.techStackChart.getContext('2d')
      
      // Convert object format to chart format
      const chartData = this.convertTechStackDataForChart()
      
      this.techStackChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: chartData.map(item => item.name),
          datasets: [{
            data: chartData.map(item => item.value),
            backgroundColor: chartData.map(item => item.color),
            borderWidth: 0,
            cutout: '60%' // Creates the donut hole
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false // We'll use our custom legend
            },
            tooltip: {
              callbacks: {
                label: function(context) {
                  const label = context.label || ''
                  const value = context.parsed
                  const total = context.dataset.data.reduce((a, b) => a + b, 0)
                  const percentage = Math.round((value / total) * 100)
                  return `${label}: ${percentage}%`
                }
              }
            }
          },
          animation: {
            animateRotate: true,
            duration: 1000
          },
          interaction: {
            intersect: false
          }
        }
      })
    },
    createActivityChart() {
      const ctx = this.$refs.activityChart.getContext('2d')

      const currentData = this.activityData[this.activityViewMode]
      
      this.activityChart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: currentData.labels,
          datasets: [
            // {
            //   label: 'Repos',
            //   data: currentData.repos,
            //   borderColor: '#C16179',
            //   backgroundColor: 'transparent',
            //   borderWidth: 2,
            //   pointBackgroundColor: '#C16179',
            //   pointBorderColor: '#C16179',
            //   pointRadius: 3,
            //   tension: 0.4
            // },
            // {
            //   label: 'Commit',
            //   data: currentData.commits,
            //   borderColor: '#FF176A',
            //   backgroundColor: 'transparent',
            //   borderWidth: 2,
            //   pointBackgroundColor: '#FF176A',
            //   pointBorderColor: '#FF176A',
            //   pointRadius: 3,
            //   tension: 0.4
            // },
            // {
            //   label: 'Stars',
            //   data: currentData.stars,
            //   borderColor: '#FF90AB',
            //   backgroundColor: 'transparent',
            //   borderWidth: 2,
            //   pointBackgroundColor: '#FF90AB',
            //   pointBorderColor: '#FF90AB',
            //   pointRadius: 3,
            //   tension: 0.4
            // }
            {
              label: 'Commit수',
              data: currentData.commits,
              borderColor: '#C16179',
              backgroundColor: 'transparent',
              borderWidth: 2,
              pointBackgroundColor: '#C16179',
              pointBorderColor: '#C16179',
              pointRadius: 3,
              tension: 0.4
            },
            {
              label: 'Commit라인수',
              data: currentData.commitLines,
              borderColor: '#FF176A',
              backgroundColor: 'transparent',
              borderWidth: 2,
              pointBackgroundColor: '#FF176A',
              pointBorderColor: '#FF176A',
              pointRadius: 3,
              tension: 0.4
            },
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false // We use our custom legend
            }
          },
          scales: {
            x: {
              grid: {
                display: false
              },
              border: {
                display: false
              },
              ticks: {
                color: '#262626',
                font: {
                  size: 12,
                  family: 'Pretendard'
                }
              }
            },
            y: {
              beginAtZero: true,
              // Let Chart.js automatically calculate min, max, and stepSize
              ticks: {
                callback: function(value) {
                  // Format large numbers (e.g., 25000 -> 25K)
                  if (value >= 1000) {
                    return (value / 1000) + 'K'
                  }
                  return value
                },
                color: '#262626',
                font: {
                  size: 12,
                  family: 'Pretendard'
                }
              },
              grid: {
                color: '#FFEAEC',
                borderDash: []
              },
              border: {
                display: false
              }
            }
          },
          elements: {
            point: {
              hoverRadius: 6
            }
          },
          interaction: {
            intersect: false,
            mode: 'index'
          },
          animation: {
            duration: 1000
          }
        }
      })
    },
    createTeamSizeChart() {
      if (!this.$refs.teamSizeChart) return
      
      const ctx = this.$refs.teamSizeChart.getContext('2d')
      
      this.teamSizeChart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: this.teamSizeData.labels,
          datasets: [{
            data: this.teamSizeData.data,
            backgroundColor: '#FF176A',
            borderRadius: 4,
            borderSkipped: false,
            barThickness: 20,
            maxBarThickness: 20,
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false }
          },
          scales: {
            x: {
              grid: { display: false },
              border: { display: false },
              ticks: {
                color: '#262626',
                font: { size: 14, family: 'Pretendard' }
              }
            },
            y: {
              beginAtZero: true,
              // Let Chart.js automatically calculate min, max, and stepSize
              ticks: {
                callback: function(value) {
                  return value
                },
              },
              grid: { color: '#FFEAEC' },
              border: { display: false }
            }
          }
        }
      })
    },
    updateTechStackData(newData) {
      // Method to update chart data dynamically
      const total = newData.reduce((sum, item) => sum + item.value, 0)
      
      // Calculate percentages
      this.techStackData = newData.map(item => ({
        ...item,
        percentage: Math.round((item.value / total) * 100)
      }))
      
      // Update chart
      if (this.techStackChart) {
        this.techStackChart.data.labels = this.techStackData.map(item => item.name)
        this.techStackChart.data.datasets[0].data = this.techStackData.map(item => item.value)
        this.techStackChart.data.datasets[0].backgroundColor = this.techStackData.map(item => item.color)
        this.techStackChart.update()
      }
    },
    switchActivityViewMode(mode) {
      if (this.activityViewMode === mode) return; // ignore duplicate clicks
      this.activityViewMode = mode
      this.updateActivityChart()
    },
    updateActivityChart() {
      if (!this.activityChart) {
        // If chart doesn't exist yet, just create it
        this.createActivityChart()
        return
      }

      // If a rebuild is already running, queue one more and bail
      if (this._rebuilding) {
        this._rebuildQueued = true
        return
      }

      this._rebuilding = true
      try {
        // 1) Tear down cleanly
        this.activityChart.destroy()
        this.activityChart = null

        // 2) Let Vue/DOM settle so the canvas is valid again
        this.$nextTick(() => {
          // 3) Rebuild for the current mode
          this.createActivityChart()

          this._rebuilding = false

          // 4) If clicks piled up during rebuild, do exactly one more
          if (this._rebuildQueued) {
            this._rebuildQueued = false
            // run on next microtask to avoid immediate re-entrancy
            Promise.resolve().then(() => this.updateActivityChart())
          }
        })
      } catch (e) {
        this._rebuilding = false
        console.error(e)
      }
    },
    
    editProfile() {
      // Handle profile editing
      console.log('Edit profile clicked');
    },
    async saveProfileChanges() {
      try {
        const uuid = auth.currentUser.uid
        
        // 기술 스택 배열 생성 (선택된 값만)
        const technology_stack = []
        this.techStackDropdowns.forEach(dropdown => {
          if (dropdown.selected) {
            technology_stack.push(dropdown.selected)
          }
        })

        // 나의 소개 저장
        await updateStudentIntroduction(uuid, this.user.introduction)
        
        // 기술 스택 저장 (배열로 직접 전송)
        await updateStudentTechnologyStack(uuid, technology_stack)
      }
      catch (error) {
        console.error('Failed to save profile data:', error)
        throw error
      }
    },
    async loadActivityChart(data) {
      try {
        // Initialize with empty data
        this.activityData = {
          monthly: {
            labels: [],
            commits: [],
            commitLines: []
          },
          weekly: {
            labels: [],
            commits: [],
            commitLines: []
          }
        }
        
        const response = data

        // Process the API response data using utility function
        if (response && response.monthly_commits) {
          let monthlyData = { labels: [], values: [] }
          let addedLinesData = { labels: [], values: [] }
          
          // Process commits data
          if (response.monthly_commits.total_count) {
            monthlyData = processActivityData(response.monthly_commits.total_count)
          }
          
          // Process added lines data
          if (response.monthly_commits.added_lines) {
            addedLinesData = processAddedLinesData(response.monthly_commits.added_lines)
          }
          
          this.activityData.monthly = {
            labels: monthlyData.labels,
            commits: monthlyData.values,
            commitLines: addedLinesData.values // Use actual added lines data
          }
        }
        
        // Weekly data will be empty for now
        this.activityData.weekly = {
          labels: [],
          commits: [],
          commitLines: []
        }
        
        console.log('활동 추이 로드 완료:', this.activityData)
      } catch (error) {
        console.error('활동 차트 데이터 로드 실패:', error)
        // 에러 시 빈 데이터 설정
        this.activityData = {
          monthly: {
            labels: [],
            commits: [],
            commitLines: []
          },
          weekly: {
            labels: [],
            commits: [],
            commitLines: []
          }
        }
      }
    },

    async loadHeatmapData() {
      try {
        const response = await getEProfileHeatmap(this.student_uuid)
        this.heatmapData = response.data.heatmap
        console.log('히트맵 데이터 로드 완료:', this.heatmapData)

        this.loadActivityChart(response.data)

        this.user.introduction = response.data.student_introduction
        
        // Load user data from API response
        this.loadUserData(response.data)
        
        // Load user data from API response
        this.loadUserData(response.data)
        
        // Load repositories data from the same response
        this.loadRepositoriesFromResponse(response.data)

        // Load tech language data from total_language_percentage
        this.loadTechLanguagesData(response.data)

        // Load tech stack data from student_technolog_stack
        this.loadTechStackData(response.data)

        // Load team size data from total_contributors_count
        this.loadTeamSizeData(response.data)

        // Load stats data from total_stats
        this.loadStatsData(response.data)

      } catch (error) {
        console.error('히트맵 데이터 로드 실패:', error)
        // 에러 시 빈 데이터 설정
        this.heatmapData = {
          Mon: {}, Tue: {}, Wed: {}, Thu: {}, Fri: {}, Sat: {}, Sun: {}
        }
        this.repositoriesData = []
        this.techStackData = []
        this.teamSizeData = {
          labels: [],
          data: []
        }
        this.stats = {
          commitLines: { added: 0, deleted: 0 },
          issues: { created: 0, closed: 0 },
          pullRequests: 0,
          openSourceContributions: 0
        }
      }
    },

    toggleDropdown(index) {
      // Close all other dropdowns
      this.techStackDropdowns.forEach((dropdown, i) => {
        if (i !== index) {
          dropdown.isOpen = false
        }
      })
      // Toggle the clicked dropdown
      this.techStackDropdowns[index].isOpen = !this.techStackDropdowns[index].isOpen
    },

    selectOption(dropdownIndex, option) {
      this.techStackDropdowns[dropdownIndex].selected = option
      this.techStackDropdowns[dropdownIndex].isOpen = false
    },

    getIconClass(techName) {
      if (!techName) return 'icon-default'
      
      const iconMap = {
        'Python': 'icon-python',
        'JavaScript': 'icon-js',
        'TypeScript': 'icon-typescript',
        'Java': 'icon-java',
        'C++': 'icon-cpp',
        'C#': 'icon-csharp',
        'Go': 'icon-go',
        'Rust': 'icon-rust',
        'Swift': 'icon-swift',
        'Kotlin': 'icon-kotlin',
        'React': 'icon-react',
        'Vue.js': 'icon-vue',
        'Angular': 'icon-angular',
        'Svelte': 'icon-svelte',
        'Django': 'icon-django',
        'Flask': 'icon-flask',
        'Express.js': 'icon-express',
        'Spring Boot': 'icon-spring',
        'PostgreSQL': 'icon-postgresql',
        'MySQL': 'icon-mysql',
        'MongoDB': 'icon-mongodb',
        'Redis': 'icon-redis',
        'Docker': 'icon-docker',
        'Kubernetes': 'icon-kubernetes',
        'AWS': 'icon-aws',
        'Google Cloud': 'icon-gcp',
        'Azure': 'icon-azure'
      }

      return iconMap[techName] || 'icon-default'
    },

    closeAllDropdowns() {
      this.techStackDropdowns.forEach(dropdown => {
        dropdown.isOpen = false
      })
    },

    // Helper method to convert techStackData object to chart array format
    convertTechStackDataForChart() {
      const colors = ['#FF176A', '#FF84A3', '#FFD1DC', '#C16179', '#FF90AB', '#FFA7AF']
      
      return Object.entries(this.techStackData)
        .filter(([language, percentage]) => percentage > 0)
        .map(([language, percentage], index) => ({
          name: language,
          value: percentage,
          color: colors[index] || colors[colors.length - 1],
          percentage: percentage
        }))
    },

    // Method to load tech stack data from API response
    loadTechLanguagesData(responseData) {
      try {
        if (responseData && responseData.total_language_percentage) {
          // Handle both object and array formats from API
          let languageData
          if (Array.isArray(responseData.total_language_percentage)) {
            // Convert array format to object format
            languageData = {}
            responseData.total_language_percentage.forEach(item => {
              languageData[item.language] = parseFloat(item.percentage) || 0
            })
          } else if (typeof responseData.total_language_percentage === 'object') {
            // Use object format directly
            languageData = responseData.total_language_percentage
          } else {
            console.warn('Invalid total_language_percentage format')
            return
          }

          // Process the language data to match your object structure
          this.techStackData = this.processLanguagePercentages(languageData)

          console.log('Tech stack data loaded from API:', this.techStackData)

          // Update the chart if it exists
          if (this.techStackChart) {
            this.createTechStackChart() // Recreate chart with new data
          }
        } else {
          console.warn('No total_language_percentage data found in API response')
        }
      } catch (error) {
        this.techStackData = []
        console.error('Error loading tech stack data:', error)
      }
    },

    loadTechStackData(responseData) {
      try {
        if (responseData.student_technology_stack) {
          const techStack = responseData.student_technology_stack

          // Parse if it's a string, otherwise use as is
          const techStackArray = typeof techStack === 'string' ? JSON.parse(techStack) : techStack

          // Update the techStackDropdowns with the loaded data
          if (Array.isArray(techStackArray)) {
            techStackArray.forEach((tech, index) => {
              if (index < this.techStackDropdowns.length && tech) {
                this.techStackDropdowns[index].selected = tech
              }
            })
            console.log('Tech stack dropdowns loaded from API:', this.techStackDropdowns)
          }
        } else {
          console.warn('No student_technology_stack data found in API response')
        }
      } catch (error) {
        console.error('Error loading tech stack dropdown data:', error)
      }
    },

    // Helper method to process language percentages and ensure they sum to 100%
    processLanguagePercentages(languageData) {
      // Convert object to array and round to nearest tenth
      let entries = Object.entries(languageData).map(([language, percentage]) => ({
        language,
        percentage: Math.round(parseFloat(percentage) * 10) / 10
      }))

      // Filter out zero values and sort by percentage descending
      entries = entries.filter(item => item.percentage > 0)
        .sort((a, b) => b.percentage - a.percentage)

      // Limit to maximum 6 languages
      if (entries.length > 6) {
        // Sum the remaining languages into "others"
        const topFive = entries.slice(0, 5)
        const othersSum = entries.slice(5).reduce((sum, item) => sum + item.percentage, 0)
        if (othersSum > 0) {
          entries = [...topFive, { language: 'others', percentage: Math.round(othersSum * 10) / 10 }]
        } else {
          entries = topFive
        }
      }

      // Ensure total is exactly 100% without exceeding
      const currentTotal = entries.reduce((sum, item) => sum + item.percentage, 0)
      const difference = Math.round((100 - currentTotal) * 10) / 10
      
      if (Math.abs(difference) >= 0.1) {
        // Adjust the largest percentage to make total exactly 100%
        if (entries.length > 0) {
          entries[0].percentage = Math.round((entries[0].percentage + difference) * 10) / 10
          // Ensure it doesn't go negative
          if (entries[0].percentage < 0) {
            entries[0].percentage = 0
          }
        }
      }

      // Convert back to object format matching your dummy data structure
      const result = {}
      entries.forEach(item => {
        result[item.language] = item.percentage
      })

      return result
    },

    // Method to load team size data from API response
    loadTeamSizeData(responseData) {
      try {
        if (responseData && responseData.total_contributors_count) {
          // Process the total_contributors_count data
          this.teamSizeData = this.processTeamSizeData(responseData.total_contributors_count)

          console.log('Team size data loaded from API:', this.teamSizeData)

          // Update the chart if it exists
          if (this.teamSizeChart) {
            this.createTeamSizeChart() // Recreate chart with new data
          }
        } else {
          console.warn('No total_contributors_count data found in API response')
        }
      } catch (error) {
        console.error('Error loading team size data:', error)
      }
    },

    // Helper method to process total_contributors_count data
    processTeamSizeData(total_contributors_count) {
      // Define the order we want to display
      const orderedKeys = ['1', '2', '3', '4', '5+']
      const keyMapping = {
        '1': '1인',
        '2': '2인', 
        '3': '3인',
        '4': '4인',
        '5+': '5인 이상'
      }

      const labels = []
      const data = []

      // Process each key in the specific order
      orderedKeys.forEach(key => {
        labels.push(keyMapping[key])
        data.push(parseInt(total_contributors_count[key]) || 0)
      })

      return {
        labels: labels,
        data: data
      }
    },

    // Method to load stats data from API response
    loadStatsData(responseData) {
      try {
        if (responseData && responseData.total_stats) {
          // Process the total_stats data
          const totalStats = responseData.total_stats
          
          // Calculate total repositories count
          const totalRepoCount = Array.isArray(responseData.repositories) 
            ? responseData.repositories.length 
            : (responseData.repositories ? 1 : 0)

          this.stats = {
            commitLines: {
              added: parseInt(totalStats.owner_added_lines) || 0, 
              deleted: parseInt(totalStats.owner_deleted_lines) || 0
            },
            issues: {
              created: parseInt(totalStats.owner_open_issue_count) || 0, 
              closed: parseInt(totalStats.owner_closed_issue_count) || 0
            },
            pullRequests: parseInt(totalStats.owner_open_pr_count) || 0,
            openSourceContributions: totalRepoCount
          }

          console.log('Stats data loaded from API:', this.stats)
        } else {
          console.warn('No total_stats data found in API response')
        }
      } catch (error) {
        console.error('Error loading stats data:', error)
      }
    },

    // Load user data from API response
    loadUserData(responseData) {
      try {
        // API 응답에서 student 정보가 직접 포함되어 있지 않을 수 있으므로
        // repositories 데이터에서 owner_github_id를 추출하거나
        // 다른 방식으로 github_id를 가져와야 할 수 있습니다
        
        // 일단 responseData에 github_id가 있는지 확인
        if (responseData && responseData.github_id) {
          this.user.github_id = responseData.github_id
        }
        
        // repositories에서 첫 번째 레포의 owner_github_id를 사용 (임시)
        if (responseData && responseData.repositories && responseData.repositories.length > 0) {
          const firstRepo = responseData.repositories[0]
          // 현재 사용자가 owner인 경우에만 github_id 사용
          if (firstRepo.is_owner && firstRepo.owner_github_id) {
            this.user.github_id = firstRepo.owner_github_id
          }
        }
        
        // student_introduction이 있으면 업데이트
        if (responseData && responseData.student_introduction) {
          this.user.introduction = responseData.student_introduction
        }
        
        console.log('User data loaded from API:', this.user)
        console.log('Full API response:', responseData)
      } catch (error) {
        console.error('Error loading user data:', error)
      }
    },

    // Add these methods to your methods object
    loadRepositoriesFromResponse(responseData) {
      try {
        this.repositoriesLoading = true
        this.repositoriesError = null
        
        // Process the repositories data
        if (responseData && responseData.repositories) {
          // Handle case where repositories might be an array or single object
          this.repositoriesData = Array.isArray(responseData.repositories) 
            ? responseData.repositories 
            : [responseData.repositories]
        } else {
          // Keep existing test data if no API data (don't clear it)
          console.log('No repository data from API, keeping existing data')
        }
        
        console.log('Repository data processed:', this.repositoriesData)
        
      } catch (error) {
        console.error('Repository data processing failed:', error)
        this.repositoriesError = error
        this.repositoriesData = [

        ]
      } finally {
        this.repositoriesLoading = false
      }
    },

    // Sorting methods
    sortByColumn(column) {
      if (this.sortBy === column) {
        // Toggle sort direction if clicking the same column
        this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc'
      } else {
        // Set new column and default to ascending
        this.sortBy = column
        this.sortDirection = 'asc'
      }
      // Reset pagination when sorting changes
      this.resetPagination()
    },

    getSortIcon(column) {
      if (this.sortBy !== column) {
        return 'icon-sort-default'
      }
      return this.sortDirection === 'asc' ? 'icon-sort-up' : 'icon-sort-down'
    },

    // Repository type, commits, PRs, issues calculation methods
    getRepoType(repo) {
      if (repo.is_owner) {
        return '-'
      } else if (repo.is_contributor) {
        return repo.owner_github_id || 'N/A'
      }
      return 'N/A'
    },

    getRepoCommits(repo) {
      if (repo.is_owner) {
        return repo.user_commit_count || 0
      } else if (repo.is_contributor) {
        return repo.user_commit_count || 0
      }
      return 0
    },

    getRepoPRs(repo) {
      if (repo.is_owner || repo.is_contributor) {
        const openPRs = repo.owner_open_pr_count || 0
        const closedPRs = repo.owner_closed_pr_count || 0
        return openPRs + closedPRs
      }
      return 0
    },

    getRepoIssues(repo) {
      if (repo.is_owner) {
        return repo.owner_issue_count || 0
      } else if (repo.is_contributor) {
        return repo.owner_issue_count || 0
      }
      return 0
    },

    // Category dropdown methods
    toggleCategoryDropdown(repoId) {
      // Close all other category dropdowns
      Object.keys(this.categoryDropdownOpen).forEach(id => {
        if (id !== repoId.toString()) {
          this.categoryDropdownOpen[id] = false
        }
      })
      
      // Toggle the clicked dropdown
      this.categoryDropdownOpen[repoId] = !this.categoryDropdownOpen[repoId]
      this.$forceUpdate() // Force reactivity update
    },

    selectCategoryOption(repoId, option) {
      // Find the repository and update its category
      const repo = this.repositoriesData.find(r => r.id === repoId)
      if (repo) {
        repo.category = option
      }
      
      // Close the dropdown
      this.categoryDropdownOpen[repoId] = false
      this.$forceUpdate() // Force reactivity update
    },

    closeCategoryDropdowns() {
      Object.keys(this.categoryDropdownOpen).forEach(id => {
        this.categoryDropdownOpen[id] = false
      })
      this.$forceUpdate() // Force reactivity update
    },

    shouldDropUp(repoId) {
      // Simple approach: check if this is one of the last few rows
      const currentIndex = this.paginatedRepositoriesData.findIndex(repo => repo.id === repoId)
      const totalRows = this.paginatedRepositoriesData.length

      // If it's in the last 3 rows, drop up
      return currentIndex >= totalRows - 3
    },

    // Pagination methods
    goToPage(page) {
      if (page >= 1 && page <= this.totalPages && page !== this.currentPage) {
        this.currentPage = page
        this.closeCategoryDropdowns()
      }
    },

    // Reset pagination when sorting changes
    resetPagination() {
      this.currentPage = 1
    }
  }
}
</script>

<style scoped>
/* Global Styles */
.e-portfolio {
  font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif;
  background: linear-gradient(to bottom, #F5F7FA 0%, #F5F7FA 55%, #FFFFFF 61%, #FFFFFF 100%);
  min-height: 100vh;
  width: 100%;
  max-width: 1920px;
  margin: 0 auto;
  padding-top: 150px; /* Proper spacing from navigation bar */
  box-sizing: border-box;
}

/* Save Section */
.save-section {
  display: flex;
  justify-content: flex-end;
  padding: 0 calc((100% - 1280px) / 2 + 20px);
  margin-bottom: 30px; /* Space before main content */
  box-sizing: border-box;
}

.save-btn {
  background: #FCFCFC;
  border: 1px solid #CB385C;
  border-radius: 30px;
  padding: 5px 17px;
  font-size: 14px;
  color: #CB385C;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 113px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
}

.save-btn:hover {
  background: #CB385C;
  color: #FCFCFC;
}

.pdf-export-btn {
  background: #FCFCFC;
  border: 1px solid #4A90E2;
  border-radius: 30px;
  padding: 5px 17px;
  font-size: 14px;
  color: #4A90E2;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 113px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
  margin-right: 10px;
}

.pdf-export-btn:hover {
  background: #4A90E2;
  color: #FCFCFC;
}

/* PDF Export Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.pdf-export-modal {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #262626;
}

.close-btn {
  background: none;
  border: none;
  font-size: 28px;
  color: #666;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background 0.2s;
}

.close-btn:hover {
  background: #f0f0f0;
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

.modal-description {
  margin: 0 0 20px 0;
  color: #666;
  font-size: 14px;
}

.search-section {
  margin-bottom: 16px;
}

.search-input {
  width: 100%;
  padding: 10px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  font-family: 'Pretendard', sans-serif;
  outline: none;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.search-input:focus {
  border-color: #4A90E2;
}

.select-actions {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.action-btn {
  padding: 8px 16px;
  background: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
  font-family: 'Pretendard', sans-serif;
}

.action-btn:hover {
  background: #e8e8e8;
  border-color: #bbb;
}

.repo-list {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 12px;
}

.repo-checkbox-item {
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.repo-checkbox-item:last-child {
  border-bottom: none;
}

.repo-checkbox-item label {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 14px;
  color: #262626;
}

.repo-checkbox-item input[type="checkbox"] {
  margin-right: 10px;
  cursor: pointer;
  width: 16px;
  height: 16px;
}

.modal-footer {
  padding: 16px 24px;
  border-top: 1px solid #e0e0e0;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.cancel-btn, .confirm-btn {
  padding: 10px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-family: 'Pretendard', sans-serif;
  border: none;
}

.cancel-btn {
  background: #f5f5f5;
  color: #666;
}

.cancel-btn:hover {
  background: #e8e8e8;
}

.confirm-btn {
  background: #4A90E2;
  color: white;
}

.confirm-btn:hover {
  background: #3a7bc8;
}

.confirm-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

/* Main Content */
.main-content {
  width: 100%;
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 20px;
  box-sizing: border-box;
}

/* Profile Section */
.profile-section {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 1rem; /* 16px */
  margin-bottom: 2.5rem; /* 40px */
  align-items: stretch; /* Ensure both cards have same height */
}

.profile-card {
  background: #FFFFFF;
  border: 1px solid #E8EDF8;
  border-radius: 1.25rem; /* 20px */
  padding: 1.875rem; /* 30px */
  min-height: 27.5rem; /* 440px */
  height: 100%; /* Match grid item height to align bottoms */
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

/* Profile Header Layout - NEW */
.profile-header {
  display: flex;
  align-items: flex-start;
  gap: 1rem; /* 16px */
  margin-bottom: 1.25rem; /* 20px */
  flex-shrink: 0;
}

/* Profile Picture Placeholder - NEW */
.profile-picture-placeholder {
  width: 5.875rem; /* 94px */
  height: 5.875rem; /* 94px */
  /* background-color: #E2E7F0; */
  background-image: url('@/assets/emblem_school_transparent.gif') ;
  background-repeat: no-repeat;
  background-position: center;
  background-size: 70%;
  border-radius: 0.625rem; /* 10px */
  flex-shrink: 0;
}

/* Right Column Container - NEW */
.right-column {
  display: flex;
  flex-direction: column;
  gap: 1rem; /* 16px */
}

/* Combined Tech Stack and Skills Card */
.combined-tech-skills-card {
  background: #FFFFFF;
  border: 1px solid #E8EDF8;
  border-radius: 1.25rem; /* 20px */
  padding: 3.125rem 3.125rem 1.875rem 3.125rem; /* 50px 50px 30px 50px */
  min-height: 27.5rem; /* 440px */
  height: 100%; /* Match grid item height to align bottoms */
  display: flex;
  flex-direction: column;
  gap: 1.875rem; /* 30px */
  box-sizing: border-box;
}

/* Tech Stack Section within combined card */
.combined-tech-skills-card .tech-stack-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Skills Section within combined card */
.combined-tech-skills-card .skills-section {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  height: 142px;
}

.profile-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.profile-name {
  font-size: 22px;
  font-weight: 600;
  color: #262626;
  margin: 0;
}

.profile-details {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 16px;
  color: #262626;
}

.detail-content {
  display: flex;
  gap: 16px;
}

.github-link {
  color: #262626;
  text-decoration: none;
  transition: all 0.2s ease;
}

.github-link:hover {
  color: #262626;
  text-decoration: underline;
}

.edit-profile-btn {
  background: #FFFFFF;
  border: 1px solid #CDCDCD;
  border-radius: 10px;
  padding: 15px 126px;
  font-size: 18px;
  color: #616161;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 355px;
  height: 46px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.edit-profile-btn:hover {
  border-color: #910024;
  color: #910024;
}

/* Tech Stack - Updated for combined card */
.tech-stack-dropdown-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
  flex: 1;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #262626;
  margin: 0px;
}

.section-subtitle {
  font-size: 16px;
  font-weight: 600;
  color: #262626;
  margin: 0px;
}

.tech-stack-content {
  display: flex;
  align-items: flex-start;
  gap: 40px;
  height: 100%;
}

.main-languages-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
  flex: 1;
}

.chart-and-legend {
  display: flex;
  align-items: flex-start;
  gap: 25px;
  min-height: 120px;
}

.chart-container {
  position: relative;
  width: 120px;
  height: 120px;
  flex-shrink: 0;
}

.chart-container canvas {
  width: 120px !important;
  height: 120px !important;
}

.chart-legend {
  display: flex;
  flex-direction: column;
  gap: 8px;
  justify-content: center;
  min-height: 120px;
  max-width: 200px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #616161;
  line-height: 1.2;
}

.legend-color {
  width: 13px;
  height: 13px;
  border-radius: 50%;
  flex-shrink: 0;
}

.vertical-divider {
  width: 1px;
  height: 180px;
  background: #E8EDF8;
  align-self: stretch;
  margin: 0px 0px 0px;
}

/* Tech stack section styles are now handled by the combined card */

.tech-column-title {
  font-size: 20px;
  font-weight: 600;
  color: #262626;
  margin: 0;
}

.tech-tags {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px 7px;
  align-items: start;
}

.tech-tag {
  background: #EFF2F9;
  border-radius: 10px;
  padding: 5px 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
  color: #616161;
  width: 192px;
  height: 30px;
}

/* Tech Stack Dropdown Styles */
.tech-dropdowns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px 7px;
  align-items: start;
}

.tech-dropdown-container {
  position: relative;
}

.tech-dropdown {
  background: #EFF2F9;
  border-radius: 10px;
  width: 192px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.tech-dropdown.dropdown-open {
  border-radius: 10px 10px 0 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  position: relative;
  z-index: 1;
}

.tech-dropdown.dropdown-disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.tech-dropdown.dropdown-disabled .dropdown-selected:hover {
  background: transparent;
}

.dropdown-selected {
  padding: 5px 14px;
  border-radius: 10px 10px 0 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
  color: #616161;
  height: 30px;
}

.dropdown-selected:hover {
  background: rgba(239, 242, 249, 0.8);
  border-radius: 10px;
}

.dropdown-options {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: #FFFFFF;
  border: 1px solid #E8EDF8;
  border-top: none;
  border-radius: 0 0 10px 10px;
  max-height: 200px;
  overflow-y: auto;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.dropdown-option {
  padding: 8px 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #616161;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.dropdown-option:hover {
  background: #F8F9FA;
  color: #262626;
}

.dropdown-option:last-child {
  border-radius: 0 0 10px 10px;
}

.icon-arrow-down {
  transition: transform 0.3s ease;
}

.icon-arrow-down.rotated {
  transform: rotate(-90deg);
}

/* Dropdown scrollbar styling */
.dropdown-options::-webkit-scrollbar {
  width: 6px;
}

.dropdown-options::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.dropdown-options::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.dropdown-options::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* Skills Section - Updated for combined card */
.skills-section {
  margin-bottom: 0; /* No margin needed in combined card */
}

.section-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 30px;
}

.section-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #262626;
  margin: 0;
}

/* Skills Stats Container */
.skills-stats-container {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.skills-stats {
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 16px 26px;
  gap: 0px;
  width: 100%;
  max-width: 750px; /* 전체 너비를 조정하여 더 균형잡힌 레이아웃 */
  height: 102px;
  background: #FAFBFD;
  border: 1px solid #E8EDF8;
  border-radius: 10px;
  box-sizing: border-box;
}

.stat-item {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 0px 10px;
  gap: 8px;
  height: 58px;
  flex: none;
  order: 0;
  flex-grow: 0;
  position: relative;
}

/* 각 항목별 너비 조정 */
.stat-item:nth-child(1) {
  width: 210px; /* 추가/삭제 커밋 라인 수 - 가장 넓게 */
}

.stat-item:nth-child(2) {
  width: 170px; /* 이슈 생성/닫은 수 - 적당히 */
}

.stat-item:nth-child(3) {
  width: 130px; /* PR 생성 수 - 기본 */
}

  .stat-item:nth-child(4) {
    width: 180px; /* 오픈소스 프로젝트 - 한 줄로 표시되도록 넓게 */
  }

.stat-item:not(:last-child)::after {
  content: '';
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 1px;
  height: 70px;
  background: #E8EDF8;
}

.stat-content {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 8px;
  width: 100%;
  height: 100%;
}

.stat-title {
  width: 100%;
  height: auto;
  font-family: 'Pretendard';
  font-style: normal;
  font-weight: 500;
  font-size: 16px;
  line-height: 1.2;
  color: #616161;
  text-align: center;
  flex: none;
  order: 0;
  flex-grow: 0;
  margin: 0;
}

.stat-value {
  width: 100%;
  height: auto;
  font-family: 'Pretendard';
  font-style: normal;
  font-weight: 500;
  font-size: 16px;
  line-height: 1.2;
  color: #262626;
  text-align: center;
  flex: none;
  order: 0;
  flex-grow: 0;
  margin: 0;
}

.stat-divider {
  display: none; /* 기존 구분선 제거 */
}

/* Activity Section */
.activity-section {
  margin-bottom: 40px;
}

/* Activity Section Header */
.activity-section-header {
  margin-bottom: 30px;
}

.activity-header-content {
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 0px;
  gap: 8px;
  width: 160px;
  height: 28px;
}

.activity-icon {
  width: 28px;
  height: 28px;
  flex: none;
  order: 0;
  flex-grow: 0;
  position: relative;
}

.activity-icon::before {
  content: '' !important;
  position: absolute !important;
  left: 8.33% !important;
  right: 8.33% !important;
  top: 12.5% !important;
  bottom: 12.5% !important;
  border: 2px solid #262626 !important;
  border-radius: 0 !important;
  background: transparent !important;
  display: block !important;
  width: auto !important;
  height: auto !important;
}

.activity-title {
  width: 124px;
  height: 26px;
  font-family: 'Pretendard';
  font-style: normal;
  font-weight: 600;
  font-size: 22px;
  line-height: 26px;
  letter-spacing: -0.004em;
  color: #262626;
  margin: 0;
  flex: none;
  order: 1;
  flex-grow: 0;
}

.activity-charts {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem; /* 16px */
  margin-bottom: 1.875rem; /* 30px */
  align-items: stretch; /* Ensure both cards have same height */
}

.chart-card {
  background: #FFFFFF;
  border-radius: 1.25rem; /* 20px */
  padding: 1.875rem 2.5rem; /* 30px 40px */
  min-height: 21.6875rem; /* 347px */
  height: 100%; /* Match grid item height */
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem; /* 20px */
  flex-shrink: 0;
}

.chart-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.chart-title h3 {
  font-size: 18px;
  font-weight: 600;
  color: #262626;
  margin: 0;
}

/* Chart Title Text Style */
.chart-title-text {
  font-family: 'Pretendard';
  font-style: normal;
  font-weight: 600;
  font-size: 20px;
  line-height: 24px;
  color: #E40052;
  margin: 0;
}

/* Override for chart title text in section header */
.section-header .chart-title-text {
  font-family: 'Pretendard' !important;
  font-style: normal !important;
  font-weight: 600 !important;
  font-size: 20px !important;
  line-height: 24px !important;
  color: #E40052 !important;
  margin: 0 !important;
}

/* UPDATED: Enhanced chart toggle styling
.chart-toggle {
  background: #FFEEF0;
  border-radius: 40px;
  padding: 3px;
  display: flex;
  font-size: 12px;
  gap: 0px;
  width: 128px;
  height: 30px;
  align-items: center;
}

.toggle-active {
  background: #FCFCFC;
  border: 1px solid #FFE2E5;
  border-radius: 42px;
  padding: 5px 15px;
  color: #CB385C;
  cursor: pointer;
  transition: all 0.3s ease;
  flex: 1;
  text-align: center;
}

.toggle-inactive {
  padding: 5px 15px;
  color: #FFA7AF;
  cursor: pointer;
  transition: all 0.3s ease;
  flex: 1;
  text-align: center;
}

.toggle-inactive:hover {
  color: #CB385C;
}

.chart-description {
  font-size: 16px;
  color: #616161;
  margin: 0 0 24px 0;
} */

/* UPDATED: Enhanced legend positioning */
.chart-legend-horizontal {
  display: flex;
  gap: 1.25rem; /* 20px */
  margin-bottom: 1.25rem; /* 20px */
  justify-content: flex-end;
  flex-shrink: 0;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

/* NEW: Activity Chart Specific Styles */
.activity-chart-container {
  position: relative;
  flex: 1; /* Take remaining space in chart-card */
  min-height: 12.5rem; /* 200px */
  width: 100%;
  margin-top: 0.625rem; /* 10px */
}

.activity-chart-container canvas {
  width: 100% !important;
  height: 100% !important;
}

.chart-area,
.bar-chart {
  height: 200px;
  display: flex;
  flex-direction: column;
}

.chart-placeholder {
  flex: 1;
  background: #f8f9fa;
  border: 2px dashed #dee2e6;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6c757d;
  border-radius: 8px;
}

.chart-y-axis {
  display: flex;
  flex-direction: column-reverse;
  justify-content: space-between;
  height: 100%;
  font-size: 12px;
  color: #262626;
  margin-right: 10px;
}

.chart-x-axis,
.bar-chart-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
  font-size: 14px;
  color: #262626;
}

.team-size-chart-container {
  position: relative;
  flex: 1; /* Take remaining space in chart-card */
  min-height: 12.5rem; /* 200px */
  width: 100%;
  margin-top: 1.25rem; /* 20px */
}

.team-size-chart-container canvas {
  width: 100% !important;
  height: 100% !important;
}

/* Time Pattern */
.time-pattern-card {
  background: #FFFFFF;
  border-radius: 1.25rem; /* 20px */
  padding: 1.875rem 2.5rem; /* 30px 40px */
  width: 100%;
  max-width: 80rem; /* 1280px */
  min-height: 19rem; /* 304px */
  height: auto;
  box-sizing: border-box;
  margin-left: 0;
  margin-right: auto;
}

/* Projects Section */
.projects-section {
  margin-bottom: 3.5rem; /* 56px */
  background: #FFFFFF;
  padding: 1.875rem 2.5rem; /* 30px 40px - match time-pattern-card */
  border-radius: 1.25rem; /* 20px */
  box-sizing: border-box;
  width: 100%;
  max-width: 100%; /* Extend to full width of main-content */
  margin-left: 0;
  margin-right: 0;
}

.projects-section .section-header {
  margin-bottom: 1.875rem; /* 30px - match time-pattern-card */
  padding-left: 0;
  display: flex;
  align-items: center;
  gap: 0.625rem; /* 10px */
}

.projects-section .section-header .icon-archive {
  color: #262626;
  font-size: 1.25rem; /* 20px - match chart-title-text */
}

.projects-section .section-header .projects-title {
  color: #262626 !important; /* Override chart-title-text default color */
  font-size: 20px !important; /* Match chart-title-text (활동 시간대) */
  line-height: 24px !important; /* Match chart-title-text */
}

.projects-table {
  background: #FFFFFF;
  border-radius: 0.625rem; /* 10px */
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  width: 100%;
  box-sizing: border-box;
  
  /* Column width variables - easily adjustable */
  --col-category: 120px;
  --col-repository: 180px;
  --col-type: 100px;
  --col-commits: 90px;
  --col-prs: 70px;
  --col-issues: 80px;
  --col-stars: 80px;
  --col-forks: 80px;
  --col-language: 120px;
  --col-contributors: 110px;
}

.table-header {
  background: #F8F9FA;
  display: grid;
  grid-template-columns: 
    var(--col-category, 120px)
    var(--col-repository, 180px) 
    var(--col-type, 100px)
    var(--col-commits, 90px) 
    var(--col-prs, 70px) 
    var(--col-issues, 80px) 
    var(--col-stars, 80px) 
    var(--col-forks, 80px) 
    var(--col-language, 120px) 
    var(--col-contributors, 110px);
  gap: 15px;
  padding: 15px 20px;
  font-size: 16px;
  font-weight: 600;
  text-align: center;
  color: #CB385C;
  border-bottom: 1px solid #F9D2D6;
}

/* Sortable Header Styles */
.sortable-header {
  cursor: pointer;
  user-select: none;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  transition: color 0.2s ease;
}

.sortable-header:hover {
  color: #910024;
}

.sortable-header i {
  width: 12px;
  height: 12px;
  opacity: 0.6;
  transition: opacity 0.2s ease;
}

.sortable-header:hover i {
  opacity: 1;
}

.table-row {
  display: grid;
  grid-template-columns: 
    var(--col-category, 120px)
    var(--col-repository, 180px) 
    var(--col-type, 100px)
    var(--col-commits, 90px) 
    var(--col-prs, 70px) 
    var(--col-issues, 80px) 
    var(--col-stars, 80px) 
    var(--col-forks, 80px) 
    var(--col-language, 120px) 
    var(--col-contributors, 110px);
  gap: 15px;
  padding: 12px 20px;
  align-items: center;
  text-align: center;
  border-bottom: 1px solid #DCE2ED;
  font-size: 16px;
  color: #262626;
}

.table-row > span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Repository column hover effect */
.table-row > span:nth-child(2) {
  cursor: default;
  transition: color 0.2s ease;
}

.table-row > span:nth-child(2):hover {
  color: #CB385C;
}

/* Language column hover effect */
.table-row > span:nth-child(9) {
  cursor: default;
  transition: color 0.2s ease;
}

.table-row > span:nth-child(9):hover {
  color: #CB385C;
}

.table-row:last-child {
  border-bottom: none;
}

.category-column {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-width: var(--col-category);
  box-sizing: border-box;
}

.category-type {
  padding: 3px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.category-dropdown {
  position: relative;
  cursor: pointer;
}

.category-dropdown.dropdown-disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.category-dropdown.dropdown-disabled .category-dropdown-selected:hover {
  background: #F8F9FA;
}

.category-dropdown-selected {
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 11px;
  text-align: center;
  background: #F8F9FA;
  color: #616161;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 4px;
  transition: all 0.2s ease;
}

.category-dropdown-selected:hover {
  background: #E9ECEF;
}

.category-dropdown.dropdown-open .category-dropdown-selected {
  border-radius: 6px 6px 0 0;
  background: #E9ECEF;
}

.category-dropdown.dropdown-up .category-dropdown-selected {
  border-radius: 0 0 6px 6px;
  background: #E9ECEF;
}

.category-dropdown-selected i {
  width: 10px;
  height: 10px;
  transition: transform 0.2s ease;
}

.category-dropdown-options {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: #FFFFFF;
  border: 1px solid #DEE2E6;
  border-top: none;
  border-radius: 0 0 6px 6px;
  max-height: 150px;
  overflow-y: auto;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  z-index: 10;
}

.category-dropdown-options.options-up {
  top: auto;
  bottom: 100%;
  border-top: 1px solid #DEE2E6;
  border-bottom: none;
  border-radius: 6px 6px 0 0;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.15);
}

.category-dropdown-option {
  padding: 6px 8px;
  font-size: 11px;
  text-align: center;
  cursor: pointer;
  transition: background-color 0.2s ease;
  color: #616161;
}

.category-dropdown-option:hover {
  background: #F8F9FA;
  color: #262626;
}

.category-dropdown-option:last-child {
  border-radius: 0 0 6px 6px;
}

.category-static {
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 11px;
  text-align: center;
  background: #F8F9FA;
  color: #616161;
}

.category-column.autonomous .category-type {
  background: #EFF2F9;
  color: #507199;
}

.category-column.course .category-type {
  background: #FFEAEC;
  color: #CB385C;
}

/* Icons - You'll need to replace these with actual icon implementations */
.icon-location,
.icon-mail,
.icon-message,
.icon-file,
.icon-activity,
.icon-archive,
.icon-link,
.icon-github,
.icon-react,
.icon-python,
.icon-kotlin,
.icon-js,
.icon-django,
.icon-arrow-down {
  width: 18px;
  height: 18px;
  background: #949494;
  border-radius: 2px;
}

.icon-location {
  width: 18px;
  height: 18px;
  background: url('@/assets/icons/icon_person.svg') no-repeat center;
  background-size: contain;
}

.icon-mail {
  width: 18px;
  height: 18px;
  background: url('@/assets/icons/icon_mail.svg') no-repeat center;
  background-size: contain;
}

.icon-github {
  width: 18px;
  height: 18px;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%23616161"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>') no-repeat center;
  background-size: contain;
  flex-shrink: 0;
  opacity: 0.7;
}

.icon-message {
  width: 20px;
  height: 20px;
  background: url('@/assets/icons/icon_message.svg') no-repeat center;
  background-size: contain;
}

.icon-archive {
  width: 18px;
  height: 18px;
  background: url('@/assets/icons/icon_archive.svg') no-repeat center;
  background-size: contain;
}

.icon-activity {
  width: 18px;
  height: 18px;
  background: url('@/assets/icons/icon_linechart.svg') no-repeat center;
  background-size: contain;
}

.icon-arrow-down {
  width: 18px;
  height: 18px;
  background: url('@/assets/icons/icon_dropdown.svg') no-repeat center;
  background-size: contain;
}

/* Dropdown Icons */
.icon-default,
.icon-python,
.icon-js,
.icon-typescript,
.icon-java,
.icon-cpp,
.icon-csharp,
.icon-go,
.icon-rust,
.icon-swift,
.icon-kotlin,
.icon-react,
.icon-vue,
.icon-angular,
.icon-svelte,
.icon-django,
.icon-flask,
.icon-express,
.icon-spring,
.icon-postgresql,
.icon-mysql,
.icon-mongodb,
.icon-redis,
.icon-docker,
.icon-kubernetes,
.icon-aws,
.icon-gcp,
.icon-azure {
  width: 18px;
  height: 18px;
  background: #949494;
  border-radius: 2px;
  flex-shrink: 0;
}

.icon-default { background: url('@/assets/icons/logos/default.svg') no-repeat center; background-size: contain; width: 18px; height: 18px; flex-shrink: 0; }
.icon-python { background: url('@/assets/icons/logos/python.svg') no-repeat center; background-size: contain; width: 18px; height: 18px; flex-shrink: 0; }
.icon-js { background: url('@/assets/icons/logos/js.svg') no-repeat center; background-size: contain; width: 18px; height: 18px; flex-shrink: 0; }
.icon-typescript { background: url('@/assets/icons/logos/typescript.svg') no-repeat center; background-size: contain; width: 18px; height: 18px; flex-shrink: 0; }
.icon-java { background: url('@/assets/icons/logos/java.svg') no-repeat center; background-size: contain; width: 18px; height: 18px; flex-shrink: 0; }
.icon-cpp { background: url('@/assets/icons/logos/cpp.svg') no-repeat center; background-size: contain; width: 18px; height: 18px; flex-shrink: 0; }
.icon-csharp { background: url('@/assets/icons/logos/csharp.svg') no-repeat center; background-size: contain; width: 18px; height: 18px; flex-shrink: 0; }
.icon-go { background: url('@/assets/icons/logos/go.svg') no-repeat center; background-size: contain; width: 18px; height: 18px; flex-shrink: 0; }
.icon-rust { background: url('@/assets/icons/logos/rust.svg') no-repeat center; background-size: contain; width: 18px; height: 18px; flex-shrink: 0; }
.icon-swift { background: url('@/assets/icons/logos/swift.svg') no-repeat center; background-size: contain; width: 18px; height: 18px; flex-shrink: 0; }
.icon-kotlin { background: url('@/assets/icons/logos/kotlin.svg') no-repeat center; background-size: contain; width: 18px; height: 18px; flex-shrink: 0; }
.icon-react { background: url('@/assets/icons/logos/react.svg') no-repeat center; background-size: contain; width: 18px; height: 18px; flex-shrink: 0; }
.icon-vue { background: url('@/assets/icons/logos/vue.svg') no-repeat center; background-size: contain; width: 18px; height: 18px; flex-shrink: 0; }
.icon-angular { background: url('@/assets/icons/logos/angular.svg') no-repeat center; background-size: contain; width: 18px; height: 18px; flex-shrink: 0; }
.icon-svelte { background: url('@/assets/icons/logos/svelte.svg') no-repeat center; background-size: contain; width: 18px; height: 18px; flex-shrink: 0; }
.icon-django { background: url('@/assets/icons/logos/django.svg') no-repeat center; background-size: contain; width: 18px; height: 18px; flex-shrink: 0; }
.icon-flask { background: url('@/assets/icons/logos/flask.svg') no-repeat center; background-size: contain; width: 18px; height: 18px; flex-shrink: 0; }
.icon-express { background: url('@/assets/icons/logos/express.svg') no-repeat center; background-size: contain; width: 18px; height: 18px; flex-shrink: 0; }
.icon-spring { background: url('@/assets/icons/logos/spring.svg') no-repeat center; background-size: contain; width: 18px; height: 18px; flex-shrink: 0; }
.icon-postgresql { background: url('@/assets/icons/logos/postgresql.svg') no-repeat center; background-size: contain; width: 18px; height: 18px; flex-shrink: 0; }
.icon-mysql { background: url('@/assets/icons/logos/mysql.svg') no-repeat center; background-size: contain; width: 18px; height: 18px; flex-shrink: 0; }
.icon-mongodb { background: url('@/assets/icons/logos/mongodb.svg') no-repeat center; background-size: contain; width: 18px; height: 18px; flex-shrink: 0; }
.icon-redis { background: url('@/assets/icons/logos/redis.svg') no-repeat center; background-size: contain; width: 18px; height: 18px; flex-shrink: 0; }
.icon-docker { background: url('@/assets/icons/logos/docker.svg') no-repeat center; background-size: contain; width: 18px; height: 18px; flex-shrink: 0; }
.icon-kubernetes { background: url('@/assets/icons/logos/kubernetes.svg') no-repeat center; background-size: contain; width: 18px; height: 18px; flex-shrink: 0; }
.icon-aws { background: url('@/assets/icons/logos/aws.svg') no-repeat center; background-size: contain; width: 18px; height: 18px; flex-shrink: 0; }
.icon-gcp { background: url('@/assets/icons/logos/gcp.svg') no-repeat center; background-size: contain; width: 18px; height: 18px; flex-shrink: 0; }
.icon-azure { background: url('@/assets/icons/logos/azure.svg') no-repeat center; background-size: contain; width: 18px; height: 18px; flex-shrink: 0; }

/* Sorting Icons */
.icon-sort-default,
.icon-sort-up,
.icon-sort-down {
  width: 12px;
  height: 12px;
  background: #CB385C;
  flex-shrink: 0;
}

.icon-sort-default {
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%23CB385C"><path d="M7 10l5 5 5-5H7z"/></svg>') no-repeat center;
  background-size: contain;
  transform: rotate(0deg);
  opacity: 0.4;
}

.icon-sort-up {
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%23CB385C"><path d="M7 14l5-5 5 5H7z"/></svg>') no-repeat center;
  background-size: contain;
}

.icon-sort-down {
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%23CB385C"><path d="M7 10l5 5 5-5H7z"/></svg>') no-repeat center;
  background-size: contain;
}

/* Profile Introduction Styles - EDITABLE */
.profile-intro {
  margin: 0.625rem 0 0 0; /* 10px top margin only, bottom handled by flex */
  flex: 1; /* Take remaining space to push content to top */
  display: flex;
  flex-direction: column;
  min-height: 0; /* Allow flex item to shrink */
}

.intro-header {
  display: flex;
  align-items: center;
  gap: 7px;
  margin-bottom: 10px;
}

.intro-header span {
  font-size: 16px;
  font-weight: 500;
  color: #262626;
}

.intro-input {
  width: 100%;
  flex: 1; /* Take remaining space in profile-intro */
  min-height: 3.75rem; /* 60px */
  padding: 0.75rem 1rem; /* 12px 16px */
  font-size: 0.875rem; /* 14px */
  line-height: 140%;
  color: #717989;
  background: #FFFFFF;
  border: 1px solid #E8EDF8;
  border-radius: 0.5rem; /* 8px */
  resize: vertical;
  font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif;
  transition: border-color 0.3s ease;
  box-sizing: border-box;
}

.intro-input:focus {
  outline: none;
  border-color: #CB385C;
  box-shadow: 0 0 0 2px rgba(203, 56, 92, 0.1);
}

.intro-input:disabled {
  background: #F5F7FA;
  cursor: not-allowed;
  opacity: 0.7;
}

.intro-input::placeholder {
  color: #CDCDCD;
}

.intro-counter {
  display: flex;
  justify-content: flex-end;
  margin-top: 0.125rem; /* 2px */
  font-size: 0.75rem; /* 12px */
  color: #949494;
  flex-shrink: 0; /* Prevent counter from shrinking */
}

/* Responsive Design */
@media (max-width: 1920px) {
  .e-portfolio {
    width: 100%;
    max-width: 1920px;
  }
  
  .save-section {
    padding: 0 calc((100% - min(1280px, 100% - 40px)) / 2 + 20px);
  }
  
  .time-pattern-card,
  .projects-table {
    width: 100%;
    max-width: 1280px;
  }
}

@media (max-width: 1400px) {
  .profile-section {
    grid-template-columns: 1fr;
  }
  
  .activity-charts {
    grid-template-columns: 1fr;
  }
  
  .skills-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .table-header,
  .table-row {
    grid-template-columns: repeat(6, 1fr);
    font-size: 14px;
  }
  
  .save-section {
    padding: 0 20px;
  }
}

@media (max-width: 768px) {
  .e-portfolio {
    padding-top: 100px;
  }
  
  .save-section {
    padding: 0 15px;
  }
  
  .main-content {
    padding: 0 15px;
  }
  
  .profile-card,
  .combined-tech-skills-card {
    padding: 20px;
  }
  
  .save-section {
    padding: 0 15px;
  }
  
  .tech-stack-content {
    flex-direction: column;
    align-items: center;
  }
  
  .skills-stats {
    grid-template-columns: 1fr;
  }
}

/* 클릭 가능한 레포지토리명 스타일 */
.repo-name-clickable {
  cursor: pointer;
  color: #CB385C;
  text-decoration: underline;
  transition: color 0.3s ease;
}

.repo-name-clickable:hover {
  color: #910024;
}

/* Pagination Styles */
.pagination-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 0;
  margin-top: 20px;
  border-top: 1px solid #E8EDF8;
}

.pagination-info {
  font-size: 14px;
  color: #616161;
  font-weight: 500;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pagination-btn {
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
  color: #616161;
  background: #FFFFFF;
  border: 1px solid #E8EDF8;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 80px;
}

.pagination-btn:hover:not(.disabled) {
  background: #F8F9FA;
  border-color: #CB385C;
  color: #CB385C;
}

.pagination-btn.disabled {
  color: #CDCDCD;
  cursor: not-allowed;
  background: #F8F9FA;
}

.page-numbers {
  display: flex;
  gap: 4px;
  margin: 0 8px;
}

.page-number {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 500;
  color: #616161;
  background: #FFFFFF;
  border: 1px solid #E8EDF8;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.page-number:hover {
  background: #F8F9FA;
  border-color: #CB385C;
  color: #CB385C;
}

.page-number.active {
  background: #CB385C;
  border-color: #CB385C;
  color: #FFFFFF;
}

.page-number.active:hover {
  background: #910024;
  border-color: #910024;
}

/* Responsive Pagination */
@media (max-width: 768px) {
  .pagination-section {
    flex-direction: column;
    gap: 15px;
    align-items: center;
  }

  .pagination-controls {
    flex-wrap: wrap;
    justify-content: center;
  }

  .pagination-btn {
    min-width: 60px;
    padding: 6px 12px;
    font-size: 12px;
  }

  .page-number {
    width: 32px;
    height: 32px;
    font-size: 12px;
  }
}
</style>