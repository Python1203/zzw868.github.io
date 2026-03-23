import {useEffect, useRef} from "react";

/**
 * WebSocket 自定义 Hook，支持自动重连
 * @param url WebSocket 服务器地址
 * @param onMessage 消息处理回调
 */
export const useWebSocketWithReconnect = (
  url: string,
  onMessage: (data: any) => void
) => {
  const ws = useRef<WebSocket | null>(null);
  const reconnectTimeout = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttempts = useRef<number>(0);
  const maxReconnectAttempts = 5; // 最大重连次数

  const connect = () => {
    console.log(`尝试连接 WebSocket: ${url}`);
    ws.current = new WebSocket(url);

    ws.current.onopen = () => {
      console.log("✅ WebSocket 已连接");
      reconnectAttempts.current = 0;
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
        reconnectTimeout.current = null;
      }
    };

    ws.current.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        onMessage(message);
      } catch (error) {
        console.error("解析消息失败:", error);
      }
    };

    ws.current.onclose = () => {
      console.log("❌ WebSocket 已断开");
      
      if (reconnectAttempts.current < maxReconnectAttempts) {
        const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000);
        console.log(`${delay / 1000}秒后尝试重连... (第${reconnectAttempts.current + 1}次)`);
        
        reconnectTimeout.current = setTimeout(() => {
          reconnectAttempts.current += 1;
          connect();
        }, delay);
      } else {
        console.error("达到最大重连次数，停止重连");
      }
    };

    ws.current.onerror = (err) => {
      console.error("⚠️ WebSocket 错误:", err);
      ws.current?.close();
    };
  };

  useEffect(() => {
    connect();
    
    return () => {
      console.log("清理 WebSocket 连接");
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
      }
      ws.current?.close();
    };
  }, [url]);

  return ws.current;
};
