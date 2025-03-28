<template>
  <fiveFlower v-if="props.data.data.length === 5" :data="props.data" />
  <fourFlower v-else-if="props.data.data.length === 4" :data="props.data" />
  <threeFlower v-else :data="props.data" />
</template>

<script setup lang="ts">
import fiveFlower from './children/FiveFlower.vue';
import fourFlower from './children/FourFlower.vue';
import threeFlower from './children/ThreeFlower.vue';
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
