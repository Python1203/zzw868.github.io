import React, {useCallback, useEffect, useMemo, useState} from "react";

// 牌型常量定义
const SUITS = ['♠', '♥', '♦', '♣'];
const RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A'];

// AI 决策模型配置
const AI_CONFIG = {
  // 激进程度阈值
  aggressiveThreshold: 0.65,
  conservativeThreshold: 0.4,
  // 下注模式
  bettingPatterns: {
    tight: { raiseFreq: 0.2, callFreq: 0.5, foldFreq: 0.3 },
    normal: { raiseFreq: 0.35, callFreq: 0.45, foldFreq: 0.2 },
    loose: { raiseFreq: 0.5, callFreq: 0.35, foldFreq: 0.15 }
  },
  // 学习率
  learningRate: 0.1,
  // 记忆深度
  memoryDepth: 20
};

// 创建牌组
function createDeck() {
  const deck = [];
  for (const suit of SUITS) {
    for (const rank of RANKS) {
      deck.push({ 
        suit, 
        rank, 
        id: rank + suit,
        value: RANKS.indexOf(rank)
      });
    }
  }
  return deck;
}

// 优化版洗牌算法 (Fisher-Yates)
function shuffle(deck) {
  const shuffled = [...deck];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
}

// 牌面颜色样式
function cardColor(suit) {
  return suit === '♥' || suit === '♦' ? "text-red-500" : "text-cyan-400";
}

// 缓存键生成优化
function cacheKey(aiHand, communityCards) {
  const aiStr = aiHand.map(c => c.rank + c.suit).sort().join('');
  const commStr = communityCards.map(c => c.rank + c.suit).sort().join('');
  return aiStr + '|' + commStr;
}

// AI 行为分析器
class AIBehaviorAnalyzer {
  constructor() {
    this.history = [];
    this.playerProfile = {
      aggression: 0.5,
      tightness: 0.5,
      predictability: 0.5
    };
  }

  recordAction(action, winRate, phase) {
    this.history.push({ action, winRate, phase, timestamp: Date.now() });
    if (this.history.length > AI_CONFIG.memoryDepth) {
      this.history.shift();
    }
    this.updatePlayerProfile();
  }

  updatePlayerProfile() {
    if (this.history.length === 0) return;

    const raiseCount = this.history.filter(h => h.action === 'raise').length;
    const foldCount = this.history.filter(h => h.action === 'fold').length;
    
    // 计算激进指数
    this.playerProfile.aggression = raiseCount / this.history.length;
    
    // 计算紧松指数
    this.playerProfile.tightness = foldCount / this.history.length;
    
    // 计算可预测性
    const actionCounts = {};
    this.history.forEach(h => {
      actionCounts[h.action] = (actionCounts[h.action] || 0) + 1;
    });
    const maxActionFreq = Math.max(...Object.values(actionCounts)) / this.history.length;
    this.playerProfile.predictability = maxActionFreq;
  }

  getRecommendation(winRate, currentBet, potOdds) {
    const profile = this.playerProfile;
    
    // 根据对手风格调整策略
    if (profile.aggression > 0.6) {
      // 对手激进，采用保守策略
      return winRate > 0.5 ? 'call' : 'fold';
    } else if (profile.tightness > 0.5) {
      // 对手保守，可以激进
      return winRate > 0.4 ? 'raise' : 'check';
    }
    
    // 默认策略
    if (winRate > 0.7) return 'raise';
    if (winRate > 0.5) return 'call';
    if (winRate > 0.3 && potOdds > 0.25) return 'call';
    return 'fold';
  }
}

// 主组件
export default function CyberpunkPokerAI() {
  // 游戏状态管理
  const [gameState, setGameState] = useState({
    deck: [],
    playerHand: [],
    aiHand: [],
    communityCards: [],
    pot: 0,
    playerChips: 1000,
    aiChips: 1000,
    currentBet: 10,
    phase: 'start',
    waitingForPlayer: false,
    lastAction: null
  });

  // UI 状态
  const [uiState, setUiState] = useState({
    message: "⚡ 赛博朋克 AI 德州扑克启动 ⚡",
    winRate: null,
    aiReason: "",
    playerAction: null,
    aiAction: null,
    showAnalysis: false,
    difficulty: 'medium'
  });

  // AI 分析器实例
  const behaviorAnalyzer = useMemo(() => new AIBehaviorAnalyzer(), []);
  const winRateCache = useMemo(() => new Map(), []);
  const workerRef = React.useRef(null);

  // Worker 初始化和管理
  useEffect(() => {
    const initWorker = () => {
      if (workerRef.current) {
        workerRef.current.terminate();
      }
      
      workerRef.current = new Worker('/workers/monteCarloWorker.js');
      
      workerRef.current.onmessage = (e) => {
        const { winRate, confidenceInterval, accuracy } = e.data;
        setUiState(prev => ({
          ...prev,
          winRate,
          confidenceInterval,
          accuracy
        }));
        
        // 更新缓存
        if (gameState.aiHand.length > 0) {
          const key = cacheKey(gameState.aiHand, gameState.communityCards);
          winRateCache.set(key, winRate);
        }
      };

      workerRef.current.onerror = (error) => {
        console.error('Worker error:', error);
        setUiState(prev => ({
          ...prev,
          message: "⚠️ AI 计算模块异常，请重试"
        }));
      };
    };

    initWorker();

    return () => {
      if (workerRef.current) {
        workerRef.current.terminate();
      }
    };
  }, []);

  // 智能胜率计算
  const calculateWinRate = useCallback((aiHand, communityCards, deck, simulations = 500) => {
    if (aiHand.length === 0) return;

    const key = cacheKey(aiHand, communityCards);
    if (winRateCache.has(key)) {
      setUiState(prev => ({ ...prev, winRate: winRateCache.get(key) }));
      return;
    }

    if (workerRef.current) {
      workerRef.current.postMessage({
        aiHand,
        communityCards,
        deck,
        simulations,
        difficulty: uiState.difficulty
      });
    }
  }, [uiState.difficulty]);

  // AI 决策引擎增强版
  const aiDecisionEngine = useCallback((winRate, betAmount, potSize, chipsRemaining) => {
    if (winRate === null) {
      return { 
        action: "check", 
        amount: 0, 
        reason: "等待胜率计算完成",
        confidence: 0
      };
    }

    // 计算底池赔率
    const potOdds = betAmount / (potSize + betAmount);
    
    // 期望值计算
    const expectedValue = (winRate * (potSize + betAmount)) - ((1 - winRate) * betAmount);
    
    // 风险系数
    const riskFactor = betAmount / chipsRemaining;
    
    // 基础决策
    let decision;
    let confidence = 0;

    if (winRate > 0.8 && expectedValue > 0) {
      decision = {
        action: "raise",
        amount: Math.min(betAmount * 3, chipsRemaining),
        reason: `超强牌力！胜率${(winRate*100).toFixed(1)}%，EV+${expectedValue.toFixed(1)}`
      };
      confidence = 0.9;
    } else if (winRate > 0.65 && expectedValue > 0) {
      decision = {
        action: "raise",
        amount: Math.min(betAmount * 2, chipsRemaining),
        reason: `优势局面，胜率${(winRate*100).toFixed(1)}%，价值加注`
      };
      confidence = 0.8;
    } else if (winRate > 0.5) {
      decision = {
        action: "call",
        amount: betAmount,
        reason: `中等牌力，胜率${(winRate*100).toFixed(1)}%，跟注观察`
      };
      confidence = 0.7;
    } else if (winRate > 0.35 && potOdds > 0.2) {
      decision = {
        action: "call",
        amount: betAmount,
        reason: `底池赔率合适，胜率${(winRate*100).toFixed(1)}%，值得跟注`
      };
      confidence = 0.6;
    } else if (winRate > 0.2) {
      decision = {
        action: "check",
        amount: 0,
        reason: `牌力较弱，胜率${(winRate*100).toFixed(1)}%，控制损失`
      };
      confidence = 0.5;
    } else {
      decision = {
        action: "fold",
        amount: 0,
        reason: `胜率低${(winRate*100).toFixed(1)}%，及时止损`
      };
      confidence = 0.8;
    }

    // 添加心理战因素
    const randomFactor = Math.random();
    if (randomFactor < 0.1 && decision.action !== 'fold') {
      decision.reason += " 🎭 诈唬模式";
      decision.isBluff = true;
    }

    return { ...decision, confidence, expectedValue };
  }, []);

  // 游戏控制函数
  const startGame = useCallback(() => {
    const newDeck = shuffle(createDeck());
    const pHand = [newDeck.pop(), newDeck.pop()];
    const aHand = [newDeck.pop(), newDeck.pop()];
    
    setGameState(prev => ({
      ...prev,
      deck: newDeck,
      playerHand: pHand,
      aiHand: aHand,
      communityCards: [],
      pot: 20,
      currentBet: 10,
      playerChips: prev.playerChips - 10,
      aiChips: prev.aiChips - 10,
      phase: 'preflop',
      waitingForPlayer: true,
      lastAction: null
    }));

    setUiState(prev => ({
      ...prev,
      message: "📤 发牌完成，翻牌前阶段。请行动！",
      winRate: null,
      aiReason: "",
      playerAction: null,
      aiAction: null
    }));

    behaviorAnalyzer.history = [];
  }, [behaviorAnalyzer]);

  // 玩家行动处理
  const handlePlayerAction = useCallback((action, customAmount = null) => {
    if (!gameState.waitingForPlayer) return;

    const { playerChips, currentBet, pot } = gameState;

    if (action === "fold") {
      setGameState(prev => ({
        ...prev,
        aiChips: prev.aiChips + prev.pot,
        phase: 'showdown'
      }));
      setUiState(prev => ({
        ...prev,
        message: "👤 你弃牌，AI 获胜",
        playerAction: "fold"
      }));
      behaviorAnalyzer.recordAction('fold', uiState.winRate, gameState.phase);
      return;
    }

    if (action === "call") {
      if (playerChips < currentBet) {
        setUiState(prev => ({ ...prev, message: "❌ 筹码不足，无法跟注" }));
        return;
      }
      
      setGameState(prev => ({
        ...prev,
        playerChips: prev.playerChips - currentBet,
        pot: prev.pot + currentBet,
        waitingForPlayer: false,
        phase: 'aiTurn'
      }));
      
      setUiState(prev => ({
        ...prev,
        message: `✅ 你跟注 ${currentBet} 筹码，AI 思考中...`,
        playerAction: "call"
      }));
      
      behaviorAnalyzer.recordAction('call', uiState.winRate, gameState.phase);
      return;
    }

    if (action === "raise") {
      const raiseAmount = customAmount || currentBet * 2;
      if (playerChips < raiseAmount) {
        setUiState(prev => ({ ...prev, message: "❌ 筹码不足，无法加注" }));
        return;
      }
      
      setGameState(prev => ({
        ...prev,
        playerChips: prev.playerChips - raiseAmount,
        pot: prev.pot + raiseAmount,
        currentBet: raiseAmount,
        waitingForPlayer: false,
        phase: 'aiTurn'
      }));
      
      setUiState(prev => ({
        ...prev,
        message: `🔥 你加注到 ${raiseAmount} 筹码，AI 应对中...`,
        playerAction: "raise"
      }));
      
      behaviorAnalyzer.recordAction('raise', uiState.winRate, gameState.phase);
      return;
    }

    if (action === "check") {
      setGameState(prev => ({
        ...prev,
        waitingForPlayer: false,
        phase: 'aiTurn'
      }));
      
      setUiState(prev => ({
        ...prev,
        message: "✋ 你过牌，AI 决策中...",
        playerAction: "check"
      }));
      
      behaviorAnalyzer.recordAction('check', uiState.winRate, gameState.phase);
      return;
    }
  }, [gameState, uiState.winRate, behaviorAnalyzer]);

  // AI 回合处理
  useEffect(() => {
    if (gameState.phase === 'aiTurn' && gameState.aiHand.length > 0) {
      // 计算胜率
      calculateWinRate(
        gameState.aiHand, 
        gameState.communityCards, 
        gameState.deck,
        uiState.difficulty === 'easy' ? 300 : 
        uiState.difficulty === 'hard' ? 1000 : 500
      );
    }
  }, [gameState.phase, gameState.aiHand, gameState.communityCards, gameState.deck, uiState.difficulty, calculateWinRate]);

  // AI 执行决策
  useEffect(() => {
    if (gameState.phase === 'aiTurn' && uiState.winRate !== null) {
      const timer = setTimeout(() => {
        const decision = aiDecisionEngine(
          uiState.winRate,
          gameState.currentBet,
          gameState.pot,
          gameState.aiChips
        );

        setUiState(prev => ({
          ...prev,
          aiReason: `${decision.reason} (信心：${(decision.confidence*100).toFixed(0)}%)`,
          aiAction: decision.action
        }));

        // 执行 AI 行动
        if (decision.action === "fold") {
          setGameState(prev => ({
            ...prev,
            playerChips: prev.playerChips + prev.pot,
            phase: 'showdown'
          }));
          setUiState(prev => ({
            ...prev,
            message: `🤖 AI 弃牌，你获胜！(${decision.reason})`
          }));
          return;
        }

        if (decision.action === "check") {
          setGameState(prev => ({
            ...prev,
            waitingForPlayer: true,
            phase: 'playerTurn'
          }));
          setUiState(prev => ({
            ...prev,
            message: `🤖 AI 过牌，轮到你行动 (${decision.reason})`
          }));
          return;
        }

        if (decision.action === "call") {
          if (gameState.aiChips < gameState.currentBet) {
            setGameState(prev => ({
              ...prev,
              playerChips: prev.playerChips + prev.pot,
              phase: 'showdown'
            }));
            setUiState(prev => ({
              ...prev,
              message: `🤖 AI 筹码不足，你获胜！(${decision.reason})`
            }));
            return;
          }
          
          setGameState(prev => ({
            ...prev,
            aiChips: prev.aiChips - gameState.currentBet,
            pot: prev.pot + gameState.currentBet,
            waitingForPlayer: true,
            phase: 'playerTurn'
          }));
          setUiState(prev => ({
            ...prev,
            message: `🤖 AI 跟注 ${gameState.currentBet} 筹码 (${decision.reason})`
          }));
          return;
        }

        if (decision.action === "raise") {
          if (gameState.aiChips < decision.amount) {
            setGameState(prev => ({
              ...prev,
              playerChips: prev.playerChips + prev.pot,
              phase: 'showdown'
            }));
            setUiState(prev => ({
              ...prev,
              message: `🤖 AI 筹码不足，你获胜！(${decision.reason})`
            }));
            return;
          }
          
          setGameState(prev => ({
            ...prev,
            aiChips: prev.aiChips - decision.amount,
            pot: prev.pot + decision.amount,
            currentBet: decision.amount,
            waitingForPlayer: true,
            phase: 'playerTurn'
          }));
          setUiState(prev => ({
            ...prev,
            message: `🤖 AI 加注到 ${decision.amount} 筹码！(${decision.reason})`
          }));
          return;
        }
      }, 1500);

      return () => clearTimeout(timer);
    }
  }, [uiState.winRate, gameState.phase, gameState.currentBet, gameState.aiChips, gameState.pot, aiDecisionEngine]);

  // 摊牌判断赢家
  const determineWinner = useCallback(() => {
    if (gameState.playerAction === "fold") return "AI 获胜";
    if (gameState.aiAction === "fold") return "你获胜";

    // 简化版比牌逻辑 (实际应使用更复杂的牌型比较)
    const playerMax = Math.max(...gameState.playerHand.map(c => c.value));
    const aiMax = Math.max(...gameState.aiHand.map(c => c.value));

    if (playerMax > aiMax) {
      setGameState(prev => ({
        ...prev,
        playerChips: prev.playerChips + prev.pot
      }));
      return "🏆 你获胜";
    }
    if (aiMax > playerMax) {
      setGameState(prev => ({
        ...prev,
        aiChips: prev.aiChips + prev.pot
      }));
      return "🤖 AI 获胜";
    }
    
    // 平局分池
    const halfPot = Math.floor(gameState.pot / 2);
    setGameState(prev => ({
      ...prev,
      playerChips: prev.playerChips + halfPot,
      aiChips: prev.aiChips + halfPot
    }));
    return "🤝 平局";
  }, [gameState]);

  // 重置游戏
  const resetGame = useCallback(() => {
    setGameState(prev => ({
      ...prev,
      pot: 0,
      currentBet: 10,
      playerHand: [],
      aiHand: [],
      communityCards: [],
      phase: 'start',
      waitingForPlayer: false
    }));
    
    setUiState(prev => ({
      ...prev,
      message: "⚡ 准备新一局，点击开始！ ⚡",
      winRate: null,
      aiReason: ""
    }));
  }, []);

  // 渲染组件
  return (
    <div className="min-h-screen bg-gradient-to-tr from-purple-900 via-pink-900 to-black text-white font-mono p-6">
      {/* 头部 */}
      <div className="text-center mb-6">
        <h1 className="text-4xl mb-2 neon-text">🤖 赛博朋克 AI 德州扑克</h1>
        <p className="text-sm text-cyan-400">增强版 AI 算法 | 蒙特卡洛模拟 | 行为分析</p>
      </div>

      {/* 游戏信息面板 */}
      <div className="max-w-6xl mx-auto mb-4">
        <div className="bg-gray-900 bg-opacity-50 rounded-lg p-4 border border-cyan-500">
          <div className="text-green-400 text-center mb-2">{uiState.message}</div>
          {uiState.aiReason && (
            <div className="text-pink-400 text-sm text-center italic">
              🧠 AI 思考：{uiState.aiReason}
            </div>
          )}
          {uiState.winRate !== null && (
            <div className="text-yellow-400 text-xs text-center mt-2">
              📊 胜率：{(uiState.winRate * 100).toFixed(1)}% | 
              准确度：{(uiState.accuracy * 100).toFixed(1)}% |
              置信区间：[{(uiState.confidenceInterval?.lower * 100).toFixed(1)}%, {(uiState.confidenceInterval?.upper * 100).toFixed(1)}%]
            </div>
          )}
        </div>
      </div>

      {/* 牌桌区域 */}
      <div className="flex flex-col md:flex-row space-y-4 md:space-y-0 md:space-x-4 mb-6 max-w-6xl mx-auto">
        {/* 玩家手牌 */}
        <div className="flex-1">
          <div className="text-lg mb-2 text-cyan-400">👤 你的手牌</div>
          <div className="flex space-x-2">
            {gameState.playerHand.map(card => (
              <div 
                key={card.id} 
                className={`border-2 border-cyan-400 rounded px-3 py-2 text-2xl ${cardColor(card.suit)}`}
              >
                {card.rank}{card.suit}
              </div>
            ))}
          </div>
          {gameState.playerHand.length > 0 && (
            <div className="text-xs text-gray-400 mt-1">
              最大牌：{RANKS[Math.max(...gameState.playerHand.map(c => c.value))]}
            </div>
          )}
        </div>

        {/* 公共牌 */}
        <div className="flex-1">
          <div className="text-lg mb-2 text-pink-400">🎯 公共牌</div>
          <div className="flex space-x-2">
            {gameState.communityCards.length > 0 ? (
              gameState.communityCards.map(card => (
                <div 
                  key={card.id} 
                  className={`border-2 border-pink-500 rounded px-3 py-2 text-2xl ${cardColor(card.suit)}`}
                >
                  {card.rank}{card.suit}
                </div>
              ))
            ) : (
              <div className="text-gray-600">等待翻牌</div>
            )}
          </div>
        </div>

        {/* AI 手牌 */}
        <div className="flex-1">
          <div className="text-lg mb-2 text-red-400">🤖 AI 手牌</div>
          <div className="flex space-x-2">
            {gameState.phase === 'showdown' ? (
              gameState.aiHand.map(card => (
                <div 
                  key={card.id} 
                  className={`border-2 border-red-600 rounded px-3 py-2 text-2xl ${cardColor(card.suit)}`}
                >
                  {card.rank}{card.suit}
                </div>
              ))
            ) : (
              <div className="text-2xl text-gray-700 select-none">❓❓</div>
            )}
          </div>
        </div>
      </div>

      {/* 筹码和底池信息 */}
      <div className="max-w-4xl mx-auto mb-6 text-center">
        <div className="text-xl neon-text-yellow mb-4">
          💰 底池：{gameState.pot} 筹码 | 当前注：{gameState.currentBet}
        </div>
        <div className="flex justify-center space-x-8">
          <div className="text-green-400">
            👤 你的筹码：<span className="text-2xl">{gameState.playerChips}</span>
          </div>
          <div className="text-red-400">
            🤖 AI 筹码：<span className="text-2xl">{gameState.aiChips}</span>
          </div>
        </div>
      </div>

      {/* 游戏控制按钮 */}
      <div className="max-w-4xl mx-auto text-center">
        {gameState.phase === 'start' && (
          <button
            onClick={startGame}
            className="px-8 py-4 bg-pink-600 hover:bg-pink-700 rounded neon-glow text-xl font-bold"
          >
            🎮 开始游戏
          </button>
        )}

        {gameState.phase === 'playerTurn' && gameState.waitingForPlayer && (
          <div className="flex flex-wrap justify-center gap-4">
            <button
              onClick={() => handlePlayerAction("fold")}
              className="px-6 py-3 bg-red-700 hover:bg-red-800 rounded neon-glow"
            >
              ❌ 弃牌
            </button>
            <button
              onClick={() => handlePlayerAction("check")}
              className="px-6 py-3 bg-cyan-700 hover:bg-cyan-800 rounded neon-glow"
            >
              ✋ 过牌
            </button>
            <button
              onClick={() => handlePlayerAction("call")}
              disabled={gameState.playerChips < gameState.currentBet}
              className={`px-6 py-3 bg-blue-700 hover:bg-blue-800 rounded neon-glow ${
                gameState.playerChips < gameState.currentBet ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              ✅ 跟注 {gameState.currentBet}
            </button>
            <button
              onClick={() => handlePlayerAction("raise")}
              disabled={gameState.playerChips < gameState.currentBet * 2}
              className={`px-6 py-3 bg-purple-700 hover:bg-purple-800 rounded neon-glow ${
                gameState.playerChips < gameState.currentBet * 2 ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              🔥 加注 {gameState.currentBet * 2}
            </button>
          </div>
        )}

        {gameState.phase === 'showdown' && (
          <div className="space-y-4">
            <div className="text-3xl neon-text-green">
              {determineWinner()}
            </div>
            <button
              onClick={resetGame}
              className="px-8 py-4 bg-pink-600 hover:bg-pink-700 rounded neon-glow text-xl font-bold"
            >
              🔄 新一局
            </button>
          </div>
        )}
      </div>

      {/* CSS 样式 */}
      <style>{`
        .neon-text {
          text-shadow:
            0 0 5px #f0f,
            0 0 10px #f0f,
            0 0 20px #f0f,
            0 0 40px #ff00ff,
            0 0 80px #ff00ff;
        }
        .neon-text-green {
          color: #0f0;
          text-shadow:
            0 0 5px #0f0,
            0 0 10px #0f0,
            0 0 20px #0f0,
            0 0 40px #0f0,
            0 0 80px #0f0;
        }
        .neon-text-yellow {
          color: #ff0;
          text-shadow:
            0 0 5px #ff0,
            0 0 10px #ff0,
            0 0 20px #ff0,
            0 0 40px #ff0,
            0 0 80px #ff0;
        }
        .neon-glow {
          box-shadow:
            0 0 5px #ff00ff,
            0 0 10px #ff00ff,
            0 0 20px #ff00ff,
            0 0 40px #ff00ff;
          transition: all 0.3s ease;
        }
        .neon-glow:hover {
          box-shadow:
            0 0 10px #ff00ff,
            0 0 20px #ff00ff,
            0 0 40px #ff00ff,
            0 0 80px #ff00ff;
          transform: translateY(-2px);
        }
      `}</style>
    </div>
  );
}
