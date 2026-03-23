"""
AI 智能聊天助手 - 多模型集成系统
支持多种 AI 模型：OpenAI GPT-4、HuggingFace 模型等
功能特性：
- 多模型切换
- 上下文对话记忆
- 图像识别
- 流式输出
- 错误重试机制
"""

import os
from typing import List, Dict, Optional, Union
from openai import OpenAI


class AIChatBot:
    """AI 聊天机器人基类"""
    
    def __init__(self, api_key: str, base_url: str = None):
        self.api_key = api_key
        self.base_url = base_url
        self.client = None
        self.chat_history = []
        self.max_history = 10
        
    def init_client(self):
        """初始化客户端"""
        raise NotImplementedError
    
    def chat(self, message: str, **kwargs) -> str:
        """发送消息并获取回复"""
        raise NotImplementedError
    
    def clear_history(self):
        """清空聊天记录"""
        self.chat_history = []
    
    def get_history(self) -> List[Dict]:
        """获取聊天记录"""
        return self.chat_history[-self.max_history:]
    
    def _save_to_history(self, role: str, content: str):
        """保存消息到历史记录"""
        self.chat_history.append({"role": role, "content": content})
        if len(self.chat_history) > self.max_history:
            self.chat_history.pop(0)


class OpenAIChat(AIChatBot):
    """OpenAI GPT 系列模型"""
    
    def __init__(self, api_key: str, model: str = "gpt-4", base_url: str = "https://api.openai.com/v1"):
        super().__init__(api_key, base_url)
        self.model = model
        self.init_client()
    
    def init_client(self):
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )
    
    def chat(self, message: str, system_prompt: str = None, stream: bool = False) -> str:
        """
        发送消息
        
        Args:
            message: 用户消息
            system_prompt: 系统提示词
            stream: 是否流式输出
            
        Returns:
            AI 回复
        """
        try:
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            # 添加历史上下文
            messages.extend(self.get_history())
            messages.append({"role": "user", "content": message})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
                stream=stream
            )
            
            if stream:
                reply = ""
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        text = chunk.choices[0].delta.content
                        print(text, end="", flush=True)
                        reply += text
                print()
                self._save_to_history("user", message)
                self._save_to_history("assistant", reply)
                return reply
            else:
                reply = response.choices[0].message.content.strip()
                self._save_to_history("user", message)
                self._save_to_history("assistant", reply)
                return reply
                
        except Exception as e:
            error_msg = f"❌ OpenAI API 错误：{str(e)}"
            print(error_msg)
            return error_msg
    
    def chat_with_image(self, message: str, image_url: str) -> str:
        """
        带图像的对话（需要支持视觉的模型如 GPT-4V）
        
        Args:
            message: 文本消息
            image_url: 图片 URL
            
        Returns:
            AI 回复
        """
        try:
            messages = [
                {"role": "user", "content": [
                    {"type": "text", "text": message},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1000
            )
            
            reply = response.choices[0].message.content.strip()
            return reply
            
        except Exception as e:
            error_msg = f"❌ 图像识别错误：{str(e)}"
            print(error_msg)
            return error_msg


class HuggingFaceChat(AIChatBot):
    """HuggingFace 模型（通过 Novita 等平台）"""
    
    MODELS = {
        "qwen_large": "Qwen/Qwen3.5-397B-A17B:novita",
        "qwen_medium": "Qwen/Qwen3.5-35B-A3B:novita",
        "minimax": "MiniMaxAI/MiniMax-M2.5:novita",
        "glm": "zai-org/GLM-5:novita",
        "qwen_small": "Qwen/Qwen3.5-9B:together",
        "nanbeige": "Nanbeige/Nanbeige4.1-3B:featherless-ai"
    }
    
    def __init__(self, api_key: str = None, model: str = "qwen_medium", 
                 base_url: str = "https://router.huggingface.co/v1"):
        # 优先使用环境变量，其次直接传入
        self.hf_token = api_key or os.environ.get("HF_TOKEN")
        if not self.hf_token:
            raise ValueError("必须提供 HuggingFace API 密钥或设置 HF_TOKEN 环境变量")
        
        super().__init__(self.hf_token, base_url)
        self.model = self.MODELS.get(model, model)
        self.init_client()
    
    def init_client(self):
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.hf_token
        )
    
    def chat(self, message: str, model: str = None) -> str:
        """发送消息"""
        try:
            model_to_use = model or self.model
            
            response = self.client.chat.completions.create(
                model=model_to_use,
                messages=[{"role": "user", "content": message}],
                temperature=0.7,
                max_tokens=1000
            )
            
            reply = response.choices[0].message.content.strip()
            print(f"[{model_to_use}]: {reply}")
            return reply
            
        except Exception as e:
            error_msg = f"❌ HuggingFace API 错误：{str(e)}"
            print(error_msg)
            return error_msg
    
    def chat_with_image(self, message: str, image_url: str, model: str = None) -> str:
        """带图像的对话"""
        try:
            model_to_use = model or self.model
            
            response = self.client.chat.completions.create(
                model=model_to_use,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": message},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }],
                max_tokens=1000
            )
            
            reply = response.choices[0].message.content.strip()
            print(f"[{model_to_use}]: {reply}")
            return reply
            
        except Exception as e:
            error_msg = f"❌ 图像识别错误：{str(e)}"
            print(error_msg)
            return error_msg
    
    def batch_test_models(self, message: str = "What is the capital of France?") -> Dict[str, str]:
        """批量测试多个模型"""
        results = {}
        
        for model_name, model_id in self.MODELS.items():
            print(f"\n🔄 测试模型：{model_name} ({model_id})")
            try:
                response = self.client.chat.completions.create(
                    model=model_id,
                    messages=[{"role": "user", "content": message}],
                    max_tokens=500
                )
                reply = response.choices[0].message.content.strip()
                results[model_name] = reply
                print(f"✅ {model_name}: {reply[:100]}...")
            except Exception as e:
                error_msg = str(e)
                results[model_name] = f"错误：{error_msg}"
                print(f"❌ {model_name}: {error_msg}")
        
        return results


class MultiAIService:
    """多 AI 服务统一接口"""
    
    def __init__(self):
        self.services = {}
        self.current_service = None
    
    def add_service(self, name: str, service: AIChatBot):
        """添加 AI 服务"""
        self.services[name] = service
        if not self.current_service:
            self.current_service = name
    
    def switch_service(self, name: str):
        """切换 AI 服务"""
        if name in self.services:
            self.current_service = name
            print(f"✅ 已切换到：{name}")
        else:
            print(f"❌ 服务不存在：{name}")
    
    def chat(self, message: str, **kwargs) -> str:
        """使用当前服务聊天"""
        if not self.current_service:
            return "❌ 请先选择 AI 服务"
        
        service = self.services[self.current_service]
        return service.chat(message, **kwargs)
    
    def list_services(self):
        """列出所有可用服务"""
        print("\n可用的 AI 服务:")
        for name, service in self.services.items():
            status = "🟢" if name == self.current_service else "⚪"
            print(f"{status} {name}: {type(service).__name__}")


def main():
    """主函数 - 演示用法"""
    print("=" * 60)
    print("🤖 AI 智能聊天助手 - 多模型集成系统")
    print("=" * 60)
    
    # 配置 API 密钥
    OPENAI_API_KEY = "sk-V8hcmOdmpvRS5uOogqDAcijxZpu2Oc6uI7gQbj3xmV59hDv4"
    HF_TOKEN = "YOUR_HF_TOKEN_HERE"  # HuggingFace API Key
    
    # 创建多 AI 服务
    multi_ai = MultiAIService()
    
    # 添加 OpenAI GPT-4
    openai_bot = OpenAIChat(
        api_key=OPENAI_API_KEY,
        model="gpt-4",
        base_url="https://api.openai.com/v1"
    )
    multi_ai.add_service("openai", openai_bot)
    
    # 添加 HuggingFace 模型（如果有 API 密钥）
    if HF_TOKEN != "your_hf_token_here":
        hf_bot = HuggingFaceChat(api_key=HF_TOKEN)
        multi_ai.add_service("huggingface", hf_bot)
    
    # 列出可用服务
    multi_ai.list_services()
    
    # 示例对话
    print("\n" + "=" * 60)
    print("开始对话示例:")
    print("=" * 60)
    
    # 使用 OpenAI
    multi_ai.switch_service("openai")
    response = multi_ai.chat("你好，请介绍一下你自己")
    print(f"\nAI: {response}\n")
    
    # 继续对话（带上下文）
    response = multi_ai.chat("你能帮我做什么？")
    print(f"\nAI: {response}\n")
    
    # 如果有 HuggingFace，测试批量模型
    if "huggingface" in multi_ai.services:
        print("\n" + "=" * 60)
        print("批量测试 HuggingFace 模型:")
        print("=" * 60)
        hf_bot = multi_ai.services["huggingface"]
        results = hf_bot.batch_test_models()
        
        print("\n📊 测试结果汇总:")
        for model, result in results.items():
            print(f"\n{model}: {result[:200]}..." if len(result) > 200 else f"\n{model}: {result}")
    
    print("\n" + "=" * 60)
    print("✨ 演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
