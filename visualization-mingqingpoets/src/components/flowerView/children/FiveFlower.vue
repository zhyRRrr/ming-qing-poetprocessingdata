<script setup lang="ts">
import { ref, onMounted, defineProps, PropType, computed } from 'vue';
import { Flower } from '@/types/flower.js';

const props = defineProps({
  data: {
    type: Object as PropType<Flower>, // 修正语法问题
    required: true, // 确保是必传值
  },
});

onMounted(() => {
  // console.log('父组件', props.data);
});

interface Point {
  x: number
  y: number
}

// 旋转点的函数
const rotatePoint = (x: number, y: number, angle: number): Point => {
  const radians = angle * (Math.PI / 180)
  const xNew = x * Math.cos(radians) - y * Math.sin(radians)
  const yNew = x * Math.sin(radians) + y * Math.cos(radians)
  return { x: xNew, y: yNew }
}

// 定义各个点的 ref 类型
const point1 = ref<Point>({ x: 2, y: 4 })
const point1ControlRight = ref<Point>({ x: 5, y: 8 })
const point2ControlLeft = ref<Point>({ x: 5, y: 12 })
const point2 = ref<Point>({ x: 10, y: 12 })

const point2ControlRight = ref<Point>({ x: 11, y: 12 })
const point3ControlLeft = ref<Point>({ x: 12, y: 11 })
const point3 = ref<Point>({ x: 12, y: 10 })

const point3ControlRight = ref<Point>({ x: 12, y: 6 })
const point4ControlLeft = ref<Point>({ x: 8, y: 5 })
const point4 = ref<Point>({ x: 4, y: 2 })

const point4ControlRight = ref<Point>({ x: 2.93, y: 0.915 })
const point5ControlLeft = ref<Point>({ x: 3.069, y: 0.035 })

// 计算路径
const path = computed<string>(() => {
  let s = `M ${point1.value.x} ${point1.value.y}
          C ${point1ControlRight.value.x} ${point1ControlRight.value.y} ${point2ControlLeft.value.x} ${point2ControlLeft.value.y} ${point2.value.x} ${point2.value.y}
          C ${point2ControlRight.value.x} ${point2ControlRight.value.y} ${point3ControlLeft.value.x} ${point3ControlLeft.value.y} ${point3.value.x} ${point3.value.y}
          C ${point3ControlRight.value.x} ${point3ControlRight.value.y} ${point4ControlLeft.value.x} ${point4ControlLeft.value.y} ${point4.value.x} ${point4.value.y}
          C ${point4ControlRight.value.x} ${point4ControlRight.value.y} ${point5ControlLeft.value.x} ${point5ControlLeft.value.y} `

  for (let i = 1; i <= 4; ++i) {
    const rotate = -72 * i

    // 旋转后的点
    const rotatedPoint1 = rotatePoint(point1.value.x, point1.value.y, rotate)
    const rotatedPoint1ControlRight = rotatePoint(
      point1ControlRight.value.x,
      point1ControlRight.value.y,
      rotate
    )
    const rotatedPoint2ControlLeft = rotatePoint(
      point2ControlLeft.value.x,
      point2ControlLeft.value.y,
      rotate
    )
    const rotatedPoint2 = rotatePoint(point2.value.x, point2.value.y, rotate)

    const rotatedPoint2ControlRight = rotatePoint(
      point2ControlRight.value.x,
      point2ControlRight.value.y,
      rotate
    )
    const rotatedPoint3ControlLeft = rotatePoint(
      point3ControlLeft.value.x,
      point3ControlLeft.value.y,
      rotate
    )
    const rotatedPoint3 = rotatePoint(point3.value.x, point3.value.y, rotate)

    const rotatedPoint3ControlRight = rotatePoint(
      point3ControlRight.value.x,
      point3ControlRight.value.y,
      rotate
    )
    const rotatedPoint4ControlLeft = rotatePoint(
      point4ControlLeft.value.x,
      point4ControlLeft.value.y,
      rotate
    )
    const rotatedPoint4 = rotatePoint(point4.value.x, point4.value.y, rotate)

    const rotatedPoint4ControlRight = rotatePoint(
      point4ControlRight.value.x,
      point4ControlRight.value.y,
      rotate
    )
    const rotatedPoint5ControlLeft = rotatePoint(
      point5ControlLeft.value.x,
      point5ControlLeft.value.y,
      rotate
    )

    s += `${rotatedPoint1.x} ${rotatedPoint1.y}
          C ${rotatedPoint1ControlRight.x} ${rotatedPoint1ControlRight.y} ${rotatedPoint2ControlLeft.x} ${rotatedPoint2ControlLeft.y} ${rotatedPoint2.x} ${rotatedPoint2.y}
          C ${rotatedPoint2ControlRight.x} ${rotatedPoint2ControlRight.y} ${rotatedPoint3ControlLeft.x} ${rotatedPoint3ControlLeft.y} ${rotatedPoint3.x} ${rotatedPoint3.y}
          C ${rotatedPoint3ControlRight.x} ${rotatedPoint3ControlRight.y} ${rotatedPoint4ControlLeft.x} ${rotatedPoint4ControlLeft.y} ${rotatedPoint4.x} ${rotatedPoint4.y}
          C ${rotatedPoint4ControlRight.x} ${rotatedPoint4ControlRight.y} ${rotatedPoint5ControlLeft.x} ${rotatedPoint5ControlLeft.y} `
  }

  s += `${point1.value.x} ${point1.value.y}`

  return s
})


</script>

<template>
  <svg
    width="100"
    height="100"
    viewBox="0 0 100 100"
    :style="{
      transform: `translate(-50px, -50px) scale(${props.data.scale}) rotate(${props.data.rotate}deg)`,
      transformOrigin: 'center center',
      border: `${props.data.select === false ? 0 : 1}px solid #000000`
    }"
  >
    <defs>
<!--      喜-->
      <radialGradient id="RadialGradient1" cx="0.55" cy="0.1" r="0.6">
        <stop offset="0%" stop-color="#87000b" />
        <stop offset="100%" stop-color="# " />
      </radialGradient>
<!--      哀-->
      <radialGradient id="RadialGradient2" cx="0.55" cy="0.1" r="0.6">
        <stop offset="0%" stop-color="#7B8ED6" />
        <stop offset="100%" stop-color="#DADEEF" />
      </radialGradient>
<!--      乐-->
      <radialGradient id="RadialGradient3" cx="0.55" cy="0.1" r="0.6">
        <stop offset="0%" stop-color="#dc9766" />
        <stop offset="100%" stop-color="#F3D7C3" />
      </radialGradient>
<!--      怒/豪-->
      <radialGradient id="RadialGradient4" cx="0.55" cy="0.1" r="0.6">
        <stop offset="0%" stop-color="#cc7265" />
        <stop offset="100%" stop-color="#C6A6A1" />
      </radialGradient>
<!--      思-->
      <radialGradient id="RadialGradient5" cx="0.55" cy="0.1" r="0.6">
        <stop offset="0%" stop-color="#5e7d5a" />
        <stop offset="100%" stop-color="#BFEFB8" />
      </radialGradient>


      <filter id="dropShadow" x="0%" y="0%" width="10%" height="10%">
        <feOffset dx="2" dy="2" result="offsetblur"/>
        <feGaussianBlur in="offsetblur" stdDeviation="2" result="blur"/>
        <feMerge>
          <feMergeNode in="blur"/>
          <feMergeNode in="SourceGraphic"/>
        </feMerge>
      </filter>

    </defs>
<!--    按值来排序-->
    <g transform="translate(50, 50) rotate(20, 0, 0)">
      <path
        d="M 0,0
           C 20,20 20,43 0,50
           C -20,43 -20,20 0,0"
        fill="url(#RadialGradient1)"
        opacity="1"
      />
    </g>

    <g transform="translate(50, 50) rotate(92, 0, 0)">
      <path
        d="M 0,0
           C 20,20 20,43 0,50
           C -20,43 -20,20 0,0"
        fill="url(#RadialGradient2)"
        opacity="1"
      />
    </g>

    <g transform="translate(50, 50) rotate(164, 0, 0)">
      <path
        d="M 0,0
           C 20,20 20,43 0,50
           C -20,43 -20,20 0,0"
        fill="url(#RadialGradient3)"
        opacity="1"
      />
    </g>

    <g transform="translate(50, 50) rotate(236, 0, 0)">
      <path
        d="M 0,0
           C 20,20 20,43 0,50
           C -20,43 -20,20 0,0"
        fill="url(#RadialGradient4)"
        opacity="1"
      />
    </g>

    <g transform="translate(50, 50) rotate(308, 0, 0)">
      <path
        d="M 0,0
           C 20,20 20,43 0,50
           C -20,43 -20,20 0,0"
        fill="url(#RadialGradient5)"
        opacity="1"
      />
    </g>

    <g transform="translate(50, 50) rotate(-10, 0, 0)">
      <path :d="path" fill="white" />
    </g>

<!--    <g transform="translate(55, 55) rotate(30, 0, 0)">-->
<!--      <path-->
<!--        d="M 0 0 C 26 -4 22 -43 0 -50 C -22 -43 -26 -4 0 0"-->
<!--        fill="url(#RadialGradient2)"-->
<!--        opacity="1"-->
<!--        filter="url(#dropShadow)"-->
<!--      />-->
<!--    </g>-->

<!--    <g transform="translate(45, 55) rotate(-30, 0, 0)">-->
<!--      <path-->
<!--        d="M 0 0 C 26 -4 22 -43 0 -50 C -22 -43 -26 -4 0 0"-->
<!--        fill="url(#RadialGradient3)"-->
<!--        opacity="1"-->
<!--        filter="url(#dropShadow)"-->
<!--      />-->
<!--    </g>-->

<!--    <g transform="translate(48, 60) rotate(-15, 0, 0)">-->
<!--      <path-->
<!--        d="M 0 0 C 26 -4 20 -38 0 -45 C -20 -38 -26 -4 0 0"-->
<!--        fill="url(#RadialGradient4)"-->
<!--        opacity="1"-->
<!--        filter="url(#dropShadow)"-->
<!--      />-->
<!--    </g>-->

<!--    <g transform="translate(52, 60) rotate(15, 0, 0)">-->
<!--      <path-->
<!--        d="M 0 0 C 26 -4 20 -38 0 -45 C -20 -38 -26 -4 0 0"-->
<!--        fill="url(#RadialGradient5)"-->
<!--        opacity="1"-->
<!--        filter="url(#dropShadow)"-->
<!--      />-->
<!--    </g>-->
  </svg>
</template>

<style scoped>
.petal-gradient {
  background: radial-gradient(circle at center, #ffc0cb, #ff69b4); /* 这里示例从浅粉色到深粉色的渐变，可按需修改颜色 */
}
</style>