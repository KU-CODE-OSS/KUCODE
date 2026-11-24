<template>
  <div class="owner-selector">
    <p class="owner-help">작성자는 자동으로 소유자가 됩니다. 함께 관리할 사용자를 추가로 선택하세요.</p>
    <input
      v-model.trim="search"
      type="search"
      class="owner-search"
      placeholder="이름 또는 사용자 ID 검색"
    />
    <div v-if="loading" class="owner-state">사용자 목록을 불러오는 중입니다.</div>
    <div v-else-if="error" class="owner-state owner-error">{{ error }}</div>
    <div v-else class="owner-list">
      <label v-for="candidate in filteredCandidates" :key="candidate.id" class="owner-option">
        <input
          type="checkbox"
          :checked="modelValue.includes(candidate.id)"
          @change="toggleOwner(candidate.id, $event.target.checked)"
        />
        <span>
          <strong>{{ candidate.name }}</strong>
          <small>{{ candidate.id }} · {{ candidate.role }}</small>
        </span>
      </label>
      <p v-if="!filteredCandidates.length" class="owner-state">선택 가능한 사용자가 없습니다.</p>
    </div>
  </div>
</template>

<script>
import { getPostOwnerCandidates } from '@/api.js'

export default {
  name: 'PostOwnerSelector',
  props: {
    modelValue: {
      type: Array,
      default: () => []
    },
    creatorId: {
      type: String,
      default: ''
    }
  },
  emits: ['update:modelValue'],
  data() {
    return {
      candidates: [],
      search: '',
      loading: false,
      error: ''
    }
  },
  computed: {
    filteredCandidates() {
      const keyword = this.search.toLowerCase()
      return this.candidates.filter(candidate => {
        if (candidate.id === this.creatorId) return false
        if (!keyword) return true
        return [candidate.id, candidate.name, candidate.role]
          .some(value => String(value || '').toLowerCase().includes(keyword))
      })
    }
  },
  mounted() {
    this.loadCandidates()
  },
  methods: {
    async loadCandidates() {
      this.loading = true
      this.error = ''
      try {
        const response = await getPostOwnerCandidates()
        this.candidates = response.data.results || []
      } catch (error) {
        console.error('Failed to load post owner candidates:', error)
        this.error = '사용자 목록을 불러오지 못했습니다.'
      } finally {
        this.loading = false
      }
    },
    toggleOwner(ownerId, checked) {
      const next = new Set(this.modelValue)
      if (checked) next.add(ownerId)
      else next.delete(ownerId)
      this.$emit('update:modelValue', [...next])
    }
  }
}
</script>

<style scoped>
.owner-selector {
  width: 100%;
}

.owner-help,
.owner-state {
  margin: 0 0 10px;
  color: #949494;
  font-size: 13px;
}

.owner-search {
  width: 100%;
  height: 40px;
  padding: 0 12px;
  border: 1px solid #dce2ed;
  border-radius: 6px;
  font: inherit;
}

.owner-list {
  max-height: 180px;
  margin-top: 10px;
  overflow-y: auto;
  border: 1px solid #eef1f5;
  border-radius: 6px;
}

.owner-option {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-bottom: 1px solid #eef1f5;
  cursor: pointer;
}

.owner-option:last-child {
  border-bottom: 0;
}

.owner-option span,
.owner-option small {
  display: block;
}

.owner-option strong {
  color: #262626;
  font-size: 14px;
}

.owner-option small {
  margin-top: 2px;
  color: #949494;
  font-size: 12px;
}

.owner-error {
  color: #b42318;
}
</style>
