import React, {useState} from "react";
import {
    CartesianGrid,
    Cell,
    Legend,
    Line,
    LineChart,
    Pie,
    PieChart,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from "recharts";
import {useWebSocketWithReconnect} from "./hooks/useWebSocketWithReconnect";

type Prediction = {
  predictedPrice: number;
  predictedTrendProbability: number;
  timestamp: string;
};

const COLORS = ["#82ca9d", "#ff4d4f"]; // 绿色涨，红色跌

/**
 * 实时股票价格预测图表组件
 * 包含折线图（价格走势）和饼图（涨跌概率）
 */
const RealTimeStockChartWithPie = () => {
  const [data, setData] = useState<{ time: string; price: number }[]>([]);
  const [latestPrediction, setLatestPrediction] = useState<Prediction | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<"connecting" | "connected" | "disconnected">("connecting");

  useWebSocketWithReconnect("ws://localhost:8080", (message) => {
    if (message.type === "prediction") {
      const pred: Prediction = message.data;
      setLatestPrediction(pred);
      setConnectionStatus("connected");

      setData((prevData) => {
        const newEntry = {
          time: new Date(pred.timestamp).toLocaleTimeString(),
          price: Number(pred.predictedPrice),
        };
        const updatedData = [...prevData, newEntry].slice(-30); // 只保留最新 30 条数据
        return updatedData;
      });
    }
  });

  // 饼图数据：涨和跌概率
  const pieData =
    latestPrediction
      ? [
          { name: "涨", value: Math.round(latestPrediction.predictedTrendProbability * 100) },
          { name: "跌", value: Math.round((1 - latestPrediction.predictedTrendProbability) * 100) },
        ]
      : [];

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* 标题区域 */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            📊 金融AI实时预测系统
          </h1>
          <p className="text-gray-600">
            基于 WebSocket 的实时股票价格预测与涨跌概率分析
          </p>
          <div className="mt-4 flex items-center justify-center gap-4">
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${
              connectionStatus === "connected" 
                ? "bg-green-100 text-green-800" 
                : "bg-yellow-100 text-yellow-800"
            }`}>
              {connectionStatus === "connected" ? "🟢 已连接" : "🟡 连接中..."}
            </span>
            <span className="text-sm text-gray-500">
              数据更新频率：5 秒/次
            </span>
          </div>
        </div>

        {/* 主要内容区域 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* 左侧：价格趋势图 */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
              📈 实时股票价格预测趋势
            </h2>
            {data.length > 0 ? (
              <>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart
                    data={data}
                    margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                    <XAxis 
                      dataKey="time" 
                      minTickGap={20}
                      tick={{ fontSize: 12 }}
                    />
                    <YAxis 
                      domain={["auto", "auto"]}
                      tick={{ fontSize: 12 }}
                    />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: "#fff",
                        border: "1px solid #e0e0e0",
                        borderRadius: "8px"
                      }}
                    />
                    <Line
                      type="monotone"
                      dataKey="price"
                      stroke="#8884d8"
                      strokeWidth={3}
                      dot={{ fill: "#8884d8", r: 4 }}
                      activeDot={{ r: 6 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
                
                {latestPrediction && (
                  <div className="mt-6 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-4">
                    <div className="text-center">
                      <p className="text-sm text-gray-600 mb-1">最新预测价格</p>
                      <p className="text-3xl font-bold text-purple-700">
                        ¥{latestPrediction.predictedPrice.toFixed(2)}
                      </p>
                      <p className="text-xs text-gray-500 mt-2">
                        更新时间：{new Date(latestPrediction.timestamp).toLocaleString()}
                      </p>
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div className="flex items-center justify-center h-64">
                <p className="text-gray-400 text-lg">等待数据...</p>
              </div>
            )}
          </div>

          {/* 右侧：涨跌概率饼图 */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
              📉 涨跌概率分布
            </h2>
            {latestPrediction ? (
              <>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={pieData}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      outerRadius={100}
                      label={({ name, percent }) =>
                        `${name}: ${(percent! * 100).toFixed(1)}%`
                      }
                    >
                      {pieData.map((_, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index]} />
                      ))}
                    </Pie>
                    <Legend verticalAlign="bottom" height={36} />
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>

                {/* 详细统计信息 */}
                <div className="mt-6 grid grid-cols-2 gap-4">
                  <div className="bg-green-50 rounded-lg p-4 text-center">
                    <p className="text-sm text-gray-600 mb-1">上涨概率</p>
                    <p className="text-2xl font-bold text-green-700">
                      {(latestPrediction.predictedTrendProbability * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div className="bg-red-50 rounded-lg p-4 text-center">
                    <p className="text-sm text-gray-600 mb-1">下跌概率</p>
                    <p className="text-2xl font-bold text-red-700">
                      {((1 - latestPrediction.predictedTrendProbability) * 100).toFixed(1)}%
                    </p>
                  </div>
                </div>
              </>
            ) : (
              <div className="flex items-center justify-center h-64">
                <p className="text-gray-400 text-lg">等待数据...</p>
              </div>
            )}
          </div>
        </div>

        {/* 底部说明 */}
        <div className="mt-8 text-center text-gray-500 text-sm">
          <p>⚠️ 本系统仅为演示目的，不构成投资建议。实际投资请咨询专业人士。</p>
        </div>
      </div>
    </div>
  );
};

export default RealTimeStockChartWithPie;
