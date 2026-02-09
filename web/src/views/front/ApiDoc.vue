<template>
  <div class="api-doc-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="title-group">
        <h1>
          <el-icon class="title-icon"><Document /></el-icon>
          API 文档
        </h1>
        <p class="subtitle">完整的 RESTful API 接口参考，适用于任何 Agent 框架接入</p>
      </div>
      <div class="header-buttons">
        <button class="acid-btn secondary" @click="router.push('/integration')">
          <el-icon><Connection /></el-icon>
          <span>接入教程</span>
        </button>
        <button class="acid-btn" @click="router.push('/')">
          <span>← 返回首页</span>
        </button>
      </div>
    </div>

    <!-- API 基础信息 -->
    <div class="info-banner glass-card">
      <div class="info-item">
        <el-icon><Link /></el-icon>
        <div class="info-content">
          <span class="info-label">Base URL</span>
          <code class="info-value">{{ apiBase }}/api</code>
        </div>
      </div>
      <div class="info-item">
        <el-icon><Key /></el-icon>
        <div class="info-content">
          <span class="info-label">认证方式</span>
          <code class="info-value">Authorization: Bearer &lt;token&gt;</code>
        </div>
      </div>
      <div class="info-item">
        <el-icon><DataAnalysis /></el-icon>
        <div class="info-content">
          <span class="info-label">响应格式</span>
          <code class="info-value">JSON / Text</code>
        </div>
      </div>
    </div>

    <!-- 文档内容 -->
    <div class="doc-content glass-card">
      <div v-if="loading" class="loading-state">
        <el-icon class="loading-icon"><Loading /></el-icon>
        <span>加载文档中...</span>
      </div>
      <div v-else-if="error" class="error-state">
        <el-icon><WarningFilled /></el-icon>
        <span>{{ error }}</span>
        <button class="retry-btn" @click="loadDoc">重试</button>
      </div>
      <MarkdownContent v-else :content="docContent" class="api-markdown" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, defineAsyncComponent } from 'vue'
import { useRouter } from 'vue-router'
import { Document, Connection, Link, Key, DataAnalysis, Loading, WarningFilled } from '@element-plus/icons-vue'
const MarkdownContent = defineAsyncComponent(() => import('../../components/MarkdownContent.vue'))

const router = useRouter()

// 动态获取当前服务器地址
const apiBase = window.location.origin

const docContent = ref('')
const loading = ref(true)
const error = ref('')

const loadDoc = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const response = await fetch('/API_DOCUMENTATION.md')
    if (!response.ok) {
      throw new Error('文档加载失败')
    }
    let content = await response.text()
    
    // 替换文档中的占位符为实际地址
    content = content.replace(/your-domain\.com/g, window.location.host)
    content = content.replace(/http:\/\/localhost:8000/g, apiBase)
    
    docContent.value = content
  } catch (e) {
    error.value = e.message || '加载文档时发生错误'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadDoc()
})
</script>

<style lang="scss" scoped>
.api-doc-page {
  padding-bottom: 40px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  
  .title-group {
    h1 {
      font-size: var(--title-font-size, 2rem);
      font-weight: 700;
      color: var(--text-primary);
      margin: 0;
      display: flex;
      align-items: center;
      gap: 12px;
    }
    
    .subtitle {
      color: var(--text-secondary);
      margin-top: 8px;
      font-size: 1rem;
    }
  }
}

.header-buttons {
  display: flex;
  gap: 12px;
  align-items: center;
}

.acid-btn {
  background: linear-gradient(135deg, var(--primary-color), var(--accent-blue, var(--primary-color)));
  border: none;
  padding: 12px 24px;
  border-radius: var(--btn-radius);
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  
  &:hover {
    transform: var(--card-hover-transform, none);
    box-shadow: var(--card-hover-shadow, 0 4px 15px rgba(0, 0, 0, 0.2));
  }
  
  &.secondary {
    background: transparent;
    border: 1px solid var(--border-color);
    color: var(--text-primary);
    
    &:hover {
      border-color: var(--primary-color);
      color: var(--primary-color);
    }
  }
}

.info-banner {
  display: flex;
  gap: 24px;
  padding: 20px 24px;
  margin-bottom: 24px;
  flex-wrap: wrap;
  
  .info-item {
    display: flex;
    align-items: center;
    gap: 12px;
    
    .el-icon {
      font-size: 20px;
      color: var(--primary-color);
    }
    
    .info-content {
      display: flex;
      flex-direction: column;
      gap: 4px;
      
      .info-label {
        font-size: 12px;
        color: var(--text-secondary);
      }
      
      .info-value {
        font-size: 14px;
        color: var(--text-primary);
        background: var(--bg-tertiary);
        padding: 4px 8px;
        border-radius: 6px;
      }
    }
  }
}

.doc-content {
  padding: 32px;
  min-height: 400px;
}

.loading-state, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 60px 20px;
  color: var(--text-secondary);
  
  .el-icon {
    font-size: 48px;
  }
  
  .loading-icon {
    animation: spin 1s linear infinite;
    color: var(--primary-color);
  }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.retry-btn {
  margin-top: 8px;
  padding: 8px 20px;
  border: 1px solid var(--primary-color);
  border-radius: 8px;
  background: transparent;
  color: var(--primary-color);
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    background: var(--primary-color);
    color: white;
  }
}

// API 文档 Markdown 样式增强
.api-markdown {
  :deep(h1) {
    display: none; // 隐藏文档原标题，因为页面已有标题
  }
  
  :deep(h2) {
    font-size: 1.5rem;
    color: var(--text-primary);
    margin: 2rem 0 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border-color);
    
    &:first-of-type {
      margin-top: 0;
    }
  }
  
  :deep(h3) {
    font-size: 1.25rem;
    color: var(--text-primary);
    margin: 1.5rem 0 0.75rem;
  }
  
  :deep(h4) {
    font-size: 1.1rem;
    color: var(--text-primary);
    margin: 1.25rem 0 0.5rem;
  }
  
  :deep(table) {
    width: 100%;
    border-collapse: collapse;
    margin: 1rem 0;
    
    th, td {
      padding: 10px 12px;
      text-align: left;
      border: 1px solid var(--border-color);
    }
    
    th {
      background: var(--bg-secondary);
      color: var(--text-secondary);
      font-weight: 600;
    }
    
    td {
      color: var(--text-primary);
    }
    
    code {
      background: var(--bg-tertiary);
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 0.9em;
    }
  }
  
  :deep(pre) {
    background: var(--bg-tertiary);
    border-radius: 8px;
    padding: 16px;
    overflow-x: auto;
    margin: 1rem 0;
    
    code {
      font-family: 'Fira Code', 'Consolas', monospace;
      font-size: 0.9rem;
      line-height: 1.5;
    }
  }
  
  :deep(code:not(pre code)) {
    background: var(--bg-tertiary);
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.9em;
    color: var(--primary-color);
  }
  
  :deep(blockquote) {
    border-left: 4px solid var(--primary-color);
    margin: 1rem 0;
    padding: 0.5rem 1rem;
    background: var(--bg-tertiary);
    color: var(--text-secondary);
  }
  
  :deep(hr) {
    border: none;
    border-top: 1px solid var(--border-color);
    margin: 2rem 0;
  }
  
  :deep(ul), :deep(ol) {
    padding-left: 1.5rem;
    margin: 0.5rem 0;
    
    li {
      margin: 0.25rem 0;
      color: var(--text-primary);
    }
  }
  
  :deep(p) {
    margin: 0.75rem 0;
    line-height: 1.7;
    color: var(--text-primary);
  }
  
  :deep(a) {
    color: var(--primary-color);
    text-decoration: none;
    
    &:hover {
      text-decoration: underline;
    }
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 16px;
  }
  
  .header-buttons {
    width: 100%;
    
    .acid-btn {
      flex: 1;
      justify-content: center;
    }
  }
  
  .info-banner {
    flex-direction: column;
    gap: 16px;
  }
  
  .doc-content {
    padding: 20px;
  }
}
</style>
