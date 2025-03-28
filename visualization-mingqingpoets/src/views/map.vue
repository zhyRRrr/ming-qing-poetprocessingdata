<script setup>
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'
import chinaMap from '../assets/json/china.json'
//import hebingImage from '../assets/hebing.png' // 导入合并图片
import honeycombImage from '../assets/honeycombCracks_1.jpg' // 导入蜂窝纹理图片
import mapSvg from '../assets/map.svg' // 导入南海诸岛 SVG
import qingdynastymapImage from '../assets/qingdynastymap.png' // 导入清朝地图图片
import taiwanImage from '../assets/taiwan.png' // 导入台湾图片
import hainanImage from '../assets/hainan.png' // 导入海南图片
import {
  poetInfo as zengYiInfo,
  pointsData as zengYiPoints,
  routesData as zengYiRoutes
} from '../assets/data/mapData.js'
import {
  poetInfo as zongWanInfo,
  pointsData as zongWanPoints,
  routesData as zongWanRoutes
} from '../assets/data/mapDataZongWan.js'
import {
  poetInfo as zuoXijiaInfo,
  pointsData as zuoXijiaPoints,
  routesData as zuoXijiaRoutes
} from '../assets/data/mapDataZuoXijia.js'

let chart = ref()
let myChart = null
let selectedPoet = ref('1') // 默认显示曾懿的数据

// 保存图层引用，便于更新时清除
let imageLayersRefs = {
  qingdynastymap: null,
  patternImage: null,
  southSeaImage: null,
  taiwanImage: null,
  hainanImage: null
}

// 初始点和终点的信息
const pathEndpoints = {
  1: {
    // 曾懿
    startPoint: '四川成都',
    endPoint: '北京'
  },
  2: {
    // 宗婉
    startPoint: '江苏常熟',
    endPoint: '北京'
  },
  3: {
    // 左錫嘉
    startPoint: '常州',
    endPoint: '山西定襄'
  }
}

// 根据选择的诗人获取相应的数据
const getPoetData = (poetId) => {
  switch (poetId) {
    case '1':
      return {
        poetInfo: zengYiInfo,
        pointsData: zengYiPoints,
        routesData: zengYiRoutes,
        endpoints: pathEndpoints['1']
      }
    case '2':
      return {
        poetInfo: zongWanInfo,
        pointsData: zongWanPoints,
        routesData: zongWanRoutes,
        endpoints: pathEndpoints['2']
      }
    case '3':
      return {
        poetInfo: zuoXijiaInfo,
        pointsData: zuoXijiaPoints,
        routesData: zuoXijiaRoutes,
        endpoints: pathEndpoints['3']
      }
    default:
      return {
        poetInfo: zengYiInfo,
        pointsData: zengYiPoints,
        routesData: zengYiRoutes,
        endpoints: pathEndpoints['1']
      }
  }
}

onMounted(() => {
  // 获取ControllerView中的select元素
  const selectElement = document.getElementById('dataSet')
  if (selectElement) {
    // 初始值
    selectedPoet.value = selectElement.value

    // 添加change事件监听
    selectElement.addEventListener('change', (event) => {
      selectedPoet.value = event.target.value
      updateChart()
    })
  }

  // 初始化图表
  chartInit()
})

// 监听选择的诗人变化
watch(selectedPoet, () => {
  updateChart()
})

// 更新图表
function updateChart() {
  if (myChart) {
    // 清除之前的图层
    clearImageLayers()

    const data = getPoetData(selectedPoet.value)
    renderChart(data.poetInfo, data.pointsData, data.routesData, data.endpoints)
  }
}

function chartInit() {
  // 在这里，null变量被赋值为echarts实例
  myChart = echarts.init(chart.value)
  echarts.registerMap('china', chinaMap)

  // 初始化时显示默认诗人的数据
  const data = getPoetData(selectedPoet.value)
  renderChart(data.poetInfo, data.pointsData, data.routesData, data.endpoints)
}

// 清除图层的函数
function clearImageLayers() {
  if (!myChart) return

  const zr = myChart.getZr()

  // 清除清朝地图图层
  if (imageLayersRefs.qingdynastymap) {
    zr.remove(imageLayersRefs.qingdynastymap)
    imageLayersRefs.qingdynastymap = null
  }

  // 清除其他图层
  if (imageLayersRefs.patternImage) {
    zr.remove(imageLayersRefs.patternImage)
    imageLayersRefs.patternImage = null
  }

  if (imageLayersRefs.southSeaImage) {
    zr.remove(imageLayersRefs.southSeaImage)
    imageLayersRefs.southSeaImage = null
  }

  if (imageLayersRefs.taiwanImage) {
    zr.remove(imageLayersRefs.taiwanImage)
    imageLayersRefs.taiwanImage = null
  }

  if (imageLayersRefs.hainanImage) {
    zr.remove(imageLayersRefs.hainanImage)
    imageLayersRefs.hainanImage = null
  }
}

function renderChart(poetInfo, pointsData, routesData, endpoints) {
  // 处理点数据，为起点和终点设置特殊形状和颜色
  const processedPointsData = pointsData.map((point) => {
    if (point.name === endpoints.startPoint) {
      return {
        ...point,
        symbol: 'triangle', // 起点使用三角形
        symbolRotate: 0, // 三角形向上
        itemStyle: {
          color: '#FF0000' // 起点红色
        }
      }
    } else if (point.name === endpoints.endPoint) {
      return {
        ...point,
        symbol: 'triangle', // 终点使用三角形
        symbolRotate: 180, // 三角形向下
        itemStyle: {
          color: '#00FF00' // 终点绿色
        }
      }
    } else {
      return point
    }
  })

  // 指定图表的配置项和数据
  var option = {
    backgroundColor: 'rgba(250, 244, 225, 0.9)', // 设置背景颜色为米黄色
    // 添加提示框组件
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(0,0,0,0.7)',
      borderColor: '#000',
      textStyle: {
        color: '#fff'
      },
      formatter: function (params) {
        if (params.seriesType === 'effectScatter') {
          let pointType = ''
          if (params.name === endpoints.startPoint) {
            pointType = '(起点)'
          } else if (params.name === endpoints.endPoint) {
            pointType = '(终点)'
          }
          return `<div style="padding: 5px">
                    <div style="font-weight: bold; margin-bottom: 5px">${params.name}${pointType}</div>
                    <div>诗人：${poetInfo.name}</div>
                  </div>`
        } else {
          return `` // 路线不显示tooltip
        }
      }
    },
    geo: {
      type: 'map',
      map: 'china',
      label: {
        show: false, // 默认不显示标签
        color: '#fff',
        fontSize: 8
      },
      itemStyle: {
        areaColor: '#fff', // 设置地图区域为半透明灰色
        borderColor: '#bbb'
      },
      zoom: 1.2,
      top: 15, // 向上移动地图
      emphasis: {
        label: {
          show: true, // 鼠标悬浮时显示标签
          color: '#333'
        },
        itemStyle: {
          areaColor: '#1BC1AD'
        }
      }
    },
    series: [
      // 添加图片覆盖层
      {
        type: 'effectScatter',
        coordinateSystem: 'geo',
        label: {
          formatter: '{b}',
          position: 'right',
          show: false, // 默认不显示标签
          fontSize: 12, //
          fontWeight: 'bold',
          color: '#000'
        },
        emphasis: {
          label: {
            show: false, // 鼠标悬浮时不显示标签
            color: '#fff',
            backgroundColor: 'rgba(0,0,0,0.7)',
            padding: [4, 8],
            borderRadius: 4
          },
          itemStyle: {
            color: '#ff0'
          }
        },
        itemStyle: {
          shadowBlur: 10,
          shadowColor: '#f00',
          color: '#f00'
        },
        symbolSize: 5, // 缩小点的大小
        rippleEffect: {
          brushType: 'stroke',
          scale: 2.5 // 减小特效的大小
        },
        zlevel: 3, // 增加点的层级，确保在最上层
        data: processedPointsData
      },
      // 动态生成路线系列
      ...routesData.map((route) => ({
        type: 'lines',
        zlevel: 2, // 设置zlevel高于地图和图片，但低于点
        effect: {
          show: false, // 默认不显示箭头动画效果
          period: 5,
          symbol: 'arrow',
          symbolSize: 5,
          color: route.color
        },
        lineStyle: {
          color: route.color,
          width: 1.5,
          opacity: 0, // 完全透明，默认不可见
          curveness: route.curveness || 0.1
        },
        emphasis: {
          lineStyle: {
            opacity: 0.9 // 悬浮时增加透明度
          },
          effect: {
            show: true, // 悬浮时显示箭头效果
            opacity: 1 // 悬浮时箭头完全不透明
          }
        },
        data: route.data
      }))
    ]
  }

  // 使用刚指定的配置项和数据显示图表。
  myChart.setOption(option, true)

  const zr = myChart.getZr()

  // 添加覆盖图片（清朝地图）
  imageLayersRefs.qingdynastymap = new echarts.graphic.Image({
    style: {
      image: qingdynastymapImage,
      x: -20,
      y: -80,
      width: 750,
      height: 540,
      opacity: 0.15
    },
    zlevel: 1.2
  })
  zr.add(imageLayersRefs.qingdynastymap)

  // 预加载蜂窝纹理图片并确保图片加载完成后再进行后续操作
  const honeycombImg = new Image()
  honeycombImg.onload = function () {
    // 获取ZRender实例和Canvas上下文
    const canvas = document.createElement('canvas')
    canvas.width = myChart.getWidth()
    canvas.height = myChart.getHeight()
    const ctx = canvas.getContext('2d')

    // 绘制蜂窝纹理作为背景
    ctx.drawImage(honeycombImg, 0, 0, canvas.width, canvas.height)

    // 创建圆形遮罩（挖洞）
    ctx.globalCompositeOperation = 'destination-out'
    ctx.beginPath()
    ctx.arc(400, 300, 200, 0, Math.PI * 2)
    ctx.fill()

    // 重置合成模式
    ctx.globalCompositeOperation = 'source-over'

    // 添加圆形边框
    ctx.strokeStyle = 'rgb(162, 162, 162)'
    ctx.lineWidth = 2
    ctx.beginPath()
    ctx.arc(400, 300, 200, 0, Math.PI * 2)
    ctx.stroke()

    // 将Canvas作为图像添加到图表
    imageLayersRefs.patternImage = new echarts.graphic.Image({
      style: {
        image: canvas,
        x: 0,
        y: 0,
        width: canvas.width,
        height: canvas.height,
        opacity: 1
      },
      zlevel: 1.4 // 设置在地图和点之间的层级
    })

    zr.add(imageLayersRefs.patternImage)

    // 加载南海诸岛SVG并添加到图表
    const southSeaImage = new Image()
    southSeaImage.onload = function () {
      // 添加南海诸岛图片到圆形区域的左下角
      imageLayersRefs.southSeaImage = new echarts.graphic.Image({
        style: {
          image: southSeaImage,
          x: 60, // 圆形区域左下角位置
          y: 60,
          width: 96,
          height: 150,
          opacity: 1
        },
        zlevel: 10 // 设置最高层级确保可见
      })
      zr.add(imageLayersRefs.southSeaImage)

      // 添加台湾图片
      const taiwanImg = new Image()
      taiwanImg.onload = function () {
        imageLayersRefs.taiwanImage = new echarts.graphic.Image({
          style: {
            image: taiwanImg,
            x: 518, // 台湾在地图上的位置，可能需要调整
            y: 378, // 位置需要根据实际情况调整
            width: 28, // 宽度根据实际情况调整
            height: 57, // 高度根据实际情况调整
            opacity: 0.1
          },
          zlevel: 10 // 确保在高层级可见
        })
        zr.add(imageLayersRefs.taiwanImage)
      }
      taiwanImg.src = taiwanImage

      // 添加海南图片
      const hainanImg = new Image()
      hainanImg.onload = function () {
        imageLayersRefs.hainanImage = new echarts.graphic.Image({
          style: {
            image: hainanImg,
            x: 395, // 海南在地图上的位置，可能需要调整
            y: 455, // 位置需要根据实际情况调整
            width: 30, // 宽度根据实际情况调整
            height: 30, // 高度根据实际情况调整
            opacity: 0.1
          },
          zlevel: 10 // 确保在高层级可见
        })
        zr.add(imageLayersRefs.hainanImage)
      }
      hainanImg.src = hainanImage
    }
    southSeaImage.src = mapSvg
  }

  // 设置图片源，触发加载
  honeycombImg.src = honeycombImage

  // 添加鼠标事件，悬浮时高亮所有路径
  myChart.off('mouseover')
  myChart.on('mouseover', function (params) {
    if (
      params.componentType === 'series' &&
      (params.seriesType === 'effectScatter' || params.seriesType === 'lines')
    ) {
      // 高亮所有路径并显示箭头效果
      for (let i = 1; i <= routesData.length; i++) {
        myChart.dispatchAction({
          type: 'highlight',
          seriesIndex: i
        })
        // 修改 effect 为显示状态
        option.series[i].effect.show = true
        // 修改线条为可见状态
        option.series[i].lineStyle.opacity = 0.9
      }
      myChart.setOption(option)
    }
  })

  myChart.off('mouseout')
  myChart.on('mouseout', function (params) {
    if (
      params.componentType === 'series' &&
      (params.seriesType === 'effectScatter' || params.seriesType === 'lines')
    ) {
      // 取消高亮所有路径并隐藏箭头效果
      for (let i = 1; i <= routesData.length; i++) {
        myChart.dispatchAction({
          type: 'downplay',
          seriesIndex: i
        })
        // 修改 effect 为隐藏状态
        option.series[i].effect.show = false
        // 修改线条为隐藏状态
        option.series[i].lineStyle.opacity = 0
      }
      myChart.setOption(option)
    }
  })
}
</script>

<template>
  <div ref="chart" class="map" style="width: 700px; height: 561px"></div>
</template>

<style scoped>
.map {
  position: relative;
}
</style>
