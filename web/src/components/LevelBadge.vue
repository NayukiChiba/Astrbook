<template>
  <span 
    class="level-badge" 
    :class="{ 'is-gradient': titleInfo.isGradient }"
    :style="badgeStyle"
    :title="`Lv.${level} - ${exp} EXP`"
  >
    <span class="level-num">Lv.{{ level }}</span>
    <span class="level-title">{{ titleInfo.title }}</span>
  </span>
</template>

<script setup>
import { computed } from 'vue'
import { getTitleForLevel } from '@/utils/levelTitle'

const props = defineProps({
  level: {
    type: Number,
    default: 1
  },
  exp: {
    type: Number,
    default: 0
  },
  size: {
    type: String,
    default: 'normal', // 'small', 'normal', 'large'
  }
})

const titleInfo = computed(() => getTitleForLevel(props.level))

const badgeStyle = computed(() => {
  const info = titleInfo.value
  
  if (info.isGradient) {
    return {
      background: info.color,
      color: info.textColor,
      '--badge-size': props.size === 'small' ? '0.75rem' : props.size === 'large' ? '1rem' : '0.8rem'
    }
  }
  
  return {
    backgroundColor: info.color,
    color: info.textColor,
    '--badge-size': props.size === 'small' ? '0.75rem' : props.size === 'large' ? '1rem' : '0.8rem'
  }
})
</script>

<style scoped>
.level-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: var(--badge-size, 0.8rem);
  font-weight: 500;
  white-space: nowrap;
  vertical-align: middle;
}

.level-badge.is-gradient {
  background-clip: padding-box;
  -webkit-background-clip: padding-box;
}

.level-num {
  opacity: 0.9;
}

.level-title {
  font-weight: 600;
  margin-left: 2px;
}
</style>
