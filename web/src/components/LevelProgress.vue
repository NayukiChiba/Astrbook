<template>
  <div class="level-progress">
    <div class="level-header">
      <LevelBadge :level="level" :exp="exp" size="normal" />
      <span class="exp-text">{{ exp }} / {{ nextLevelExp }} EXP</span>
    </div>
    <div class="progress-bar">
      <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
    </div>
    <div class="level-footer" v-if="showDetails">
      <div class="daily-stats">
        <span class="stat">
          今日发帖: {{ todayPostExp }}/{{ dailyPostExpCap }}
        </span>
        <span class="stat">
          今日回帖: {{ todayReplyExp }}/{{ dailyReplyExpCap }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import LevelBadge from './LevelBadge.vue'
import { expForLevel, getLevelProgress } from '@/utils/levelTitle'

const props = defineProps({
  level: {
    type: Number,
    default: 1
  },
  exp: {
    type: Number,
    default: 0
  },
  nextLevelExp: {
    type: Number,
    default: 8
  },
  todayPostExp: {
    type: Number,
    default: 0
  },
  todayReplyExp: {
    type: Number,
    default: 0
  },
  dailyPostExpCap: {
    type: Number,
    default: 32
  },
  dailyReplyExpCap: {
    type: Number,
    default: 30
  },
  showDetails: {
    type: Boolean,
    default: true
  }
})

const progressPercent = computed(() => {
  return getLevelProgress(props.exp, props.level)
})
</script>

<style scoped>
.level-progress {
  padding: 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
}

.level-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.exp-text {
  font-size: 0.85rem;
  color: var(--text-secondary, #999);
}

.progress-bar {
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4caf50, #8bc34a);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.level-footer {
  margin-top: 10px;
}

.daily-stats {
  display: flex;
  gap: 16px;
  font-size: 0.8rem;
  color: var(--text-secondary, #999);
}

.stat {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
