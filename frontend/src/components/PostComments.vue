<template>
  <section class="comments-section">
    <div class="comments-header">
      <h2>{{ responseLabel }} {{ total ? `(${total})` : '' }}</h2>
      <button type="button" class="refresh-button" @click="loadComments">새로고침</button>
    </div>

    <div v-if="loading" class="comments-state">{{ responseLabel }}을 불러오는 중입니다.</div>
    <div v-else-if="error" class="comments-state comments-error">{{ error }}</div>
    <div v-else-if="!comments.length" class="comments-state">아직 작성된 {{ responseLabel }}이 없습니다.</div>

    <div v-else class="comment-list">
      <article v-for="comment in comments" :key="comment.id" class="comment-thread">
        <div class="comment-card">
          <div class="comment-meta">
            <strong>{{ comment.author.name }}</strong>
            <time>{{ formatDate(comment.created_at) }}</time>
          </div>
          <p>{{ comment.content }}</p>
          <div class="comment-actions">
            <button type="button" @click="startReply(comment)">답글</button>
            <button
              v-if="canDelete(comment)"
              type="button"
              class="delete-button"
              @click="removeComment(comment.id)"
            >삭제</button>
          </div>
        </div>

        <div v-for="reply in comment.replies" :key="reply.id" class="comment-card reply-card">
          <div class="comment-meta">
            <strong>{{ reply.author.name }}</strong>
            <time>{{ formatDate(reply.created_at) }}</time>
          </div>
          <p>{{ reply.content }}</p>
          <div class="comment-actions">
            <button type="button" @click="startReply(reply)">답글</button>
            <button
              v-if="canDelete(reply)"
              type="button"
              class="delete-button"
              @click="removeComment(reply.id)"
            >삭제</button>
          </div>
        </div>
      </article>
    </div>

    <form class="comment-form" @submit.prevent="submitComment">
      <div v-if="replyingTo" class="replying-to">
        <span>{{ replyingTo.author.name }}님에게 답글 작성 중</span>
        <button type="button" @click="cancelReply">취소</button>
      </div>
      <textarea
        v-model="newContent"
        :placeholder="`${responseLabel}을 입력해주세요`"
        rows="4"
        required
      ></textarea>
      <div class="form-footer">
        <span>{{ authStore.memberName || '현재 사용자' }}</span>
        <button type="submit" :disabled="submitting || !newContent.trim()">
          {{ submitting ? '등록 중...' : `${responseLabel} 등록` }}
        </button>
      </div>
    </form>
  </section>
</template>

<script>
import { addComment, deleteComment, getComments } from '@/api.js'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'PostComments',
  props: {
    postId: {
      type: [Number, String],
      required: true
    },
    responseLabel: {
      type: String,
      default: '댓글'
    }
  },
  emits: ['count-change'],
  setup() {
    const authStore = useAuthStore()
    return { authStore }
  },
  data() {
    return {
      comments: [],
      total: 0,
      loading: false,
      submitting: false,
      error: '',
      newContent: '',
      replyingTo: null
    }
  },
  watch: {
    postId: {
      immediate: true,
      handler(value) {
        if (value) this.loadComments()
      }
    }
  },
  methods: {
    async loadComments() {
      if (!this.postId) return
      this.loading = true
      this.error = ''
      try {
        const response = await getComments(this.postId, 1, 100)
        this.comments = response.data.results || []
        this.total = this.comments.reduce(
          (count, comment) => count + 1 + (comment.replies?.length || 0),
          0
        )
        this.$emit('count-change', this.total)
      } catch (error) {
        console.error('Failed to load comments:', error)
        this.error = `${this.responseLabel}을 불러오지 못했습니다.`
      } finally {
        this.loading = false
      }
    },
    startReply(comment) {
      this.replyingTo = comment
      const mention = comment.author?.name ? `@${comment.author.name} ` : ''
      if (!this.newContent.startsWith(mention)) this.newContent = mention
    },
    cancelReply() {
      this.replyingTo = null
      this.newContent = ''
    },
    async submitComment() {
      const content = this.newContent.trim()
      const authorId = this.authStore.memberId
      if (!content || !authorId) {
        if (!authorId) this.error = '로그인 사용자 정보를 확인할 수 없습니다.'
        return
      }

      this.submitting = true
      this.error = ''
      try {
        await addComment(
          this.postId,
          authorId,
          content,
          this.replyingTo?.id || null
        )
        this.newContent = ''
        this.replyingTo = null
        await this.loadComments()
      } catch (error) {
        console.error('Failed to add comment:', error)
        this.error = `${this.responseLabel} 등록에 실패했습니다.`
      } finally {
        this.submitting = false
      }
    },
    canDelete(comment) {
      return Boolean(comment.author?.id && comment.author.id === this.authStore.memberId)
    },
    async removeComment(commentId) {
      if (!window.confirm(`${this.responseLabel}을 삭제하시겠습니까?`)) return
      try {
        await deleteComment(commentId, this.authStore.memberId)
        await this.loadComments()
      } catch (error) {
        console.error('Failed to delete comment:', error)
        this.error = `${this.responseLabel} 삭제에 실패했습니다.`
      }
    },
    formatDate(value) {
      if (!value) return ''
      return new Intl.DateTimeFormat('ko-KR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      }).format(new Date(value))
    }
  }
}
</script>

<style scoped>
.comments-section {
  width: 100%;
  max-width: 972px;
  margin-top: 56px;
  padding-top: 32px;
  border-top: 1px solid #dce2ed;
}

.comments-header,
.comment-meta,
.comment-actions,
.replying-to,
.form-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.comments-header h2 {
  margin: 0;
  color: #262626;
  font-size: 20px;
}

.refresh-button,
.comment-actions button,
.replying-to button {
  padding: 0;
  border: 0;
  background: transparent;
  color: #910024;
  cursor: pointer;
}

.comments-state {
  padding: 28px 0;
  color: #949494;
}

.comments-error,
.delete-button {
  color: #b42318 !important;
}

.comment-list {
  margin-top: 20px;
}

.comment-thread {
  border-bottom: 1px solid #eef1f5;
}

.comment-card {
  padding: 18px 0;
}

.reply-card {
  margin-left: 32px;
  padding: 16px;
  border-radius: 6px;
  background: #f8f8f8;
}

.comment-meta strong {
  color: #262626;
}

.comment-meta time,
.form-footer span {
  color: #949494;
  font-size: 12px;
}

.comment-card p {
  margin: 10px 0;
  color: #616161;
  line-height: 1.6;
  white-space: pre-wrap;
}

.comment-actions {
  justify-content: flex-end;
}

.comment-form {
  margin-top: 28px;
}

.replying-to {
  margin-bottom: 8px;
  color: #616161;
  font-size: 13px;
}

.comment-form textarea {
  width: 100%;
  padding: 14px;
  border: 1px solid #dce2ed;
  border-radius: 6px;
  box-sizing: border-box;
  font: inherit;
  resize: vertical;
}

.form-footer {
  margin-top: 10px;
}

.form-footer button {
  padding: 10px 18px;
  border: 0;
  border-radius: 6px;
  background: #910024;
  color: white;
  cursor: pointer;
}

.form-footer button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
