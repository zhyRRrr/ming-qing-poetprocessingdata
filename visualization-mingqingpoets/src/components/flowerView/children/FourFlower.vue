<script setup lang="ts">
import { onMounted, defineProps, PropType } from 'vue';
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
</script>

<template>
  <!--  style="border:1px black solid"-->
  <svg
    width="74"
    height="60"
    viewBox="0 0 74 60"
    :style="{
      transform: `translate(-37px, -30px) scale(${props.data.scale}) rotate(${props.data.rotate}deg)`,
      // rotate(${Math.floor(Math.random() * 360)}deg
      transformOrigin: 'center center',
      border: `${props.data.select === false ? 0 : 1}px solid #000000`
    }"
  >
    <defs>
      <radialGradient id="RadialGradient1" cx="0.55" cy="0.1" r="0.6">
        <stop offset="0%" stop-color="#FEA9B0" />
        <stop offset="100%" stop-color="#F9C6CA" />
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
        <stop offset="100%" stop-color="#FDC5BD" />
      </radialGradient>
      <!--      思-->
      <radialGradient id="RadialGradient5" cx="0.55" cy="0.1" r="0.6">
        <stop offset="0%" stop-color="#5e7d5a" />
        <stop offset="100%" stop-color="#BFEFB8" />
      </radialGradient>


      <filter id="dropShadow" x="-50%" y="-50%" width="200%" height="200%">
        <feOffset dx="4" dy="4" result="offsetblur"/>
        <feGaussianBlur in="offsetblur" stdDeviation="4" result="blur"/>
        <feMerge>
          <feMergeNode in="blur"/>
          <feMergeNode in="SourceGraphic"/>
        </feMerge>
      </filter>

    </defs>
    <!--    按值来排序-->
    <g transform="translate(37, 50) rotate(0, 0, 0)">
      <path
        d="M 0 0 C 30 -3 23 -45 0 -50 C -23 -45 -30 -3 0 0"
        fill="red"
        opacity="1"
      />
    </g>

    <g transform="translate(41, 55) rotate(33, 0, 0)">
      <path
        d="M 0 0 C 28 -4 22 -43 0 -50 C -22 -43 -28 -4 0 0"
        fill="url(#RadialGradient2)"
        opacity="1"
      />
    </g>

    <g transform="translate(33, 55) rotate(-33, 0, 0)">
      <path
        d="M 0 0 C 28 -4 22 -43 0 -50 C -22 -43 -28 -4 0 0"
        fill="url(#RadialGradient3)"
        opacity="1"
      />
    </g>

    <g transform="translate(37, 60) rotate(0, 0, 0)">
      <path
        d="M 0 0 C 16 -1 33 -36 0 -40 C -33 -36 -16 -1 0 0"
        fill="url(#RadialGradient4)"
        opacity="1"
        filter="url(#dropShadow)"
      />
    </g>
  </svg>
</template>

<style scoped>
</style>
