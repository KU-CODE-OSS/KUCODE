<template>
  <div class="e-portfolio">
    <!-- Save Button -->
      <div class="save-section">
        <button class="save-btn">변경사항 저장</button>
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
              <h2 class="profile-name">최다영 님</h2>
              <div class="profile-details">
                <div class="detail-item">
                  <i class="icon-location"></i>
                  <div class="detail-content">
                    <span>고려대학교 컴퓨터학과</span>
                  </div>
                </div>
                <div class="detail-item">
                  <i class="icon-mail"></i>
                  <span>joyyoj1@korea.ac.kr</span>
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
              rows="4"
              maxlength="150"
            ></textarea>
            <div class="intro-counter">
              {{ user.introduction.length }}/150
            </div>
          </div>
          
          <button class="edit-profile-btn">프로필 편집</button>
        </div>

        <!-- Right Column Container -->
        <div class="right-column">
          <!-- Tech Stack Section -->
          <div class="tech-stack-card">
            <h3 class="section-title">나의 기술 스택</h3>
            
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
              <div class="tech-stack-section">
                <h4 class="tech-column-title">주요 기술 스택</h4>
                <div class="tech-dropdowns">
                  <div 
                    v-for="(dropdown, index) in techStackDropdowns" 
                    :key="index"
                    class="tech-dropdown-container"
                  >
                    <div 
                      class="tech-dropdown"
                      :class="{ 'dropdown-open': dropdown.isOpen }"
                      @click.stop="toggleDropdown(index)"
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

          <!-- Skills Section - MOVED HERE -->
          <div class="skills-card">
            <div class="skills-stats">
              <div class="stat-item">
                <h4><div class="section-subtitle">개발 생산성</div>(추가·삭제 라인 수)</h4>
                <p>{{ stats.commitLines.added.toLocaleString() }} / {{ stats.commitLines.deleted.toLocaleString() }}</p>
              </div>
              <div class="stat-item">
                <h4><div class="section-subtitle">문제 해결력</div>(생성·해결 이슈)</h4>
                <p>{{ stats.issues.created }} / {{ stats.issues.closed }}</p>
              </div>
              <div class="stat-item">
                <h4><div class="section-subtitle">협업 능력</div>(PR 생성)</h4>
                <p>{{ stats.pullRequests }}개</p>
              </div>
              <div class="stat-item">
                <h4><div class="section-subtitle">오픈소스 기여 역량</div>(참여 오픈소스)</h4>
                <p>{{ stats.openSourceContributions }}개</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Activity Section -->
      <section class="activity-section">
        <div class="activity-charts">
          <!-- Activity Trends Chart -->
          <div class="chart-card">
            <div class="chart-header">
              <div class="chart-title">
                <i class="icon-activity"></i>
                <h3>활동 추이</h3>
              </div>
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
              <h3>활동 프로젝트 인원 비율</h3>
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
            <i class="icon-activity"></i>
            <h3>활동 시간대</h3>
          </div>
          
          <!-- 히트맵 컴포넌트 -->
          <EProfileHeatmap :heatmapData="heatmapData" />
        </div>
      </section>

      <!-- Projects Section -->
      <section class="projects-section">
        <div class="section-header">
          <i class="icon-archive"></i>
          <h3>나의 프로젝트</h3>
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
            <span class="sortable-header" @click="sortByColumn('star_count')">
              Stars
              <i :class="getSortIcon('star_count')"></i>
            </span>
            <span class="sortable-header" @click="sortByColumn('fork_count')">
              Forks
              <i :class="getSortIcon('fork_count')"></i>
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
            <span>Language</span>
            <span class="sortable-header" @click="sortByColumn('contributors_count')">
              Contributors
              <i :class="getSortIcon('contributors_count')"></i>
            </span>
          </div>
          
          <!-- Replace the static table rows with dynamic data -->
          <div class="table-row" v-for="repo in sortedRepositoriesData" :key="repo.id">
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
                'dropdown-up': shouldDropUp(repo.id)
              }"
              @click.stop="toggleCategoryDropdown(repo.id)"
              :ref="`categoryDropdown_${repo.id}`"
            >
              <div class="category-dropdown-selected">
                <span>{{ repo.category || 'N/A' }}</span>
                <i class="icon-arrow-down" :class="{ 'rotated': categoryDropdownOpen[repo.id] }"></i>
              </div>
              <div 
                v-if="categoryDropdownOpen[repo.id]" 
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
          <span>{{ repo.star_count?.toLocaleString() || '0' }}</span>
          <span>{{ repo.fork_count?.toLocaleString() || '0' }}</span>
          <span>{{ repo.commit_count?.toLocaleString() || '0' }}</span>
          <span>{{ repo.pr_count?.toLocaleString() || '0' }}</span>
          <span>{{ repo.total_issue_count?.toLocaleString() || '0' }}</span>
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
      </section>

    </main>
    
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
import EProfileHeatmap from './EProfileComponents/EProfileHeatmap.vue'
import RepoDetailModal from './EProfileComponents/RepoDetailModal.vue'
import { getEProfileHeatmap } from '@/api.js'
import { processActivityData, processAddedLinesData, estimateCommitLines } from './EProfileComponents/chartUtils/chartUtils.js'

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
        name: '김이진',
        university: '고려대학교',
        department: '컴퓨터공학과',
        email: 'abcde123@korea.ac.kr',
        introduction: ''
      },
      techStack: {
        languages: ['Python', 'C++', 'JavaScript'],
        frameworks: ['Django', 'React', 'Vue.js']
      },
      stats: {
        commitLines: { added: 1200, deleted: 500 },
        issues: { created: 45, closed: 20 },
        pullRequests: 120,
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
          selected: 'Python',
          isOpen: false,
          options: []
        },
        {
          selected: 'JavaScript',
          isOpen: false,
          options: []
        },
        {
          selected: 'Go',
          isOpen: false,
          options: []
        },
        {
          selected: 'Rust',
          isOpen: false,
          options: []
        },
        {
          selected: 'Kubernetes',
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
      student_uuid: 'rcmPR6PxrxcXP7Pmz0D2tZKsifm2',
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
      ]
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
        } else if (['star_count', 'fork_count', 'commit_count', 'pr_count', 'total_issue_count', 'contributors_count'].includes(this.sortBy)) {
          // Numeric comparison
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
    // 모달 관련 메서드
    openRepoModal(repo) {
      this.selectedRepo = repo
      this.showRepoModal = true
    },
    closeRepoModal() {
      this.showRepoModal = false
      this.selectedRepo = null
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
    saveChanges() {
      // Handle saving changes
      console.log('Save changes clicked');
    },
    async loadActivityChart() {
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
        
        const response = await getEProfileHeatmap(this.student_uuid)
        console.log(response)

        // Process the API response data using utility function
        if (response.data && response.data.monthly_commits) {
          let monthlyData = { labels: [], values: [] }
          let addedLinesData = { labels: [], values: [] }
          
          // Process commits data
          if (response.data.monthly_commits.total_count) {
            monthlyData = processActivityData(response.data.monthly_commits.total_count)
          }
          
          // Process added lines data
          if (response.data.monthly_commits.added_lines) {
            addedLinesData = processAddedLinesData(response.data.monthly_commits.added_lines)
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
        
        // Load repositories data from the same response
        this.loadRepositoriesFromResponse(response.data)

        // Load tech stack data from total_language_percentage
        this.loadTechStackData(response.data)

        // Load team size data from total_contributors_count
        this.loadTeamSizeData(response.data)

        // Load stats data from total_stats
        this.loadStatsData(response.data)

      } catch (error) {
        console.error('히트맵 데이터 로드 실패:', error)
        // 에러 시 기본 데이터 설정 (선택사항)
        this.heatmapData = {
          Mon: {}, Tue: {}, Wed: {}, Thu: {}, Fri: {}, Sat: {}, Sun: {}
        }

        this.repositoriesData = [
          {
            id: "822988405",
            name: "20241R0136COSE48000",
            category: "산학캡스톤디자인",
            url: "https://github.com/dlwls423/20241R0136COSE48000",
            student_id: "2020320088",
            owner_github_id: "dlwls423",
            created_at: "2024-07-02T08:07:03Z",
            updated_at: "2024-07-02T08:07:03Z",
            fork_count: 0,
            star_count: 0,
            commit_count: 276,
            total_issue_count: 0,
            pr_count: 0,
            language: "Java, CSS, JavaScript, HTML",
            language_percentages: {
                "others": 0
            },
            contributors_count: 0,
            contributors_list: [],
            license: null,
            has_readme: false,
            description: "산학캡스톤디자인 2024-1, 머니머지 BE 레포지토리",
            release_version: null,
            is_course: true,
          },

          {
            "id": "738312382",
            "name": "value-together",
            "is_course": false,
            "category": "-",
            "url": "https://github.com/dlwls423/value-together",
            "student_id": "2020320088",
            "owner_github_id": "dlwls423",
            "created_at": "2024-01-03T00:04:04Z",
            "updated_at": "2024-01-03T00:04:04Z",
            "fork_count": 0,
            "star_count": 0,
            "commit_count": 739,
            "total_issue_count": 0,
            "pr_count": 0,
            "language": "Java, Dockerfile",
            "language_percentages": {
                "Java": 99.9,
                "Dockerfile": 0.1,
                "others": 0
            },
            "contributors_count": 5,
            "contributors_list": [
                [
                    "이예진",
                    "컴퓨터학과",
                    "2020320088",
                    "dlwls423"
                ]
            ],
            "license": null,
            "has_readme": true,
            "description": "가치 있는일을 같이 진행하자! 일정 공유 어플리케이션! ",
            "release_version": null,
            "monthly_commits": [],
          },
          {
            "id": "725163550",
            "name": "hobby-bungae",
            "is_course": false,
            "category": "-",
            "url": "https://github.com/dlwls423/hobby-bungae",
            "student_id": "2020320088",
            "owner_github_id": "dlwls423",
            "created_at": "2023-11-29T15:11:21Z",
            "updated_at": "2023-11-29T15:11:21Z",
            "fork_count": 0,
            "star_count": 0,
            "commit_count": 165,
            "total_issue_count": 0,
            "pr_count": 0,
            "language": "Java",
            "language_percentages": {
                "Java": 100,
                "others": 0
            },
            "contributors_count": 4,
            "contributors_list": [
                [
                    "이예진",
                    "컴퓨터학과",
                    "2020320088",
                    "dlwls423"
                ]
            ],
            "license": null,
            "has_readme": true,
            "description": "스파르타 내일배움캠프 Spring 3기 - 스프링 숙련 주차 팀 과제 : HabbyMate",
            "release_version": null,
            "monthly_commits": [],
          },
          {
            id: "822988409",
            name: "20241R0136COSE48000",
            category: "산학캡스톤",
            url: "https://github.com/dlwls423/20241R0136COSE48000",
            student_id: "2020320088",
            owner_github_id: "dlwls423",
            created_at: "2024-07-02T08:07:03Z",
            updated_at: "2024-07-02T08:07:03Z",
            fork_count: 0,
            star_count: 0,
            commit_count: 276,
            total_issue_count: 0,
            pr_count: 0,
            language: "Java, CSS, JavaScript, HTML",
            language_percentages: {
                "others": 0
            },
            contributors_count: 0,
            contributors_list: [],
            license: null,
            has_readme: false,
            description: "산학캡스톤디자인 2024-1, 머니머지 BE 레포지토리",
            release_version: null,
            is_course: true,
          },
        ]

        this.techStackData = {
          "Java": 70,
          "HTML": 13.5,
          "JavaScript": 10.9,
          "CSS": 5.5,
          "C": 0.1,
          "others": 0
        }

        const total_contributors_count = {
            "0": 1,
            "1": 13,
            "2": 0,
            "3": 0,
            "4": 4,
            "5+": 2
        }

        this.teamSizeData = {
          labels: ['1인', '2인', '3인', '4인', '5인 이상'],
          data: [13, 0, 0, 4, 2]
        }

        const total_stats = {
          "total_commits": 3555,
          "added_lines": 509673,
          "deleted_lines": 174331,
          "total_changed_lines": 684004,
          "total_open_issues": 3,
          "total_closed_issues": 1,
          "total_open_prs": 0,
          "total_closed_prs": 3,
          "total_stars": 3,
          "total_forks": 0
        }
        this.stats = {
          commitLines: {added: 0, deleted: 0},
          issues: {created: 0, closed: 0},
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
    loadTechStackData(responseData) {
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
        this.techStackData = {
          "Java": 70,
          "HTML": 13.5,
          "JavaScript": 10.9,
          "CSS": 5.5,
          "C": 0.1,
          "others": 0
        }
        console.error('Error loading tech stack data:', error)
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

          this.stats = {
            commitLines: {
              added: parseInt(totalStats.added_lines) || 0, 
              deleted: parseInt(totalStats.deleted_lines) || 0
            },
            issues: {
              created: parseInt(totalStats.total_open_issues) || 0, 
              closed: parseInt(totalStats.total_closed_issues) || 0
            },
            pullRequests: parseInt(totalStats.total_closed_prs) || 0,
            openSourceContributions: 0 // Keep as 0 as in your example
          }

          console.log('Stats data loaded from API:', this.stats)
        } else {
          console.warn('No total_stats data found in API response')
        }
      } catch (error) {
        console.error('Error loading stats data:', error)
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
          this.repositoriesData = []
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
    },

    getSortIcon(column) {
      if (this.sortBy !== column) {
        return 'icon-sort-default'
      }
      return this.sortDirection === 'asc' ? 'icon-sort-up' : 'icon-sort-down'
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
      const currentIndex = this.sortedRepositoriesData.findIndex(repo => repo.id === repoId)
      const totalRows = this.sortedRepositoriesData.length
      
      // If it's in the last 3 rows, drop up
      return currentIndex >= totalRows - 3
    }
  }
}
</script>

<style scoped>
/* Global Styles */
.e-portfolio {
  font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif;
  background: #FFFFFF;
  min-height: 100vh;
  width: 1920px;
  margin: 0 auto;
  padding-top: 150px; /* Proper spacing from navigation bar */
}

/* Save Section */
.save-section {
  display: flex;
  justify-content: flex-end;
  padding: 0 320px; /* Align with content area */
  margin-bottom: 30px; /* Space before main content */
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
  width: 113px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.save-btn:hover {
  background: #CB385C;
  color: #FCFCFC;
}

/* Main Content */
.main-content {
  width: 1280px;
  margin: 0 auto;
  padding: 0 20px;
}

/* Profile Section */
.profile-section {
  display: grid;
  grid-template-columns: 415px 848px;
  gap: 16px;
  margin-bottom: 40px;
}

.profile-card {
  background: #FAFBFD;
  border: 1px solid #E8EDF8;
  border-radius: 20px;
  padding: 30px;
  height: 440px; /* Updated height */
}

/* Profile Header Layout - NEW */
.profile-header {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 20px;
}

/* Profile Picture Placeholder - NEW */
.profile-picture-placeholder {
  width: 94px;
  height: 94px;
  /* background-color: #E2E7F0; */
  background-image: url('@/assets/emblem_school_transparent.gif') ;
  background-repeat: no-repeat;
  background-position: center;
  background-size: 70%;
  border-radius: 10px;
  flex-shrink: 0;
}

/* Right Column Container - NEW */
.right-column {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.tech-stack-card {
  background: #FAFBFD;
  border: 1px solid #E8EDF8;
  border-radius: 20px;
  padding: 30px 50px;
  height: 280px;
  position: relative
}

/* Skills Card - MOVED AND UPDATED */
.skills-card {
  background: #FAFBFD;
  border: 1px solid #E8EDF8;
  border-radius: 20px;
  padding: 1px 15px;
  height: 142px;
  display: flex;
  align-items: center;
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
  gap: 16px;
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

/* Tech Stack */
.tech-stack-card {
  display: flex;
  flex-direction: column;
  gap: 20px;
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

.tech-stack-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
  flex: 1;
}

.tech-column-title {
  font-size: 16px;
  font-weight: 600;
  color: #616161;
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

/* Skills Section */
.skills-section {
  margin-bottom: 40px;
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

.skills-stats {
  display: flex;
  width: 100%;
  align-items: center;
  height: 100%;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-right: 1px solid #E8EDF8;
  padding: 20px 10px;
  text-align: center;
  min-height: 80px;
}

.stat-item:nth-child(1) {
  flex: 2.5; /* 추가 / 삭제 커밋 라인 수 - longest text */
}

.stat-item:nth-child(2) {
  flex: 2; /* 이슈 생성 / 닫은 수 - medium text */
}

.stat-item:nth-child(3) {
  flex: 1.5; /* PR 생성 수 - short text */
}

.stat-item:nth-child(4) {
  flex: 2; /* 오픈 소스 프로젝트 - medium text */
}

.stat-item:last-child {
  border-right: none;
}

.stat-item h4 {
  font-size: 16px;
  font-weight: 500;
  color: #616161;
  margin: 0 0 26px 0;
  text-align: center;
  line-height: 1.3;
}

.stat-item p {
  font-size: 16px;
  font-weight: 500;
  color: #262626;
  margin: 0;
}

/* Activity Section */
.activity-section {
  margin-bottom: 40px;
}

.activity-charts {
  display: grid;
  grid-template-columns: 632px 632px;
  gap: 16px;
  margin-bottom: 30px;
}

.chart-card {
  background: #FFFBFB;
  border-radius: 20px;
  padding: 30px 40px;
  height: 347px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
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
  gap: 20px;
  margin-bottom: 20px;
  justify-content: flex-end;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

/* NEW: Activity Chart Specific Styles */
.activity-chart-container {
  position: relative;
  height: 200px;
  width: 100%;
  margin-top: 10px;
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
  height: 200px;
  width: 100%;
  margin-top: 20px;
}

.team-size-chart-container canvas {
  width: 100% !important;
  height: 100% !important;
}

/* Time Pattern */
.time-pattern-card {
  background: #FFFBFB;
  border-radius: 20px;
  padding: 30px 40px;
  width: 1280px;
  height: 304px;
}

/* Projects Section */
.projects-section {
  margin-bottom: 40px;
}

.projects-table {
  background: #FFFFFF;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  width: 1280px;
  
  /* Column width variables - easily adjustable */
  --col-category: 130px;
  --col-repository: 220px;
  --col-stars: 90px;
  --col-forks: 90px;
  --col-commits: 100px;
  --col-prs: 80px;
  --col-issues: 90px;
  --col-language: 130px;
  --col-contributors: 130px;
}

.table-header {
  background: #F8F9FA;
  display: grid;
  grid-template-columns: 
    var(--col-category, 90px)
    var(--col-repository, 180px) 
    var(--col-stars, 70px) 
    var(--col-forks, 70px) 
    var(--col-commits, 80px) 
    var(--col-prs, 60px) 
    var(--col-issues, 70px) 
    var(--col-language, 100px) 
    var(--col-contributors, 110px);
  gap: 18px;
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
    var(--col-category, 90px)
    var(--col-repository, 180px) 
    var(--col-stars, 70px) 
    var(--col-forks, 70px) 
    var(--col-commits, 80px) 
    var(--col-prs, 60px) 
    var(--col-issues, 70px) 
    var(--col-language, 100px) 
    var(--col-contributors, 110px);
  gap: 18px;
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
  margin: 20px 0 30px 0;
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
  min-height: 60px;
  padding: 12px 16px;
  font-size: 14px;
  line-height: 140%;
  color: #717989;
  background: #FFFFFF;
  border: 1px solid #E8EDF8;
  border-radius: 8px;
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

.intro-input::placeholder {
  color: #CDCDCD;
}

.intro-counter {
  display: flex;
  justify-content: flex-end;
  margin-top: 5px;
  font-size: 12px;
  color: #949494;
}

/* Responsive Design */
@media (max-width: 1920px) {
  .e-portfolio {
    width: 100%;
    max-width: 1920px;
  }
  
  .save-section {
    padding: 0 calc((100% - 1280px) / 2);
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
}

@media (max-width: 768px) {
  .e-portfolio {
    padding-top: 100px;
  }
  
  .main-content {
    width: 100%;
    padding: 0 15px;
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
</style>