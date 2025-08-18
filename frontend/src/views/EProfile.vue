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
              <h2 class="profile-name">김OO 님</h2>
              <div class="profile-details">
                <div class="detail-item">
                  <i class="icon-location"></i>
                  <div class="detail-content">
                    <span>고려대학교</span>
                    <span>컴퓨터공학과</span>
                  </div>
                </div>
                <div class="detail-item">
                  <i class="icon-mail"></i>
                  <span>abcde123@korea.ac.kr</span>
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
              maxlength="300"
            ></textarea>
            <div class="intro-counter">
              {{ user.introduction.length }}/300
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
                      v-for="(lang, index) in techStackData" 
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
                      @click="toggleDropdown(index)"
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
                <h4>추가 / 삭제 커밋 라인 수</h4>
                <p>1200 / 500</p>
              </div>
              <div class="stat-item">
                <h4>이슈 생성 / 닫은 수</h4>
                <p>45 / 20</p>
              </div>
              <div class="stat-item">
                <h4>PR 생성 수</h4>
                <p>120수</p>
              </div>
              <div class="stat-item">
                <h4>오픈 소스 프로젝트</h4>
                <p>30개</p>
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
              <div class="chart-toggle">
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
              </div>
            </div>
            <p class="chart-description">최근 대규모의 커밋량 변동이 많았습니다</p>
            
            <!-- Chart Legend -->
            <div class="chart-legend-horizontal">
              <div class="legend-item">
                <div class="legend-dot" style="background: #C16179;"></div>
                <span>Repos</span>
              </div>
              <div class="legend-item">
                <div class="legend-dot" style="background: #FF176A;"></div>
                <span>Commit</span>
              </div>
              <div class="legend-item">
                <div class="legend-dot" style="background: #FF90AB;"></div>
                <span>Stars</span>
              </div>
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
            <p class="chart-description">2인 프로젝트 비율이 가장 높습니다</p>
            
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
            <span>Category</span>
            <span>Repository</span>
            <span>Stars</span>
            <span>Forks</span>
            <span>Commits</span>
            <span>PRs</span>
            <span>Issues</span>
            <span>Watchers</span>
            <span>Language</span>
            <span>Contribution</span>
            <span>기여학생</span>
          </div>
          
          <div class="table-row">
            <div class="category-tag autonomous">자율</div>
            <span>tensorflow</span>
            <span>181023</span>
            <span>컴퓨터학과</span>
            <span>1517192</span>
            <span>23550</span>
            <span>38455</span>
            <span>7657</span>
            <span>C++</span>
            <span>3474</span>
            <span><i class="icon-link"></i></span>
          </div>
          
          <div class="table-row">
            <div class="category-tag course">컴퓨터프로..</div>
            <span>tensorflow</span>
            <span>181023</span>
            <span>컴퓨터학과</span>
            <span>1517192</span>
            <span>23550</span>
            <span>38455</span>
            <span>7657</span>
            <span>C++</span>
            <span>3474</span>
            <span><i class="icon-link"></i></span>
          </div>
          
          <div class="table-row">
            <div class="category-tag course">알고리즘</div>
            <span>tensorflow</span>
            <span>181023</span>
            <span>컴퓨터학과</span>
            <span>1517192</span>
            <span>23550</span>
            <span>38455</span>
            <span>7657</span>
            <span>C++</span>
            <span>3474</span>
            <span><i class="icon-link"></i></span>
          </div>
        </div>
      </section>

    </main>
  </div>
</template>

<script>
import { Chart, registerables } from 'chart.js'
import EProfileHeatmap from './EProfileComponents/EProfileHeatmap.vue'
import { getEProfileHeatmap } from '@/api.js'
import { processActivityData, processAddedLinesData, estimateCommitLines } from './EProfileComponents/chartUtils/chartUtils.js'

// Register Chart.js components
Chart.register(...registerables)

export default {
  name: 'EPortfolioDashboard',
  components: {
    EProfileHeatmap
  },
  data() {
    return {
      user: {
        name: '김OO',
        university: '고려대학교',
        department: '컴퓨터공학과',
        email: 'abcde123@korea.ac.kr',
        introduction: '간단한 자기소개 입력해주세요.'
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
      techStackData: [
        {
          name: 'Python',
          value: 45,
          color: '#FF176A',
          percentage: 45
        },
        {
          name: 'C++',
          value: 30,
          color: '#FF84A3',
          percentage: 30
        },
        {
          name: '기타',
          value: 25,
          color: '#FFD1DC',
          percentage: 25
        }
      ],
      // 히트맵 데이터
      heatmapData: {},
      techStackChart: null,
      // Activity Chart Data - NEW ADDITIONS
      activityChart: null,
      activityViewMode: 'monthly', // 'monthly' or 'weekly'
      // Sample activity data - replace with actual API data
      activityData: {
        monthly: {
          labels: ['5월', '6월', '7월', '8월', '10월', '11월'],
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
        labels: ['1인', '2인', '3인', '4인', '5인 이상'],
        data: [15, 7, 3, 4, 1] // Percentages that add up to 80 (max scale)
      },
      techStackDropdowns: [
        {
          selected: 'Python',
          isOpen: false,
          options: ['Python', 'JavaScript', 'Java', 'C++', 'C#', 'Go', 'Rust', 'Swift', 'Kotlin', 'TypeScript']
        },
        {
          selected: 'React',
          isOpen: false,
          options: ['React', 'Vue.js', 'Angular', 'Svelte', 'Next.js', 'Nuxt.js', 'Express.js', 'Django', 'Flask', 'Spring Boot']
        },
        {
          selected: 'Django',
          isOpen: false,
          options: ['Django', 'Flask', 'FastAPI', 'Express.js', 'Spring Boot', 'Laravel', 'Ruby on Rails', 'ASP.NET', 'Phoenix', 'Gin']
        },
        {
          selected: 'PostgreSQL',
          isOpen: false,
          options: ['PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'SQLite', 'Oracle', 'SQL Server', 'MariaDB', 'Cassandra', 'DynamoDB']
        },
        {
          selected: 'Docker',
          isOpen: false,
          options: ['Docker', 'Kubernetes', 'AWS', 'Google Cloud', 'Azure', 'Heroku', 'Vercel', 'Netlify', 'DigitalOcean', 'Firebase']
        }
      ]
    }
  },
  mounted() {
    this.loadActivityChart()
    this.loadHeatmapData()

    this.createTechStackChart()
    setTimeout(() => {
      this.createActivityChart()
    }, 50)
    this.createTeamSizeChart()

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
    createTechStackChart() {
      const ctx = this.$refs.techStackChart.getContext('2d')
      
      this.techStackChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: this.techStackData.map(item => item.name),
          datasets: [{
            data: this.techStackData.map(item => item.value),
            backgroundColor: this.techStackData.map(item => item.color),
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
              min: 0,
              max: 30,
              ticks: {
                stepSize: 5,
                color: '#262626',
                font: { size: 12, family: 'Pretendard' }
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
      this.activityViewMode = mode
      this.updateActivityChart()
    },
    updateActivityChart() {
      if (!this.activityChart) return
      
      const currentData = this.activityData[this.activityViewMode]
      
      // Clear and rebuild the datasets completely
      // this.activityChart.data.labels = [...currentData.labels]
      // this.activityChart.data.datasets[0].data = [...currentData.repos]
      // this.activityChart.data.datasets[1].data = [...currentData.commits]
      // this.activityChart.data.datasets[2].data = [...currentData.stars]
      
      // this.activityChart.data.labels = [...currentData.labels]
      // this.activityChart.data.datasets[0].data = [...currentData.commits]
      // this.activityChart.data.datasets[1].data = [...currentData.commitLines]
      
      // Force a complete re-render
      // this.activityChart.update()
      
      this.activityChart.destroy()
      this.createActivityChart()
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
        const githubId = "dlwls423" // 임시 테스트용 GitHub 아이디
        
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
        
        const response = await getEProfileHeatmap(githubId)
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
        
        // For now, keep weekly as empty or use sample data
        this.activityData.weekly = {
          labels: ['1주차', '2주차', '3주차', '4주차', '5주차', '6주차'],
          commits: [8, 12, 15, 18, 14, 10],
          commitLines: [68, 102, 128, 153, 119, 85]
        }
        
        console.log('활동 추이 로드 완료:', this.activityData)
      } catch (error) {
        console.error('활동 차트 데이터 로드 실패:', error)
        // 에러 시 기본 데이터 설정
        this.activityData = {
          monthly: {
            labels: ['5월', '6월', '7월', '8월', '10월', '11월'],
            commits: [10, 15, 3, 37, 28, 15],
            commitLines: [85, 128, 26, 315, 238, 128]
          },
          weekly: {
            labels: ['1주차', '2주차', '3주차', '4주차', '5주차', '6주차'],
            commits: [8, 12, 15, 18, 14, 10],
            commitLines: [68, 102, 128, 153, 119, 85]
          }
        }
      }
    },

    async loadHeatmapData() {
      try {
        // TODO: 실제 로그인된 사용자의 GitHub 아이디를 가져오는 로직으로 변경 필요
        const githubId = "dlwls423" // 임시 테스트용 GitHub 아이디
        const response = await getEProfileHeatmap(githubId)
        this.heatmapData = response.data.heatmap
        console.log('히트맵 데이터 로드 완료:', this.heatmapData)
      } catch (error) {
        console.error('히트맵 데이터 로드 실패:', error)
        // 에러 시 기본 데이터 설정 (선택사항)
        this.heatmapData = {
          Mon: {}, Tue: {}, Wed: {}, Thu: {}, Fri: {}, Sat: {}, Sun: {}
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
  background: #E2E7F0;
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
}

/* Skills Card - MOVED AND UPDATED */
.skills-card {
  background: #FAFBFD;
  border: 1px solid #E8EDF8;
  border-radius: 20px;
  padding: 1px 50px;
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

.tech-stack-content {
  display: flex;
  align-items: flex-start;
  gap: 50px;
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
  align-items: center;
  gap: 25px;
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
  gap: 10px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  color: #616161;
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
  z-index: 1;
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
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.dropdown-selected {
  padding: 5px 14px;
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

.tech-dropdown.dropdown-open .dropdown-selected {
  border-radius: 10px 10px 0 0;
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
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 1000;
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
  transform: rotate(180deg);
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
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 25px;
  text-align: center;
  width: 100%;
  align-items: center;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  border-right: 1px solid #E8EDF8;
  padding: 0 10px;
}

.stat-item:last-child {
  border-right: none;
}

.stat-item h4 {
  font-size: 16px;
  font-weight: 500;
  color: #616161;
  margin: 0 0 26px 0;
  white-space: nowrap;
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

/* UPDATED: Enhanced chart toggle styling */
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
}

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
}

.table-header {
  background: #F8F9FA;
  display: grid;
  grid-template-columns: repeat(11, 1fr);
  gap: 18px;
  padding: 15px 20px;
  font-size: 16px;
  font-weight: 600;
  color: #CB385C;
  border-bottom: 1px solid #F9D2D6;
}

.table-row {
  display: grid;
  grid-template-columns: repeat(11, 1fr);
  gap: 18px;
  padding: 12px 20px;
  align-items: center;
  border-bottom: 1px solid #DCE2ED;
  font-size: 16px;
  color: #262626;
}

.table-row:last-child {
  border-bottom: none;
}

.category-tag {
  padding: 4px 21px;
  border-radius: 10px;
  font-size: 14px;
  text-align: center;
  max-width: 100px;
}

.category-tag.autonomous {
  background: #EFF2F9;
  color: #507199;
}

.category-tag.course {
  background: #FFEAEC;
  color: #CB385C;
}

/* Icons - You'll need to replace these with actual icon implementations */
.icon-location,
.icon-mail,
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

.icon-message {
  width: 20px;
  height: 20px;
  background: #949494;
  border-radius: 2px;
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
</style>