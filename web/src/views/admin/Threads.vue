<template>
  <div class="threads-page">
    <div class="page-title">
      <el-icon class="icon"><ChatDotRound /></el-icon>
      <div class="text">
        <h2>帖子管理</h2>
        <p>查看和管理所有帖子</p>
      </div>
    </div>
    
    <div class="card">
      <el-skeleton v-if="loading && threads.length === 0" :rows="8" animated />

      <div
        v-else
        v-loading="loading && threads.length > 0"
        element-loading-background="rgba(0, 0, 0, 0)"
        style="width: 100%"
      >
        <el-table :data="threads" style="width: 100%">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="title" label="标题" min-width="200">
            <template #default="{ row }">
              <router-link :to="`/admin/thread/${row.id}`" class="thread-link">
                {{ row.title }}
              </router-link>
            </template>
          </el-table-column>
          <el-table-column label="分类" width="160">
            <template #default="{ row }">
              <el-select 
                v-model="row.category" 
                size="small"
                @change="handleCategoryChange(row)"
                class="category-select"
              >
                <el-option 
                  v-for="cat in categories" 
                  :key="cat.key" 
                  :label="cat.name" 
                  :value="cat.key"
                >
                  <div class="category-option">
                    <CategoryIcon :category="cat.key" class="category-icon" />
                    <span>{{ cat.name }}</span>
                  </div>
                </el-option>
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="作者" width="150">
            <template #default="{ row }">
              <div class="author-cell">
                <el-avatar :size="28" :src="row.author.avatar">
                  {{ row.author.nickname[0] }}
                </el-avatar>
                <span>{{ row.author.nickname }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="reply_count" label="回复数" width="80" align="center" />
          <el-table-column label="最后回复" width="140">
            <template #default="{ row }">
              {{ formatTime(row.last_reply_at) }}
            </template>
          </el-table-column>
          <el-table-column label="发布时间" width="140">
            <template #default="{ row }">
              {{ formatTime(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="80" fixed="right">
            <template #default="{ row }">
              <el-button 
                type="danger" 
                text 
                size="small"
                @click="handleDelete(row)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <div class="pagination-wrapper">
          <el-pagination
            v-model:current-page="page"
            v-model:page-size="pageSize"
            :total="total"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next, jumper"
            @current-change="loadThreads"
            @size-change="loadThreads"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineOptions({ name: 'AdminThreads' })

import { ref, onMounted } from 'vue'
import { getThreads, getCategories, adminDeleteThread, adminUpdateThreadCategory } from '../../api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getThreadsListCache, setThreadsListCache, clearThreadsListCache } from '../../state/dataCache'
import CategoryIcon from '../../components/icons/CategoryIcons.vue'
import dayjs from 'dayjs'

const threads = ref([])
const categories = ref([])
const loading = ref(true)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const formatTime = (time) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm')
}

const loadCategories = async () => {
  try {
    categories.value = await getCategories()
  } catch (error) {
    console.error('Failed to load categories:', error)
  }
}

const loadThreads = async (options = {}) => {
  const force = options?.force === true
  if (!force) {
    const cached = getThreadsListCache(page.value, pageSize.value)
    if (cached) {
      threads.value = cached.items || []
      total.value = cached.total || 0
      loading.value = false
      return
    }
  }

  loading.value = true
  try {
    const res = await getThreads({ page: page.value, page_size: pageSize.value })
    const cachedRes = setThreadsListCache(page.value, pageSize.value, res)
    threads.value = cachedRes.items || []
    total.value = cachedRes.total || 0
  } catch (error) {
    ElMessage.error('加载帖子失败')
  } finally {
    loading.value = false
  }
}

const handleCategoryChange = async (row) => {
  try {
    const res = await adminUpdateThreadCategory(row.id, row.category)
    ElMessage.success(`分类已更改为: ${res.category_name}`)
    // 清除缓存以便下次刷新
    clearThreadsListCache()
  } catch (error) {
    ElMessage.error('修改分类失败')
    // 恢复原值 - 重新加载
    loadThreads({ force: true })
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除帖子 "${row.title}" 吗？此操作不可恢复。`,
      '确认删除',
      { type: 'warning' }
    )
    await adminDeleteThread(row.id)
    ElMessage.success('删除成功')
    loadThreads({ force: true })
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  loadCategories()
})

loadThreads()
</script>

<style lang="scss" scoped>
.threads-page {
  max-width: 1400px;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 32px;
  
  .icon {
    font-size: 32px;
    filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.2));
  }
  
  .text {
    h2 {
      font-size: 24px;
      font-weight: 600;
      margin-bottom: 4px;
      background: linear-gradient(90deg, #fff, #aaa);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    
    p {
      color: var(--text-secondary);
      font-size: 14px;
    }
  }
}

.card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--glass-border);
  border-radius: 24px;
  padding: 24px;
  backdrop-filter: blur(10px);
}

.thread-link {
  color: var(--text-primary);
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
  
  &:hover {
    color: var(--acid-purple);
  }
}

.author-cell {
  display: flex;
  align-items: center;
  gap: 10px;
  
  span {
    color: var(--text-secondary);
  }
}

// 分类选择器样式
.category-select {
  width: 100%;
}

.category-option {
  display: flex;
  align-items: center;
  gap: 8px;
  
  .category-icon {
    width: 16px;
    height: 16px;
    color: var(--acid-purple);
  }
}

:deep(.el-select) {
  .el-input__wrapper {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid var(--glass-border);
    box-shadow: none;
    
    &:hover {
      border-color: var(--acid-purple);
    }
  }
  
  .el-input__inner {
    color: var(--text-primary);
  }
}

.pagination-wrapper {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}

// 表格样式覆盖
:deep(.el-table) {
  background: transparent;
  --el-table-border-color: var(--glass-border);
  --el-table-header-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-row-hover-bg-color: rgba(255, 255, 255, 0.05);
  
  th.el-table__cell {
    background: transparent;
    color: var(--text-secondary);
    font-weight: 500;
    border-bottom: 1px solid var(--glass-border);
  }
  
  td.el-table__cell {
    border-bottom: 1px solid var(--glass-border);
    color: var(--text-primary);
  }
  
  .el-table__inner-wrapper::before {
    display: none;
  }
}

// 分页样式覆盖
:deep(.el-pagination) {
  --el-pagination-bg-color: transparent;
  --el-pagination-button-disabled-bg-color: transparent;
  --el-pagination-hover-color: var(--acid-purple);
  
  .el-pager li {
    background: transparent;
    color: var(--text-secondary);
    
    &.is-active {
      color: var(--acid-purple);
      font-weight: bold;
    }
  }
  
  button {
    background: transparent;
    color: var(--text-secondary);
  }
}
</style>
