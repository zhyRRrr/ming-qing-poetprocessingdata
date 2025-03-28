<script setup>
import ChinaNavigate from '@/views/ChinaNavigate.vue'
// import ListView from '@/views/ListView.vue'
import ScatterDiagram from '@/views/ScatterDiagram.vue'

import TreeTrunk from '@/views/TreeTrunk.vue'
import ThreeFlower from '@/components/flowerView/children/ThreeFlower.vue'
import FourFlower from '@/components/flowerView/children/FourFlower.vue'
import FiveFlower from '@/components/flowerView/children/FiveFlower.vue'
import riverChart from '@/views/RiverChart.vue'
import ControllerView from '@/views/ControllerView.vue'
import Map from '@/views/map.vue'
import WordCloudView from '@/views/WordCloudView.vue'
import { ref, watch } from 'vue'

// 定义ControllerView组件引用和选中的诗人
const controllerViewRef = ref(null)
const selectedPoet = ref('全部诗人')

// 添加watch以在控制台输出诗人变化，便于调试
watch(selectedPoet, (newPoet, oldPoet) => {
  console.log(`App.vue - 诗人从 "${oldPoet}" 变更为 "${newPoet}"`)
})

// 监听ControllerView的诗人选择变化
function onControllerMounted() {
  if (controllerViewRef.value) {
    // 由于ControllerView组件中defineExpose了selectedPoet变量，我们可以直接访问
    selectedPoet.value = controllerViewRef.value.selectedPoet
    console.log('App.vue - 控制器组件挂载完成，当前诗人:', selectedPoet.value)

    // 设置更直接的代理方式，确保实时更新
    Object.defineProperty(controllerViewRef.value, 'selectedPoet', {
      get: () => selectedPoet.value,
      set: (newValue) => {
        console.log('App.vue - 通过代理设置诗人:', newValue)
        selectedPoet.value = newValue
      }
    })

    // 额外监听全局事件，以防其他方式的更新
    window.addEventListener('poet-changed', (event) => {
      console.log('App.vue - 接收到全局诗人变化事件:', event.detail.poet)
      selectedPoet.value = event.detail.poet
    })
  }
}
</script>

<template>
  <div id="main" style="position: absolute">
    <controller-view
      ref="controllerViewRef"
      @mounted="onControllerMounted"
      style="position: absolute; left: 0; top: 0; border: 1px solid black"
    ></controller-view>
    <!-- <ChinaNavigate style="position: absolute; top: 0; left: 399px; border: 1px solid black;"></ChinaNavigate> -->
    <Map style="position: absolute; top: 0; left: 399px; border: 1px solid black"></Map>
    <TreeTrunk
      style="position: absolute; rotate: -90deg; top: 280px; left: 280px; border: 1px solid black"
    ></TreeTrunk>
    <riverChart
      style="position: absolute; bottom: 0; right: 1px; border: 1px solid black"
    ></riverChart>

    <!-- 词云图组件 -->
    <WordCloudView
      :selected-poet="selectedPoet"
      style="
        position: absolute;
        top: 0;
        left: 1100px;
        width: 400px;
        height: 560px;
        border: 1px solid black;
      "
    ></WordCloudView>

    <!--    transform: rotate(-90deg);-->
    <!--    <tree-view style="position: absolute; top: 0; left: 0;"></tree-view>-->
    <!-- <TreeView style="position: absolute; bottom: 0"></TreeView> -->
    <!--    <WordCloud style="position: absolute; top: 0; left: 1830px;"></WordCloud>-->
    <!--    <ScatterDiagram style="position: absolute; bottom: 0; left: 770px"></ScatterDiagram>-->

    <!--    <three-flower style="position: absolute; left: 20px; top: 20px;" :data="{select: true}"></three-flower>-->
    <!--    <four-flower style="position: absolute; left: 0; top: 0;" :data="{select: true}"></four-flower>-->
  </div>
</template>

<style scoped>
#main {
  background-image: url('./assets/honeycombCracks_1.jpg');
  position: absolute;
  left: 0;
  top: 0;
  width: 2560px;
  height: 1440px;
  overflow: hidden;
}
</style>
