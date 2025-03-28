<template>
  <div>
    <svg ref="svg" width="600" height="400"></svg>
  </div>
</template>

<script>
import * as d3 from 'd3';
import * as d3array from 'd3-array'

export default {
  name: 'ScatterPlot',
  data() {
    return {
      data: [], // Initialize data as an empty array
      tooltip: null
    };
  },
  mounted: async function() {
    try {
      const response = await fetch('/reduced_data.csv');
      const csvData = await response.text();
      this.data = d3.csvParse(csvData).map(d => [+d.PC1, +d.PC2]);
      this.createScatterPlot();
      // console.log(this.data);
    } catch (error) {
      console.error("Error loading CSV data:", error);
      // Handle the error appropriately, e.g., display an error message to the user
    }
  },
  beforeUnmount() {
    if (this.tooltip) {
      this.tooltip.remove();
    }
  },
  methods: {
    createScatterPlot() {
      const svg = d3.select(this.$refs.svg),
        margin = { top: 20, right: 20, bottom: 30, left: 40 },
        width = +svg.attr('width') - margin.left - margin.right,
        height = +svg.attr('height') - margin.top - margin.bottom,
        g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

      // Scale the x and y axes to the range [-1, 1]
      const x = d3.scaleLinear()
        .domain([-1, 1]) // Fixed domain
        .range([0, width]);

      const y = d3.scaleLinear()
        .domain([-1, 1]) // Fixed domain
        .range([height, 0]);

        const xAxis = d3.axisBottom(x)
        .tickFormat('') // 隐藏x轴刻度标签
        .tickSize(1); // 隐藏x轴刻度线
 
      const yAxis = d3.axisLeft(y)
        .tickFormat('') // 隐藏y轴刻度标签
        .tickSize(1); // 隐藏x轴刻度线

      g.append('g')
        .attr('transform', `translate(0,${height})`)
        .call(xAxis);

      g.append('g')
        .call(yAxis);

      const dots = g.selectAll('.dot')
        .data(this.data)
        .enter().append('circle')
        .attr('class', 'dot')
        .attr('r', 10)
        .attr('cx', d => x(d[0]))
        .attr('cy', d => y(d[1]));


      dots.on('mouseover', (event, d) => {
        const self = d3.select(event.target);
        self.transition()
          .duration(300)
          .attr('r', 8);

        if (!this.tooltip) {
          this.tooltip = d3.select('body').append('div')
            .attr('class', 'tooltip')
            .style('position', 'absolute')
            .style('pointer-events', 'none');
        }
        this.tooltip
          .style('left', `${event.pageX + 5}px`)
          .style('top', `${event.pageY + 5}px`)
          .text(`${d[0]}, ${d[1]}`);
      })
        .on('mouseout', (event) => {
          const self = d3.select(event.target);
          self.transition()
            .duration(300)
            .attr('r', 5);

          if (this.tooltip) {
            this.tooltip.remove();
            this.tooltip = null;
          }
        });
    }
  }
};
</script>


<!--<style scoped>-->
<!--.dot:hover {-->
<!--  stroke: #000;-->
<!--  stroke-width: 3px;-->
<!--}-->

<!--.tooltip {-->
<!--  width: auto;-->
<!--  padding: 10px;-->
<!--  background-color: #f9f9f9;-->
<!--  border: 1px solid #d3d3d3;-->
<!--  border-radius: 4px;-->
<!--  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);-->
<!--  pointer-events: none;-->
<!--  font-size: 12px;-->
<!--  color: #333;-->
<!--}-->
<!--</style>-->

<!--<style scoped>-->
<!--#container{-->
<!--  width:500px;-->
<!--  height:600px;-->
<!--  background-color:#cccccc;-->
<!--}-->
<!--</style>-->


