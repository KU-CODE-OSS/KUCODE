<template>
  <div class="qna-create-page">
    <main class="create-container">
      <button type="button" class="back-button" @click="goBack">이전</button>
      <h1>Q&A 질문 작성</h1>

      <form class="create-form" @submit.prevent="handleSubmit">
        <label>
          <span>제목</span>
          <input v-model.trim="form.title" type="text" placeholder="질문 제목을 입력해주세요" required />
        </label>

        <label>
          <span>내용</span>
          <textarea v-model.trim="form.content" rows="12" placeholder="질문 내용을 입력해주세요" required></textarea>
        </label>

        <div class="owners-field">
          <span>공동 소유자</span>
          <PostOwnerSelector v-model="form.ownerIds" :creator-id="authStore.memberId || ''" />
        </div>

        <p v-if="error" class="error-message">{{ error }}</p>
        <div class="form-actions">
          <button type="button" class="cancel-button" @click="goBack">취소</button>
          <button type="submit" class="submit-button" :disabled="loading">
            {{ loading ? '저장 중...' : '질문 등록' }}
          </button>
        </div>
      </form>
    </main>
  </div>
</template>

<script>
import { createOrUpdatePost } from '@/api.js'
import PostOwnerSelector from '@/components/PostOwnerSelector.vue'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'QnaCreate',
  components: { PostOwnerSelector },
  setup() {
    const authStore = useAuthStore()
    return { authStore }
  },
  data() {
    return {
      form: {
        title: '',
        content: '',
        ownerIds: []
      },
      loading: false,
      error: ''
    }
  },
  methods: {
    goBack() {
      this.$router.push({ path: '/board', query: { category: 'qna' } })
    },
    async handleSubmit() {
      const authorId = this.authStore.memberId
      if (!authorId) {
        this.error = '로그인 사용자 정보를 확인할 수 없습니다.'
        return
      }

      this.loading = true
      this.error = ''
      try {
        const now = new Date()
        await createOrUpdatePost({
          author: authorId,
          owner_ids: this.form.ownerIds,
          title: this.form.title,
          content: this.form.content,
          category: 'QNA',
          year: now.getFullYear(),
          semester: now.getMonth() < 6 ? '1' : '2',
          is_internal: true
        })
        this.goBack()
      } catch (error) {
        console.error('Failed to create Q&A post:', error)
        this.error = '질문 등록에 실패했습니다.'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.qna-create-page {
  min-height: 100vh;
  padding-top: 120px;
  background: #fff;
  color: #262626;
}

.create-container {
  width: min(848px, calc(100% - 48px));
  margin: 0 auto;
  padding: 72px 0;
}

.back-button {
  border: 0;
  background: transparent;
  color: #949494;
  cursor: pointer;
}

h1 {
  margin: 28px 0 36px;
  font-size: 24px;
}

.create-form {
  padding-top: 28px;
  border-top: 1px solid #dce2ed;
}

.create-form > label,
.owners-field {
  display: grid;
  grid-template-columns: 120px 1fr;
  gap: 24px;
  margin-bottom: 28px;
  color: #616161;
}

input,
textarea {
  width: 100%;
  padding: 14px;
  border: 1px solid #dce2ed;
  border-radius: 6px;
  box-sizing: border-box;
  font: inherit;
}

textarea {
  resize: vertical;
}

.error-message {
  color: #b42318;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 24px;
  border-top: 1px solid #dce2ed;
}

.form-actions button {
  padding: 12px 24px;
  border-radius: 6px;
  cursor: pointer;
}

.cancel-button {
  border: 1px solid #dce2ed;
  background: #fff;
}

.submit-button {
  border: 1px solid #910024;
  background: #910024;
  color: #fff;
}

@media (max-width: 720px) {
  .create-form > label,
  .owners-field {
    grid-template-columns: 1fr;
    gap: 8px;
  }
}
</style>
