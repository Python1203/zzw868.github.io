import React, {useEffect, useState} from "react";

const suits = ['♠', '♥', '♦', '♣'];
const ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A'];

function createDeck() {
  const deck = [];
  for (const suit of suits) {
    for (const rank of ranks) {
      deck.push({ suit, rank, id: rank + suit });
    }
  }
  return deck;
}

function shuffle(deck) {
  for (let i = deck.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [deck[i], deck[j]] = [deck[j], deck[i]];
  }
}

function cardColor(suit) {
  return suit === '♥' || suit === '♦' ? "text-red-500" : "text-cyan-400";
}

function cacheKey(aiHand, communityCards) {
  const aiStr = aiHand.map(c => c.rank + c.suit).sort().join('');
  const commStr = communityCards.map(c => c.rank + c.suit).sort().join('');
  return aiStr + '|' + commStr;
}

export default function CyberpunkPokerWithPublicWorker() {
  const [deck, setDeck] = useState([]);
  const [playerHand, setPlayerHand] = useState([]);
  const [aiHand, setAiHand] = useState([]);
  const [communityCards, setCommunityCards] = useState([]);
  const [pot, setPot] = useState(0);
  const [playerChips, setPlayerChips] = useState(1000);
  const [aiChips, setAiChips] = useState(1000);
  const [currentBet, setCurrentBet] = useState(10);
  const [message, setMessage] = useState("⚡ 赛博朋克AI德州扑克启动 ⚡");
  const [phase, setPhase] = useState("start");
  const [playerAction, setPlayerAction] = useState(null);
  const [aiAction, setAiAction] = useState(null);
  const [waitingForPlayer, setWaitingForPlayer] = useState(false);
  const [winRate, setWinRate] = useState(null);
  const [lastAiReason, setLastAiReason] = useState("");
  const winRateCache = React.useRef(new Map());

  // 初始化 Worker
  React.useEffect(() => {
    const worker = new Worker('/workers/monteCarloWorker.js');
    worker.onmessage = (e) => {
      setWinRate(e.data.winRate);
    };
    return () => {
      worker.terminate();
    };
  }, []);

  // 请求胜率计算
  function requestWinRate(aiHand, communityCards, deck, simulations) {
    const key = cacheKey(aiHand, communityCards);
    if (winRateCache.current.has(key)) {
      setWinRate(winRateCache.current.get(key));
      return;
    }
    const worker = new Worker('/workers/monteCarloWorker.js');
    worker.postMessage({ aiHand, communityCards, deck, simulations });
    worker.onmessage = (e) => {
      winRateCache.current.set(key, e.data.winRate);
      setWinRate(e.data.winRate);
      worker.terminate();
    };
  }

  // AI简单决策
  function aiDecision(winRate, currentBet, aiChips, pot) {
    if (winRate === null) return { action: "check", amount: 0, reason: "等待胜率计算" };
    if (winRate > 0.75 && aiChips >= currentBet * 3) return { action: "raise", amount: currentBet * 3, reason: `胜率高(${(winRate*100).toFixed(1)}%)，激进加注` };
    if (winRate > 0.5 && aiChips >= currentBet * 2) return { action: "raise", amount: currentBet * 2, reason: `胜率不错(${(winRate*100).toFixed(1)}%)，适度加注` };
    if (winRate > 0.3 && aiChips >= currentBet) return { action: "call", amount: currentBet, reason: `胜率一般(${(winRate*100).toFixed(1)}%)，跟注` };
    if (winRate > 0.15) return { action: "check", amount: 0, reason: `胜率较低(${(winRate*100).toFixed(1)}%)，过牌` };
    return { action: "fold", amount: 0, reason: `胜率低(${(winRate*100).toFixed(1)}%)，弃牌` };
  }

  // 新局初始化
  function startGame() {
    const newDeck = createDeck();
    shuffle(newDeck);
    const pHand = [newDeck.pop(), newDeck.pop()];
    const aHand = [newDeck.pop(), newDeck.pop()];
    setDeck(newDeck);
    setPlayerHand(pHand);
    setAiHand(aHand);
    setCommunityCards([]);
    setPot(0);
    setCurrentBet(10);
    setPlayerChips(chips => chips - 10);
    setAiChips(chips => chips - 10);
    setPot(20);
    setMessage("发牌完成，预翻牌阶段。请行动！");
    setPhase("playerTurn");
    setPlayerAction(null);
    setAiAction(null);
    setWaitingForPlayer(true);
    setWinRate(null);
    setLastAiReason("");
  }

  // 玩家行动示例
  function handlePlayerAction(action) {
    if (!waitingForPlayer) return;
    setWaitingForPlayer(false);

    if (action === "fold") {
      setMessage("你弃牌，AI获胜。");
      setAiChips(chips => chips + pot);
      setPhase("showdown");
      setPlayerAction("fold");
      return;
    }

    if (action === "call") {
      if (playerChips < currentBet) {
        setMessage("筹码不足，无法跟注。");
        setWaitingForPlayer(true);
        return;
      }
      setPlayerChips(chips => chips - currentBet);
      setPot(p => p + currentBet);
      setMessage(`你跟注${currentBet}筹码，AI行动中...`);
      setPlayerAction("call");
      setPhase("aiTurn");
      return;
    }

    if (action === "raise") {
      const raiseAmount = currentBet * 2;
      if (playerChips < raiseAmount) {
        setMessage("筹码不足，无法加注。");
        setWaitingForPlayer(true);
        return;
      }
      setPlayerChips(chips => chips - raiseAmount);
      setPot(p => p + raiseAmount);
      setCurrentBet(raiseAmount);
      setMessage(`你加注${raiseAmount}筹码，AI行动中...`);
      setPlayerAction("raise");
      setPhase("aiTurn");
      return;
    }

    if (action === "check") {
      setMessage("你选择过牌，AI行动中...");
      setPlayerAction("check");
      setPhase("aiTurn");
      return;
    }
  }

  // AI行动逻辑
  useEffect(() => {
    if (phase === "aiTurn") {
      requestWinRate(aiHand, communityCards, deck, 300);
    }
  }, [phase, aiHand, communityCards, deck]);

  useEffect(() => {
    if (phase === "aiTurn" && winRate !== null) {
      const aiMove = aiDecision(winRate, currentBet, aiChips, pot);
      setLastAiReason(aiMove.reason);
      const timer = setTimeout(() => {
        if (aiMove.action === "fold") {
          setMessage(`AI弃牌，你获胜！ (${aiMove.reason})`);
          setPlayerChips(chips => chips + pot);
          setPhase("showdown");
          return;
        }
        if (aiMove.action === "check") {
          setMessage(`AI选择过牌。 (${aiMove.reason})`);
          setPhase("playerTurn");
          setWaitingForPlayer(true);
          return;
        }
        if (aiMove.action === "call") {
          if (aiChips < aiMove.amount) {
            setMessage(`AI筹码不足，弃牌，你获胜！ (${aiMove.reason})`);
            setPlayerChips(chips => chips + pot);
            setPhase("showdown");
            return;
          }
          setAiChips(chips => chips - aiMove.amount);
          setPot(p => p + aiMove.amount);
          setMessage(`AI跟注${aiMove.amount}筹码。 (${aiMove.reason})`);
          setPhase("playerTurn");
          setWaitingForPlayer(true);
          return;
        }
        if (aiMove.action === "raise") {
          if (aiChips < aiMove.amount) {
            setMessage(`AI筹码不足，弃牌，你获胜！ (${aiMove.reason})`);
            setPlayerChips(chips => chips + pot);
            setPhase("showdown");
            return;
          }
          setAiChips(chips => chips - aiMove.amount);
          setPot(p => p + aiMove.amount);
          setCurrentBet(aiMove.amount);
          setMessage(`AI加注${aiMove.amount}筹码，请选择行动！ (${aiMove.reason})`);
          setPhase("playerTurn");
          setWaitingForPlayer(true);
          return;
        }
      }, 1500);
      return () => clearTimeout(timer);
    }
  }, [winRate, phase, currentBet, aiChips, pot]);

  // 摊牌判断赢家（简化）
  function showdown() {
    if (playerAction === "fold") return "AI获胜";
    if (aiAction === "fold") return "你获胜";

    const playerMax = Math.max(...playerHand.map(c => ranks.indexOf(c.rank)));
    const aiMax = Math.max(...aiHand.map(c => ranks.indexOf(c.rank)));

    if (playerMax > aiMax) {
      setPlayerChips(chips => chips + pot);
      return "你获胜";
    }
    if (aiMax > playerMax) {
      setAiChips(chips => chips + pot);
      return "AI获胜";
    }
    setPlayerChips(chips => chips + pot / 2);
    setAiChips(chips => chips + pot / 2);
    return "平局";
  }

  // 重新开始
  function resetGame() {
    setPot(0);
    setCurrentBet(10);
    setPlayerHand([]);
    setAiHand([]);
    setCommunityCards([]);
    setMessage("⚡ 新局准备，点击开始！ ⚡");
    setPhase("start");
    setPlayerAction(null);
    setAiAction(null);
    setWaitingForPlayer(false);
    setWinRate(null);
    setLastAiReason("");
    winRateCache.current.clear();
  }

  return (
    <div className="min-h-screen bg-gradient-to-tr from-purple-900 via-pink-900 to-black text-white font-mono p-6 flex flex-col items-center">
      <h1 className="text-4xl mb-4 neon-text">赛博朋克 AI 德州扑克（Web Worker版）</h1>

      <div className="mb-2 text-green-400">{message}</div>
      {lastAiReason && <div className="mb-2 text-pink-400 text-sm italic">AI思考: {lastAiReason}</div>}

      <div className="flex space-x-4 mb-6 w-full max-w-4xl">
        <div className="flex-1">
          <div className="text-lg mb-1">你的手牌</div>
          <div className="flex space-x-2">
            {playerHand.map(card => (
              <div key={card.id} className={`border-2 border-cyan-400 rounded px-3 py-2 text-2xl ${cardColor(card.suit)}`}>
                {card.rank}{card.suit}
              </div>
            ))}
          </div>
        </div>
        <div className="flex-1">
          <div className="text-lg mb-1">公共牌</div>
          <div className="flex space-x-2">
            {communityCards.length > 0 ? communityCards.map(card => (
              <div key={card.id} className={`border-2 border-pink-500 rounded px-3 py-2 text-2xl ${cardColor(card.suit)}`}>
                {card.rank}{card.suit}
              </div>
            )) : <div className="text-gray-600">等待翻牌</div>}
          </div>
        </div>
        <div className="flex-1">
          <div className="text-lg mb-1">AI手牌</div>
          <div className="flex space-x-2">
            {phase === "showdown" ? (
              aiHand.map(card => (
                <div key={card.id} className={`border-2 border-red-600 rounded px-3 py-2 text-2xl ${cardColor(card.suit)}`}>
                  {card.rank}{card.suit}
                </div>
              ))
            ) : (
              <div className="text-2xl text-gray-700 select-none">??</div>
            )}
          </div>
        </div>
      </div>

      <div className="mb-4 neon-text-yellow text-xl w-full max-w-4xl text-center">
        底池: {pot} 筹码 | 当前最低注: {currentBet}
      </div>
      <div className="flex space-x-6 mb-6 w-full max-w-4xl justify-center">
        <div>你的筹码: <span className="text-green-400">{playerChips}</span></div>
        <div>AI筹码: <span className="text-red-400">{aiChips}</span></div>
      </div>

      {phase === "start" && (
        <button
          onClick={startGame}
          className="px-6 py-3 bg-pink-600 hover:bg-pink-700 rounded neon-glow"
        >
          开始游戏
        </button>
      )}

      {(phase === "playerTurn" && waitingForPlayer) && (
        <div className="flex space-x-4 mb-6">
          <button
            onClick={() => handlePlayerAction("fold")}
            className="px-4 py-2 bg-red-700 hover:bg-red-800 rounded neon-glow"
          >
            弃牌
          </button>
          <button
            onClick={() => handlePlayerAction("check")}
            className="px-4 py-2 bg-cyan-700 hover:bg-cyan-800 rounded neon-glow"
          >
            过牌
          </button>
          <button
            onClick={() => handlePlayerAction("call")}
            className={`px-4 py-2 bg-blue-700 hover:bg-blue-800 rounded neon-glow ${playerChips < currentBet ? "opacity-50 cursor-not-allowed" : ""}`}
            disabled={playerChips < currentBet}
          >
            跟注
          </button>
          <button
            onClick={() => handlePlayerAction("raise")}
            className={`px-4 py-2 bg-purple-700 hover:bg-purple-800 rounded neon-glow ${playerChips < currentBet * 2 ? "opacity-50 cursor-not-allowed" : ""}`}
            disabled={playerChips < currentBet * 2}
          >
            加注
          </button>
        </div>
      )}

      {phase === "showdown" && (
        <>
          <div className="mt-6 text-3xl neon-text-green mb-6">
            {showdown()}
          </div>
          <button
            onClick={resetGame}
            className="px-6 py-3 bg-pink-600 hover:bg-pink-700 rounded neon-glow"
          >
            新一局
          </button>
        </>
      )}

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
          transition: box-shadow 0.3s ease;
        }
        .neon-glow:hover {
          box-shadow:
            0 0 10px #ff00ff,
            0 0 20px #ff00ff,
            0 0 40px #ff00ff,
            0 0 80px #ff00ff;
        }
      `}</style>
    </div>
  );
}