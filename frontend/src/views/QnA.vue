<template>
  <div class="qna-page">
    <div class="qna-container">
      <!-- Left Sidebar Navigation -->
      <aside class="sidebar-navigation">
        <button class="sidebar-nav-item active">
          <span>Q&A</span>
          <svg width="12" height="8" viewBox="0 0 12 8" fill="none" class="arrow-icon">
            <path d="M1 1L6 6L11 1" stroke="#CB385C" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </aside>

      <!-- Main Content Area -->
      <main class="main-content">
        <div class="content-header">
          <h1 class="page-title">Q&A</h1>

          <div class="header-actions">
            <div class="filter-dropdown" @click="toggleYearDropdown">
              <span>{{ selectedYear }}년</span>
              <svg width="12" height="8" viewBox="0 0 12 8" fill="none" class="dropdown-icon">
                <path d="M1 1.5L6 6.5L11 1.5" stroke="#616161" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <div v-if="showYearDropdown" class="dropdown-menu">
                <div
                  v-for="year in availableYears"
                  :key="year"
                  class="dropdown-option"
                  @click.stop="selectYear(year)"
                >
                  {{ year }}년
                </div>
              </div>
            </div>

            <button class="write-post-btn" @click="openWriteQuestion">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none" class="btn-icon">
                <circle cx="10" cy="10" r="9.25" stroke="#616161" stroke-width="1.5"/>
                <path d="M10 6V14M6 10H14" stroke="#616161" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
              질문 작성
            </button>

            <div class="search-container">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none" class="search-icon">
                <circle cx="9" cy="9" r="5.75" stroke="#616161" stroke-width="1.5"/>
                <path d="M13 13L16 16" stroke="#616161" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
            </div>
          </div>
        </div>

        <div class="content-meta">
          <span class="total-count">총 {{ questionList.length }}건</span>
        </div>

        <!-- Questions List View -->
        <div v-if="!selectedQuestion" class="questions-table">
          <div class="table-wrapper">
            <div class="table-header">
              <div class="table-row header-row">
                <div class="table-cell col-number">번호</div>
                <div class="table-cell col-title">제목</div>
                <div class="table-cell col-date">등록 일자</div>
                <div class="table-cell col-author">작성자</div>
                <div class="table-cell col-answers">답변수</div>
                <div class="table-cell col-views">조회수</div>
              </div>
            </div>

            <div class="table-body">
              <div
                v-for="question in questionList"
                :key="question.id"
                class="table-row"
                @click="openQuestion(question)"
              >
                <div class="table-cell col-number">{{ question.number }}</div>
                <div class="table-cell col-title">
                  {{ question.title }}
                  <span v-if="question.is_resolved" class="resolved-badge">해결됨</span>
                </div>
                <div class="table-cell col-date">{{ question.date }}</div>
                <div class="table-cell col-author">{{ question.author }}</div>
                <div class="table-cell col-answers">{{ question.answer_count }}</div>
                <div class="table-cell col-views">{{ question.views }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Question Detail View -->
        <div v-else class="question-detail">
          <div class="detail-header">
            <button class="back-btn" @click="closeQuestion">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M12 4L6 10L12 16" stroke="#616161" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              목록으로
            </button>
            <h2 class="detail-title">{{ selectedQuestion.title }}</h2>
          </div>

          <div class="detail-meta">
            <span class="meta-item">작성자: {{ selectedQuestion.author }}</span>
            <span class="meta-item">작성일: {{ selectedQuestion.date }}</span>
            <span class="meta-item">조회수: {{ selectedQuestion.views }}</span>
            <span v-if="selectedQuestion.is_resolved" class="resolved-badge">해결됨</span>
          </div>

          <div class="detail-content">
            <p>{{ selectedQuestion.content }}</p>
          </div>

          <!-- Comments/Answers Section -->
          <div class="comments-section">
            <h3 class="comments-title">답변 ({{ comments.length }})</h3>

            <div class="comment-list">
              <div
                v-for="comment in comments"
                :key="comment.id"
                class="comment-item"
                :class="{ 'is-reply': comment.parent_id }"
              >
                <div class="comment-header">
                  <span class="comment-author">{{ comment.author }}</span>
                  <span class="comment-date">{{ comment.created_at }}</span>
                </div>
                <div class="comment-content">{{ comment.content }}</div>
                <div class="comment-actions">
                  <button @click="replyToComment(comment)" class="action-btn">답글</button>
                  <button
                    v-if="canDeleteComment(comment)"
                    @click="deleteComment(comment.id)"
                    class="action-btn delete-btn"
                  >
                    삭제
                  </button>
                </div>
              </div>
            </div>

            <!-- Add Comment Form -->
            <div class="add-comment-form">
              <textarea
                v-model="newCommentContent"
                placeholder="답변을 입력하세요..."
                rows="4"
                class="comment-input"
              ></textarea>
              <button @click="submitComment" class="submit-comment-btn" :disabled="!newCommentContent.trim()">
                답변 작성
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script>
export default {
  name: 'QnAPage',
  data() {
    return {
      selectedYear: 2025,
      showYearDropdown: false,
      availableYears: [2025, 2024, 2023, 2022, 2021, 2020],
      selectedQuestion: null,
      questionList: [
        // Sample data - will be replaced with API calls
        {
          id: 1,
          number: 1,
          title: 'Vue.js 라우터 설정 관련 질문입니다',
          content: 'Vue Router에서 nested routes를 설정하는 방법을 알고 싶습니다. 특히 동적 라우팅과 관련하여 궁금한 점이 있습니다.',
          author: '김철수',
          date: '2025-01-15',
          views: 42,
          answer_count: 3,
          is_resolved: false
        },
        {
          id: 2,
          number: 2,
          title: 'Pinia store에서 데이터 캐싱 방법',
          content: 'Pinia store에 데이터를 캐싱하고 세션 스토리지와 동기화하는 방법에 대해 알고 싶습니다.',
          author: '이영희',
          date: '2025-01-14',
          views: 58,
          answer_count: 5,
          is_resolved: true
        },
        {
          id: 3,
          number: 3,
          title: 'Firebase Authentication 연동 문제',
          content: 'Firebase Auth를 사용할 때 토큰 갱신 처리는 어떻게 하나요?',
          author: '박민수',
          date: '2025-01-13',
          views: 35,
          answer_count: 2,
          is_resolved: false
        }
      ],
      comments: [],
      newCommentContent: '',
      replyingTo: null
    }
  },
  methods: {
    toggleYearDropdown() {
      this.showYearDropdown = !this.showYearDropdown
    },
    selectYear(year) {
      this.selectedYear = year
      this.showYearDropdown = false
      // TODO: PLACEHOLDER_API_CALL() - Filter questions by year
      console.log('Filter by year:', year)
    },
    openWriteQuestion() {
      // TODO: PLACEHOLDER_API_CALL() - Navigate to question write page
      console.log('Open write question page')
      alert('질문 작성 페이지로 이동 (구현 예정)')
    },
    openQuestion(question) {
      this.selectedQuestion = question
      this.loadComments(question.id)
    },
    closeQuestion() {
      this.selectedQuestion = null
      this.comments = []
      this.newCommentContent = ''
      this.replyingTo = null
    },
    loadComments(questionId) {
      // TODO: PLACEHOLDER_API_CALL() - GET /api/board/qna_comments
      // For now, load sample data
      this.comments = [
        {
          id: 1,
          question_id: questionId,
          parent_id: null,
          author: '전문가A',
          content: 'Vue Router 공식 문서를 참고하시면 좋습니다. nested routes는 children 속성을 사용합니다.',
          created_at: '2025-01-15 10:30',
          author_id: 'expert_a_id'
        },
        {
          id: 2,
          question_id: questionId,
          parent_id: 1,
          author: '김철수',
          content: '감사합니다! 도움이 되었습니다.',
          created_at: '2025-01-15 11:00',
          author_id: 'user_kim_id'
        }
      ]
    },
    replyToComment(comment) {
      this.replyingTo = comment
      this.newCommentContent = `@${comment.author} `
    },
    async submitComment() {
      if (!this.newCommentContent.trim()) return

      // TODO: PLACEHOLDER_API_CALL() - POST /api/board/add_qna_comment
      // Expected payload: { question_id, author_id, content, parent_id }
      console.log('Submit comment:', {
        question_id: this.selectedQuestion.id,
        content: this.newCommentContent,
        parent_id: this.replyingTo?.id || null
      })

      // Optimistic UI update
      const newComment = {
        id: Date.now(),
        question_id: this.selectedQuestion.id,
        parent_id: this.replyingTo?.id || null,
        author: '현재 사용자', // TODO: Get from authStore
        content: this.newCommentContent,
        created_at: new Date().toLocaleString('ko-KR'),
        author_id: 'current_user_id' // TODO: Get from authStore
      }

      this.comments.push(newComment)
      this.newCommentContent = ''
      this.replyingTo = null
    },
    canDeleteComment(comment) {
      // TODO: Check if current user is the author
      // return authStore.memberId === comment.author_id
      return false // Placeholder
    },
    async deleteComment(commentId) {
      if (!confirm('정말 삭제하시겠습니까?')) return

      // TODO: PLACEHOLDER_API_CALL() - POST /api/board/delete_qna_comment
      // Expected payload: { comment_id, author_id }
      console.log('Delete comment:', commentId)

      // Optimistic UI update
      const index = this.comments.findIndex(c => c.id === commentId)
      if (index !== -1) {
        // Check if comment has replies
        const hasReplies = this.comments.some(c => c.parent_id === commentId)
        if (hasReplies) {
          this.comments[index].content = '삭제된 댓글입니다.'
          this.comments[index].is_deleted = true
        } else {
          this.comments.splice(index, 1)
        }
      }
    }
  }
}
</script>

<style scoped>
/* Global Styles */
.qna-page {
  font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif;
  background: #FCFCFC;
  min-height: 100vh;
  padding-top: 100px;
}

.qna-container {
  display: flex;
  max-width: 1920px;
  margin: 0 auto;
  padding: 0 320px;
  gap: 0;
}

/* Sidebar Navigation */
.sidebar-navigation {
  width: 268px;
  min-width: 268px;
  border-right: 2px solid #DCE2ED;
  padding-top: 57px;
}

.sidebar-nav-item {
  width: 100%;
  padding: 16px 24px;
  background: none;
  border: none;
  text-align: left;
  font-size: 16px;
  font-weight: 500;
  color: #616161;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.2s;
}

.sidebar-nav-item.active {
  color: #CB385C;
  font-weight: 600;
}

.arrow-icon {
  transition: transform 0.2s;
}

/* Main Content */
.main-content {
  flex: 1;
  padding: 57px 57px 57px 57px;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #262626;
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-dropdown {
  position: relative;
  padding: 8px 16px;
  background: #FCFCFC;
  border: 1px solid #DCE2ED;
  border-radius: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #262626;
}

.dropdown-icon {
  transition: transform 0.2s;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 8px;
  background: white;
  border: 1px solid #DCE2ED;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 100;
  min-width: 100px;
}

.dropdown-option {
  padding: 10px 16px;
  cursor: pointer;
  font-size: 14px;
  color: #262626;
  transition: background 0.2s;
}

.dropdown-option:hover {
  background: #F5F5F5;
}

.write-post-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #FCFCFC;
  border: 1px solid #DCE2ED;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: #616161;
  transition: all 0.2s;
}

.write-post-btn:hover {
  background: #F5F5F5;
}

.search-container {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  background: #FCFCFC;
  border: 1px solid #DCE2ED;
  border-radius: 20px;
  cursor: pointer;
}

.content-meta {
  margin-bottom: 16px;
}

.total-count {
  font-size: 14px;
  color: #616161;
}

/* Questions Table */
.questions-table {
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.table-wrapper {
  width: 100%;
}

.table-header {
  background: #FFEAEC;
}

.table-row {
  display: grid;
  grid-template-columns: 80px 1fr 120px 100px 80px 80px;
  border-bottom: 1px solid #F0F0F0;
  transition: background 0.2s;
}

.header-row {
  font-weight: 600;
  color: #262626;
}

.table-body .table-row {
  cursor: pointer;
}

.table-body .table-row:hover {
  background: #FAFAFA;
}

.table-cell {
  padding: 16px;
  font-size: 14px;
  color: #262626;
  display: flex;
  align-items: center;
}

.col-title {
  justify-content: flex-start;
  gap: 8px;
}

.resolved-badge {
  padding: 2px 8px;
  background: #4CAF50;
  color: white;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
}

/* Question Detail */
.question-detail {
  background: white;
  border-radius: 8px;
  padding: 32px;
}

.detail-header {
  margin-bottom: 24px;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 12px;
  background: none;
  border: 1px solid #DCE2ED;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  color: #616161;
  margin-bottom: 16px;
  transition: background 0.2s;
}

.back-btn:hover {
  background: #F5F5F5;
}

.detail-title {
  font-size: 24px;
  font-weight: 700;
  color: #262626;
  margin: 0;
}

.detail-meta {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #F0F0F0;
}

.meta-item {
  font-size: 13px;
  color: #616161;
}

.detail-content {
  margin-bottom: 32px;
  font-size: 15px;
  line-height: 1.6;
  color: #262626;
}

/* Comments Section */
.comments-section {
  border-top: 2px solid #F0F0F0;
  padding-top: 24px;
}

.comments-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 16px;
  color: #262626;
}

.comment-list {
  margin-bottom: 24px;
}

.comment-item {
  padding: 16px;
  background: #FAFAFA;
  border-radius: 8px;
  margin-bottom: 12px;
}

.comment-item.is-reply {
  margin-left: 32px;
  background: #F5F5F5;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.comment-author {
  font-weight: 600;
  font-size: 14px;
  color: #262626;
}

.comment-date {
  font-size: 12px;
  color: #999;
}

.comment-content {
  font-size: 14px;
  line-height: 1.5;
  color: #262626;
  margin-bottom: 8px;
}

.comment-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 4px 12px;
  background: none;
  border: 1px solid #DCE2ED;
  border-radius: 4px;
  font-size: 12px;
  color: #616161;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background: #F0F0F0;
}

.action-btn.delete-btn {
  border-color: #FF5252;
  color: #FF5252;
}

.action-btn.delete-btn:hover {
  background: #FFEBEE;
}

/* Add Comment Form */
.add-comment-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.comment-input {
  width: 100%;
  padding: 12px;
  border: 1px solid #DCE2ED;
  border-radius: 8px;
  font-size: 14px;
  font-family: 'Pretendard', sans-serif;
  resize: vertical;
  outline: none;
  transition: border-color 0.2s;
}

.comment-input:focus {
  border-color: #CB385C;
}

.submit-comment-btn {
  align-self: flex-end;
  padding: 10px 24px;
  background: #CB385C;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.submit-comment-btn:hover {
  background: #B22F4E;
}

.submit-comment-btn:disabled {
  background: #CCC;
  cursor: not-allowed;
}

/* Responsive Design */
@media (max-width: 1600px) {
  .qna-container {
    padding: 0 160px;
  }
}

@media (max-width: 1280px) {
  .qna-container {
    padding: 0 80px;
  }
}

@media (max-width: 768px) {
  .qna-container {
    flex-direction: column;
    padding: 0 20px;
  }

  .sidebar-navigation {
    width: 100%;
    border-right: none;
    border-bottom: 2px solid #DCE2ED;
    padding-top: 0;
  }

  .table-row {
    grid-template-columns: 60px 1fr 100px 80px 60px 60px;
  }

  .comment-item.is-reply {
    margin-left: 16px;
  }
}
</style>
