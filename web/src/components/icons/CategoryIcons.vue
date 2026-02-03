<template>
  <component :is="iconComponent" class="category-icon-svg" />
</template>

<script setup>
import { computed, h } from 'vue'

const props = defineProps({
  category: {
    type: String,
    default: 'chat'
  }
})

// 图标 SVG 路径定义
const icons = {
  // 闲聊水区 - 聊天气泡
  chat: () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
    h('path', { d: 'M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z' })
  ]),
  
  // 羊毛区 - 标签/优惠
  deals: () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
    h('path', { d: 'M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z' }),
    h('line', { x1: '7', y1: '7', x2: '7.01', y2: '7' })
  ]),
  
  // 杂谈区 - 文件/笔记
  misc: () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
    h('path', { d: 'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z' }),
    h('polyline', { points: '14 2 14 8 20 8' }),
    h('line', { x1: '16', y1: '13', x2: '8', y2: '13' }),
    h('line', { x1: '16', y1: '17', x2: '8', y2: '17' }),
    h('polyline', { points: '10 9 9 9 8 9' })
  ]),
  
  // 技术分享区 - 代码
  tech: () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
    h('polyline', { points: '16 18 22 12 16 6' }),
    h('polyline', { points: '8 6 2 12 8 18' })
  ]),
  
  // 求助区 - 问号
  help: () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
    h('circle', { cx: '12', cy: '12', r: '10' }),
    h('path', { d: 'M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3' }),
    h('line', { x1: '12', y1: '17', x2: '12.01', y2: '17' })
  ]),
  
  // 自我介绍区 - 挥手
  intro: () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
    h('path', { d: 'M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2' }),
    h('circle', { cx: '12', cy: '7', r: '4' })
  ]),
  
  // 游戏动漫区 - 游戏手柄
  acg: () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
    h('line', { x1: '6', y1: '12', x2: '10', y2: '12' }),
    h('line', { x1: '8', y1: '10', x2: '8', y2: '14' }),
    h('line', { x1: '15', y1: '13', x2: '15.01', y2: '13' }),
    h('line', { x1: '18', y1: '11', x2: '18.01', y2: '11' }),
    h('rect', { x: '2', y: '6', width: '20', height: '12', rx: '2' })
  ]),
  
  // 全部 - 地球
  all: () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
    h('circle', { cx: '12', cy: '12', r: '10' }),
    h('line', { x1: '2', y1: '12', x2: '22', y2: '12' }),
    h('path', { d: 'M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z' })
  ])
}

const iconComponent = computed(() => {
  return icons[props.category] || icons.chat
})
</script>

<style scoped>
.category-icon-svg {
  width: 1em;
  height: 1em;
  display: inline-block;
  vertical-align: -0.125em;
}
</style>
