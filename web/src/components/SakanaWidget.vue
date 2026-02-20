<template>
  <!-- 固定在左下角的 sakana 组件挂载点 -->
  <div class="sakana-widget-container" :class="{ 'single-character': singleCharacter }">
    <div ref="widgetEl" id="sakana-widget-mount"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import 'sakana-widget/lib/index.css'
import SakanaWidget from 'sakana-widget'

const widgetEl = ref(null)
const singleCharacter = ref(false)  // 仅一个角色时隐藏切换按钮
let widgetInstance = null

// 从 localStorage 读取配置
function loadSettings() {
  try {
    const stored = localStorage.getItem('sakana_settings')
    if (stored) {
      const data = JSON.parse(stored)
      return {
        urls:    Array.from({ length: 6 }, (_, i) => data.urls?.[i] || ''),
        enabled: [true, data.enabled?.[1] !== false, data.enabled?.[2] !== false,
                  !!data.enabled?.[3], !!data.enabled?.[4], !!data.enabled?.[5]],
        names:   [data.names?.[0] || '自定义1', data.names?.[1] || '自定义2', data.names?.[2] || '自定义3'],
      }
    }
  } catch (e) {
    // 解析失败使用默认值
  }
  return {
    urls:    ['', '', '', '', '', ''],
    enabled: [true, true, true, false, false, false],
    names:   ['自定义1', '自定义2', '自定义3'],
  }
}

// 注册激活的角色并返回角色名称列表
function registerCustomCharacters() {
  const base = SakanaWidget.getCharacter('chisato')
  const { urls, enabled, names } = loadSettings()

  // 后三个自定义角色（无默认图片，未填 URL 则不注册）
  const customDefs = [
    { name: 'custom1', label: names[0] },
    { name: 'custom2', label: names[1] },
    { name: 'custom3', label: names[2] },
  ]

  const activeCharacters = []

  // chisato（Astr娘）始终注册并激活
  SakanaWidget.registerCharacter('chisato', { ...base, image: urls[0] || '/AstrSeio.png' })
  activeCharacters.push('chisato')

  // 覆写内置 takina，使用 Kobe 图片（彻底替换原版角色图）
  SakanaWidget.registerCharacter('takina', { ...base, image: '/Kobe.png' })
  if (enabled[1]) activeCharacters.push('takina')

  // wululu 开启时注册并激活
  if (enabled[2]) {
    SakanaWidget.registerCharacter('wululu', { ...base, image: '/Wululu.png' })
    activeCharacters.push('wululu')
  }

  customDefs.forEach(({ name }, i) => {
    const realIndex = i + 3
    if (enabled[realIndex] && urls[realIndex]) {
      SakanaWidget.registerCharacter(name, { ...base, image: urls[realIndex] })
      activeCharacters.push(name)
    }
  })

  return activeCharacters
}

onMounted(() => {
  const activeCharacters = registerCustomCharacters()
  singleCharacter.value = activeCharacters.length <= 1

  // 默认使用 Astr娘（chisato）
  widgetInstance = new SakanaWidget({
    size: 180,
    character: 'chisato',
    rod: false,      // 不显示支撑杆
  })
    .setState({ y: 0.8 }) // 人物初始向上偏移，与底部按钮拉开距离
    .mount(widgetEl.value)
})

onUnmounted(() => {
  // 组件卸载时销毁实例
  if (widgetInstance) {
    widgetInstance.unmount()
    widgetInstance = null
  }
})
</script>

<style scoped>
/* 固定在页面左下角 */
.sakana-widget-container {
  position: fixed;
  bottom: 20px;
  left: 32px;
  z-index: 999;
  pointer-events: none;
}

/* 让挂载点本身可响应鼠标事件 */
.sakana-widget-container :deep(.sakana-widget) {
  pointer-events: all;
}

/* 只有一个角色时隐藏切换按钮（sakana-widget 所有控制按钮共用 ctrl-item 类，
   通过 title 属性区分切换角色按钮） */
.sakana-widget-container.single-character :deep(.sakana-widget-ctrl-item[title="Next Character"]) {
  display: none !important;
}

/* 移动端隐藏 */
@media (max-width: 768px) {
  .sakana-widget-container {
    display: none;
  }
}
</style>
