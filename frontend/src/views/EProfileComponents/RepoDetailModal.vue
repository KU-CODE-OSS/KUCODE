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
              <span>Stars</span>
              <span>Forks</span>
              <span>Commits</span>
              <span>PRs</span>
              <span>Issues</span>
              <span>Language</span>
              <span>Contributors</span>
            </div>
            <!-- 데이터 행 -->
            <div class="table-data">
              <span>{{ repo?.star_count?.toLocaleString() || '0' }}</span>
              <span>{{ repo?.fork_count?.toLocaleString() || '0' }}</span>
              <span>{{ repo?.commit_count?.toLocaleString() || '0' }}</span>
              <span>{{ repo?.pr_count?.toLocaleString() || '0' }}</span>
              <span>{{ repo?.total_issue_count?.toLocaleString() || '0' }}</span>
              <span>{{ repo?.language || 'N/A' }}</span>
              <span>{{ repo?.contributors_count?.toLocaleString() || '0' }}</span>
            </div>
          </div>
        </div>
        
        <!-- 프로젝트 요약 섹션 -->
        <div class="section">
          <h3 class="section-title">프로젝트 요약</h3>
          <div class="summary-box">
            <div v-if="parsedSummary" class="summary-content">
              <!-- 프로젝트 개요 -->
              <div class="summary-overview">
                <div class="overview-main">
                  {{ parsedSummary.scale }} · {{ parsedSummary.primary_language }} 중심 · 활동 수준: {{ parsedSummary.activity }}
                </div>
                <div class="overview-features">
                  주요 기능: {{ parsedSummary.features.join(', ') }}
                </div>
                <div class="overview-tech">
                  기술 스택: {{ parsedSummary.tech_stack.join(', ') }}
                </div>
              </div>
              
              <!-- 기술 세부사항 -->
              <div class="summary-technical">
                <h4 class="summary-subtitle">기술 세부사항</h4>
                <div class="technical-overview">
                  {{ parsedSummary.testing }} · {{ parsedSummary.deployment }} · {{ parsedSummary.architecture }}
                </div>
                <div class="technical-details">
                  프레임워크: {{ parsedSummary.frameworks.join(', ') }}
                </div>
                <div class="technical-tools">
                  개발 도구: {{ parsedSummary.development_tools.length > 0 ? parsedSummary.development_tools.join(', ') : '없음' }}
                </div>
              </div>
              
              <!-- 품질 지표 -->
              <div class="summary-quality">
                <h4 class="summary-subtitle">품질 지표</h4>
                <div class="quality-overview">
                  베스트 프랙티스: {{ parsedSummary.best_practices }} · 유지보수성: {{ parsedSummary.maintainability }}
                </div>
                <div class="quality-details">
                  코드 구조화: {{ parsedSummary.code_organization }}, 문서 품질: {{ parsedSummary.documentation_quality }}
                </div>
              </div>
            </div>
            <div v-else class="summary-fallback">
              <p>{{ repo?.summary || '프로젝트 설명이 없습니다.' }}</p>
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
                <span v-for="month in recentMonths" :key="month">{{ month }}</span>
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
      languageChart: null
    }
  },
  computed: {
    recentMonths() {
      const months = ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월']
      const currentDate = new Date()
      const currentMonth = currentDate.getMonth()
      
      const recentMonths = []
      for (let i = 11; i >= 0; i--) {
        const monthIndex = (currentMonth - i + 12) % 12
        recentMonths.push(months[monthIndex])
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
      
      // 현재 날짜 기준으로 최근 12개월 데이터 생성
      const currentDate = new Date()
      const monthlyData = []
      
      for (let i = 11; i >= 0; i--) {
        const targetDate = new Date(currentDate.getFullYear(), currentDate.getMonth() - i, 1)
        const yearMonth = `${targetDate.getFullYear()}-${String(targetDate.getMonth() + 1).padStart(2, '0')}`
        
        // API 데이터에서 해당 월의 커밋 수 찾기
        monthlyData.push(monthlyDataMap[yearMonth] || 0)
      }
      
      return monthlyData
    },
    
    // 동적 Y축 라벨 생성
    yAxisLabels() {
      const maxValue = Math.max(...this.timelineData, 1)
      
      // 최대값이 10 이하면 5개 구간, 100 이하면 10개 구간, 그 이상이면 10개 구간
      let intervals = 5
      if (maxValue > 10) intervals = 10
      
      const labels = []
      for (let i = intervals; i >= 0; i--) {
        const value = Math.round((i / intervals) * maxValue)
        labels.push(value)
      }
      
      return labels
    },
    
    // 차트 좌표 계산
    timelinePoints() {
      const points = []
      const chartWidth = 493
      const chartHeight = 200
      const maxValue = Math.max(...this.timelineData, 1)
      
      this.timelineData.forEach((value, index) => {
        const x = (index / 11) * chartWidth // 0~11 인덱스를 0~493으로 매핑
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
    
    // 프로젝트 요약 데이터 파싱
    parsedSummary() {
      if (!this.repo || !this.repo.summary) {
        return null
      }
      
      try {
        // summary가 문자열인 경우 JSON 파싱 시도
        let summaryData = this.repo.summary
        if (typeof summaryData === 'string') {
          summaryData = JSON.parse(summaryData)
        }
        
        // project_summary, technical_details, quality_indicators 구조 확인
        if (summaryData.project_summary && summaryData.technical_details && summaryData.quality_indicators) {
          const project = summaryData.project_summary
          const technical = summaryData.technical_details
          const quality = summaryData.quality_indicators
          
          return {
            scale: project.scale || 'N/A',
            primary_language: project.primary_language || 'N/A',
            activity: project.activity || 'N/A',
            features: project.features || [],
            tech_stack: project.tech_stack || [],
            testing: technical.testing || 'N/A',
            deployment: technical.deployment || 'N/A',
            architecture: technical.architecture || 'N/A',
            frameworks: technical.frameworks || [],
            development_tools: technical.development_tools || [],
            best_practices: quality.best_practices || 'N/A',
            maintainability: quality.maintainability || 'N/A',
            code_organization: quality.code_organization || 'N/A',
            documentation_quality: quality.documentation_quality || 'N/A'
          }
        }
        
        return null
      } catch (error) {
        console.error('프로젝트 요약 파싱 오류:', error)
        return null
      }
    }
  },
  methods: {
    closeModal() {
      this.$emit('close')
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
    }
  },
  
  watch: {
    show(newVal) {
      if (newVal) {
        this.$nextTick(() => {
          this.createLanguageChart()
        })
      } else {
        // 모달이 닫힐 때 차트 정리
        if (this.languageChart) {
          this.languageChart.destroy()
          this.languageChart = null
        }
      }
    },
    
    repo: {
      handler() {
        if (this.show && this.languageChart) {
          this.updateLanguageChart()
        }
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

.section-title {
  font-family: 'Pretendard';
  font-style: normal;
  font-weight: 600;
  font-size: 18px;
  line-height: 21px;
  color: #262626;
  margin: 0;
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
  gap: 35px;
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
  width: 120px;
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

/* 프로젝트 요약 */
.summary-box {
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

/* 파싱된 요약 내용 스타일 */
.summary-content {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.summary-overview {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.overview-main {
  font-family: 'Pretendard';
  font-style: normal;
  font-weight: 600;
  font-size: 16px;
  line-height: 19px;
  color: #262626;
}

.overview-features,
.overview-tech {
  font-family: 'Pretendard';
  font-style: normal;
  font-weight: 400;
  font-size: 14px;
  line-height: 17px;
  color: #616161;
}

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
  bottom: -30px;
  left: 67px;
  width: 493px;
  max-width: calc(100% - 67px);
  display: flex;
  justify-content: space-between;
  font-family: 'Pretendard';
  font-style: normal;
  font-weight: 400;
  font-size: 14px;
  line-height: 17px;
  color: #262626;
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
