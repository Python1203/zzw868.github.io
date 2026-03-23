"""
AI 聊天代理服务器 - 安全地代理 API 请求，密钥只存在服务器端
运行: python proxy-server.py
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, origins=["http://localhost:*", "http://127.0.0.1:*", "https://zzw868.github.io"])

OPENAI_API_KEY  = os.environ.get("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
HF_TOKEN        = os.environ.get("HF_TOKEN", "")
BAIDU_API_KEY   = os.environ.get("BAIDU_API_KEY", "")
BAIDU_BASE_URL  = "https://qianfan.baidubce.com/v2"

HF_MODELS = {
    "huggingface_qwen":     "Qwen/Qwen3.5-35B-A3B:novita",
    "huggingface_minimax":  "MiniMaxAI/MiniMax-M2.5:novita",
    "huggingface_glm":      "zai-org/GLM-5:novita",
    "huggingface_nanbeige": "Nanbeige/Nanbeige4.1-3B:featherless-ai",
}


@app.route("/api/chat", methods=["POST"])
def chat():
    data      = request.get_json()
    service   = data.get("service", "openai")
    message   = data.get("message", "")
    history   = data.get("history", [])
    image_b64 = data.get("image")

    try:
        # ── OpenAI ──────────────────────────────────────────────────
        if service == "openai":
            client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
            messages = [{"role": "system", "content": "你是一个有用的 AI 助手，回答简洁、准确。"}]
            messages += history
            messages.append({"role": "user", "content": message})
            resp = client.chat.completions.create(
                model="gpt-4", messages=messages, temperature=0.7, max_tokens=1000
            )
            return jsonify({"reply": resp.choices[0].message.content.strip()})

        # ── HuggingFace 系列 ─────────────────────────────────────────
        elif service in HF_MODELS:
            client   = OpenAI(base_url="https://router.huggingface.co/v1", api_key=HF_TOKEN)
            model_id = HF_MODELS[service]
            if image_b64 and service == "huggingface_qwen":
                content = [
                    {"type": "text", "text": message or "Describe this image."},
                    {"type": "image_url", "image_url": {"url": image_b64}},
                ]
            else:
                content = message
            resp = client.chat.completions.create(
                model=model_id,
                messages=[{"role": "user", "content": content}],
                max_tokens=1000,
            )
            return jsonify({"reply": resp.choices[0].message.content.strip()})

        # ── 百度文心 v2（bce-v3 key 直接作为 Bearer Token）────────────
        elif service == "baidu":
            client   = OpenAI(api_key=BAIDU_API_KEY, base_url=BAIDU_BASE_URL)
            messages = list(history) + [{"role": "user", "content": message}]
            resp = client.chat.completions.create(
                model="ernie-4.0-8k", messages=messages, max_tokens=1000
            )
            return jsonify({"reply": resp.choices[0].message.content.strip()})

        else:
            return jsonify({"error": f"未知服务: {service}"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "services": {
            "openai":      bool(OPENAI_API_KEY),
            "huggingface": bool(HF_TOKEN),
            "baidu":       bool(BAIDU_API_KEY),
        }
    })


if __name__ == "__main__":
    print("🚀 AI 代理服务器启动中...")
    print("📡 监听: http://localhost:5001")
    print("🔑 密钥从 .env 文件读取，不暴露给前端")
    app.run(host="0.0.0.0", port=5001, debug=False)
