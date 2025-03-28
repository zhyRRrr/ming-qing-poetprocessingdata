<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import FlowerView from '@/components/flowerView/FlowerView.vue'

const width = ref(1560)
const height = ref(770)
const familyPoets = ref([])
const noFamilyPoets = ref([])
const canvas = ref(null)
const x = ref([])
const y = ref([])
const mainInfo = ref(null)
const PI = Math.acos(-1)
const items = ref([])

let base_x = null

const fetchData = async () => {
  const [response1, response2, response3] = await Promise.all([
    axios.get('http://localhost:8080/plumBlossom/getFamilyPoets'),
    axios.get('http://localhost:8080/plumBlossom/getNoFamilyPoets'),
    axios.get('http://localhost:8080/plumBlossom/getMainInfo')
  ])
  familyPoets.value = response1.data.data
  noFamilyPoets.value = response2.data.data
  mainInfo.value = response3.data.data
}

// 平滑贝塞尔曲线函数
const bezierCurve = (p0, p1, p2, p3, inserted) => {
  const points = []
  for (let t = 0; t <= 1; t += 1 / (inserted + 1)) {
    const x =
      p0[0] * Math.pow(1 - t, 3) +
      3 * p1[0] * t * Math.pow(1 - t, 2) +
      3 * p2[0] * Math.pow(t, 2) * (1 - t) +
      p3[0] * Math.pow(t, 3)
    const y =
      p0[1] * Math.pow(1 - t, 3) +
      3 * p1[1] * t * Math.pow(1 - t, 2) +
      3 * p2[1] * Math.pow(t, 2) * (1 - t) +
      p3[1] * Math.pow(t, 3)
    points.push([x, y])
  }
  return points
}

// 数据平滑函数
const smoothingBezier = (x, y, k = 0.5, inserted = 10) => {
  // 生成原始数据折线的中点集
  const midPoints = x.value
    .map((_, i) => {
      if (i === 0) return null
      return {
        start: [x.value[i - 1], y.value[i - 1]],
        end: [x.value[i], y.value[i]],
        mid: [(x.value[i] + x.value[i - 1]) / 2, (y.value[i] + y.value[i - 1]) / 2]
      }
    })
    .filter(Boolean)

  // console.log(midPoints)

  midPoints.push({
    start: [x.value[x.value.length - 1], y.value[y.value.length - 1]],
    end: [x.value[0], y.value[0]],
    mid: [
      (x.value[0] + x.value[x.value.length - 1]) / 2,
      (y.value[0] + y.value[y.value.length - 1]) / 2
    ]
  })

  // 找出中点连线及其分割点
  const controlPoints = ref([])
  for (let i = 0; i < midPoints.length; i++) {
    const next = (i + 1) % midPoints.length

    const d0 = Math.sqrt(
      Math.pow(midPoints[i].start[0] - midPoints[i].end[0], 2) +
      Math.pow(midPoints[i].start[1] - midPoints[i].end[1], 2)
    )
    const d1 = Math.sqrt(
      Math.pow(midPoints[next].start[0] - midPoints[next].end[0], 2) +
      Math.pow(midPoints[next].start[1] - midPoints[next].end[1], 2)
    )

    const kSplit = d0 / (d0 + d1)

    const split = [
      midPoints[i].mid[0] + (midPoints[next].mid[0] - midPoints[i].mid[0]) * kSplit,
      midPoints[i].mid[1] + (midPoints[next].mid[1] - midPoints[i].mid[1]) * kSplit
    ]

    const dx = midPoints[i].end[0] - split[0]
    const dy = midPoints[i].end[1] - split[1]

    const s = [midPoints[i].mid[0] + dx, midPoints[i].mid[1] + dy]
    const e = [midPoints[next].mid[0] + dx, midPoints[next].mid[1] + dy]

    const cp0 = [s[0] + (midPoints[i].end[0] - s[0]) * k, s[1] + (midPoints[i].end[1] - s[1]) * k]
    const cp1 = [e[0] + (midPoints[i].end[0] - e[0]) * k, e[1] + (midPoints[i].end[1] - e[1]) * k]

    if (controlPoints.value.length > 0) {
      // console.log("添加元素", controlPoints.value)
      controlPoints.value[i].splice(2, 0, cp0)
    } else {
      controlPoints.value.push([midPoints[i].start, cp0, midPoints[i].end])
    }

    if (i < midPoints.length - 1) {
      controlPoints.value.push([midPoints[i + 1].start, cp1, midPoints[i + 1].end])
    } else {
      controlPoints.value[0].splice(1, 0, cp1)
    }
  }
  // console.log(controlPoints)

  return controlPoints.value.flatMap((control) =>
    bezierCurve(control[0], control[1], control[2], control[3], inserted)
  )
}

const drawTree = () => {
  const ctx = canvas.value.getContext('2d')
  ctx.fillStyle = 'red'
  x.value.forEach((xVal, i) => ctx.fillRect(xVal - 3, y.value[i] - 3, 6, 6))

  const points = smoothingBezier(x, y, 0.5, 10)
  ctx.beginPath()
  ctx.moveTo(points[0][0], points[0][1])
  points.forEach(([px, py]) => ctx.lineTo(px, py))
  ctx.closePath()
  // ctx.fill()  // 开启填充
  ctx.stroke() // 开启边框线
}

const solveEquationIntegerBinary = (k3, k4, b3, b4, c, left, right) => {
  while (left < right) {
    let mid = Math.floor((left + right) / 2)
    let value = mid + Math.cos(k4 * mid + b4) * (k3 * mid + b3)
    if (value < c) {
      left = mid + 1
    } else {
      right = mid
    }
  }
  return left
}


const pointArr = []
const pointArr_1 = []


// 200， 130， 80， 50
const calculatePoints = async () => {
  const spanYear = mainInfo.value?.endYear - mainInfo.value?.startYear
  base_x = 1100 / spanYear
  console.log("跨越年份:",spanYear, base_x)

  getMainBranch(0, 200, 70,  200, 350, 45)

  if (familyPoets.value) {
    const spanYear = familyPoets.value?.familyMaxBirthday - mainInfo.value?.startYear
    const startX = 200
    const startY = 350
    const endX = startX + 260 + base_x * spanYear
    const endY = 150
    const fx = startX + 130
    const fy = startY + (endY - startY) * 4 / 5
    getChildBranch(startX, startY, fx, fy, endX, endY, 30, 5, familyPoets)
  }

  for (let i = pointArr_1.length - 1; i >= 0; i--) pointArr.push(pointArr_1[i])

  x.value.push(pointArr[0].x)
  y.value.push(pointArr[0].y)
  for (let i = 1; i < pointArr.length; i++) {
    if (pointArr[i].x !== x.value[x.value.length - 1] || pointArr[i].y !== y.value[y.value.length - 1]) {
      x.value.push(pointArr[i].x)
      y.value.push(pointArr[i].y)
    }
  }
}

// 构建主干
const getMainBranch = (startX, startY, startWidth, endX, endY, endWidth) => {

  // 用一次函数控制点的轨迹 y = k * x + b
  const spanX = endX - startX
  const spanY = endY - startY
  const fx = startX + spanX / 2
  const fy = startY + spanY * 3 / 4
  // 一段轨迹
  const k1 = (fy - startY) / (fx - startX)
  const b1 = startY - k1 * startX
  // 二段轨迹
  const k2 = (endY - fy) / (endX - fx)
  const b2 = endY - k2 * endX
  const getY = (x) => {
    return x <= fx
      ? k1 * x + b1
      : k2 * x + b2
  }

  // 通过一次函数更改树干的宽度
  const k3 = (endWidth - startWidth) / spanX
  const b3 = startWidth - k3 * startX
  const getWidth = (x) => {
    return k3 * x + b3
  }

  // 获取对应点
  const getMappingPoint = (x) => {
    const width = getWidth(x)
    const k = -1 / k1
    if (x < fx){
      const dx = Math.sqrt( width * width / (1 + k * k))
      return {x: x - dx, y: getY(x) - dx * k}
    }else{
      return {x: x,y: getY(x) + getWidth(x)}
    }
  }

  // 开始构建主干
  for (let i = startX; i <= endX; i += 50) {
    pointArr.push({x: i, y: getY(i)})
    pointArr_1.push(getMappingPoint(i))
  }
}

// 递归编写分支
const getChildBranch = (startX, startY, fx, fy, endX, endY, startWidth, endWidth, info, sign) => {
  // 还是通过两段设置
  const k1 = (fy - startY) / (fx - startX)
  const b1 = startY - k1 * startX
  const k2 = (endY - fy) / (endX - fx)
  const b2 = fy - k2 * fx
  const getY = (x) => {
    return x < fx
      ? k1 * x + b1
      : k2 * x + b2
  }

  const k3 = (endWidth - startWidth) / (endX - startX)
  const b3 = startWidth - k3 * startX
  const getWidth = (x) => {
    return k3 * x + b3
  }

  // 获取对应点
  const getMappingPoint = (x) => {
    const width = getWidth(x)
    console.log(width)
    const k = -1 / k1
    if (x < fx){
      const dx = Math.sqrt(width * width / (1 + k * k))
      return {x: x + dx, y: getY(x) + dx * k}
    }else {
      return {x: x, y: getY(x) + getWidth(x)}
    }
  }

  const arr = []
  pointArr.push({x: startX, y: startY})
  arr.push(getMappingPoint(startX))

  pointArr.push({x: (startX + fx) / 2, y: (startY + fy) / 2})
  arr.push(getMappingPoint((startX + fx) / 2))


  pointArr.push({x: fx, y: fy})
  arr.push(getMappingPoint(fx))

  pointArr.push({x: endX, y: endY})
  arr.push(getMappingPoint(endX))

  getChildBranch(fx,fy,fx + 80, )


  for (let i = arr.length - 1; i >= 0; i--) pointArr.push(arr[i])
}

// 地域分支
const getAreaBranch = () => {

}

onMounted(() => {
  fetchData().then(() => {
    console.log(familyPoets.value)
    console.log(noFamilyPoets.value)
    console.log(mainInfo.value)
    calculatePoints().then(() => {
      drawTree()
    })
  })
})
</script>

<template>
  <div class="TreeChart">
    <div class="backgroundContainer"></div>
    <canvas ref="canvas" :width="width" :height="height"></canvas>
    <flower-view
      v-for="(item, index) in items"
      :key="index"
      style="position: absolute; scale: 25%"
      :style="{ left: item.left + 'px', top: item.top + 'px' }"
    />
  </div>
</template>

<style scoped>
.TreeChart {
  width: 1560px;
  height: 770px;
  /* background-color: blue; */
}
.backgroundContainer {
  width: 1100px;
  height: 770px;
  position: absolute;
  left: 460px;
  background-color: blue;
}

canvas {
  border: 0;
  position: absolute;
}
</style>
