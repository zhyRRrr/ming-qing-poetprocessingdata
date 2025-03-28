<script>
import * as d3 from 'd3';
import { sankey, sankeyLinkHorizontal } from 'd3-sankey';
import axios from 'axios';
import eventBus from '@/utils/eventBus.ts';

export default {
  name: 'SankeyChart',
  data() {
    return {
      width: 1120,
      height: 880,
      sankey: null,
      color: null,
      svg: null,
      nodes: [],
      links: [],
      data: []
    };
  },
  methods: {
    chart(graph) {
      this.sankey = sankey()
        .nodeSort(null)
        .linkSort(null)
        .nodeWidth(10)
        .nodePadding(2)
        .extent([
          [0, 10],
          [this.width - 10, this.height - 10]
        ]);

      const { nodes, links } = this.sankey({
        nodes: graph.nodes.map((d) => Object.create(d)),
        links: graph.links.map((d) => Object.create(d))
      });

      // 固定颜色映射，假设已经根据topic实际情况调整好键值对
      const colorMapping = {
        '0': '#FF0000',
        '1': '#FF7D00',
        '2': '#FFFF00',
        '3': '#00FF00',
        '4': '#00FFFF',
        '5': '#0000FF',
        '6': '#FF00FF',
        default: '#ccc'
      };

      console.log(nodes, links)

      this.svg = d3
        .create('svg')
        .attr('viewBox', [0, 0, this.width, this.height])
        .attr('width', this.width)
        .attr('height', this.height);

      // 添加节点（轴线）颜色
      this.svg
        .append('g')
        .selectAll('rect')
        .data(nodes)
        .join('rect')
        .attr('x', (d) => d.x0)
        .attr('y', (d) => d.y0)
        .attr('height', (d) => d.y1 - d.y0)
        .attr('width', (d) => d.x1 - d.x0)
        .attr('fill', (d) => colorMapping[d.name] || colorMapping.default)
        .append('title')
        .text((d) => `${d.name}\n${d.value.toLocaleString()}`);

      // 修改此处，根据topic设置链接（河流）颜色
      this.svg
        .append('g')
        .attr('fill', 'none')
        .selectAll('g')
        .data(links)
        .join('path')
        .attr('d', sankeyLinkHorizontal())
        .attr('stroke', (d) => {
          console.log(d)
          const topic = nodes[d.source].topic;
          return colorMapping[topic] || colorMapping.default;
        })
        .attr('stroke-width', (d) => d.width)
        .style('mix-blend-mode', 'multiply')
        .append('title')
        .text((d) => `${d.names.join(' → ')}\n${d.value.toLocaleString()}`);

      // 添加文字
      this.svg
        .append('g')
        .style('font', '10px sans-serif')
        .selectAll('text')
        .data(nodes)
        .join('text')
        .attr('x', (d) => (d.x0 < this.width / 2? d.x1 + 6 : d.x0 - 6))
        .attr('y', (d) => (d.y1 + d.y0) / 2)
        .attr('dy', '0.35em')
        .attr('text-anchor', (d) => (d.x0 < this.width / 2? 'start' : 'end'))
        .text((d) => d.name)
        .append('tspan')
        .attr('fill-opacity', 0.7)
        .text((d) => ` ${d.value.toLocaleString()}`);

      return this.svg.node();
    },
    graph(data) {
      const keys = ['poetName', 'topic', 'emotion'];
      let index = -1;
      const nodes = [];
      const nodeByKey = new d3.InternMap([], JSON.stringify);
      const indexByKey = new d3.InternMap([], JSON.stringify);

      const links = [];

      for (const k of keys) {
        for (const d of data) {
          const key = [k, d[k]];
          if (nodeByKey.has(key)) continue;
          const node = { name: d[k], topic: d.topic }; // 添加topic属性
          nodes.push(node);
          nodeByKey.set(key, node);
          indexByKey.set(key, ++index);
        }
      }
      console.log(nodeByKey);

      for (let i = 1; i < keys.length; ++i) {
        const a = keys[i - 1];
        const b = keys[i];
        const prefix = keys.slice(0, i + 1);
        const linkByKey = new d3.InternMap([], JSON.stringify);
        for (const d of data) {
          const names = prefix.map((k) => d[k]);
          const value = d.value || 1;

          let link = linkByKey.get(names);
          if (link) {
            link.value += value;
            continue;
          }
          link = {
            source: indexByKey.get([a, d[a]]),
            target: indexByKey.get([b, d[b]]),
            names,
            value
          };
          links.push(link);
          linkByKey.set(names, link);
        }
      }
      return { nodes, links };
    },
    async start() {
      const response = await axios.get("http://localhost:8080/plumBlossom/getRiverData");
      this.data = response.data.data;
      // data.sort((a, b) => a.year - b.year);
      const graphData = this.graph(this.data);
      const chartSvg = this.chart(graphData);
      const container = this.$refs['sankey-chart-container'];
      container.appendChild(chartSvg);
    }
  },
  mounted() {
    this.start();

    eventBus.on("treeSelect", (poetIds) => {
      if (poetIds.value.length === 0) {
        const graphData = this.graph(this.data);
        const chartSvg = this.chart(graphData);
        const container = this.$refs['sankey-chart-container'];
        container.innerHTML = '';
        container.appendChild(chartSvg);
      } else {
        console.log(poetIds.value);
        console.log(this.data);
        const filteredData = this.data.filter(item => poetIds.value.includes(Number(item.poetId)));
        const f = filteredData.map((item) => ({
          year: item.year,
          poetId: item.poetId,
          poetName: item.poetName,
          topic: item.topic,
          emotion: item.emotion,
          value: item.value
        }));
        const graphData = this.graph(f);
        const chartSvg = this.chart(graphData);
        const container = this.$refs['sankey-chart-container'];
        container.innerHTML = '';
        container.appendChild(chartSvg);
      }

      const colorMapping = {
        '喜': '#87000b',
        '怒/豪': '#cc7265',
        '哀': '#7B8ED6',
        '乐': '#dc9766',
        '思': '#5e7d5a',
        default: '#ccc'
      };
    });
  }
};
</script>

<template>
  <div id="sankey-chart-container" ref="sankey-chart-container"></div>
</template>

<style scoped>
#sankey-chart-container {
  width: 1120px;
  height: 880px;
}
</style>