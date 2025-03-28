<script setup>
import { ref, onMounted } from 'vue'
import * as d3 from 'd3'
import axios from 'axios'
import eventBus from '../utils/eventBus.ts'

const mapContainer = ref(null)
const noProcessData = ref(null)
const processData = ref(null)

// 模拟的每个省的人口数据
let populationData = {}

const drawMap = () => {
  // 清空之前的地图内容
  const svgContainer = d3.select(mapContainer.value).select("svg");
  svgContainer.remove();  // 移除现有的 SVG 元素

  const width = 700
  const height = 500

  const svg = d3
    .select(mapContainer.value)
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .attr('padding', 0)

  const projection = d3.geoMercator().center([120, 37]).scale(500)

  const path = d3.geoPath().projection(projection)

  // 使用 fetch 加载 .geojson 文件
  fetch('/china.geojson') // 相对于 public 目录
    .then((response) => response.json()) // 将响应解析为 JSON
    .then((geojson) => {
      const provinces = svg.append('g').selectAll('path')
        .data(geojson.features)
        .enter()
        .append('path')
        .attr('d', path)
        .attr('fill', 'lightgray')
        .attr('stroke', 'black')
        .attr('stroke-width', 1)

      // 为每个省份绘制人口圆圈
      provinces.each(function(d) {
        const provinceName = d.properties.name

        // 获取对应省份的人口数据
        const population = populationData[provinceName]

        console.log(population)

        if (population) {
          const centroid = path.centroid(d) // 获取省份的中心坐标
          const radius = Math.sqrt(population) * 3 // 根据人口数计算圆的半径，调整 /1000 来适应比例

          // 绘制圆圈
          svg.append('circle')
            .attr('cx', centroid[0])
            .attr('cy', centroid[1])
            .attr('r', radius)
            .attr('fill', 'rgba(255,105,105,0.6)')
            .attr('stroke', 'red')
            .attr('stroke-width', 1)
        }
      })
    })
    .catch((error) => {
      console.error('Error loading or parsing GeoJSON:', error)
    })

  fetch('/southchinasea.svg')
    .then((response) => response.text())
    .then((svgText) => {
      const parser = new DOMParser()
      const xmlDoc = parser.parseFromString(svgText, 'image/svg+xml')
      const southChinaSeaGroup = xmlDoc.querySelector('#southchinasea')
      if (southChinaSeaGroup) {
        svg.node().appendChild(southChinaSeaGroup)
        d3.select(southChinaSeaGroup)
          .attr('transform', 'translate(520,360)scale(0.3)')
          .attr('class', 'southchinasea')
          .attr('stroke', 'black')
          .attr('stroke-width', 1)
          .attr('fill', 'lightgray')
      } else {
        console.error('South China Sea group not found in SVG')
      }
    })
    .catch((error) => {
      console.error('Error loading South China Sea SVG:', error)
    })
}

onMounted(() => {
  fetchData()
  drawMap()
})

eventBus.on("treeSelect", (poetIds) => {
  if (poetIds.value.length > 0) {
    const provinceCounts = {}
    noProcessData.value.forEach(d => {
      poetIds.value.forEach(poetId => {
        if (poetId === d.poetId) {
          const province = d.province
          if (provinceCounts[province]) {
            provinceCounts[province] += 1
          } else {
            provinceCounts[province] = 1
          }
        }
      })
    })
    populationData = provinceCounts
    console.log('populationData', populationData)
  }else {
    populationData = processData.value
    console.log('populationData', populationData)
  }
  drawMap()
})

const fetchData = async () => {
  const response = await axios.get("http://localhost:8080/plumBlossom/getNavigate")
  noProcessData.value = response.data.data
  const provinceCounts = {}
  noProcessData.value.forEach(d => {
    const province = d.province
    if (provinceCounts[province]) {
      provinceCounts[province] += 1
    } else {
      provinceCounts[province] = 1
    }
  })

  // 将统计结果赋值给 processData
  processData.value = provinceCounts
  populationData = processData.value
  console.log(processData.value)
}
</script>

<template>
  <div style="width: 700px; height: 561px;">
    <div ref="mapContainer"></div>
  </div>
</template>
