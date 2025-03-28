<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import '@/assets/css/ControllerView.css'

// 定义事件
const emits = defineEmits(['mounted'])

// 定义主题聚类命令
const topicCommand =
  'python lda_visualization/topic_clustering.py --n_neighbors 3 --min_dist 2.0 --spread 4.0 --scale 3.0 --n_clusters 8 --output topic_clusters_interactive.png --input processdata/topic.csv'
// 定义情感可视化命令
const emotionCommand =
  'python emotion/emotion_visualization.py --n_neighbors 3 --min_dist 2.0 --spread 4.0 --scale 3.0 --point_size 15 --point_alpha 0.7 --jitter 0.03 --boundary_alpha 0.04 --expand_factor 0.4 --padding 0.2 --smoothness 0.6 --color_scheme Set1 --output ./emotion_clusters.png'
// 定义词云图命令
const wordcloudCommand = 'python wordcloud_ciyun/create_wordcloud.py'

// 使用Map记录每个脚本的运行状态
const runningScripts = ref(new Map())
// 定义是否连接到服务器
const isConnected = ref(false)
// 定义最大重连尝试次数
const maxReconnectAttempts = 5
// 当前重连尝试次数
let reconnectAttempts = 0
// 重连定时器
let reconnectTimer: ReturnType<typeof setTimeout> | null = null

// 定义输出日志
const outputLog = ref('')
// 定义是否显示输出窗口
const showOutput = ref(false)
// 定义是否显示服务器帮助窗口
const showServerHelp = ref(false)
// 定义选择的类型
const selectedType = ref('topic')
// 定义诗人列表
const poetList = ref<Array<{ id: number; name: string }>>([
  { id: 1, name: '曾懿' },
  { id: 2, name: '宗婉' },
  { id: 3, name: '左錫嘉' }
])
// 定义选中的诗人
const selectedPoet = ref('全部诗人')

// 导出选中的诗人，供父组件使用
defineExpose({
  selectedPoet
})

let socket: WebSocket | null = null

// 计算属性：检查特定脚本是否在运行
const isTopicScriptRunning = computed(() => runningScripts.value.has('主题聚类'))
const isEmotionScriptRunning = computed(() => runningScripts.value.has('情感可视化'))
const isWordcloudScriptRunning = computed(() => runningScripts.value.has('词云图'))

// 连接到本地WebSocket服务器
const connectToServer = () => {
  // 如果已经有连接，先关闭
  if (socket && socket.readyState !== WebSocket.CLOSED) {
    socket.close()
  }

  socket = new WebSocket('ws://localhost:6789')

  socket.onopen = () => {
    console.log('已连接到Python服务器')
    isConnected.value = true
    reconnectAttempts = 0 // 重置重连计数
    // 连接建立后，请求所有正在运行的脚本状态
    checkRunningScripts()
    // 连接建立后，获取诗人列表
    fetchPoetList()
  }

  // 处理服务器发送的消息
  socket.onmessage = (event) => {
    try {
      // 解析服务器发送的消息
      const data = JSON.parse(event.data)

      if (data.type === 'output') {
        // 将消息添加到输出日志中
        outputLog.value += data.content + '\n'
      } else if (data.type === 'status') {
        // 处理脚本完成状态
        if (data.status === 'completed' || data.status === 'error') {
          if (data.scriptId && runningScripts.value.has(data.scriptId)) {
            // 移除已完成的脚本
            const scriptMap = new Map(runningScripts.value)
            scriptMap.delete(data.scriptId)
            runningScripts.value = scriptMap

            // 如果是当前查看的脚本输出，显示输出窗口
            if (data.scriptId === currentScriptId.value) {
              showOutput.value = true
            }
          }
        }
      } else if (data.type === 'script_list') {
        // 更新运行中脚本列表
        const scriptMap = new Map()
        data.scripts.forEach((script: { id: string; command: string }) => {
          scriptMap.set(script.id, script.command)
        })
        runningScripts.value = scriptMap
      } else if (data.type === 'poet_list') {
        // 处理诗人列表数据
        handlePoetListResponse(data)
      }
    } catch (e) {
      // 处理解析错误
      outputLog.value += event.data + '\n'
    }
  }

  socket.onclose = (event) => {
    console.log('与Python服务器的连接已关闭', event.code, event.reason)
    isConnected.value = false

    // 尝试重连，除非是正常关闭
    if (event.code !== 1000 && event.code !== 1001) {
      scheduleReconnect()
    }
  }

  socket.onerror = (error) => {
    console.error('WebSocket错误:', error)
    isConnected.value = false
    // 连接失败时显示帮助
    if (reconnectAttempts >= maxReconnectAttempts) {
      showServerHelp.value = true
    }
  }
}

// 请求获取诗人列表
const fetchPoetList = async () => {
  try {
    // 如果socket连接已建立，通过WebSocket请求
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(
        JSON.stringify({
          action: 'fetch_poets'
        })
      )
    } else {
      // 否则通过API请求
      const response = await fetch('http://localhost:5000/poets')
      if (response.ok) {
        const data = await response.json()
        if (data.success && data.poets) {
          updatePoetList(data.poets)
        }
      }
    }
  } catch (error) {
    console.error('获取诗人列表失败:', error)
  }
}

// 处理WebSocket返回的诗人列表
const handlePoetListResponse = (data: { success: boolean; poets: string[] }) => {
  if (data.success && data.poets) {
    updatePoetList(data.poets)
  }
}

// 更新诗人列表
const updatePoetList = (poets: string[]) => {
  // 保留原有的三个诗人
  const existingPoets = poetList.value.slice(0, 3)

  // 添加来自数据库的其他诗人
  const dbPoets = poets
    .filter((poet: string) => !existingPoets.some((p) => p.name === poet))
    .map((poet: string, index: number) => ({ id: index + 4, name: poet }))

  // 合并列表
  poetList.value = [...existingPoets, ...dbPoets]
}

// 处理诗人选择变化
const handlePoetChange = (event: Event) => {
  const selectElement = event.target as HTMLSelectElement
  const selectedOption = selectElement.options[selectElement.selectedIndex]
  selectedPoet.value = selectedOption.text
  console.log('选择诗人变更为:', selectedPoet.value)

  // 添加延迟，确保Vue更新完成
  setTimeout(() => {
    // 模拟发布事件，确保所有组件都知道诗人变更了
    window.dispatchEvent(
      new CustomEvent('poet-changed', {
        detail: { poet: selectedPoet.value }
      })
    )
  }, 100)
}

// 安排重连
const scheduleReconnect = () => {
  if (reconnectTimer) {
    clearTimeout(reconnectTimer)
  }

  if (reconnectAttempts < maxReconnectAttempts) {
    const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000) // 指数后退，最大30秒
    console.log(
      `安排在 ${delay}ms 后重连，尝试次数: ${reconnectAttempts + 1}/${maxReconnectAttempts}`
    )

    reconnectTimer = setTimeout(() => {
      reconnectAttempts++
      console.log(`尝试重连 (${reconnectAttempts}/${maxReconnectAttempts})...`)
      connectToServer()
    }, delay)
  } else {
    console.log('达到最大重连尝试次数，不再重连')
    showServerHelp.value = true
  }
}

// 请求服务器返回当前运行的脚本列表
const checkRunningScripts = () => {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(
      JSON.stringify({
        action: 'list_scripts'
      })
    )
  }
}

// 设置定期检查脚本状态
let statusCheckInterval: ReturnType<typeof setInterval> | null = null

// 开始定期检查
const startStatusCheck = () => {
  if (statusCheckInterval) {
    clearInterval(statusCheckInterval)
  }

  // 每5秒检查一次运行中的脚本
  statusCheckInterval = setInterval(() => {
    if (isConnected.value) {
      checkRunningScripts()
    }
  }, 5000)
}

// 尝试连接服务器
onMounted(() => {
  connectToServer()
  startStatusCheck()

  // 添加页面可见性变化事件监听器
  document.addEventListener('visibilitychange', handleVisibilityChange)

  // 触发mounted事件，通知父组件
  emits('mounted')
})

// 处理页面可见性变化
const handleVisibilityChange = () => {
  if (document.visibilityState === 'visible') {
    // 页面变为可见时，如果连接已断开，尝试重连
    if (!isConnected.value) {
      console.log('页面变为可见，尝试重新连接...')
      reconnectAttempts = 0 // 重置重连尝试次数
      connectToServer()
    } else {
      // 如果已连接，检查脚本状态
      checkRunningScripts()
    }
  }
}

// 断开WebSocket连接
onUnmounted(() => {
  if (socket) {
    socket.close()
  }

  if (statusCheckInterval) {
    clearInterval(statusCheckInterval)
  }

  if (reconnectTimer) {
    clearTimeout(reconnectTimer)
  }

  // 移除事件监听器
  document.removeEventListener('visibilitychange', handleVisibilityChange)
})

// 定义当前脚本ID，用于输出显示
const currentScriptId = ref('')

// 运行Python脚本
const runScript = (command: string, scriptId: string) => {
  if (!isConnected.value) {
    showServerHelp.value = true
    return
  }

  // 设置当前脚本ID并清空输出日志
  currentScriptId.value = scriptId
  outputLog.value = ''

  // 将脚本添加到运行中列表
  const scriptMap = new Map(runningScripts.value)
  scriptMap.set(scriptId, command)
  runningScripts.value = scriptMap

  // 发送命令到Python服务器，包含脚本ID
  socket?.send(
    JSON.stringify({
      action: 'run',
      command: command,
      scriptId: scriptId
    })
  )
}

// 运行主题聚类脚本
const runTopicScript = () => {
  runScript(topicCommand, '主题聚类')
}

// 运行情感可视化脚本
const runEmotionScript = () => {
  runScript(emotionCommand, '情感可视化')
}

// 运行词云图脚本
const runWordcloudScript = () => {
  // 如果选择了特定诗人，添加到命令中
  let command = wordcloudCommand
  if (selectedPoet.value && selectedPoet.value !== '全部诗人') {
    command = `${wordcloudCommand} --poet "${selectedPoet.value}"`
  }
  runScript(command, '词云图')
}

// 关闭输出窗口
const closeOutput = () => {
  showOutput.value = false
}

// 关闭服务器帮助窗口
const closeServerHelp = () => {
  showServerHelp.value = false
}

// 重连到服务器
const reconnectToServer = () => {
  reconnectAttempts = 0 // 重置重连尝试次数
  connectToServer()
}

// 显示命令的相关代码
const showCommandModal = ref(false)
const currentCommand = ref('')
const copySuccess = ref(false)

const showTopicCommand = () => {
  currentCommand.value = topicCommand
  showCommandModal.value = true
  copySuccess.value = false
}

const showEmotionCommand = () => {
  currentCommand.value = emotionCommand
  showCommandModal.value = true
  copySuccess.value = false
}

const showWordcloudCommand = () => {
  // 如果选择了特定诗人，添加到命令中
  let command = wordcloudCommand
  if (selectedPoet.value && selectedPoet.value !== '全部诗人') {
    command = `${wordcloudCommand} --poet "${selectedPoet.value}"`
  }
  currentCommand.value = command
  showCommandModal.value = true
  copySuccess.value = false
}

const copyCommand = () => {
  navigator.clipboard.writeText(currentCommand.value).then(
    () => {
      copySuccess.value = true
      setTimeout(() => {
        copySuccess.value = false
      }, 2000)
    },
    (err) => {
      console.error('复制失败: ', err)
    }
  )
}

const closeModal = () => {
  showCommandModal.value = false
}

const openTerminal = () => {
  // 尝试打开默认终端
  if (navigator.platform.indexOf('Win') > -1) {
    // Windows
    window.open('cmd://')
  } else if (navigator.platform.indexOf('Mac') > -1) {
    // MacOS
    window.open('terminal://')
  } else {
    // Linux 或其他系统
    alert('请手动打开终端并粘贴命令执行')
  }
}

// 终止特定命令
const terminateScript = (scriptId: string) => {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(
      JSON.stringify({
        action: 'terminate',
        scriptId: scriptId
      })
    )
  }
}
</script>

<template>
  <div class="container">
    <div class="dataSetBox">
      数据集
      <select id="dataSet" name="dataSet" @change="handlePoetChange">
        <option value="0">全部诗人</option>
        <option v-for="poet in poetList" :key="poet.id" :value="poet.id">{{ poet.name }}</option>
      </select>
    </div>
    <div class="riverThemeBox">
      河流图配色
      <input
        type="radio"
        value="topic"
        name="riverTheme"
        v-model="selectedType"
        checked
        style="margin-left: 10px"
      />主题 <input type="radio" value="emotion" name="riverTheme" v-model="selectedType" />情感
      <input type="radio" value="wordcloud" name="riverTheme" v-model="selectedType" />词云图
    </div>

    <div class="buttonContainer">
      <!-- 根据选择的类型显示对应的按钮 -->
      <div v-if="selectedType === 'topic'">
        <button class="actionButton" @click="runTopicScript" :disabled="!isConnected">
          <span v-if="isConnected">
            {{ isTopicScriptRunning ? '正在运行...' : '运行主题聚类' }}
          </span>
          <span v-else>未连接</span>
        </button>
        <button class="helpButton" @click="showTopicCommand" title="查看主题聚类命令">?</button>
      </div>

      <div v-if="selectedType === 'emotion'">
        <button class="actionButton" @click="runEmotionScript" :disabled="!isConnected">
          <span v-if="isConnected">
            {{ isEmotionScriptRunning ? '正在运行...' : '运行情感可视化' }}
          </span>
          <span v-else>未连接</span>
        </button>
        <button class="helpButton" @click="showEmotionCommand" title="查看情感可视化命令">?</button>
      </div>

      <div v-if="selectedType === 'wordcloud'">
        <button class="actionButton" @click="runWordcloudScript" :disabled="!isConnected">
          <span v-if="isConnected">
            {{ isWordcloudScriptRunning ? '正在运行...' : '生成词云图' }}
          </span>
          <span v-else>未连接</span>
        </button>
        <button class="helpButton" @click="showWordcloudCommand" title="查看词云图命令">?</button>
      </div>

      <div class="connectionStatus" :class="{ connected: isConnected, disconnected: !isConnected }">
        {{ isConnected ? '已连接' : '未连接' }}
      </div>
    </div>

    <!-- 运行中的任务列表 -->
    <div v-if="runningScripts.size > 0" class="taskListContainer">
      <h4>正在运行的任务</h4>
      <div class="taskList">
        <div v-for="[scriptId] in runningScripts" :key="scriptId" class="taskItem">
          <span class="taskName">{{ scriptId }}</span>
          <button class="terminateButton" @click="terminateScript(scriptId)" title="终止任务">
            ✕
          </button>
        </div>
      </div>
    </div>

    <!-- 运行输出窗口 -->
    <div v-if="showOutput" class="modalOverlay" @click="closeOutput">
      <div class="modalContent outputWindow" @click.stop>
        <h3>{{ currentScriptId }}脚本输出</h3>
        <div class="outputDisplay">
          <pre>{{ outputLog }}</pre>
        </div>
        <div class="modalButtons">
          <button class="closeButton" @click="closeOutput">关闭</button>
        </div>
      </div>
    </div>

    <!-- 服务器帮助弹窗 -->
    <div v-if="showServerHelp" class="modalOverlay" @click="closeServerHelp">
      <div class="modalContent setupHelp" @click.stop>
        <h3>需要启动Python服务器</h3>
        <p>要直接运行Python脚本，需要在本地启动一个Python WebSocket服务器。</p>
        <ol class="instructionList">
          <li>点击下方按钮下载服务器脚本</li>
          <li>在终端中运行: <code>python python_socket_server.py</code></li>
          <li>服务器启动后，刷新此页面</li>
        </ol>

        <div class="actionsContainer">
          <button class="reconnectButton" @click="reconnectToServer">重新连接</button>
          <button class="closeButton" @click="closeServerHelp">关闭</button>
        </div>

        <div class="noteBox">
          <p>
            <strong>注意：</strong>
            服务器运行时需保持终端窗口开启。此方法可以安全直接地在本地执行Python脚本。
          </p>
        </div>
      </div>
    </div>

    <!-- 命令显示弹窗 -->
    <div v-if="showCommandModal" class="modalOverlay" @click="closeModal">
      <div class="modalContent" @click.stop>
        <h3>命令详情</h3>
        <div class="commandDisplay">
          <pre>{{ currentCommand }}</pre>
        </div>
        <div class="modalButtons">
          <button class="copyButton" @click="copyCommand">
            {{ copySuccess ? '复制成功' : '复制命令' }}
          </button>
          <button class="terminalButton" @click="openTerminal">打开终端</button>
          <button class="closeButton" @click="closeModal">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped></style>
