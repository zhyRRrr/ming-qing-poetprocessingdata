<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue'

// 定义props接收选中的诗人
const props = defineProps({
  selectedPoet: {
    type: String,
    default: '全部诗人'
  }
})

// 词云图URL
const wordCloudUrl = ref('')
// 加载状态
const loading = ref(false)
// 错误信息
const error = ref('')
// 内部保存当前诗人
const currentPoet = ref(props.selectedPoet)

// 监听选中诗人变化 - 立即响应
watch(
  () => props.selectedPoet,
  async (newPoet) => {
    console.log('WordCloudView - 监听到诗人变化:', newPoet)
    if (newPoet && newPoet !== currentPoet.value) {
      currentPoet.value = newPoet
      await generateWordCloud(newPoet)
    }
  },
  { immediate: true }
)

// 额外监听全局事件，以防props变化没有被正确捕获
const handlePoetChanged = (event) => {
  const newPoet = event.detail.poet
  console.log('WordCloudView - 接收到全局诗人变化事件:', newPoet)
  if (newPoet && newPoet !== currentPoet.value) {
    currentPoet.value = newPoet
    generateWordCloud(newPoet)
  }
}

// 生成词云图
const generateWordCloud = async (poet) => {
  try {
    console.log('开始为诗人生成词云图:', poet)
    loading.value = true
    error.value = ''

    // 请求生成词云图并获取图片
    const response = await fetch('http://localhost:5000/generate_wordcloud', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ poet_name: poet })
    })

    console.log('API响应状态:', response.status)

    if (!response.ok) {
      throw new Error(`请求失败：${response.status}`)
    }

    const data = await response.json()
    console.log('API返回数据:', Object.keys(data))

    if (data.success) {
      // 设置词云图URL (base64编码的图片数据)
      wordCloudUrl.value = `data:image/png;base64,${data.image}`
      console.log('词云图更新成功')
    } else {
      error.value = data.error || '生成词云图失败'
      console.error('词云图生成失败:', data.error)
    }
  } catch (err) {
    console.error('生成词云图错误:', err)
    error.value = `生成词云图错误: ${err.message}`
  } finally {
    loading.value = false
  }
}

// 初始化时设置事件监听
onMounted(() => {
  // 监听自定义事件
  window.addEventListener('poet-changed', handlePoetChanged)

  // 初始生成词云图
  generateWordCloud(props.selectedPoet)

  console.log('WordCloudView 已挂载，初始诗人:', props.selectedPoet)
})

// 组件卸载时清理事件监听
onUnmounted(() => {
  window.removeEventListener('poet-changed', handlePoetChanged)
})
</script>

<template>
  <div class="wordcloud-container">
    <div class="current-poet">
      <span>当前诗人: {{ currentPoet }}</span>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>正在生成词云图...</p>
    </div>

    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button @click="generateWordCloud(currentPoet)">重试</button>
    </div>

    <div v-else-if="wordCloudUrl" class="wordcloud-display">
      <img :src="wordCloudUrl" alt="词云图" />
    </div>

    <div v-else class="empty-state">
      <p>暂无词云图数据</p>
    </div>
  </div>
</template>

<style scoped>
.wordcloud-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: transparent;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}

.current-poet {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 10px;
  padding: 5px 10px;
  background-color: rgba(240, 240, 240, 0.7);
  border-radius: 4px;
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 10;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.wordcloud-display {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: transparent;
}

.wordcloud-display img {
  max-width: 100%;
  max-height: 90%;
  object-fit: contain;
  background-color: transparent;
  mix-blend-mode: multiply;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: rgba(255, 255, 255, 0.5);
  padding: 20px;
  border-radius: 8px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top-color: #3498db;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.error {
  color: #e74c3c;
  text-align: center;
  padding: 20px;
  background-color: rgba(255, 255, 255, 0.7);
  border-radius: 8px;
}

.empty-state {
  color: #7f8c8d;
  text-align: center;
  background-color: rgba(255, 255, 255, 0.7);
  padding: 20px;
  border-radius: 8px;
}
</style>
