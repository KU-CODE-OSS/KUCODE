<template>
  <div class="board-page">
    <header class="board-hero">
      <div class="hero-text">
        <p class="hero-eyebrow">NOTICE BOARD</p>
        <h1>{{ activeTabMeta.label }}</h1>
        <p class="hero-description">
          {{ activeTabMeta.description }}
        </p>
      </div>
      <div class="hero-actions">
        <button type="button" class="ghost-btn" @click="resetFilters">
          필터 초기화
        </button>
        <button type="button" class="primary-btn" @click="startNewPost">
          글 작성
        </button>
      </div>
    </header>

    <div class="board-layout">
      <aside class="board-navigation">
        <p class="nav-label">카테고리</p>
        <ul class="nav-list">
          <li v-for="filter in categoryStats" :key="filter.value">
            <button
              type="button"
              class="nav-chip"
              :class="{ active: filter.value === activeCategory }"
              @click="selectCategory(filter.value)"
            >
              <span>{{ filter.label }}</span>
              <span class="nav-count">{{ filter.count }}</span>
            </button>
          </li>
        </ul>
        <p class="nav-helper">
          원하는 주제를 선택하면 관련 게시글만 빠르게 모아볼 수 있어요.
        </p>
      </aside>

      <section class="board-panel">
        <nav class="board-tabs" role="tablist">
          <button
            v-for="tab in navTabs"
            :key="tab.value"
            type="button"
            class="tab-btn"
            :class="{ active: tab.value === activeNav }"
            role="tab"
            @click="setActiveNav(tab.value)"
          >
            {{ tab.label }}
          </button>
        </nav>

        <div class="board-toolbar">
          <form class="search-form" @submit.prevent="handleSearchSubmit">
            <input
              v-model.trim="searchQuery"
              type="search"
              placeholder="키워드로 게시글 검색"
              aria-label="게시글 검색"
            />
            <button type="submit" class="ghost-btn">
              검색
            </button>
          </form>
          <div class="toolbar-actions">
            <label class="sort-label">
              정렬
              <select v-model="sortOption" aria-label="정렬 기준">
                <option
                  v-for="option in sortOptions"
                  :key="option.value"
                  :value="option.value"
                >
                  {{ option.label }}
                </option>
              </select>
            </label>
          </div>
        </div>

        <div class="board-meta">
          <span class="result-count">총 {{ filteredPosts.length }}건</span>
          <span class="meta-updated">최근 업데이트 {{ lastUpdated }}</span>
        </div>

        <div class="board-table-wrapper">
          <table class="board-table">
            <thead>
              <tr>
                <th scope="col" class="col-number">번호</th>
                <th scope="col" class="col-title">제목</th>
                <th scope="col" class="col-date">등록일</th>
                <th scope="col" class="col-writer">작성자</th>
                <th scope="col" class="col-views">조회수</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="post in paginatedPosts"
                :key="post.id"
                :class="{ pinned: post.isPinned }"
                tabindex="0"
                @click="openPost(post)"
                @keyup.enter="openPost(post)"
                @keyup.space.prevent="openPost(post)"
              >
                <td class="col-number">
                  <span v-if="post.isPinned" class="pin-chip">공지</span>
                  <span v-else>{{ post.no }}</span>
                </td>
                <td class="col-title">
                  <div class="title-line">
                    <span>{{ post.title }}</span>
                    <span
                      v-if="post.status"
                      class="status-chip"
                      :class="post.status"
                    >
                      {{ statusCopy[post.status] }}
                    </span>
                  </div>
                  <ul class="tag-list" v-if="post.tags && post.tags.length">
                    <li v-for="tag in post.tags" :key="tag">{{ tag }}</li>
                  </ul>
                </td>
                <td class="col-date">{{ formatDate(post.date) }}</td>
                <td class="col-writer">{{ post.author }}</td>
                <td class="col-views">
                  {{ post.views.toLocaleString('ko-KR') }}
                </td>
              </tr>
            </tbody>
          </table>
          <div v-if="!paginatedPosts.length" class="empty-state">
            <p>조건에 맞는 게시글이 없습니다.</p>
            <button type="button" class="primary-btn" @click="resetFilters">
              필터 초기화
            </button>
          </div>
        </div>

        <div class="board-pagination" v-if="totalPages > 1">
          <button
            type="button"
            class="pagination-btn"
            :disabled="page === 1"
            @click="changePage(page - 1)"
          >
            이전
          </button>
          <div class="page-numbers">
            <button
              v-for="pageNumber in paginationRange"
              :key="pageNumber"
              type="button"
              class="page-number"
              :class="{ active: pageNumber === page }"
              @click="changePage(pageNumber)"
            >
              {{ pageNumber }}
            </button>
          </div>
          <button
            type="button"
            class="pagination-btn"
            :disabled="page === totalPages"
            @click="changePage(page + 1)"
          >
            다음
          </button>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
export default {
  name: 'BoardView',
  data() {
    return {
      navTabs: [
        {
          label: '공지사항',
          value: 'notice',
          description: 'SW 경력개발센터의 공식 공지와 학사 일정을 한 곳에서 확인하세요.'
        },
        {
          label: 'Q&A',
          value: 'qna',
          description: '자주 묻는 질문과 실시간 답변으로 궁금증을 해결하세요.'
        },
        {
          label: '커뮤니티',
          value: 'community',
          description: '학생들의 경험과 노하우를 공유하는 열린 공간입니다.'
        },
        {
          label: '이벤트',
          value: 'event',
          description: '현재 진행 중인 행사와 참여 신청 소식을 모았습니다.'
        }
      ],
      categoryFilters: [
        { label: '전체', value: 'all' },
        { label: '학사', value: 'academic' },
        { label: '장학', value: 'scholarship' },
        { label: '행사', value: 'event' },
        { label: '취업', value: 'career' },
        { label: '지원 프로그램', value: 'support' }
      ],
      sortOptions: [
        { label: '최신순', value: 'latest' },
        { label: '조회순', value: 'views' },
        { label: '댓글순', value: 'comments' }
      ],
      posts: [
        {
          id: 'notice-001',
          no: 138,
          board: 'notice',
          category: 'academic',
          title: '2025-2학기 수강신청 사전 점검 안내',
          date: '2025-11-15',
          author: '학사관리팀',
          views: 1284,
          comments: 4,
          tags: ['필독', '학사'],
          status: 'due',
          isPinned: true
        },
        {
          id: 'notice-002',
          no: 137,
          board: 'notice',
          category: 'career',
          title: '겨울방학 기업 연계 인턴십 참여자 모집',
          date: '2025-11-12',
          author: '경력개발센터',
          views: 978,
          comments: 9,
          tags: ['모집', '현장실습'],
          status: 'closing',
          isPinned: true
        },
        {
          id: 'notice-003',
          no: 136,
          board: 'notice',
          category: 'event',
          title: 'SW Week 2025 행사 일정 및 사전등록',
          date: '2025-11-10',
          author: '운영위원회',
          views: 742,
          comments: 6,
          tags: ['행사', '사전등록'],
          status: 'new',
          isPinned: false
        },
        {
          id: 'notice-004',
          no: 135,
          board: 'notice',
          category: 'scholarship',
          title: '2025년 1차 해외 연수 장학생 추가 모집',
          date: '2025-11-08',
          author: '학생지원팀',
          views: 654,
          comments: 12,
          tags: ['장학', '해외연수'],
          status: '',
          isPinned: false
        },
        {
          id: 'notice-005',
          no: 134,
          board: 'notice',
          category: 'support',
          title: '캡스톤 디자인 멘토링 4차 매칭 결과',
          date: '2025-11-07',
          author: '멘토링TF',
          views: 601,
          comments: 5,
          tags: ['멘토링', '캡스톤'],
          status: '',
          isPinned: false
        },
        {
          id: 'notice-006',
          no: 133,
          board: 'notice',
          category: 'career',
          title: 'AI 트랙 취업 부트캠프 서류 합격자 발표',
          date: '2025-11-05',
          author: '커리어개발실',
          views: 884,
          comments: 14,
          tags: ['AI', '부트캠프'],
          status: 'closing',
          isPinned: false
        },
        {
          id: 'notice-007',
          no: 132,
          board: 'notice',
          category: 'event',
          title: '메타버스 해커톤 현장 스케치 영상 공개',
          date: '2025-11-04',
          author: '홍보팀',
          views: 412,
          comments: 3,
          tags: ['영상', '후기'],
          status: '',
          isPinned: false
        },
        {
          id: 'notice-008',
          no: 131,
          board: 'notice',
          category: 'academic',
          title: '동계 계절학기 개설 교과목 안내',
          date: '2025-11-02',
          author: '학사관리팀',
          views: 533,
          comments: 7,
          tags: ['계절학기'],
          status: '',
          isPinned: false
        },
        {
          id: 'notice-009',
          no: 130,
          board: 'notice',
          category: 'scholarship',
          title: '2025 SW 장학생 오리엔테이션 재공지',
          date: '2025-11-01',
          author: '학생지원팀',
          views: 477,
          comments: 2,
          tags: ['오리엔테이션'],
          status: '',
          isPinned: false
        },
        {
          id: 'notice-010',
          no: 129,
          board: 'notice',
          category: 'support',
          title: '연구실 안전 교육 이수 확인 방법 안내',
          date: '2025-10-30',
          author: '연구지원실',
          views: 389,
          comments: 1,
          tags: ['안전', '필독'],
          status: '',
          isPinned: false
        },
        {
          id: 'community-001',
          no: 58,
          board: 'community',
          category: 'career',
          title: 'SW스타트업 체험 수기 공유',
          date: '2025-11-11',
          author: '홍길동',
          views: 342,
          comments: 11,
          tags: ['후기', '스타트업'],
          status: 'new',
          isPinned: false
        },
        {
          id: 'community-002',
          no: 57,
          board: 'community',
          category: 'academic',
          title: '알고리즘 스터디 7기 모집합니다',
          date: '2025-11-09',
          author: '문수빈',
          views: 281,
          comments: 18,
          tags: ['스터디', '모집'],
          status: '',
          isPinned: false
        },
        {
          id: 'community-003',
          no: 56,
          board: 'community',
          category: 'event',
          title: '디자인-개발 협업 밋업 참여 후기',
          date: '2025-11-03',
          author: '최새롬',
          views: 198,
          comments: 5,
          tags: ['협업', '후기'],
          status: '',
          isPinned: false
        },
        {
          id: 'qna-001',
          no: 88,
          board: 'qna',
          category: 'support',
          title: '현장실습 지원금 지급 일정 문의',
          date: '2025-11-13',
          author: '김유진',
          views: 613,
          comments: 4,
          tags: ['FAQ'],
          status: 'due',
          isPinned: false
        },
        {
          id: 'qna-002',
          no: 87,
          board: 'qna',
          category: 'academic',
          title: '교환학생 학점 인정 범위가 궁금합니다',
          date: '2025-11-06',
          author: '이현우',
          views: 411,
          comments: 2,
          tags: ['학사'],
          status: '',
          isPinned: false
        },
        {
          id: 'qna-003',
          no: 86,
          board: 'qna',
          category: 'support',
          title: '캡스톤 장비 대여 절차 안내 부탁드립니다',
          date: '2025-11-01',
          author: '엄지연',
          views: 305,
          comments: 6,
          tags: ['장비대여'],
          status: '',
          isPinned: false
        },
        {
          id: 'event-001',
          no: 24,
          board: 'event',
          category: 'event',
          title: '데이터 사이언스 캠프 참가자 모집',
          date: '2025-11-14',
          author: '프로그램TF',
          views: 512,
          comments: 8,
          tags: ['캠프', '모집'],
          status: 'new',
          isPinned: false
        },
        {
          id: 'event-002',
          no: 23,
          board: 'event',
          category: 'support',
          title: '오픈소스 컨트리뷰톤 최종 발표 일정',
          date: '2025-11-05',
          author: '산학협력단',
          views: 289,
          comments: 7,
          tags: ['오픈소스'],
          status: '',
          isPinned: false
        }
      ],
      searchQuery: '',
      sortOption: 'latest',
      activeNav: 'notice',
      activeCategory: 'all',
      page: 1,
      pageSize: 10,
      statusCopy: {
        new: 'NEW',
        due: 'D-1',
        closing: '마감임박'
      }
    }
  },
  computed: {
    activeTabMeta() {
      return (
        this.navTabs.find((tab) => tab.value === this.activeNav) || this.navTabs[0]
      )
    },
    postsForActiveNav() {
      return this.posts.filter((post) => post.board === this.activeNav)
    },
    categoryStats() {
      const dataset = this.postsForActiveNav
      const counts = dataset.reduce((acc, post) => {
        if (!acc[post.category]) {
          acc[post.category] = 0
        }
        acc[post.category] += 1
        return acc
      }, {})

      return this.categoryFilters.map((filter) => ({
        ...filter,
        count:
          filter.value === 'all' ? dataset.length : (counts[filter.value] || 0)
      }))
    },
    filteredPosts() {
      let result = [...this.postsForActiveNav]

      if (this.activeCategory !== 'all') {
        result = result.filter((post) => post.category === this.activeCategory)
      }

      if (this.searchQuery) {
        const keyword = this.searchQuery.toLowerCase()
        result = result.filter((post) => {
          const haystack = [
            post.title,
            post.author,
            ...(post.tags || [])
          ]
            .join(' ')
            .toLowerCase()
          return haystack.includes(keyword)
        })
      }

      return [...result].sort((a, b) => this.comparePosts(a, b))
    },
    paginatedPosts() {
      const start = (this.page - 1) * this.pageSize
      return this.filteredPosts.slice(start, start + this.pageSize)
    },
    totalPages() {
      return Math.max(1, Math.ceil(this.filteredPosts.length / this.pageSize))
    },
    paginationRange() {
      const windowSize = 5
      const range = []
      let start = Math.max(1, this.page - Math.floor(windowSize / 2))
      let end = start + windowSize - 1

      if (end > this.totalPages) {
        end = this.totalPages
        start = Math.max(1, end - windowSize + 1)
      }

      for (let i = start; i <= end; i += 1) {
        range.push(i)
      }

      return range
    },
    lastUpdated() {
      const dataset = this.postsForActiveNav
      if (!dataset.length) {
        return '-'
      }
      const latest = Math.max(
        ...dataset.map((post) => new Date(post.date).getTime())
      )
      return new Intl.DateTimeFormat('ko-KR', { dateStyle: 'long' }).format(
        new Date(latest)
      )
    }
  },
  watch: {
    searchQuery() {
      this.page = 1
    },
    sortOption() {
      this.page = 1
    },
    filteredPosts() {
      if (this.page > this.totalPages) {
        this.page = 1
      }
    }
  },
  methods: {
    setActiveNav(value) {
      if (this.activeNav === value) return
      this.activeNav = value
      this.activeCategory = 'all'
      this.page = 1
    },
    selectCategory(value) {
      if (this.activeCategory === value) return
      this.activeCategory = value
      this.page = 1
    },
    handleSearchSubmit() {
      this.page = 1
    },
    changePage(targetPage) {
      if (targetPage < 1 || targetPage > this.totalPages) return
      this.page = targetPage
      this.scrollToPanel()
    },
    resetFilters() {
      this.searchQuery = ''
      this.sortOption = 'latest'
      this.activeCategory = 'all'
      this.page = 1
      this.scrollToPanel()
    },
    startNewPost() {
      if (this.$router && typeof this.$router.push === 'function') {
        this.$router
          .push({ name: 'BoardWrite', query: { board: this.activeNav } })
          .catch(() => {})
      }
    },
    openPost(post) {
      if (this.$router && typeof this.$router.push === 'function') {
        this.$router
          .push({ name: 'BoardDetail', params: { id: post.id } })
          .catch(() => {})
      }
    },
    comparePosts(a, b) {
      if (this.sortOption === 'latest') {
        return new Date(b.date) - new Date(a.date)
      }
      if (this.sortOption === 'views') {
        return b.views - a.views
      }
      if (this.sortOption === 'comments') {
        return b.comments - a.comments
      }
      return 0
    },
    formatDate(value) {
      if (!value) return '-'
      const formatted = new Intl.DateTimeFormat('ko-KR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      })
        .format(new Date(value))
        .replace(/\.\s?/g, '.')
      return formatted.endsWith('.') ? formatted.slice(0, -1) : formatted
    },
    scrollToPanel() {
      if (typeof window === 'undefined') return
      const panel = this.$el ? this.$el.querySelector('.board-panel') : null
      if (!panel) return
      const { top } = panel.getBoundingClientRect()
      window.scrollTo({
        top: window.scrollY + top - 80,
        behavior: 'smooth'
      })
    }
  }
}
</script>

<style scoped>
.board-page {
  min-height: 100vh;
  padding: 48px 24px 80px;
  background: #ffffff;
  font-family: 'Pretendard', 'Noto Sans KR', sans-serif;
}

.board-hero {
  max-width: 1200px;
  margin: 0 auto 32px;
  padding: 32px 40px;
  border-radius: 24px;
  border: 1px solid #f2d9df;
  background: linear-gradient(120deg, #fffbfb 0%, #fff7f9 100%);
  display: flex;
  justify-content: space-between;
  gap: 32px;
  box-shadow: 0 25px 65px rgba(203, 56, 92, 0.15);
}

.hero-text h1 {
  font-size: 32px;
  line-height: 1.3;
  font-weight: 700;
  color: #910024;
  margin: 4px 0 12px;
}

.hero-eyebrow {
  font-size: 14px;
  font-weight: 600;
  color: #cb385c;
  letter-spacing: 0.3em;
}

.hero-description {
  font-size: 16px;
  color: #616161;
  max-width: 600px;
}

.hero-actions {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.board-layout {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 260px 1fr;
  gap: 32px;
}

.board-navigation {
  border-radius: 20px;
  border: 1px solid #f0d9df;
  background: #fffbfb;
  padding: 24px;
  position: sticky;
  top: 120px;
  height: fit-content;
}

.nav-label {
  font-size: 16px;
  font-weight: 600;
  color: #262626;
  margin-bottom: 16px;
}

.nav-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.nav-chip {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-radius: 12px;
  border: 1px solid #f0d9df;
  background: #ffffff;
  padding: 12px 16px;
  font-size: 15px;
  font-weight: 500;
  color: #616161;
  transition: all 0.2s ease;
}

.nav-chip.active {
  border-color: #cb385c;
  background: rgba(203, 56, 92, 0.1);
  color: #cb385c;
  font-weight: 600;
}

.nav-count {
  font-size: 14px;
  font-weight: 600;
}

.nav-helper {
  margin-top: 20px;
  font-size: 13px;
  color: #949494;
  line-height: 1.5;
}

.board-panel {
  border-radius: 24px;
  border: 1px solid #e8edf8;
  background: #ffffff;
  padding: 32px;
  box-shadow: 0 10px 30px rgba(16, 24, 40, 0.08);
}

.board-tabs {
  display: flex;
  gap: 12px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f2f8;
  margin-bottom: 24px;
}

.tab-btn {
  flex: 1;
  padding: 14px;
  border-radius: 14px;
  border: 1px solid #e8edf8;
  background: #fafbfd;
  font-size: 16px;
  font-weight: 600;
  color: #949494;
  transition: all 0.2s ease;
}

.tab-btn.active {
  background: #910024;
  color: #ffffff;
  border-color: #910024;
  box-shadow: 0 10px 25px rgba(145, 0, 36, 0.3);
}

.board-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.search-form {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 260px;
}

.search-form input {
  flex: 1;
  padding: 12px 16px;
  border-radius: 12px;
  border: 1px solid #dce2ed;
  background: #fcfcfc;
  font-size: 14px;
}

.toolbar-actions {
  display: flex;
  align-items: center;
}

.sort-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #616161;
  font-weight: 500;
}

.sort-label select {
  border-radius: 10px;
  border: 1px solid #dce2ed;
  background: #ffffff;
  padding: 8px 32px 8px 12px;
  font-size: 14px;
}

.board-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  color: #616161;
  margin-bottom: 12px;
}

.result-count {
  font-weight: 600;
  color: #262626;
}

.board-table-wrapper {
  border-radius: 18px;
  border: 1px solid #e8edf8;
  overflow: hidden;
}

.board-table {
  width: 100%;
  border-collapse: collapse;
}

.board-table thead {
  background: #f8f8f8;
}

.board-table th {
  text-align: left;
  font-size: 14px;
  font-weight: 600;
  color: #616161;
  padding: 16px 18px;
  border-bottom: 1px solid #e8edf8;
}

.board-table td {
  padding: 18px;
  font-size: 14px;
  color: #262626;
  border-bottom: 1px solid #f3f5fa;
}

.board-table tbody tr {
  cursor: pointer;
  transition: background 0.2s ease;
}

.board-table tbody tr:hover {
  background: #fffbfb;
}

.board-table tbody tr.pinned {
  background: rgba(203, 56, 92, 0.05);
}

.title-line {
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 600;
}

.tag-list {
  list-style: none;
  margin: 8px 0 0;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag-list li {
  padding: 4px 10px;
  background: #f5f7fc;
  color: #616161;
  font-size: 12px;
  border-radius: 999px;
}

.pin-chip {
  padding: 6px 12px;
  border-radius: 999px;
  background: #cb385c;
  color: #ffffff;
  font-size: 12px;
  font-weight: 600;
}

.status-chip {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
}

.status-chip.new {
  background: #eef3ff;
  color: #4f6bff;
}

.status-chip.due {
  background: #fff4e0;
  color: #ff8a00;
}

.status-chip.closing {
  background: #ffe5ea;
  color: #cb385c;
}

.col-number {
  width: 90px;
}

.col-title {
  width: 45%;
}

.col-date,
.col-writer,
.col-views {
  width: 15%;
}

.empty-state {
  padding: 60px 20px;
  text-align: center;
  color: #616161;
  display: flex;
  flex-direction: column;
  gap: 16px;
  align-items: center;
}

.board-pagination {
  margin-top: 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.pagination-btn {
  padding: 10px 20px;
  border-radius: 12px;
  border: 1px solid #dce2ed;
  background: #ffffff;
  font-weight: 600;
  color: #616161;
  min-width: 96px;
}

.pagination-btn:disabled {
  color: #c0c0c0;
  border-color: #f0f0f0;
  background: #fafafa;
  cursor: not-allowed;
}

.page-numbers {
  display: flex;
  gap: 8px;
}

.page-number {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  border: 1px solid #dce2ed;
  background: #ffffff;
  font-weight: 600;
  color: #616161;
}

.page-number.active {
  background: #cb385c;
  border-color: #cb385c;
  color: #ffffff;
  box-shadow: 0 10px 20px rgba(203, 56, 92, 0.25);
}

.primary-btn,
.ghost-btn {
  border-radius: 999px;
  padding: 12px 22px;
  font-size: 14px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.primary-btn {
  background: #cb385c;
  color: #ffffff;
  box-shadow: 0 10px 25px rgba(203, 56, 92, 0.35);
}

.primary-btn:hover {
  background: #920024;
}

.ghost-btn {
  background: #f8f8f8;
  color: #616161;
  border: 1px solid #dce2ed;
}

.ghost-btn:hover {
  color: #cb385c;
  border-color: #cb385c;
}

@media (max-width: 1100px) {
  .board-layout {
    grid-template-columns: 1fr;
  }

  .board-navigation {
    position: relative;
    top: 0;
    order: 2;
  }
}

@media (max-width: 768px) {
  .board-hero,
  .board-panel {
    padding: 24px;
  }

  .board-tabs {
    flex-direction: column;
  }

  .board-toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .board-meta {
    flex-direction: column;
    gap: 6px;
    align-items: flex-start;
  }

  .board-table th,
  .board-table td {
    padding: 12px;
  }

  .board-pagination {
    flex-direction: column;
  }
}
</style>
