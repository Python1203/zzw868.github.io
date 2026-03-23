<template>
  <div class="dashboard">
    <div class="filter-panel">
      <label for="market-select">选择市场：</label>
      <select id="market-select" v-model="selectedMarket" @change="onMarketChange">
        <option v-for="market in markets" :key="market" :value="market">{{ market }}</option>
      </select>

      <label for="time-range">时间范围：</label>
      <select id="time-range" v-model="selectedRange" @change="onRangeChange">
        <option v-for="range in timeRanges" :key="range.value" :value="range.value">{{ range.label }}</option>
      </select>

      <label for="indicator-select">指标：</label>
      <select id="indicator-select" v-model="selectedIndicator" @change="onIndicatorChange">
        <option v-for="ind in indicators" :key="ind.value" :value="ind.value">{{ ind.label }}</option>
      </select>
    </div>

    <div class="charts-container">
      <div class="chart-wrapper">
        <h3>K线图 (Candlestick)</h3>
        <div ref="klineChartRef" class="chart"></div>
      </div>
      <div class="chart-wrapper">
        <h3>深度图 (Depth Chart)</h3>
        <div ref="depthChartRef" class="chart"></div>
      </div>
      <div class="chart-wrapper">
        <h3>成交量趋势</h3>
        <div ref="volumeChartRef" class="chart"></div>
      </div>
      <div class="chart-wrapper">
        <h3>价格趋势</h3>
        <div ref="priceChartRef" class="chart"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {onBeforeUnmount, onMounted, ref, watch} from 'vue';
import {createPinia, defineStore} from 'pinia';
import * as echarts from 'echarts/core';
import {BarChart, CandlestickChart, LineChart,} from 'echarts/charts';
import {
  DataZoomComponent,
  GridComponent,
  LegendComponent,
  TitleComponent,
  ToolboxComponent,
  TooltipComponent,
  VisualMapComponent,
} from 'echarts/components';
import {CanvasRenderer} from 'echarts/renderers';

// 注册必须的组件
echarts.use([
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  DataZoomComponent,
  VisualMapComponent,
  ToolboxComponent,
  LineChart,
  BarChart,
  CandlestickChart,
  CanvasRenderer,
]);

// Pinia 状态管理
const useMarketStore = defineStore('market', () => {
  const selectedMarket = ref('BTC-USD');
  const selectedRange = ref('1d');
  const selectedIndicator = ref('none');

  // 数据结构： [timestamp, open, close, low, high, volume]
  const klineData = ref([]);
  const depthData = ref({ bids: [], asks: [] });
  const priceData = ref([]);
  const volumeData = ref([]);

  let ws = null;

  // 真实 WebSocket 连接示例 (Binance Spot)
  function connectWebSocket() {
    if (ws) {
      ws.close();
      ws = null;
    }
    // Binance Kline WebSocket 地址示例，市场和时间范围动态拼接
    const streamName = `${selectedMarket.value.toLowerCase().replace('-', '')}@kline_${selectedRange.value}`;
    const url = `wss://stream.binance.com:9443/ws/${streamName}`;
    ws = new WebSocket(url);

    ws.onopen = () => {
      console.log('WebSocket 已连接:', url);
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.e === 'kline') {
        const k = message.k;
        // 更新K线数据：时间戳, open, close, low, high, volume
        const newCandle = [
          k.t,
          parseFloat(k.o),
          parseFloat(k.c),
          parseFloat(k.l),
          parseFloat(k.h),
          parseFloat(k.v),
        ];
        updateKlineData(newCandle);
        updatePriceAndVolume(newCandle);
      }
    };

    ws.onclose = () => {
      console.log('WebSocket 连接关闭');
    };

    ws.onerror = (err) => {
      console.error('WebSocket 错误:', err);
    };
  }

  // 更新K线数据，保持最新30条
  function updateKlineData(newCandle) {
    const idx = klineData.value.findIndex(c => c[0] === newCandle[0]);
    if (idx !== -1) {
      klineData.value[idx] = newCandle;
    } else {
      klineData.value.push(newCandle);
      if (klineData.value.length > 30) {
        klineData.value.shift();
      }
    }
  }

  // 更新价格和成交量数据
  function updatePriceAndVolume(newCandle) {
    const timeStr = new Date(newCandle[0]).toLocaleTimeString();
    const pricePoint = [timeStr, newCandle[2]]; // close price
    const volumePoint = [timeStr, newCandle[5]]; // volume

    // 更新价格数据
    if (priceData.value.length > 0 && priceData.value[priceData.value.length -1][0] === timeStr) {
      priceData.value[priceData.value.length -1] = pricePoint;
    } else {
      priceData.value.push(pricePoint);
      if (priceData.value.length > 30) priceData.value.shift();
    }

    // 更新成交量数据
    if (volumeData.value.length > 0 && volumeData.value[volumeData.value.length -1][0] === timeStr) {
      volumeData.value[volumeData.value.length -1] = volumePoint;
    } else {
      volumeData.value.push(volumePoint);
      if (volumeData.value.length > 30) volumeData.value.shift();
    }
  }

  // 模拟深度数据（真实项目应调用API）
  function generateDepthData() {
    const bids = [];
    const asks = [];
    const base = 50000;
    for (let i = 0; i < 20; i++) {
      bids.push([base - i * 50, Math.random() * 10 + 5]);
      asks.push([base + i * 50, Math.random() * 10 + 5]);
    }
    depthData.value = { bids, asks };
  }

  // 计算技术指标：MA、BOLL、MACD
  function calculateMA(dayCount, data) {
    const result = [];
    for (let i = 0; i < data.length; i++) {
      if (i < dayCount - 1) {
        result.push(null);
        continue;
      }
      let sum = 0;
      for (let j = 0; j < dayCount; j++) {
        sum += data[i - j][2]; // close price
      }
      result.push(sum / dayCount);
    }
    return result;
  }

  function calculateBOLL(data, period = 20) {
    const close = data.map(d => d[2]);
    const middle = calculateMA(period, data);
    const stddev = [];
    for (let i = 0; i < data.length; i++) {
      if (i < period - 1) {
        stddev.push(null);
        continue;
      }
      let sum = 0;
      for (let j = 0; j < period; j++) {
        sum += Math.pow(close[i - j] - middle[i], 2);
      }
      stddev.push(Math.sqrt(sum / period));
    }
    const upper = middle.map((m, i) => (m !== null && stddev[i] !== null ? m + 2 * stddev[i] : null));
    const lower = middle.map((m, i) => (m !== null && stddev[i] !== null ? m - 2 * stddev[i] : null));
    return { middle, upper, lower };
  }

  function calculateMACD(data, shortPeriod = 12, longPeriod = 26, signalPeriod = 9) {
    const close = data.map(d => d[2]);
    const ema = (period, data) => {
      const k = 2 / (period + 1);
      const emaArr = [];
      emaArr[0] = data[0];
      for (let i = 1; i < data.length; i++) {
        emaArr[i] = data[i] * k + emaArr[i - 1] * (1 - k);
      }
      return emaArr;
    };
    const emaShort = ema(shortPeriod, close);
    const emaLong = ema(longPeriod, close);
    const dif = emaShort.map((v, i) => v - emaLong[i]);
    const dea = ema(signalPeriod, dif);
    const macd = dif.map((v, i) => 2 * (v - dea[i]));
    return { dif, dea, macd };
  }

  return {
    selectedMarket,
    selectedRange,
    selectedIndicator,
    klineData,
    depthData,
    priceData,
    volumeData,
    connectWebSocket,
    generateDepthData,
    calculateMA,
    calculateBOLL,
    calculateMACD,
    updateKlineData,
    updatePriceAndVolume,
  };
});

// 创建Pinia实例
const pinia = createPinia();
const store = useMarketStore(pinia);

const selectedMarket = ref(store.selectedMarket.value);
const selectedRange = ref(store.selectedRange.value);
const selectedIndicator = ref(store.selectedIndicator.value);

const markets = ['BTC-USD', 'ETH-USD', 'LTC-USD'];
const timeRanges = [
  { label: '1分钟', value: '1m' },
  { label: '5分钟', value: '5m' },
  { label: '15分钟', value: '15m' },
  { label: '1小时', value: '1h' },
  { label: '1天', value: '1d' },
];
const indicators = [
  { label: '无', value: 'none' },
  { label: 'MA (移动平均)', value: 'ma' },
  { label: 'BOLL (布林线)', value: 'boll' },
  { label: 'MACD', value: 'macd' },
];

const klineChartRef = ref(null);
const depthChartRef = ref(null);
const priceChartRef = ref(null);
const volumeChartRef = ref(null);

let klineChart = null;
let depthChart = null;
let priceChart = null;
let volumeChart = null;

function initCharts() {
  if (klineChartRef.value) klineChart = echarts.init(klineChartRef.value);
  if (depthChartRef.value) depthChart = echarts.init(depthChartRef.value);
  if (priceChartRef.value) priceChart = echarts.init(priceChartRef.value);
  if (volumeChartRef.value) volumeChart = echarts.init(volumeChartRef.value);
}

// K线图配置，支持多指标
function getKlineOption() {
  const data = store.klineData.value;
  const categoryData = data.map(item => new Date(item[0]).toLocaleString());
  const values = data.map(item => [item[1], item[2], item[3], item[4]]);
  const volumes = data.map(item => item[5]);

  const series = [
    {
      name: 'K线',
      type: 'candlestick',
      data: values,
      itemStyle: {
        color: '#ff00ff',
        color0: '#00ffff',
        borderColor: '#ff00ff',
        borderColor0: '#00ffff',
      },
    },
    {
      name: '成交量',
      type: 'bar',
      xAxisIndex: 1,
      yAxisIndex: 1,
      data: volumes,
      itemStyle: {
        color: '#ff00ff',
      },
    },
  ];

  if (store.selectedIndicator.value === 'ma') {
    const ma5 = store.calculateMA(5, data);
    series.push({
      name: 'MA5',
      type: 'line',
      data: ma5,
      smooth: true,
      lineStyle: { color: '#00ffff' },
    });
  } else if (store.selectedIndicator.value === 'boll') {
    const boll = store.calculateBOLL(data);
    series.push(
      {
        name: 'BOLL中轨',
        type: 'line',
        data: boll.middle,
        smooth: true,
        lineStyle: { color: '#ffff00' },
      },
      {
        name: 'BOLL上轨',
        type: 'line',
        data: boll.upper,
        smooth: true,
        lineStyle: { color: '#ffaa00' },
      },
      {
        name: 'BOLL下轨',
        type: 'line',
        data: boll.lower,
        smooth: true,
        lineStyle: { color: '#ffaa00' },
      }
    );
  } else if (store.selectedIndicator.value === 'macd') {
    const macd = store.calculateMACD(data);
    series.push(
      {
        name: 'DIF',
        type: 'line',
        data: macd.dif,
        smooth: true,
        lineStyle: { color: '#00ffff' },
      },
      {
        name: 'DEA',
        type: 'line',
        data: macd.dea,
        smooth: true,
        lineStyle: { color: '#ff00ff' },
      },
      {
        name: 'MACD',
        type: 'bar',
        data: macd.macd,
        itemStyle: { color: '#ffaa00' },
        xAxisIndex: 2,
        yAxisIndex: 2,
      }
    );
  }

  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
    },
    legend: {
      data: series.map(s => s.name),
      textStyle: { color: '#fff' },
    },
    grid: [
      { left: '10%', right: '8%', height: '55%' },
      { left: '10%', right: '8%', top: '65%', height: '15%' },
      { left: '10%', right: '8%', top: '85%', height: '10%' },
    ],
    xAxis: [
      {
        type: 'category',
        data: categoryData,
        scale: true,
        boundaryGap: false,
        axisLine: { lineStyle: { color: '#00ffff' } },
        splitLine: { show: false },
        axisTick: { alignWithLabel: true },
        axisLabel: { color: '#00ffff' },
        min: 'dataMin',
        max: 'dataMax',
      },
      {
        type: 'category',
        gridIndex: 1,
        data: categoryData,
        axisLine: { lineStyle: { color: '#00ffff' } },
        axisTick: { alignWithLabel: true },
        axisLabel: { show: false },
      },
      {
        type: 'category',
        gridIndex: 2,
        data: categoryData,
        axisLine: { lineStyle: { color: '#00ffff' } },
        axisTick: { alignWithLabel: true },
        axisLabel: { show: false },
      },
    ],
    yAxis: [
      {
        scale: true,
        splitArea: { show: true, areaStyle: { color: ['#111122', '#222233'] } },
        axisLine: { lineStyle: { color: '#00ffff' } },
        splitLine: { lineStyle: { color: '#003333' } },
        axisLabel: { color: '#00ffff' },
      },
      {
        gridIndex: 1,
        splitNumber: 2,
        axisLine: { lineStyle: { color: '#00ffff' } },
        axisLabel: { color: '#00ffff' },
        axisTick: { show: false },
        splitLine: { show: false },
      },
      {
        gridIndex: 2,
        splitNumber: 2,
        axisLine: { lineStyle: { color: '#00ffff' } },
        axisLabel: { color: '#00ffff' },
        axisTick: { show: false },
        splitLine: { show: false },
      },
    ],
    dataZoom: [
      {
        type: 'inside',
        xAxisIndex: [0, 1, 2],
        start: 50,
        end: 100,
      },
      {
        show: true,
        xAxisIndex: [0, 1, 2],
        type: 'slider',
        top: '90%',
        start: 50,
        end: 100,
        textStyle: { color: '#00ffff' },
      },
    ],
    toolbox: {
      feature: {
        saveAsImage: { title: '保存为图片' },
        dataZoom: { title: { zoom: '区域缩放', back: '区域缩放还原' } },
        restore: { title: '还原' },
      },
      iconStyle: {
        borderColor: '#00ffff',
      },
    },
    series,
  };
}

// 深度图配置
function getDepthOption() {
  const bids = store.depthData.value.bids || [];
  const asks = store.depthData.value.asks || [];

  function accumulate(data) {
    let sum = 0;
    return data.map(([price, volume]) => {
      sum += volume;
      return [price, sum];
    });
  }

  const bidData = accumulate(bids.slice().reverse());
  const askData = accumulate(asks);

  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'value',
      scale: true,
      axisLine: { lineStyle: { color: '#00ffff' } },
      splitLine: { lineStyle: { color: '#003333' } },
      axisLabel: { color: '#00ffff' },
    },
    yAxis: {
      type: 'value',
      scale: true,
      axisLine: { lineStyle: { color: '#00ffff' } },
      splitLine: { lineStyle: { color: '#003333' } },
      axisLabel: { color: '#00ffff' },
    },
    series: [
      {
        name: '买入',
        type: 'line',
        step: 'end',
        data: bidData,
        itemStyle: { color: '#00ff00' },
        areaStyle: { color: 'rgba(0,255,0,0.3)' },
        lineStyle: { width: 2 },
      },
      {
        name: '卖出',
        type: 'line',
        step: 'start',
        data: askData,
        itemStyle: { color: '#ff0000' },
        areaStyle: { color: 'rgba(255,0,0,0.3)' },
        lineStyle: { width: 2 },
      },
    ],
    legend: {
      data: ['买入', '卖出'],
      textStyle: { color: '#00ffff' },
    },
    toolbox: {
      feature: {
        saveAsImage: { title: '保存为图片' },
        restore: { title: '还原' },
      },
      iconStyle: {
        borderColor: '#00ffff',
      },
    },
  };
}

// 价格趋势图配置
function getPriceOption() {
  const data = store.priceData.value;
  const times = data.map(item => item[0]);
  const prices = data.map(item => item[1]);
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: times,
      axisLine: { lineStyle: { color: '#00ffff' } },
      axisLabel: { color: '#00ffff' },
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#00ffff' } },
      splitLine: { lineStyle: { color: '#003333' } },
      axisLabel: { color: '#00ffff' },
    },
    series: [{
      data: prices,
      type: 'line',
      smooth: true,
      lineStyle: { color: '#ff00ff', width: 3 },
      areaStyle: { color: 'rgba(255,0,255,0.3)' },
    }],
    toolbox: {
      feature: {
        saveAsImage: { title: '保存为图片' },
        restore: { title: '还原' },
      },
      iconStyle: {
        borderColor: '#00ffff',
      },
    },
  };
}

// 成交量趋势图配置
function getVolumeOption() {
  const data = store.volumeData.value;
  const times = data.map(item => item[0]);
  const volumes = data.map(item => item[1]);
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: times,
      axisLine: { lineStyle: { color: '#00ffff' } },
      axisLabel: { color: '#00ffff' },
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#00ffff' } },
      splitLine: { lineStyle: { color: '#003333' } },
      axisLabel: { color: '#00ffff' },
    },
    series: [{
      data: volumes,
      type: 'bar',
      itemStyle: { color: '#ff00ff' },
      barMaxWidth: '20px',
    }],
    toolbox: {
      feature: {
        saveAsImage: { title: '保存为图片' },
        restore: { title: '还原' },
      },
      iconStyle: {
        borderColor: '#00ffff',
      },
    },
  };
}

function updateAllCharts() {
  if (klineChart) klineChart.setOption(getKlineOption());
  if (depthChart) depthChart.setOption(getDepthOption());
  if (priceChart) priceChart.setOption(getPriceOption());
  if (volumeChart) volumeChart.setOption(getVolumeOption());
}

function linkCharts() {
  if (klineChart && volumeChart) {
    echarts.connect([klineChart, volumeChart]);
  }
}

function onMarketChange() {
  store.selectedMarket.value = selectedMarket.value;
  store.connectWebSocket();
  store.generateDepthData();
}
function onRangeChange() {
  store.selectedRange.value = selectedRange.value;
  store.connectWebSocket();
}
function onIndicatorChange() {
  store.selectedIndicator.value = selectedIndicator.value;
}

function resizeCharts() {
  klineChart?.resize();
  depthChart?.resize();
  priceChart?.resize();
  volumeChart?.resize();
}
window.addEventListener('resize', resizeCharts);

onMounted(() => {
  initCharts();
  store.generateDepthData();
  store.connectWebSocket();
  updateAllCharts();
  linkCharts();

  // 监听数据变化自动更新图表
  watch(
    () => [store.klineData.value, store.depthData.value, store.priceData.value, store.volumeData.value, store.selectedIndicator.value],
    () => updateAllCharts(),
    { deep: true }
  );

  onBeforeUnmount(() => {
    window.removeEventListener('resize', resizeCharts);
    klineChart?.dispose();
    depthChart?.dispose();
    priceChart?.dispose();
    volumeChart?.dispose();
    if (store.ws) store.ws.close();
  });
});

watch(selectedMarket, (v) => (store.selectedMarket.value = v));
watch(selectedRange, (v) => (store.selectedRange.value = v));
watch(selectedIndicator, (v) => (store.selectedIndicator.value = v));
watch(store.selectedMarket, (v) => (selectedMarket.value = v));
watch(store.selectedRange, (v) => (selectedRange.value = v));
watch(store.selectedIndicator, (v) => (selectedIndicator.value = v));
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Orbitron&display=swap');

.dashboard {
  max-width: 1100px;
  margin: 20px auto;
  font-family: 'Orbitron', sans-serif;
  color: #00ffff;
  background: #0a0a14;
  padding: 20px;
  border-radius: 20px;
  box-shadow:
    0 0 20px #00ffff,
    inset 0 0 40px #00ffff;
}

.filter-panel {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}
label {
  font-weight: bold;
}
select {
  background: #111122;
  border: 2px solid #ff00ff;
  border-radius: 8px;
  padding: 6px 12px;
  color: #ff00ff;
  font-weight: bold;
  font-size: 1rem;
  cursor: pointer;
  box-shadow:
    0 0 10px #ff00ff;
  transition: border-color 0.3s ease;
}
select:hover,
select:focus {
  border-color: #00ffff;
  outline: none;
  box-shadow:
    0 0 20px #00ffff;
}

.charts-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
  gap: 20px;
}

.chart-wrapper {
  background: #111122;
  border-radius: 15px;
  padding: 15px;
  box-shadow:
    0 0 15px #ff00ff;
}
.chart-wrapper h3 {
  text-align: center;
  margin-bottom: 10px;
  color: #ff00ff;
  text-shadow:
    0 0 10px #ff00ff;
}
.chart {
  width: 100%;
  height: 320px;
}
</style>
