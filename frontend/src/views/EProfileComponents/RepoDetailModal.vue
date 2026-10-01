<template>
  <div v-if="show" class="modal-overlay" @click="closeModal">
    <div class="modal-content" @click.stop>
      <!-- 프로젝트 헤더 (레포명 - 프로젝트 타입 - GitHub 링크) -->
      <div class="project-header">
        <h2 class="project-title">{{ repo?.name || 'N/A' }}</h2>
        <div class="project-type-tag">
          <span>{{ repo?.category || '자율' }}</span>
        </div>
        <a 
          v-if="repo?.owner_github_id && repo?.name" 
          :href="`https://github.com/${repo.owner_github_id}/${repo.name}`" 
          target="_blank" 
          class="github-link"
        >
          <i class="github-icon">🔗</i>
          GitHub 보기
        </a>
      </div>
      
      <!-- 편집/저장 버튼 -->
      <button class="modal-save-btn" @click="isEditingRepo ? saveChanges() : toggleEditMode()">
        {{ isEditingRepo ? '저장' : '편집' }}
      </button>
      
      <!-- 닫기 버튼 -->
      <button class="modal-close-btn" @click="closeModal">
        <div class="close-icon"></div>
      </button>
      
      <!-- 메인 컨텐츠 -->
      <div class="modal-main-content">
        <!-- 프로젝트 세부 정보 섹션 -->
        <div class="section">
          <h3 class="section-title project-details-title">프로젝트 세부 정보</h3>
          <div class="info-table">
            <!-- 헤더 행 -->
            <div class="table-header">
              <span>Type</span>
              <span>Commits</span>
              <span>PRs</span>
              <span>Issues</span>
              <span>Stars</span>
              <span>Forks</span>
              <span>Languages</span>
              <span>Contributors</span>
            </div>
            <!-- 데이터 행 -->
            <div class="table-data">
              <span>{{ getRepoType() }}</span>
              <span>{{ getRepoCommits()?.toLocaleString() || '0' }}</span>
              <span>{{ getRepoPRs()?.toLocaleString() || '0' }}</span>
              <span>{{ getRepoIssues()?.toLocaleString() || '0' }}</span>
              <span>{{ repo?.star_count?.toLocaleString() || '0' }}</span>
              <span>{{ repo?.fork_count?.toLocaleString() || '0' }}</span>
              <div class="language-cell">
                <span class="language-preview">{{ topLanguagesPreview }}</span>
                <button class="link-button" @click.stop="toggleLanguagePanel" v-if="allLanguagesList.length > 0">전체 보기</button>
                <div v-if="showLanguagePanel" class="language-popover" @click.stop>
                  <div class="popover-header">
                    <span>Languages</span>
                    <button class="close-x" @click.stop="closeLanguagePanel">✕</button>
                  </div>
                  <p class="language-flow">{{ languagesFlowText }}</p>
                </div>
              </div>
              <span>{{ repo?.contributors_count?.toLocaleString() || '0' }}</span>
            </div>
          </div>
        </div>
        
        <!-- 프로젝트 메모 섹션 -->
        <div class="section">
          <h3 class="section-title">프로젝트 소개</h3>
          <div class="memo-box">
            <textarea 
              v-model="projectMemo"
              class="memo-textarea"
              placeholder="프로젝트에 대한 소개를 입력하세요..."
              @input="adjustTextareaHeight"
              ref="memoTextarea"
              :disabled="!isEditingRepo"
            ></textarea>
          </div>
        </div>
        
        <!-- 프로젝트 요약 섹션 -->
        <div class="section">
          <div class="section-header">
            <h3 class="section-title">프로젝트 요약</h3>
            <div class="readme-icon" title="README가 없습니다">
              <span class="readme-question">?</span>
            </div>
          </div>
          <div class="summary-box">
            <p v-for="notice in summaryNotices" :key="notice" class="summary-notice">{{ notice }}</p>
            <div v-if="parsedSummary" class="summary-content">
              <!-- 프로젝트 개요 (현재 JSON 스키마 기준) -->
              <div class="summary-grid">
                <div class="summary-item full">
                  <div class="label">규모</div>
                  <div class="value">{{ parsedSummary.scale }}</div>
                </div>
                <div class="summary-item full">
                  <div class="label">주요 언어</div>
                  <div class="value">{{ parsedSummary.primary_language }}</div>
                </div>
                <div class="summary-item full">
                  <div class="label">목적</div>
                  <div class="value">{{ parsedSummary.purpose }}</div>
                </div>
                <div class="summary-item full">
                  <div class="label">핵심 기능</div>
                  <ul class="value list">
                    <li v-for="(f, idx) in parsedSummary.features" :key="idx">{{ f }}</li>
                    <li v-if="!parsedSummary.features.length">확인할 수 없습니다.</li>
                  </ul>
                </div>
                <div class="summary-item full">
                  <div class="label">기술 스택</div>
                  <div class="value chips">
                    <span v-for="(t, idx) in parsedSummary.tech_stack" :key="idx" class="chip">{{ t }}</span>
                    <span v-if="!parsedSummary.tech_stack.length">확인할 수 없습니다.</span>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="summary-fallback">
              <p>{{ summaryFallbackMessage }}</p>
            </div>
          </div>
        </div>
        
        <!-- 차트 섹션 -->
        <div class="charts-section">
          <!-- 프로젝트 타임라인 차트 -->
          <div class="chart-container timeline-chart">
            <div class="chart-header">
              <div class="chart-title-line"></div>
              <h3>프로젝트 타임라인</h3>
            </div>
            <div class="chart-content">
              <!-- Y축 라벨 -->
              <div class="y-axis-labels">
                <span v-for="label in yAxisLabels" :key="label">{{ label }}</span>
              </div>
              
              <!-- 차트 영역 -->
              <div class="chart-area">
                <!-- 그리드 라인 -->
                <div class="grid-lines">
                  <div v-for="i in yAxisLabels.length" :key="i" class="grid-line"></div>
                </div>
                
                <!-- 차트 (선과 점을 SVG로 통합) -->
                <svg class="chart-svg" viewBox="0 0 493 200">
                  <!-- 그리드 라인들 -->
                  <line v-for="(label, index) in yAxisLabels" 
                        :key="index"
                        x1="0" 
                        :y1="(index / (yAxisLabels.length - 1)) * 200" 
                        x2="493" 
                        :y2="(index / (yAxisLabels.length - 1)) * 200" 
                        stroke="#FFEAEC" 
                        stroke-width="1"/>
                  
                  <!-- 연결선 -->
                  <path :d="timelinePath" 
                        stroke="#FF84A3" stroke-width="1" fill="none" stroke-linecap="round"/>
                  
                  <!-- 데이터 포인트 (원) -->
                  <circle v-for="(point, index) in timelinePoints" 
                          :key="index"
                          :cx="point.x" 
                          :cy="point.y" 
                          r="3" 
                          fill="#FF84A3"/>
                </svg>
              </div>
              
              <!-- X축 라벨 -->
              <div class="x-axis-labels">
                <div v-for="month in recentMonths" :key="month" class="x-axis-label">
                  <div class="label-month">{{ month.split('-')[1] }}월</div>
                  <div class="label-year">{{ month.split('-')[0] }}</div>
                </div>
              </div>
              
              <!-- 범례 -->
              <div class="chart-legend">
                <div class="legend-item">
                  <div class="legend-color"></div>
                  <span>Commit</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 주요 사용 언어 차트 -->
          <div class="chart-container language-chart">
            <div class="chart-header">
              <div class="chart-title-line"></div>
              <h3>주요 사용 언어</h3>
            </div>
            <div class="chart-content">
              <!-- 도넛 차트 -->
              <div class="donut-chart">
                <canvas ref="languageChart" width="140" height="140"></canvas>
                <div class="donut-center">
                  <span v-if="getTopLanguage() !== '데이터 없음'" class="top-language">{{ getTopLanguage() }}</span>
                  <div v-else class="no-data-center">
                    <i class="no-data-icon">📊</i>
                    <span class="no-data-text">데이터 없음</span>
                  </div>
                </div>
              </div>
              
              <!-- 범례 -->
              <div class="language-legend">
                <div v-for="(percentage, language, index) in languageData" :key="language" class="legend-item">
                  <div class="legend-color" :style="{ background: getLanguageColor(index) }"></div>
                  <span v-if="language === '데이터 없음'" class="no-data-legend">{{ language }}</span>
                  <span v-else>{{ language }} ({{ percentage.toFixed(1) }}%)</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  
</template>

<script>
import { Chart, registerables } from 'chart.js'
import { updateRepoIntroduction } from '@/api.js'
import { auth } from '../../services/firebase'

// Register Chart.js components
Chart.register(...registerables)

export default {
  name: 'RepoDetailModal',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    repo: {
      type: Object,
      default: null
    }
  },
  data() {
    return {
  languageChart: null,
  showLanguagePanel: false,
  projectMemo: '',
  isEditingRepo: false
    }
  },
  computed: {
    // 가장 최신 월 찾기
    latestMonth() {
      if (!this.repo || !this.repo.monthly_commits || this.repo.monthly_commits.length === 0) {
        // 데이터가 없으면 현재 날짜 사용
        const now = new Date()
        return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
      }
      
      // monthly_commits에서 가장 최신 월 찾기
      const months = this.repo.monthly_commits.map(([month]) => month)
      return months.sort().reverse()[0] // 내림차순 정렬 후 첫 번째 (가장 최신)
    },
    
    recentMonths() {
      // 가장 최신 월 기준으로 12개월 전부터 최신 월까지 13개월
      const [latestYear, latestMonthNum] = this.latestMonth.split('-').map(Number)
      const recentMonths = []
      
      for (let i = 12; i >= 0; i--) {
        let year = latestYear
        let month = latestMonthNum - i
        
        // 월이 0 이하로 가면 이전 년도로
        while (month <= 0) {
          month += 12
          year -= 1
        }
        
        recentMonths.push(`${year}-${String(month).padStart(2, '0')}`)
      }
      
      return recentMonths
    },
    
    // 타임라인 데이터 생성 (실제 레포지토리 monthly_commits 데이터 기반)
    timelineData() {
      if (!this.repo || !this.repo.monthly_commits) return []
      
      // monthly_commits 데이터를 월별로 정리
      const monthlyDataMap = {}
      this.repo.monthly_commits.forEach(([month, count]) => {
        monthlyDataMap[month] = count
      })
      
      // recentMonths 기준으로 데이터 생성
      const monthlyData = this.recentMonths.map(yearMonth => {
        return monthlyDataMap[yearMonth] || 0
      })
      
      return monthlyData
    },
    
    // 동적 Y축 라벨 생성
    yAxisLabels() {
      const maxValue = Math.max(...this.timelineData, 1)
      
      // 최댓값에 따라 Y축 라벨 생성
      if (maxValue <= 5) {
        // 0, 1, 2, 3, 4, 5
        return [5, 4, 3, 2, 1, 0]
      } else if (maxValue <= 10) {
        // 0, 2, 4, 6, 8, 10
        const step = 2
        const labels = []
        for (let i = Math.ceil(maxValue / step) * step; i >= 0; i -= step) {
          labels.push(i)
        }
        return labels
      } else {
        // 적당한 간격으로 6개 구간 생성
        const step = Math.ceil(maxValue / 5)
        const labels = []
        for (let i = 5; i >= 0; i--) {
          labels.push(i * step)
        }
        return labels
      }
    },
    
    // 언어 전체 목록 및 프리뷰
    allLanguagesList() {
      const raw = this.repo?.language || ''
      return raw.split(',').map(s => s.trim()).filter(Boolean)
    },
    topLanguagesPreview() {
      const list = this.allLanguagesList
      if (list.length === 0) return 'N/A'
      const top = list.slice(0, 3)
      const rest = list.length - top.length
      return rest > 0 ? `${top.join(', ')} 외 ${rest}개` : top.join(', ')
    },
    languagesFlowText() {
      const list = this.allLanguagesList
      if (list.length === 0) return 'N/A'
      // join with comma and space; avoid trailing comma
      return list.join(', ')
    },

    // 차트 좌표 계산
    timelinePoints() {
      const points = []
      const chartWidth = 493
      const chartHeight = 200
      // Y축 라벨의 최댓값 사용 (라벨과 차트 일치)
      const maxValue = this.yAxisLabels[0]
      
      this.timelineData.forEach((value, index) => {
        const x = (index / 12) * chartWidth // 0~12 인덱스를 0~493으로 매핑 (13개월)
        const y = chartHeight - (value / maxValue) * chartHeight // 값이 클수록 위쪽에 위치
        points.push({ x, y })
      })
      
      return points
    },
    
    // SVG 경로 생성
    timelinePath() {
      if (this.timelinePoints.length === 0) return ''
      
      const points = this.timelinePoints
      let path = `M ${points[0].x} ${points[0].y}`
      
      for (let i = 1; i < points.length; i++) {
        path += ` L ${points[i].x} ${points[i].y}`
      }
      
      return path
    },
    
    // 언어 분포 데이터 (실제 레포지토리 language_percentages 기반)
    languageData() {
      if (!this.repo || !this.repo.language_percentages) {
        return { '데이터 없음': 100 }
      }
      
      const percentages = this.repo.language_percentages || {}
      
      // others 제외하고 상위 3개 언어 + 기타로 구성
      const allLanguages = Object.entries(percentages)
        .filter(([key]) => key.toLowerCase() !== 'others')
        .sort((a, b) => b[1] - a[1])
      
      // 데이터가 없는 경우
      if (allLanguages.length === 0) {
        return { '데이터 없음': 100 }
      }
      
      const top3 = allLanguages.slice(0, 3)
      const others = allLanguages.slice(3)
      
      const result = {}
      
      // 상위 3개 언어
      top3.forEach(([language, percentage]) => {
        result[language] = percentage
      })
      
      // 기타 언어들의 합계
      if (others.length > 0) {
        const othersSum = others.reduce((sum, [_, percentage]) => sum + percentage, 0)
        result['기타'] = othersSum
      }
      
      return result
    },
    
    // Chart.js 데이터 변환
    chartData() {
      const colors = ['#FF176A', '#FF84A3', '#FFD1DC', '#FFDCE5']
      
      const data = Object.entries(this.languageData)
        .map(([language, percentage], index) => ({
          name: language,
          value: percentage,
          color: language === '데이터 없음' ? '#E8EDF8' : (colors[index] || colors[colors.length - 1]),
          percentage: percentage
        }))
      
      return data
    },
    
    summaryNotices() {
      if (!this.repo) return []
      const notices = []
      if (this.repo.github_availability === 'not_listed') {
        notices.push('현재 GitHub 공개 목록에서 확인되지 않아 저장된 레포지토리 정보를 표시합니다.')
      }
      if (this.repo.summary_status === 'stale') {
        notices.push('레포지토리 변경 후 요약이 아직 갱신되지 않았습니다. 이전 요약입니다.')
      } else if (this.repo.summary_status === 'limited') {
        notices.push('GitHub 파일에 접근할 수 없어 저장된 레포지토리 정보만으로 만든 요약입니다.')
      } else if (this.repo.summary_status === 'legacy') {
        notices.push('이전 방식으로 생성된 요약으로, 최신 여부는 아직 확인되지 않았습니다.')
      }
      return notices
    },

    summaryFallbackMessage() {
      if (!this.repo) return '레포지토리 정보가 없습니다.'
      if (this.repo.summary_status === 'insufficient_data') {
        return '요약을 만들기에 충분한 레포지토리 정보가 없습니다.'
      }
      if (this.repo.summary_status === 'error') {
        return '요약 생성에 실패했습니다. 나중에 다시 시도할 수 있습니다.'
      }
      if (this.repo.summary) return '저장된 요약 데이터를 읽을 수 없습니다.'
      return '프로젝트 요약이 아직 생성되지 않았습니다.'
    },

    // 프로젝트 요약 데이터 파싱 (현재 백엔드 JSON 스키마 전용)
    parsedSummary() {
      if (!this.repo || !this.repo.summary) return null

      try {
        // summary가 문자열이면 파싱
        let summaryData = this.repo.summary
        if (typeof summaryData === 'string') {
          summaryData = JSON.parse(summaryData)
        }

        if (!summaryData || typeof summaryData !== 'object') return null

        // 현재 스키마: { user_content: { description }, project_summary: { ... } }
  const project = (summaryData.project_summary || {})

        return {
          scale: project.scale || 'N/A',
          primary_language: project.primary_language || 'N/A',
          purpose: project.purpose || 'N/A',
          features: project.key_functionalities || project.features || [],
          tech_stack: project.tech_stack || [],
        }
      } catch (error) {
        console.error('프로젝트 요약 파싱 오류:', error)
        return null
      }
    }
  },
  methods: {
    closeModal() {
      this.isEditingRepo = false
      this.$emit('close')
    },
    
    toggleEditMode() {
      this.isEditingRepo = true
    },
    
    async saveChanges() {
      try {
        if (!this.repo || !this.repo.id) {
          alert('레포지토리 정보가 없습니다.')
          return
        }
        
        const uuid = auth.currentUser.uid
        const repo_id = this.repo.id
        
        await updateRepoIntroduction(uuid, repo_id, this.projectMemo)
        this.isEditingRepo = false
        alert('저장 완료')
      } catch (error) {
        console.error('저장 실패:', error)
        alert('저장에 실패했습니다. 다시 시도해주세요.')
      }
    },
    toggleLanguagePanel() {
      this.showLanguagePanel = !this.showLanguagePanel
    },
    closeLanguagePanel() {
      this.showLanguagePanel = false
    },
    
    getTopLanguage() {
      if (!this.repo || !this.repo.language_percentages) {
        return '데이터 없음'
      }
      
      const percentages = this.repo.language_percentages || {}
      const allLanguages = Object.entries(percentages)
        .filter(([key]) => key.toLowerCase() !== 'others')
        .sort((a, b) => b[1] - a[1])
      
      if (allLanguages.length === 0) {
        return '데이터 없음'
      }
      
      return allLanguages[0][0]
    },
    
    getLanguageColor(index) {
      const colors = ['#FF176A', '#FF84A3', '#FFD1DC', '#FFDCE5']
      const language = Object.keys(this.languageData)[index]
      return language === '데이터 없음' ? '#E8EDF8' : colors[index % colors.length]
    },
    
    createLanguageChart() {
      // 기존 차트가 있으면 정리
      if (this.languageChart) {
        this.languageChart.destroy()
        this.languageChart = null
      }
      
      // DOM 요소 확인
      if (!this.$refs.languageChart) {
        console.warn('languageChart canvas not found')
        return
      }
      
      const ctx = this.$refs.languageChart.getContext('2d')
      const chartData = this.chartData
      
      if (chartData.length === 0) {
        console.warn('No chart data available')
        return
      }
      
      this.languageChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: chartData.map(item => item.name),
          datasets: [{
            data: chartData.map(item => item.value),
            backgroundColor: chartData.map(item => item.color),
            borderWidth: 0,
            cutout: '60%'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false
            },
            tooltip: {
              callbacks: {
                label: function(context) {
                  const label = context.label || ''
                  const value = context.parsed
                  return `${label}: ${value.toFixed(1)}%`
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
    
    updateLanguageChart() {
      if (this.languageChart) {
        const chartData = this.chartData
        this.languageChart.data.labels = chartData.map(item => item.name)
        this.languageChart.data.datasets[0].data = chartData.map(item => item.value)
        this.languageChart.data.datasets[0].backgroundColor = chartData.map(item => item.color)
        this.languageChart.update()
      }
    },
    
    adjustTextareaHeight() {
      this.$nextTick(() => {
        const textarea = this.$refs.memoTextarea
        if (textarea) {
          // 높이를 초기화하고 스크롤 높이에 맞춰 조정
          textarea.style.height = 'auto'
          textarea.style.height = Math.max(60, textarea.scrollHeight) + 'px'
        }
      })
    },

    getRepoMemo() {
      if (!this.repo) return 0
      this.projectMemo = this.repo.project_introduction
      return 0
    },

    // Repository type, commits, PRs, issues calculation methods
    getRepoType() {
      if (!this.repo) return 'N/A'
      if (this.repo.is_owner) {
        return 'Owner'
      } else if (this.repo.is_contributor) {
        return 'Contributor'
      }
      return 'N/A'
    },

    getRepoCommits() {
      if (!this.repo) return 0
      if (this.repo.is_owner || this.repo.is_contributor) {
        return this.repo.user_commit_count || 0
      }
      return 0
    },

    getRepoPRs() {
      if (!this.repo) return 0
      if (this.repo.is_owner || this.repo.is_contributor) {
        const openPRs = this.repo.owner_open_pr_count || 0
        const closedPRs = this.repo.owner_closed_pr_count || 0
        return openPRs + closedPRs
      }
      return 0
    },

    getRepoIssues() {
      if (!this.repo) return 0
      if (this.repo.is_owner) {
        return this.repo.owner_issue_count || 0
      } else if (this.repo.is_contributor) {
        return this.repo.owner_issue_count || 0
      }
      return 0
    }
  },
  
  watch: {
    show(newVal) {
      if (newVal) {
        // 모달이 열릴 때 프로젝트 소개 데이터 로드
        if (this.repo && this.repo.project_introduction) {
          this.projectMemo = this.repo.project_introduction
        } else {
          this.projectMemo = ''
        }
        this.isEditingRepo = false
        this.$nextTick(() => {
          this.createLanguageChart()
          this.adjustTextareaHeight()
        })
      } else {
        // 모달이 닫힐 때 차트 정리
        if (this.languageChart) {
          this.languageChart.destroy()
          this.languageChart = null
        }
        // 언어 팝오버 닫기
        this.showLanguagePanel = false
      }
    },
    
    repo: {
      handler() {
        if (this.show && this.languageChart) {
          this.updateLanguageChart()
        }
        this.getRepoMemo()
      },
      deep: true
    }
  },
  
  beforeUnmount() {
    // 컴포넌트가 제거될 때 차트 정리
    if (this.languageChart) {
      this.languageChart.destroy()
      this.languageChart = null
    }
  }
}
</script>

<style scoped>
/* 모달 기본 스타일 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  position: relative;
  width: 1064px;
  height: 924px;
  background: #FFFFFF;
  border-radius: 20px;
  font-family: 'Pretendard', sans-serif;
  overflow: hidden; /* 스크롤바가 모달 경계를 넘지 않도록 */
}

/* 프로젝트 타입 태그 */
.project-type-tag {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4px 12px;
  gap: 10px;
  height: 25px;
  background: #EFF2F9;
  border-radius: 10px;
  white-space: nowrap;
}

.project-type-tag span {
  font-family: 'Pretendard';
  font-style: normal;
  font-weight: 400;
  font-size: 14px;
  line-height: 17px;
  text-align: center;
  color: #507199;
}

/* 프로젝트 헤더 */
.project-header {
  position: absolute;
  left: 50px;
  top: 40px;
  display: flex;
  align-items: center;
  gap: 15px;
}

/* 프로젝트 제목 */
.project-title {
  font-family: 'Pretendard';
  font-style: normal;
  font-weight: 600;
  font-size: 20px;
  line-height: 24px;
  letter-spacing: -0.004em;
  color: #262626;
  margin: 0;
}

/* GitHub 링크 */
.github-link {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #F8F9FA;
  border: 1px solid #E8EDF8;
  border-radius: 8px;
  text-decoration: none;
  font-family: 'Pretendard';
  font-style: normal;
  font-weight: 500;
  font-size: 14px;
  line-height: 17px;
  color: #507199;
  transition: all 0.3s ease;
}

.github-link:hover {
  background: #EFF2F9;
  border-color: #CB385C;
  color: #CB385C;
}

.github-icon {
  font-size: 16px;
}

/* 저장 버튼 */
.modal-save-btn {
  position: absolute;
  right: 90px;
  top: 40px;
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
  font-family: 'Pretendard';
  font-weight: 500;
}

.modal-save-btn:hover {
  background: #CB385C;
  color: #FCFCFC;
}

/* 닫기 버튼 */
.modal-close-btn {
  position: absolute;
  right: 50px;
  top: 40px;
  width: 32px;
  height: 32px;
  background: none;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-icon {
  width: 13.31px;
  height: 13.31px;
  position: relative;
}

.close-icon::before,
.close-icon::after {
  content: '';
  position: absolute;
  width: 2px;
  height: 13.31px;
  background: #262626;
  top: 50%;
  left: 50%;
}

.close-icon::before {
  transform: translate(-50%, -50%) rotate(45deg);
}

.close-icon::after {
  transform: translate(-50%, -50%) rotate(-45deg);
}

/* 메인 컨텐츠 */
.modal-main-content {
  position: absolute;
  left: 50px;
  top: 100px;
  width: 964px;
  height: 780px;
  display: flex;
  flex-direction: column;
  gap: 35px;
  overflow-y: auto; /* 세로 스크롤 추가 */
  overflow-x: hidden; /* 가로 스크롤 숨김 */
  padding-right: 20px; /* 스크롤바 공간 확보 */
}

/* 스크롤바 스타일링 */
.modal-main-content::-webkit-scrollbar {
  width: 8px;
}

.modal-main-content::-webkit-scrollbar-track {
  background: #F8F9FA;
  border-radius: 4px;
}

.modal-main-content::-webkit-scrollbar-thumb {
  background: #CB385C;
  border-radius: 4px;
}

.modal-main-content::-webkit-scrollbar-thumb:hover {
  background: #A02D4A;
}

/* Firefox 스크롤바 스타일링 */
.modal-main-content {
  scrollbar-width: thin;
  scrollbar-color: #CB385C #F8F9FA;
}

/* 섹션 공통 스타일 */
.section {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-title {
  font-family: 'Pretendard';
  font-style: normal;
  font-weight: 600;
  font-size: 18px;
  line-height: 21px;
  color: #262626;
  margin: 0;
}

/* README 아이콘 */
.readme-icon {
  position: relative;
  width: 20px;
  height: 20px;
  background: #FFD700;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.readme-icon:hover {
  background: #FFC107;
  transform: scale(1.1);
}

.readme-question {
  font-family: 'Pretendard';
  font-style: normal;
  font-weight: 600;
  font-size: 14px;
  line-height: 17px;
  color: #FFFFFF;
  text-align: center;
}

/* README 툴팁 */
.readme-icon::after {
  content: attr(title);
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: #333333;
  color: white;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 12px;
  white-space: nowrap;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s ease;
  z-index: 1000;
  margin-bottom: 5px;
}

.readme-icon::before {
  content: '';
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 5px solid transparent;
  border-top-color: #333333;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s ease;
  z-index: 1000;
  margin-bottom: -5px;
}

.readme-icon:hover::after,
.readme-icon:hover::before {
  opacity: 1;
  visibility: visible;
}

.project-details-title {
  margin-bottom: -10px;
}

/* 정보 테이블 */
.info-table {
  width: 100%;
  height: 100px;
  position: relative;
  box-sizing: border-box;
}

.table-header,
.table-data {
  display: flex;
  align-items: center;
  gap: 25px;
  position: absolute;
  width: 100%;
  height: 19px;
}

.table-header {
  top: 25px;
}

.table-data {
  top: 75px;
}

.table-header span,
.table-data span {
  width: 100px;
  height: 19px;
  font-family: 'Pretendard';
  font-style: normal;
  font-weight: 600;
  font-size: 16px;
  line-height: 19px;
  text-align: center;
}

.table-header span {
  color: #CB385C;
}

.table-data span {
  font-weight: 500;
  color: #262626;
}

/* Make language cell align like other table cells */
.table-data .language-cell {
  width: 120px;
  /* height removed to let preview + button show */
  justify-content: center;
  align-items: center;
  flex-direction: column; /* stack preview and button */
  gap: 2px;
  font-family: 'Pretendard';
  font-style: normal;
  font-weight: 500;
  font-size: 16px;
  line-height: 19px;
  text-align: center;
  color: #262626;
}

.language-cell {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  position: relative; /* popover positioning base */
}

.language-preview {
  max-width: 100px; /* a touch wider to show more */
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.link-button {
  background: none;
  border: none;
  color: #CB385C;
  font-size: 12px;
  cursor: pointer;
  padding: 0;
}

/* inline popover below the cell */
.language-popover {
  position: absolute;
  top: 44px; /* below stacked preview/button */
  left: -2px; /* nudge to align closer to grid */
  min-width: 260px;
  max-width: 420px;
  max-height: 240px;
  background: #FFFFFF;
  border: 1px solid #E8EDF8;
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
  padding: 12px 12px 12px 4px; /* minimal left padding */
  z-index: 1100;
  overflow: auto;
}

.language-popover .popover-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 600;
  color: #262626;
  margin: 0 0 4px 0; /* remove extra margins */
}

.language-popover .close-x {
  background: none;
  border: none;
  cursor: pointer;
  color: #949494;
}

.language-flow {
  margin: 0 0 0 14px; /* slight indent to align visually with header */
  color: #616161;
  font-size: 14px;
  line-height: 1.7;
  word-break: keep-all; /* better Korean/English readability */
  white-space: normal; /* allow wrapping */
}

/* Prevent long values (e.g., languages) from overflowing */
.table-data .truncate {
  display: inline-block;
  max-width: 140px; /* slightly wider to accommodate longer labels */
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  vertical-align: bottom;
}

/* 구분선 */
.info-table::before,
.info-table::after {
  content: '';
  position: absolute;
  width: 100%;
  height: 0px;
  border: 1px solid #F9D2D6;
  border-radius: 1px;
}

.info-table::before {
  top: 15px;
}

.info-table::after {
  top: 55px;
}

/* 프로젝트 소개 */
.memo-box {
  display: flex;
  justify-content: flex-start;
  align-items: flex-start;
  padding: 25px 35px;
  gap: 10px;
  width: 100%;
  min-height: 110px;
  background: #FAFBFD;
  border-radius: 10px;
  box-sizing: border-box;
}

.memo-textarea {
  width: 100%;
  min-height: 60px;
  max-height: 300px;
  background: transparent;
  border: none;
  outline: none;
  resize: none;
  font-family: 'Pretendard';
  font-style: normal;
  font-weight: 400;
  font-size: 15px;
  line-height: 18px;
  color: #616161;
  padding: 0;
  margin: 0;
  overflow-y: auto;
}

.memo-textarea:disabled {
  background: #F5F7FA;
  cursor: not-allowed;
  opacity: 0.7;
}

.memo-textarea::placeholder {
  color: #949494;
  font-style: italic;
}

.memo-textarea::-webkit-scrollbar {
  width: 6px;
}

.memo-textarea::-webkit-scrollbar-track {
  background: transparent;
}

.memo-textarea::-webkit-scrollbar-thumb {
  background: #CB385C;
  border-radius: 3px;
}

.memo-textarea::-webkit-scrollbar-thumb:hover {
  background: #A02D4A;
}

/* 프로젝트 요약 */
.summary-box {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: flex-start;
  padding: 25px 35px;
  gap: 10px;
  width: 100%;
  min-height: 110px;
  background: #FAFBFD;
  border-radius: 10px;
  box-sizing: border-box;
}

.summary-box p {
  width: 884px;
  height: 50px;
  font-family: 'Pretendard';
  font-style: normal;
  font-weight: 400;
  font-size: 15px;
  line-height: 18px;
  color: #616161;
  margin: 0;
}

.summary-box .summary-notice {
  width: auto;
  height: auto;
  color: #8a5360;
  font-size: 13px;
  line-height: 1.5;
}

/* 파싱된 요약 내용 스타일 */
.summary-content {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.summary-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

/* all items are full width */

.label {
  font-weight: 700;
  font-size: 15px;
  color: #262626;
}

.value {
  font-size: 14px;
  color: #616161;
  line-height: 1.6;
  white-space: pre-wrap;
}

.value.list {
  list-style-type: disc;
  list-style-position: outside;
  padding-left: 18px;
  margin: 0;
}

.value.list li {
  margin: 4px 0;
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.chip {
  background: #EFF2F9;
  color: #507199;
  border: 1px solid #E8EDF8;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
}

/* legacy styles removed in favor of summary-grid */

.summary-technical,
.summary-quality {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.summary-subtitle {
  font-family: 'Pretendard';
  font-style: normal;
  font-weight: 600;
  font-size: 15px;
  line-height: 18px;
  color: #262626;
  margin: 0;
}

.technical-overview,
.technical-details,
.technical-tools,
.quality-overview,
.quality-details {
  font-family: 'Pretendard';
  font-style: normal;
  font-weight: 400;
  font-size: 14px;
  line-height: 17px;
  color: #616161;
}

.summary-fallback {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 차트 섹션 */
.charts-section {
  display: flex;
  gap: 20px;
  height: 360px;
  width: 100%;
  box-sizing: border-box;
}

.chart-container {
  background: #FFFBFB;
  border-radius: 20px;
  padding: 25px;
  position: relative;
}

.timeline-chart {
  width: 600px;
  flex-shrink: 0;
  min-height: 320px;
  padding-bottom: 40px;
}

.language-chart {
  width: 348px;
  flex-shrink: 0;
}

/* 차트 헤더 */
.chart-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 25px;
}

.chart-title-line {
  width: 0px;
  height: 16px;
  border: 2px solid #FF176A;
}

.chart-header h3 {
  font-family: 'Pretendard';
  font-style: normal;
  font-weight: 600;
  font-size: 18px;
  line-height: 21px;
  color: #FF176A;
  margin: 0;
}

/* 타임라인 차트 */
.chart-content {
  position: relative;
  height: calc(100% - 60px);
}

.y-axis-labels {
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  font-family: 'Pretendard';
  font-style: normal;
  font-weight: 400;
  font-size: 12px;
  line-height: 14px;
  color: #262626;
}

.chart-area {
  position: absolute;
  left: 67px;
  top: 0;
  width: 493px;
  height: 100%;
  max-width: calc(100% - 67px);
}

.chart-svg {
  width: 100%;
  height: 100%;
}

.x-axis-labels {
  position: absolute;
  bottom: -45px;
  left: 67px;
  width: 493px;
  max-width: calc(100% - 67px);
  display: flex;
  justify-content: space-between;
  font-family: 'Pretendard';
  font-style: normal;
  font-weight: 400;
  color: #262626;
}

.x-axis-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 2px;
}

.label-month {
  font-size: 13px;
  font-weight: 500;
  line-height: 16px;
  color: #262626;
}

.label-year {
  font-size: 11px;
  font-weight: 400;
  line-height: 13px;
  color: #616161;
}

.chart-legend {
  position: absolute;
  top: -20px;
  right: 0;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.legend-color {
  width: 10px;
  height: 10px;
  background: #FF84A3;
  border-radius: 10px;
}

.legend-item span {
  font-family: 'Pretendard';
  font-style: normal;
  font-weight: 400;
  font-size: 12px;
  line-height: 14px;
  color: #616161;
}

/* 도넛 차트 */
.donut-chart {
  position: relative;
  width: 140px;
  height: 140px;
  margin: 0 auto 15px;
  margin-top: 55px;
}

.donut-chart canvas {
  z-index: 10;
  position: relative;
}

.donut-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80px;
  height: 80px;
  background: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Pretendard';
  font-style: normal;
  font-weight: 500;
  font-size: 16px;
  line-height: 19px;
  color: #FF176A;
  z-index: 1;
}

.top-language {
  color: #FF176A;
  font-weight: 600;
}

.no-data-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.no-data-icon {
  font-size: 20px;
  opacity: 0.6;
}

.no-data-text {
  color: #949494;
  font-size: 12px;
  font-weight: 400;
}

.no-data-legend {
  color: #949494;
  font-style: italic;
}

/* 언어 범례 */
.language-legend {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  width: 100%;
  margin-top: 25px;
}

.language-legend .legend-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.language-legend .legend-color {
  width: 13px;
  height: 13px;
  border-radius: 10px;
}

.language-legend .legend-color.cpp {
  background: #FF176A;
}

.language-legend .legend-color.python {
  background: #FF84A3;
}

.language-legend .legend-color.other {
  background: #FFD1DC;
}

.language-legend .legend-item span {
  font-family: 'Pretendard';
  font-style: normal;
  font-weight: 500;
  font-size: 14px;
  line-height: 17px;
  color: #616161;
}
</style>
