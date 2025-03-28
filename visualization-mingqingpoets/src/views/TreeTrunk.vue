<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import axios from 'axios'
import FlowerView from '@/components/flowerView/FlowerView.vue'
import shuWenLiImage from "@/assets/shuWenLi.png";
import {
  CycleInfo,
  FamilyPoetsResponse,
  Flower,
  HaveFamilyInfo,
  MainInfo, MainInfoResponse,
  NoFamilyInfo,
  NoFamilyPoetsResponse, PoetInfo,
  Point
} from '@/types/flower'
import eventBus from '@/utils/eventBus'

const image = new Image()
image.src = shuWenLiImage

// 定义数据结构


const PI:number = Math.acos(-1)
const mainInfo = ref<MainInfo>();
const familyPoets = ref<HaveFamilyInfo>()
const noFamilyPoets = ref<NoFamilyInfo>()
const cycleInfo = ref<CycleInfo>()

const width = ref(840)
const height = ref(1440)

const container = ref<HTMLCanvasElement | null>(null)
const backgroundContainer = ref<HTMLCanvasElement | null>(null)
const canvas = ref<HTMLCanvasElement | null>(null)
const familyFi = ref<HTMLCanvasElement | null>(null)
const familySe = ref<(HTMLCanvasElement)[]>([])
const noFamilyFi = ref<HTMLCanvasElement | null>(null)
const noFamilySe = ref<(HTMLCanvasElement)[]>([])
const shade = ref<(HTMLCanvasElement | null)[]>([])
const toolBox = ref<(HTMLCanvasElement | null)[]>([])

// const x = ref([])
// const y = ref([])
const pointArea = ref<Point[]>([]);
const familyFiPointArea = ref<Point[]>([])
const familySePointArea = ref<Point[][]>([])
const familyThPointArea = ref<Point[][][]>([])

const noFamilyFiPointArea = ref<Point[]>([])
const noFamilySePointArea = ref<Point[][]>([])

const items = ref<Flower[]>([])

const poemMaxNum = ref(0)

const fetchData = async (): Promise<void> => {
  const [response1, response2, response3] : [FamilyPoetsResponse, NoFamilyPoetsResponse, MainInfoResponse] = await Promise.all([
    axios.get('http://localhost:8080/plumBlossom/getFamilyPoets'),
    axios.get('http://localhost:8080/plumBlossom/getNoFamilyPoets'),
    axios.get('http://localhost:8080/plumBlossom/getMainInfo')
  ])

  familyPoets.value = response1.data.data
  noFamilyPoets.value = response2.data.data
  mainInfo.value = response3.data.data
  poemMaxNum.value = Math.max(familyPoets.value.poemMaxNum, noFamilyPoets.value.poemMaxNum)
  const response4 = await axios.get('http://localhost:8080/plumBlossom/getCycle', {
    params: {
      startYear: mainInfo.value.startYear,
      endYear: mainInfo.value.endYear
    }
  });
  cycleInfo.value = response4.data.data
}

// 平滑贝塞尔曲线函数
const bezierCurve = (p0: Point, p1: Point, p2: Point, p3: Point, inserted: number): Point[] => {
  const points: Point[] = [];
  for (let t = 0; t <= 1; t += 1 / (inserted + 1)) {
    const x = p0.x * Math.pow(1 - t, 3) + 3 * p1.x * t * Math.pow(1 - t, 2) + 3 * p2.x * Math.pow(t, 2) * (1 - t) + p3.x * Math.pow(t, 3);
    const y = p0.y * Math.pow(1 - t, 3) + 3 * p1.y * t * Math.pow(1 - t, 2) + 3 * p2.y * Math.pow(t, 2) * (1 - t) + p3.y * Math.pow(t, 3);
    points.push({x, y})
  }
  return points;
};
// 数据平滑函数
const smoothingBezier = (points: Array<Point>, k: number = 0.5, inserted: number = 10): Point[] => {
  const pointLength = points.length;

  // 生成原始数据折线的中点集
  const midPoints: { start: Point; end: Point; mid: Point; }[] = points.map((point, i) => {
    if (i === 0) return null;
    return {
      start: points[i - 1],
      end: points[i],
      mid: {
        x: (points[i - 1].x + points[i].x) / 2,
        y: (points[i - 1].y + points[i].y) / 2
      }
    };
  }).filter(Boolean) as { start: Point; end: Point; mid: Point; }[];

  midPoints.push({
    start: points[pointLength - 1],
    end: points[0],
    mid: {
      x: (points[0].x + points[pointLength - 1].x) / 2,
      y: (points[0].y + points[pointLength - 1].y) / 2
    }
  });

  // 找出中点连线及其分割点
  const controlPoints: { start: Point; mid0: Point; mid1: Point; end: Point; }[] = [];
  for (let i = 0; i < midPoints.length; i++) {
    const next = (i + 1) % midPoints.length;

    const d0 = Math.sqrt(
      Math.pow(midPoints[i].start.x - midPoints[i].end.x, 2) +
      Math.pow(midPoints[i].start.y - midPoints[i].end.y, 2)
    );
    const d1 = Math.sqrt(
      Math.pow(midPoints[next].start.x - midPoints[next].end.x, 2) +
      Math.pow(midPoints[next].start.y - midPoints[next].end.y, 2)
    );

    const kSplit = d0 / (d0 + d1);

    const split: Point = {
      x: midPoints[i].mid.x + (midPoints[next].mid.x - midPoints[i].mid.x) * kSplit,
      y: midPoints[i].mid.y + (midPoints[next].mid.y - midPoints[i].mid.y) * kSplit
    };

    const dx = midPoints[i].end.x - split.x;
    const dy = midPoints[i].end.y - split.y;

    const s: Point = {
      x: midPoints[i].mid.x + dx,
      y: midPoints[i].mid.y + dy
    };
    const e: Point = {
      x: midPoints[next].mid.x + dx,
      y: midPoints[next].mid.y + dy
    };

    const cp0: Point = {
      x: s.x + (midPoints[i].end.x - s.x) * k,
      y: s.y + (midPoints[i].end.y - s.y) * k
    };
    const cp1: Point = {
      x: e.x + (midPoints[i].end.x - e.x) * k,
      y: e.y + (midPoints[i].end.y - e.y) * k
    };

    if (controlPoints.length > 0) {
      controlPoints[i].mid1 = cp0;
    } else {
      controlPoints.push({
        start: midPoints[i].start,
        mid0: {x: 0, y: 0},
        mid1: cp0,
        end: midPoints[i].end
      });
    }

    if (i < midPoints.length - 1) {
      controlPoints.push({
        start: midPoints[i + 1].start,
        mid0: cp1,
        mid1: {x: 0, y: 0},
        end: midPoints[i + 1].end
      });
    } else {
      controlPoints[0].mid0 = cp1;
    }
  }

  // 将处理后的controlPoints转换为符合bezierCurve函数参数要求的格式
  const bezierCurveInput: [Point, Point, Point, Point][] = controlPoints.map(({ start, mid0, mid1, end }) => [start, mid0, mid1, end]);

  return bezierCurveInput.flatMap((control) =>
    bezierCurve(control[0], control[1], control[2], control[3], inserted)
  );
}
// 画树
const drawTree = () => {
  const ctx = canvas.value?.getContext('2d')
  if (!ctx) return;

  // ctx.fillStyle = 'red'
  // pointArea.value.forEach((point) => ctx.fillRect(point.x - 3, point.y - 3, 6, 6))

  // 调用数据平滑函数
  const points = smoothingBezier(pointArea.value, 0.5, 10)
  ctx.beginPath()
  ctx.moveTo(points[0].x, points[0].y)
  points.forEach((point) => ctx.lineTo(point.x, point.y))
  ctx.closePath()

  // const pattern = ctx.createPattern(image, "repeat")
  ctx.fillStyle = ctx.createPattern(image, "repeat")

  ctx.fill()
  // ctx.stroke()



  const ctx2 = familyFi.value?.getContext('2d')
  if (!ctx2) return;
  // familyFiPointArea.value.forEach(point => ctx2.fillRect(point.x - 3, point.y - 3, 6, 6))
  const points_2 = smoothingBezier(familyFiPointArea.value,0.5, 10)
  ctx2.beginPath()
  ctx2.moveTo(points_2[0].x, points_2[0].y)
  points_2.forEach(point => ctx2.lineTo(point.x, point.y))
  ctx2.closePath()
  ctx2.fillStyle = "white"
  ctx2.fill()
  ctx2.stroke()


  familySe.value.map((can, idx) => {
    const ctx = can?.getContext('2d')
    if (!ctx) return
    // familySePointArea.value[idx].forEach(point => ctx.fillRect(point.x - 3, point.y - 3, 6, 6))
    const points = smoothingBezier(familySePointArea.value[idx], 0.5, 10)
    ctx.beginPath()
    ctx.moveTo(points[0].x, points[0].y)
    points.forEach((point) => ctx.lineTo(point.x, point.y))
    ctx.closePath()
    ctx.fillStyle = "green"
    ctx.fill()
  })

  const ctx3 = noFamilyFi.value?.getContext('2d')
  if (!ctx3) return;
  // noFamilyFiPointArea.value.forEach(point => ctx3.fillRect(point.x - 3, point.y - 3, 6, 6))
  const points_3 = smoothingBezier(noFamilyFiPointArea.value,0.5, 10)
  ctx3.beginPath()
  ctx3.moveTo(points_3[0].x, points_3[0].y)
  points_3.forEach(point => ctx3.lineTo(point.x, point.y))
  ctx3.closePath()
  ctx3.fillStyle = "white"
  ctx3.fill()
  ctx3.stroke()



  noFamilySe.value.map((can, idx) => {
    const ctx = can?.getContext('2d')
    if (!ctx) return
    // noFamilySePointArea.value[idx].forEach(point => ctx.fillRect(point.x - 3, point.y - 3, 6, 6))
    const points = smoothingBezier(noFamilySePointArea.value[idx], 0.5, 10)
    ctx.beginPath()
    ctx.moveTo(points[0].x, points[0].y)
    points.forEach((point) => ctx.lineTo(point.x, point.y))
    ctx.closePath()
    ctx.fillStyle = "green"
    ctx.fill()
  })




  // ctx.stroke()
}

// 还原回原数组
const solveEquationIntegerBinary = (k3: number, k4: number, b3: number, b4: number, c: number, left: number, right: number): number => {
  while (left < right) {
    let mid = Math.floor((left + right) / 2);
    let value = mid + Math.cos(k4 * mid + b4) * (k3 * mid + b3);
    if (value < c) {
      left = mid + 1;
    } else {
      right = mid;
    }
  }
  return left;
}

const calculatePoints = async (): Promise<void> => {
  const totalYear = mainInfo.value.endYear - mainInfo.value.startYear
  const ex = 700 / totalYear

  const pointMapArea = ref<Point[]>([])
  const noFamilyFiMapPointArea = ref<Point[]>([])
  // 主分支控制函数
  // region
  const mainBranch_x = 0
  const mainBranch_fx = 70
  const mainBranch_span_x = 810
  const mainBranch_y1 = 650
  const mainBranch_y2 = 850
  const mainBranch_y3 = 900
  const mainBranch_k1 = (mainBranch_y2 - mainBranch_y1) / (mainBranch_fx - mainBranch_x)
  const mainBranch_b1 = mainBranch_y1 - mainBranch_k1 * mainBranch_x
  const mainBranch_k2 = (mainBranch_y3 - mainBranch_y2) / (mainBranch_x + mainBranch_span_x - mainBranch_fx)
  const mainBranch_b2 = mainBranch_y2 - mainBranch_k2 * mainBranch_fx
  const getMainBranch_y = (cal_x: number) => cal_x <= mainBranch_fx ? cal_x * mainBranch_k1 + mainBranch_b1 : cal_x * mainBranch_k2 + mainBranch_b2

  const mainBranch_width = 60
  const mainBranch_k3 = (3 - mainBranch_width) / mainBranch_span_x
  const mainBranch_b3 = mainBranch_width - mainBranch_k3 * mainBranch_x
  const getMainBranch_width = (cal_x: number) => mainBranch_k3 * cal_x + mainBranch_b3

  const mainBranch_angle = PI / 4
  const mainBranch_k4 = PI / 4 / mainBranch_span_x
  const mainBranch_b4 = mainBranch_angle - mainBranch_k4 * mainBranch_x
  const getMainBranch_angle = (cal_x: number) => mainBranch_k4 * cal_x + mainBranch_b4

  const getMainBranch = (cal_x: number, flag: boolean = true) => {
    const cal_y = getMainBranch_y(cal_x)
    const wd = getMainBranch_width(cal_x)
    const angle = getMainBranch_angle(cal_x)
    const dx = Math.cos(angle) * wd
    const dy = Math.sin(angle) * wd

    if (flag) {
      pointArea.value.push({x: cal_x, y: cal_y })
      pointMapArea.value.push({ x: cal_x - dx, y: cal_y + dy })
    }else {
      noFamilyFiPointArea.value.push({x: cal_x, y: cal_y })
      noFamilyFiMapPointArea.value.push({ x: cal_x - dx, y: cal_y + dy })
    }
  }
  // endregion

  getMainBranch(0)
  getMainBranch(30)

  // 开启家族分支
  if (familyPoets.value) {
    const familyChildBranch_dy = 180 / familyPoets.value?.familyMaxSpan
    // 控制在分支上方还是下方
    let familyChildBranch_flag = -1

    const familyFiMapPointArea = ref<Point[]>([])
    // 家族总分支控制函数
    // region
    const familyBranch_x = 30
    const familyBranch_span_year = familyPoets.value.familyMaxBirthday - mainInfo.value.startYear
    const familyBranch_span_x = 70 + familyBranch_span_year * ex + 10

    const familyBranch_fx = familyBranch_x + 200
    const familyBranch_y1 = getMainBranch_y(familyBranch_x)
    const familyBranch_y2 = 300
    const familyBranch_y3 = 200
    const familyBranch_k1 = (familyBranch_y2 - familyBranch_y1) / (familyBranch_fx - familyBranch_x)
    const familyBranch_b1 = familyBranch_y1 - familyBranch_k1 * familyBranch_x
    const familyBranch_k2 = (familyBranch_y3 - familyBranch_y2) / (familyBranch_x + familyBranch_span_x - familyBranch_fx)
    const familyBranch_b2 = familyBranch_y2 - familyBranch_k2 * familyBranch_fx
    const getFamilyBranch_y = (cal_x: number) => cal_x <= familyBranch_fx ? cal_x * familyBranch_k1 + familyBranch_b1 : cal_x * familyBranch_k2 + familyBranch_b2
    // 控制分支的宽度
    const familyBranch_width = getMainBranch_width(familyBranch_x)
    const familyBranch_k3 = (-1 * (familyBranch_width - 8)) / familyBranch_span_x
    const familyBranch_b3 = familyBranch_width - familyBranch_k3 * familyBranch_x
    const getFamilyBranch_width = (cal_x: number) => familyBranch_k3 * cal_x + familyBranch_b3
    //控制偏移量
    const familyBranch_y4 = PI / 4
    const familyBranch_k4 = (PI / 2 - familyBranch_y4) / familyBranch_span_x
    const familyBranch_b4 = familyBranch_y4 - familyBranch_k4 * familyBranch_x
    const getFamilyBranch_angle = (cal_x: number) => familyBranch_k4 * cal_x + familyBranch_b4
    const getFamilyBranch = (cal_x: number) => {
      let cal_y = getFamilyBranch_y(cal_x)
      let wd = getFamilyBranch_width(cal_x)
      let angle = getFamilyBranch_angle(cal_x)
      let dx = Math.cos(angle) * wd
      let dy = Math.sin(angle) * wd

      familyFiPointArea.value.push({x: cal_x, y: cal_y })
      familyFiMapPointArea.value.push({ x: cal_x + dx, y: cal_y + dy })
    }

    // endregion

    getFamilyBranch(familyBranch_x)
    pointArea.value.pop();
    getFamilyBranch(familyBranch_fx)

    familyPoets.value.familyInfos.forEach((family: FamilyInfo, idx_1: number) => {
      familySePointArea.value[idx_1] = [];
      familyThPointArea.value[idx_1] = [];
      const familySeMapPointArea = ref<Point[]>([])

      // 家族分支控制函数
      // region
      const familyChildBranchStart = family?.placeInfos[0].poetInfos[0].birthday
      let familyChildBranch_x = 70 + (familyChildBranchStart - mainInfo.value.startYear) * ex
      let familyChildBranch_y = getFamilyBranch_y(familyChildBranch_x)

      if (familyChildBranch_flag === 1) {
        const cal_x = solveEquationIntegerBinary(familyBranch_k3, familyBranch_k4, familyBranch_b3, familyBranch_b4, familyChildBranch_x, 0, 1000)
        familyChildBranch_y = getFamilyBranch_y(cal_x) + Math.sin(getFamilyBranch_angle(cal_x)) * getFamilyBranch_width(cal_x)
      }

      const familyChildBranchSpan_year = family?.placeMaxBirthday - familyChildBranchStart
      const familyChildBranchSpan_x = 30 + familyChildBranchSpan_year * ex
      const familyChildBranchSpan_y = Math.max(20, familyChildBranchSpan_year * familyChildBranch_dy)

      const familyChildBranch_fx = familyChildBranch_x + familyChildBranchSpan_x / 3
      const familyChildBranch_y1 = familyChildBranch_y
      const familyChildBranch_y2 = familyChildBranch_y + familyChildBranch_flag *  familyChildBranchSpan_y * 3 / 5
      const familyChildBranch_y3 = familyChildBranch_y + familyChildBranch_flag * familyChildBranchSpan_y
      const familyChildBranch_k1 = (familyChildBranch_y2 - familyChildBranch_y1) / (familyChildBranch_fx - familyChildBranch_x)
      const familyChildBranch_b1 = familyChildBranch_y1 - familyChildBranch_k1 * familyChildBranch_x
      const familyChildBranch_k2 = (familyChildBranch_y3 - familyChildBranch_y2) / (familyChildBranchSpan_x + familyChildBranch_x - familyChildBranch_fx)
      const familyChildBranch_b2 = familyChildBranch_y2 - familyChildBranch_k2 * familyChildBranch_fx
      const getFamilyChildBranch_y = (cal_x: number) => cal_x <= familyChildBranch_fx ? familyChildBranch_k1 * cal_x + familyChildBranch_b1 : familyChildBranch_k2 * cal_x + familyChildBranch_b2

      const familyChildBranch_width = Math.max(20, getFamilyBranch_width(familyChildBranch_x))
      const familyChildBranch_k3 = (-1 * (familyChildBranch_width - 5)) / familyChildBranchSpan_x
      const familyChildBranch_b3 = familyChildBranch_width - familyChildBranch_k3 * familyChildBranch_x
      const getFamilyChildBranch_width = (cal_x: number) => familyChildBranch_k3 * cal_x + familyChildBranch_b3

      const familyChildBranch_angle = 0
      const familyChildBranch_k4 = (PI / 2 - familyChildBranch_angle) / familyChildBranchSpan_x
      const familyChildBranch_b4 = familyChildBranch_angle - familyChildBranch_k4 * familyChildBranch_x
      const getFamilyChildBranch_angle = (cal_x: number) => familyChildBranch_k4 * cal_x + familyChildBranch_b4

      const getFamilyChildBranch = (cal_x: number) => {
        const cal_y = getFamilyChildBranch_y(cal_x)
        const wd = getFamilyChildBranch_width(cal_x)
        const angle = getFamilyChildBranch_angle(cal_x)
        const dx = Math.cos(angle) * wd
        const dy = Math.sin(angle) * wd
        familySePointArea.value[idx_1].push({x: cal_x, y: cal_y})
        familySeMapPointArea.value.push({x: cal_x + dx, y: cal_y - familyChildBranch_flag * dy})
      }
      //endregion

      getFamilyChildBranch(familyChildBranch_x)
      getFamilyChildBranch(familyChildBranch_fx)



      // 家族中只有一个地域
      if (family.placeInfos.length === 1){
        family?.placeInfos[0].poetInfos.forEach((poet: PoetInfo, _i) => {
          const cal_x = 100 + (poet.birthday - mainInfo.value.startYear) * ex
          const cal_y = getFamilyChildBranch_y(cal_x)
          pushInfo(poet, _i, cal_x, cal_y, familyChildBranch_flag)
        })
      }
      else {
        familySePointArea.value[idx_1].pop()
        const familyPlaceBranchMaxSpan = family.placeMaxSpan
        const familyPlaceBranch_dy = familyPlaceBranchMaxSpan === 0 ? 0 : (familyChildBranchSpan_y * 6) / 7 / familyPlaceBranchMaxSpan

        let familyPlaceBranch_flag = -1 // 控制地域分支在上一级分支的上方还是下方
        family?.placeInfos.forEach((placeInfo, idx_2: number) => {
          familyThPointArea.value[idx_1][idx_2] = []
          const familyThMapPointArea = ref<Point[]>([])

          let familyPlaceBranch_x = 90 + (placeInfo.poetInfos[0].birthday - mainInfo.value.startYear) * ex
          let familyPlaceBranch_y = getFamilyChildBranch_y(familyPlaceBranch_x)

          if (familyPlaceBranch_flag === 1) {
            const cal_x = solveEquationIntegerBinary(familyChildBranch_k3, familyChildBranch_k4, familyChildBranch_b3, familyChildBranch_b4, familyPlaceBranch_x, 0, 1200)
            familyPlaceBranch_y = getFamilyChildBranch_y(cal_x) - familyPlaceBranch_flag * Math.sin(getFamilyChildBranch_angle(cal_x)) * getFamilyChildBranch_width(cal_x)
          }
          if (placeInfo.poetInfos.length === 1 || placeInfo.poetInfos[0].birthday === placeInfo.poetInfos[placeInfo.poetInfos.length - 1]?.birthday){
            // 如果只有一个点
            const getFamilyPlaceBranch_k = -3 * familyChildBranch_flag * familyPlaceBranch_flag
            const getFamilyPlaceBranch_y = (cal_x: number) =>  getFamilyPlaceBranch_k * cal_x + familyPlaceBranch_y - getFamilyPlaceBranch_k * familyPlaceBranch_x
            const getFamilyPlaceBranch_width = (cal_x: number) => - 1 * 0.3 * cal_x + 10 + 0.3 * familyPlaceBranch_x
            const getFamilyPlaceBranch = (cal_x: number) => {
              const cal_y = getFamilyPlaceBranch_y(cal_x)
              const width = getFamilyPlaceBranch_width(cal_x)

              familyThPointArea.value[idx_1][idx_2].push({x: cal_x, y: cal_y})
              familyThMapPointArea.value.push({x: cal_x + width, y: cal_y - familyPlaceBranch_flag * familyChildBranch_flag * 5})
            }
            getFamilyPlaceBranch(familyPlaceBranch_x)
            getFamilyPlaceBranch(familyPlaceBranch_x + 10)
            placeInfo?.poetInfos.forEach((poet, _i) => {
              const cal_x = 100 + (poet.birthday - mainInfo.value.startYear) * ex
              const cal_y = getFamilyPlaceBranch_y(cal_x)
              pushInfo(poet, _i, cal_x, cal_y, familyChildBranch_flag * familyPlaceBranch_flag)
            })
          }
          // else {
          //   const familyPlaceBranchSpan_year = placeInfo?.poetMaxBirthday - placeInfo.poetInfos[0].birthday
          //   const familyPlaceBranchSpan_x = 20 + familyPlaceBranchSpan_year * ex + 3
          //   const familyPlaceBranchSpan_y = Math.max(10, familyPlaceBranchSpan_year * familyPlaceBranch_dy)
          //
          //   const familyPlaceBranch_fx = familyPlaceBranch_x + familyPlaceBranchSpan_x / 5
          //   const familyPlaceBranch_y1 = familyPlaceBranch_y
          //   const familyPlaceBranch_y2 = familyPlaceBranch_y + (familyChildBranch_flag * -1 * familyPlaceBranch_flag * familyPlaceBranchSpan_y) / 2
          //   const familyPlaceBranch_y3 = familyPlaceBranch_y + familyChildBranch_flag * -1 * familyPlaceBranch_flag * familyPlaceBranchSpan_y
          //   const familyPlaceBranch_k1 = (familyPlaceBranch_y2 - familyPlaceBranch_y1) / (familyPlaceBranch_fx - familyPlaceBranch_x)
          //   const familyPlaceBranch_b1 = familyPlaceBranch_y1 - familyPlaceBranch_k1 * familyPlaceBranch_x
          //   const familyPlaceBranch_k2 = (familyPlaceBranch_y3 - familyPlaceBranch_y2) / (familyPlaceBranchSpan_x + familyPlaceBranch_x - familyPlaceBranch_fx)
          //   const familyPlaceBranch_b2 = familyPlaceBranch_y2 - familyPlaceBranch_k2 * familyPlaceBranch_fx
          //   const getFamilyPlaceBranch_y = (cal_x: number) => cal_x <= familyPlaceBranch_fx ? familyPlaceBranch_k1 * cal_x + familyPlaceBranch_b1 : familyPlaceBranch_k2 * cal_x + familyPlaceBranch_b2
          //
          //   const familyPlaceBranch_width = getFamilyChildBranch_width(familyPlaceBranch_x)
          //   const familyPlaceBranch_k3 = (-1 * (familyPlaceBranch_width - 5)) / familyPlaceBranchSpan_x
          //   const familyPlaceBranch_b3 = familyPlaceBranch_width - familyPlaceBranch_k3 * familyPlaceBranch_x
          //   const getFamilyPlaceBranch_width = (cal_x: number) => familyPlaceBranch_k3 * cal_x + familyPlaceBranch_b3
          //
          //   const familyPlaceBranch_angle = (familyPlaceBranch_flag * PI) / 12
          //   const familyPlaceBranch_k4 = (PI / 2 - familyPlaceBranch_angle) / familyPlaceBranchSpan_x
          //   const familyPlaceBranch_b4 = familyPlaceBranch_angle - familyPlaceBranch_k4 * familyPlaceBranch_x
          //   const getFamilyPlaceBranch_angle = (cal_x: number) => familyPlaceBranch_k4 * cal_x + familyPlaceBranch_b4
          //
          //
          //   const getFamilyPlaceBranch = (cal_x: number) => {
          //     const cal_y = getFamilyPlaceBranch_y(cal_x)
          //     const wd = getFamilyPlaceBranch_width(cal_x)
          //     const angle = getFamilyPlaceBranch_angle(cal_x)
          //     const dx = Math.cos(angle) * wd
          //     const dy = Math.sin(angle) * wd
          //
          //     familyThPointArea.value[idx_1][idx_2].push({x: cal_x, y: cal_y})
          //     familyThMapPointArea.value.push({x: cal_x + dx, y: cal_y + familyChildBranch_flag * familyPlaceBranch_flag * dy})
          //   }
          //
          //   getFamilyPlaceBranch(familyPlaceBranch_x)
          //   getFamilyPlaceBranch(familyPlaceBranch_fx)
          //   placeInfo.poetInfos.forEach((poet) => {
          //     const cal_x = 200 + (poet?.birthday - mainInfo.value.startYear) * ex
          //     const cal_y = getFamilyPlaceBranch_y(cal_x)
          //     items.value.push({
          //       poetId: poet.poetId,
          //       left: cal_x,
          //       top: cal_y,
          //       data: poet.emotionInfos,
          //       select: false,
          //       scale: 0.5
          //     })
          //   })
          //
          //   getFamilyPlaceBranch(familyPlaceBranch_x + familyPlaceBranchSpan_x)
          // }

          familyThMapPointArea.value.reverse().map(point => familyThPointArea.value[idx_1][idx_2].push(point))
          if (familyPlaceBranch_flag === -1) {
            familyThPointArea.value[idx_1][idx_2].map(point => familySePointArea.value[idx_1].push(point))
          }else {
            familyThPointArea.value[idx_1][idx_2].map(point => familySeMapPointArea.value.push(point))
          }

          familyPlaceBranch_flag = -1 * familyPlaceBranch_flag
        })
      }

      getFamilyChildBranch(familyChildBranch_x + familyChildBranchSpan_x)

      familySeMapPointArea.value.reverse().map(point => familySePointArea.value[idx_1].push(point))

      if (familyChildBranch_flag === -1) {
        familySePointArea.value[idx_1].map(point => familyFiPointArea.value.push(point))
      }else {
        familySePointArea.value[idx_1].map(point => familyFiMapPointArea.value.push(point))
      }
      familyChildBranch_flag = -1 * familyChildBranch_flag
    })

    getFamilyBranch(familyBranch_x + familyBranch_span_x)
    familyFiMapPointArea.value.reverse().map(point => familyFiPointArea.value.push(point))
    familyFiPointArea.value.map(point => pointArea.value.push(point))
  }
  getMainBranch(mainBranch_fx, false)

  // 如果有 没有家族诗人
  if (noFamilyPoets.value) {
    const ey = 200 / noFamilyPoets.value.maxSpan
    // 控制分支在上方还是在下方, -1 在上方
    let place_flag = -1
    let cnt = 3;
    noFamilyPoets.value?.placeInfos.forEach((placeInfo, idx_1: number) => {
      noFamilySePointArea.value[idx_1] = []
      const noFamilySeMapPointArea = ref<Point[]>([])

// 90 50 40 20
      let place_x1 = 90 + (placeInfo.poetInfos[0].birthday - mainInfo.value.startYear) * ex
      let place_y1 = getMainBranch_y(place_x1)
      // 需偏移回原坐标
      if (place_flag === -1) {
        const cal_x = solveEquationIntegerBinary(mainBranch_k3,mainBranch_k4,mainBranch_b3,mainBranch_b4,place_x1,0,1600)
        const dy = Math.sin(getMainBranch_angle(cal_x)) * getMainBranch_width(cal_x)
        place_y1 += dy + 5
      }
      const place_year = placeInfo?.poetMaxBirthday - placeInfo.poetInfos[0].birthday

      if (place_year === 0){
        // 如果只有一年
        const place_k = -0.6 * place_flag
        const getPlaceBranch_y = (cal_x: number) => place_k * cal_x + place_y1 - place_k * place_x1
        const getPlaceBranch_width = (cal_x: number) => -1 * 0.3 * cal_x + 20 + 0.3 * place_x1
        const getPlaceBranch = (cal_x: number) => {
          const cal_y = getPlaceBranch_y(cal_x)
          const width = getPlaceBranch_width(cal_x)
          noFamilySePointArea.value[idx_1].push({x: cal_x, y: cal_y})
          noFamilySeMapPointArea.value.push({ x: cal_x + width, y: cal_y})
        }
        getPlaceBranch(place_x1)
        getPlaceBranch(place_x1 + 10)
        placeInfo?.poetInfos.forEach((poet, _i) => {
          const cal_x = 100 + (poet.birthday - mainInfo.value.startYear) * ex
          const cal_y = getPlaceBranch_y(cal_x)
          pushInfo(poet, _i, cal_x, cal_y, place_flag)
        })
      }else {
        const place_span_x = 20 + place_year * ex
        const place_span_y = Math.max(20, place_year * ey + (place_flag === 1 ? 0 : cnt-- * 15))
        const place_fx = place_x1 + place_span_x / 4
        const place_fy = place_y1 - place_flag * place_span_y / 2
        const place_x2 = place_x1 + place_span_x
        const place_y2 = place_y1 - place_flag * place_span_y
        const place_k1 = (place_fy - place_y1) / (place_fx - place_x1)
        const place_b1 = place_y1 - place_k1 * place_x1
        const place_k2 = (place_y2 - place_fy) / (place_x2 - place_fx)
        const place_b2 = place_fy - place_k2 * place_fx
        const getPlace_y = (cal_x: number) => cal_x < place_fx ? place_k1 * cal_x + place_b1 : place_k2 * cal_x + place_b2

        const place_width = getMainBranch_width(place_x1)
        const place_k3 = (5 - place_width) / place_span_x
        const place_b3 = place_width - place_k3 * place_x1
        const getPlace_width = (cal_x: number) => place_k3 * cal_x + place_b3

        const place_angle = 0
        const place_k4 = (5 * PI / 12 - place_angle) / place_span_x
        const place_b4 = place_angle - place_k4 * place_x1
        const getPlace_angle = (cal_x: number) => place_k4 * cal_x + place_b4

        const getPlace_branch = (cal_x: number) => {
          const cal_y = getPlace_y(cal_x)
          const width = getPlace_width(cal_x)
          const angle = getPlace_angle(cal_x)
          const dx = Math.cos(angle) * width
          const dy = Math.sin(angle) * width
          noFamilySePointArea.value[idx_1].push({x: cal_x, y: cal_y})
          noFamilySeMapPointArea.value.push({ x: cal_x + dx, y: cal_y + place_flag * dy})
        }

        getPlace_branch(place_x1)
        getPlace_branch((place_x1 + place_fx) / 2)
        getPlace_branch(place_fx)
        getPlace_branch((place_fx + place_x2) / 2)
        getPlace_branch(place_x2)

        placeInfo?.poetInfos.forEach((poet, _i) => {
          const cal_x = 100 + (poet.birthday - mainInfo.value.startYear) * ex
          const cal_y = getPlace_y(cal_x)
          pushInfo(poet, _i, cal_x, cal_y, -1 * place_flag)
        })
      }
      noFamilySeMapPointArea.value.reverse().map(point => noFamilySePointArea.value[idx_1].push(point))
      if (place_flag === 1) {
        noFamilySePointArea.value[idx_1].map(point => noFamilyFiPointArea.value.push(point))
      }else {
        noFamilySePointArea.value[idx_1].map(point => noFamilyFiMapPointArea.value.push(point))
      }
      place_flag *= -1
    })

    getMainBranch(120 + (noFamilyPoets.value?.noFamilyMaxBirthday - mainInfo.value.startYear) * ex, false)
  }



  noFamilyFiMapPointArea.value.reverse().map(point => noFamilyFiPointArea.value.push(point))
  noFamilyFiPointArea.value.map(point => pointArea.value.push(point))
  pointMapArea.value.reverse().map((point) => pointArea.value.push(point))
}


const pushInfo: void  = (poet: PoetInfo, index: number, cal_x: number, cal_y: number, flag: boolean) => {
  let cx = 100
  if (index !== 0) cx = cal_x - items.value[items.value.length - 1].left
  if (cx > 30) {
    items.value.push({
      poetId: poet.poetId,
      left: cal_x,
      top: cal_y,
      data: poet?.emotionInfos,
      select: false,
      scale: poet.poemNum / 3 / poemMaxNum.value + 0.3,
      rotate: Math.floor(Math.random() * 180)
    })
  }else {
    const cy = Math.sqrt(30 ** 2 - (cal_x - items.value[items.value.length - 1].left) ** 2)
    // const new_y =
    items.value.push({
      poetId: poet.poetId,
      left: cal_x,
      top: items.value[items.value.length - 1].top + flag * cy,
      data: poet?.emotionInfos,
      select: false,
      scale: poet.poemNum / 3 / poemMaxNum.value + 0.32,
      rotate: Math.floor(Math.random() * 180)
    })
  }
}

onMounted(() => {
  // 加载数据
  fetchData().then(() => {
    const backgroundContainerCtx = backgroundContainer.value?.getContext('2d');
    const ex = 700 / (mainInfo.value.endYear - mainInfo.value.startYear);

    // 设置线条颜色
    backgroundContainerCtx.strokeStyle = 'gray'; // 设置线条颜色为灰色
    // 设置虚线样式
    backgroundContainerCtx.setLineDash([5, 5]); // [5, 5]表示每5px绘制线条，然后间隔5px



    cycleInfo.value.forEach(item => {
      const x = (item.year - mainInfo.value.startYear) * ex + 100;
      // 绘制线条
      backgroundContainerCtx.beginPath();
      backgroundContainerCtx.moveTo(x, 0);
      backgroundContainerCtx.lineTo(x, 1400);
      backgroundContainerCtx.stroke();

      // 设置文本样式
      backgroundContainerCtx.fillStyle = 'black'; // 设置文字颜色
      backgroundContainerCtx.font = '16px Arial'; // 设置字体样式和大小
      backgroundContainerCtx.textAlign = 'center'; // 设置文本水平居中
      backgroundContainerCtx.textBaseline = 'middle'; // 设置文本垂直居中

      // 垂直文本（旋转90度）
      const angle = Math.PI / 2; // 90度旋转

      // 保存当前状态
      backgroundContainerCtx.save();

      // 移动坐标系到文本绘制位置
      backgroundContainerCtx.translate(x, 1416); // 设置文本绘制的坐标位置

      // 旋转文本坐标系 90 度
      backgroundContainerCtx.rotate(angle);

      // 绘制文本（此时文本会垂直显示）
      backgroundContainerCtx.fillText(item.cycle, 0, 0); // 文字位置相对于旋转后的坐标系

      // 恢复状态
      backgroundContainerCtx.restore();
    });
    // 计算初始点
    calculatePoints().then(() => {
      // 根据点画树
      drawTree()
    })
  })
})

const timeout = ref<ReturnType<typeof setTimeout> | null>(null);
// 鼠标移动处理
const move = (e: MouseEvent) => {
  if (!shade.value || !toolBox.value) return;

  // 清除之前的计时器
  if (timeout.value) {
    clearTimeout(timeout.value);
    toolBox.value.style.opacity = "0";
  }

  // 开始新的计时
  timeout.value = setTimeout(() => {
    const point: Point = {
      y: e.clientX,
      x: 1440 - e.clientY,
    };


    // 遍历检测区域
    let inArea = false;

    familySe.value.some((area) => {
      if (isInArea(area, point, "A家族")) {
        inArea = true;
        return true;
      }
    });

    if (!inArea && familyFi.value && isInArea(familyFi.value, point,"所有家族信息")) {
      inArea = true;
    }

    if (!inArea) {
      noFamilySe.value.some((area) => {
        if (isInArea(area, point, 'A地点')) {
          inArea = true;
          return true;
        }
      });
    }

    if (!inArea && noFamilyFi.value && isInArea(noFamilyFi.value, point, '所有没有家族诗人信息')) {
      inArea = true;
    }
  }, 500);
};

// 区域检测函数
const isInArea = (canvas: HTMLCanvasElement, point: Point, content: string): boolean => {
  const ctx = canvas.getContext("2d");
  if (!ctx || !toolBox.value) return false;

  if (ctx.isPointInPath(point.x, point.y)) {
    toolBox.value.style.opacity = "1";
    toolBox.value.style.left = `${point.x + 15}px`;
    toolBox.value.style.top = `${point.y + 10}px`;
    toolBox.value.innerText = content
    return true;
  }
  return false;
};

// 鼠标离开处理
const leave = () => {
  if (timeout.value) {
    clearTimeout(timeout.value);
    timeout.value = null;
  }
  if (toolBox.value) {
    toolBox.value.style.opacity = "0";
  }
};

// 鼠标单击事件
const click = () => {

}

// 鼠标刷选
const isSelecting = ref(false); // 是否正在刷选
const selectionStart = reactive({ x: 0, y: 0 }); // 选择框起点
const selectionEnd = reactive({ x: 0, y: 0 });   // 选择框终点
// 鼠标移动事件
const onMouseMove = (e: MouseEvent) => {
  if (!isSelecting.value || !container.value) return;

  // const rect = container.value.getBoundingClientRect();
  selectionEnd.y = e.clientX;
  selectionEnd.x = 1440 - e.clientY;
};
const startSelection = (e: MouseEvent) => {
  isSelecting.value = true

  selectionStart.x = 1440 - e.clientY;
  selectionStart.y = e.clientX;

  selectionEnd.x = selectionStart.x;
  selectionEnd.y = selectionStart.y;

  // 监听鼠标移动和抬起事件
  document.addEventListener("mousemove", onMouseMove);
  document.addEventListener("mouseup", endSelection);
}
const endSelection = () => {
  isSelecting.value = false;

  // 计算刷选框的边界
  const minX = Math.min(selectionStart.x, selectionEnd.x);
  const maxX = Math.max(selectionStart.x, selectionEnd.x);
  const minY = Math.min(selectionStart.y, selectionEnd.y);
  const maxY = Math.max(selectionStart.y, selectionEnd.y);

  // 判断每个 item 是否在刷选框内
  items.value.forEach((item) => {
    item.select =
      item.left >= minX &&
      item.left <= maxX &&
      item.top >= minY &&
      item.top <= maxY;
  });

  document.removeEventListener("mousemove", onMouseMove);
  document.removeEventListener("mouseup", endSelection);
  emitEvent()
}

const emitEvent = () => {
  const poetIds = ref<number[]>([])
  items.value.forEach((item) => {
    if (item.select) poetIds.value.push(item.poetId)
  })
  console.log(poetIds)
  eventBus.emit("treeSelect", poetIds)
}

const handleClick = (item: Flower) => {
  item.select = !item.select
  emitEvent()
}


</script>

<template>
  <div class="TreeChart" ref="container" @mousedown="startSelection">
    <canvas ref="backgroundContainer" style="margin-left: 100px;" width="750px" height="1440px"></canvas>
    <canvas ref="canvas" :width="width" :height="height"></canvas>
    <canvas ref="familyFi" :width="width" :height="height" style="opacity: 0;"></canvas>
    <canvas v-for="(item, index) in familySePointArea" :key="index" :ref="(el) => { familySe[index] = el }" :width="width" :height="height" style="opacity: 0;"></canvas>

    <canvas ref="noFamilyFi" :width="width" :height="height" style="opacity: 0;"></canvas>
    <canvas v-for="(item, index) in noFamilySePointArea" :key="index" :ref="(el) => { noFamilySe[index] = el }" :width="width" :height="height" style="opacity: 0;"></canvas>



    <div
      class="toolBox"
      ref="toolBox"
      style="
        position: absolute;
        left: 0;
        top: 0;
        width: 100px;
        height: 100px;
        background-color: #919495;
        opacity: 0;
        rotate: 90deg;
      "
    >
      提示框
    </div>

    <canvas
      ref="shade"
      :width="width"
      :height="height"
      @mousemove="move"
      @mouseleave="leave"
      @onclick="click"
    />

    <flower-view
      v-for="(item, index) in items"
      :key="index"
      style="position: absolute;"
      :style="{ left: item.left + 'px', top: item.top + 'px' }"
      :data=item
      @click="handleClick(item)"
    />

    <div
      v-if="isSelecting"
      class="selection-box"
      style="
        position: absolute;
        border: 2px dashed #0078d4;
        background-color: rgba(0, 120, 212, 0.2);
        pointer-events: none;
        left: 0;
        top: 0;
        height: 100px;
        width: 100px;
      "
      :style="{
        left: Math.min(selectionStart.x, selectionEnd.x) + 'px',
        top: Math.min(selectionStart.y, selectionEnd.y) + 'px',
        width: Math.abs(selectionEnd.x - selectionStart.x) + 'px',
        height: Math.abs(selectionEnd.y - selectionStart.y) + 'px'
      }"

    ></div>
  </div>
</template>

<style scoped>
.TreeChart {
  width: 880px;
  height: 1440px;
  /* background-color: blue; */
}

canvas {
  border: 0;
  position: absolute;
}
</style>


// 分支浮动，提示框里显示家族或者地区信息，诗人的数量，诗词数量，出一个诗词量最多的诗人

// 刷选花，在选框外的花和背景暗淡，里面的亮

// 鼠标单击花，控制多选
