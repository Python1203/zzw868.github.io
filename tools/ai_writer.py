#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 金融博客自动创作脚本
支持多种 AI 模型，随机主题选择，防止内容雷同
适用于 Hexo 博客系统

使用方法：
    python scripts/ai_writer.py [--model qwen-max] [--count 1]
    
环境变量：
    AI_API_KEY: AI 模型 API 密钥
    AI_BASE_URL: API 基础 URL（可选，国内模型需要）
"""

import os
import sys
import random
import argparse
from datetime import datetime
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    print("❌ 缺少依赖：请安装 openai 库")
    print("运行：pip install openai")
    sys.exit(1)


# ==================== 配置区域 ====================

class Config:
    """配置类"""
    
    # 输出目录
    POSTS_DIR = "source/_posts"
    
    # 默认模型配置
    DEFAULT_MODEL = "qwen-max"  # 可切换：gpt-4o, qwen-max, ernie-4.0, deepseek-chat
    
    # API 配置（从环境变量读取）
    API_KEY = os.getenv("AI_API_KEY", "")
    BASE_URL = os.getenv("AI_BASE_URL", "https://api.openai.com/v1")
    
    # 百度文心配置
    BAIDU_API_KEY = os.getenv("BAIDU_API_KEY", "")
    
    # 文章生成参数
    MIN_WORDS = 1200
    MAX_WORDS = 2000
    
    # 标签池
    TAGS_POOL = [
        ["A 股", "量化投资", "金融科技"],
        ["宏观经济", "美联储", "利率政策"],
        ["家庭理财", "资产配置", "定投策略"],
        ["ESG", "可持续投资", "绿色金融"],
        ["养老金融", "保险规划", "长期投资"],
        ["加密货币", "区块链", "DeFi"],
        ["人工智能", "机器学习", "量化交易"],
        ["风险管理", "对冲策略", "投资组合"],
        ["行业分析", "财报解读", "估值方法"],
        ["技术分析", "K 线形态", "趋势判断"]
    ]
    
    # 分类池
    CATEGORIES_POOL = [
        "金融资讯",
        "量化投资",
        "宏观经济",
        "理财规划",
        "行业研究",
        "技术分析",
        "加密货币",
        "保险规划"
    ]


# ==================== 主题库 ====================

class TopicLibrary:
    """主题库 - 防止内容雷同"""
    
    # 主题分类
    THEMES = {
        "macro": [
            "全球宏观经济增速分析与展望",
            "美联储利率决议对全球资本市场的影响",
            "中国货币政策走向与 A 股投资机会",
            "通胀压力下的资产配置策略",
            "全球经济衰退风险与避险资产选择",
            "主要经济体 GDP 数据对比分析",
            "央行数字货币发展趋势",
            "国际贸易格局变化对投资的影响"
        ],
        
        "market": [
            "A 股市场结构性机会深度解析",
            "美股科技股估值分析与风险提示",
            "港股市场投资价值与风险评估",
            "新兴市场投资机会对比",
            "大宗商品价格走势与投资策略",
            "债券市场配置价值分析",
            "REITs 投资逻辑与风险控制",
            "量化对冲策略实战应用"
        ],
        
        "strategy": [
            "家庭资产配置定投策略详解",
            "不同年龄段的保险配置方案",
            "养老金长期投资规划指南",
            "教育金储备的最佳实践",
            "高净值人群财富传承策略",
            "年轻白领理财进阶之路",
            "退休规划与医疗险配置",
            "房产投资 vs 金融投资对比"
        ],
        
        "esg": [
            "ESG 投资趋势与基金选择",
            "绿色金融政策解读与机遇",
            "碳中和背景下的投资主线",
            "社会责任投资的价值逻辑",
            "新能源产业链投资分析",
            "可持续发展与企业治理",
            "ESG 评级体系对比研究",
            "影响力投资案例分析"
        ],
        
        "tech": [
            "AI 在量化交易中的应用实践",
            "大数据选股模型构建方法",
            "机器学习预测股价走势",
            "区块链技术在金融领域的应用",
            "智能投顾发展现状与前景",
            "高频交易策略解析",
            "自然语言处理在 sentiment analysis 中的应用",
            "深度学习在期权定价中的探索"
        ],
        
        "crypto": [
            "比特币减半周期与投资时机",
            "以太坊升级对生态的影响",
            "DeFi 项目风险评估与选择",
            "NFT 市场发展趋势分析",
            "稳定币监管政策影响",
            "Layer2 解决方案投资逻辑",
            "Web3.0 投资机会与挑战",
            "加密货币合规化进程"
        ],
        
        "insurance": [
            "养老金融与长期医疗险配置",
            "重疾险选购全攻略",
            "定期寿险 vs 终身寿险对比",
            "高端医疗险价值分析",
            "意外险配置的注意事项",
            "年金险 vs 银行理财对比",
            "互联网保险产品评测",
            "理赔流程与纠纷处理"
        ],
        
        "risk": [
            "黑天鹅事件应对策略",
            "投资组合风险分散方法",
            "止损止盈策略设计",
            "流动性风险管理",
            "汇率风险对冲工具",
            "信用风险评估框架",
            "操作风险防范措施",
            "系统性风险预警指标"
        ]
    }
    
    @classmethod
    def get_random_topic(cls, category=None):
        """获取随机主题"""
        if category and category in cls.THEMES:
            return random.choice(cls.THEMES[category])
        
        # 随机选择一个类别和主题
        category = random.choice(list(cls.THEMES.keys()))
        topic = random.choice(cls.THEMES[category])
        return category, topic
    
    @classmethod
    def get_all_topics(cls):
        """获取所有主题"""
        all_topics = []
        for category, topics in cls.THEMES.items():
            for topic in topics:
                all_topics.append((category, topic))
        return all_topics


# ==================== Prompt 模板 ====================

class PromptTemplates:
    """Prompt 模板库"""
    
    BASE_TEMPLATE = """你是一位资深的全球金融首席分析师，拥有 20 年从业经验。请针对"{topic}"撰写一篇深度分析博文。

【写作要求】
1. 格式要求：
   - 必须包含 Hexo Front-matter 格式（title, date, tags, categories）
   - 使用 Markdown 格式，多用标题、加粗和列表
   - 字数{min_words}-{max_words}字
   - 语气专业、客观、严谨

2. 内容结构：
   - 引言：简述话题背景和重要性（200 字左右）
   - 现状分析：深入剖析当前市场状况、数据支撑（500 字以上）
   - 核心观点：提出 3-5 个关键论点，每个论点有论据支持
   - 风险提示：明确指出潜在风险和不确定性因素
   - 专业建议：给出具体、可操作的理财建议或投资策略
   - 总结：简要回顾核心观点

3. 质量标准：
   - 数据准确，引用权威来源
   - 逻辑清晰，层次分明
   - 避免过度乐观或悲观
   - 兼顾专业性和可读性
   - 不使用绝对化表述

【特别提示】
- 如涉及具体数据，请注明时间点和来源
- 投资建议需强调"仅供参考，不构成投资建议"
- 保持中立客观，避免情绪化表达
- 适当使用图表描述（用文字说明图表内容）

请开始撰写："""

    QUICK_TEMPLATE = """作为金融分析师，请就"{topic}"写一篇短评。

要求：
- 包含 Hexo Front-matter
- 正文 600-800 字
- 观点鲜明，论证简洁
- 使用 Markdown 格式

开始："""

    DEEP_TEMPLATE = """你是一位顶级投行首席经济学家。请针对"{topic}"撰写一份深度研究报告。

【报告框架】
1. 执行摘要（200 字）
2. 宏观背景分析（400 字）
3. 行业深度研究（600 字）
4. 数据模型分析（300 字）
5. 投资标的筛选（300 字）
6. 风险提示与对策（200 字）
7. 结论与建议（200 字）

【技术要求】
- 总字数 2500-3000 字
- 使用专业术语但解释清晰
- 引用最新数据和研究成果
- 提供具体股票代码或基金代码（如适用）
- 包含估值模型或财务预测

【免责声明】
文末需添加："本文仅代表作者个人观点，不构成任何投资建议。市场有风险，投资需谨慎。"

开始撰写："""


# ==================== AI 客户端 ====================

class AIClient:
    """AI 客户端封装"""
    
    def __init__(self, api_key=None, base_url=None, model=None):
        self.api_key = api_key or Config.API_KEY
        self.base_url = base_url or Config.BASE_URL
        self.model = model or Config.DEFAULT_MODEL
        self.baidu_api_key = Config.BAIDU_API_KEY
        
        if not self.api_key and not self.baidu_api_key:
            raise ValueError("❌ 未设置 AI_API_KEY 或 BAIDU_API_KEY 环境变量")
        
        # 如果是百度文心，使用特殊处理
        if self.model.startswith("ernie") or (self.baidu_api_key and not self.api_key):
            self.use_baidu = True
        else:
            self.use_baidu = False
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
    
    def generate(self, prompt, model=None, temperature=0.7, max_tokens=3000):
        """生成内容"""
        if self.use_baidu:
            return self._generate_baidu(prompt)
        
        # OpenAI 兼容接口
        try:
            print(f"🔧 调用 API: {self.model}")
            print(f"🌐 Base URL: {self.base_url}")
            
            response = self.client.chat.completions.create(
                model=model or self.model,
                messages=[
                    {"role": "system", "content": "你是一位专业的金融分析师，擅长用数据说话，观点客观中立。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=0.9,
                frequency_penalty=0.3,  # 降低重复度
                presence_penalty=0.3
            )
            
            # 调试输出：检查响应类型
            print(f"🔍 响应类型：{type(response)}")
            
            # 如果响应是字符串，说明是错误
            if isinstance(response, str):
                print(f"⚠️  警告：API 返回字符串而非对象")
                print(f"❌ 响应内容：{response[:500]}...")
                return None
            
            # 检查是否有 choices 属性
            if not hasattr(response, 'choices'):
                print(f"⚠️  响应缺少 choices 属性")
                print(f"📄 响应内容：{response}")
                return None
            
            return response.choices[0].message.content
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ AI 调用失败：{error_msg}")
            
            # 针对性提示
            if "402" in error_msg or "Payment Required" in error_msg:
                print("\n💰 提示：账户余额不足，请充值后重试")
                print("   访问：https://platform.deepseek.com/billing")
                print("   或使用其他有免费额度的 API（如通义千问、百度文心）")
            elif "401" in error_msg or "Unauthorized" in error_msg:
                print("\n🔑 提示：API Key 无效或已过期")
                print("   请检查环境变量 AI_API_KEY 是否正确设置")
            elif "429" in error_msg or "Rate limit" in error_msg:
                print("\n⏱️  提示：请求频率超限，请稍后再试")
            elif "Connection" in error_msg or "Network" in error_msg:
                print("\n🌐 提示：网络连接问题，请检查网络")
            
            return None
    
    def _generate_baidu(self, prompt):
        """使用百度文心生成内容"""
        try:
            import requests
            
            # 获取 access_token
            token_url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={self.baidu_api_key}&client_secret={self.baidu_api_key}"
            response = requests.post(token_url)
            token_data = response.json()
            access_token = token_data.get("access_token")
            
            if not access_token:
                print(f"❌ 无法获取百度 Access Token: {token_data}")
                return None
            
            # 调用文心一言 API
            api_url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions?access_token={access_token}"
            
            headers = {
                "Content-Type": "application/json"
            }
            
            payload = {
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一位专业的金融分析师，擅长用数据说话，观点客观中立。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            response = requests.post(api_url, headers=headers, json=payload)
            result = response.json()
            
            print(f"🔍 百度响应类型：{type(result)}")
            
            if "result" in result:
                return result["result"]
            else:
                print(f"❌ 百度 API 返回错误：{result}")
                return None
                
        except Exception as e:
            print(f"❌ 百度 AI 调用失败：{str(e)}")
            return None


# ==================== 文章生成器 ====================

class ArticleGenerator:
    """文章生成器"""
    
    def __init__(self, ai_client):
        self.ai_client = ai_client
        self.generated_count = 0
    
    def generate_article(self, topic=None, template="base", category=None):
        """生成单篇文章"""
        
        # 1. 选择主题
        if not topic:
            category, topic = TopicLibrary.get_random_topic(category)
        
        print(f"\n📝 本次主题：{topic}")
        print(f"📂 所属分类：{category}")
        
        # 2. 选择模板
        if template == "quick":
            prompt_template = PromptTemplates.QUICK_TEMPLATE
            min_words = 600
            max_words = 800
        elif template == "deep":
            prompt_template = PromptTemplates.DEEP_TEMPLATE
            min_words = 2500
            max_words = 3000
        else:  # base
            prompt_template = PromptTemplates.BASE_TEMPLATE
            min_words = Config.MIN_WORDS
            max_words = Config.MAX_WORDS
        
        # 3. 生成 Prompt
        prompt = prompt_template.format(
            topic=topic,
            min_words=min_words,
            max_words=max_words
        )
        
        # 4. 调用 AI
        print("🤖 AI 正在创作中...")
        content = self.ai_client.generate(prompt)
        
        if not content:
            print("❌ 生成失败")
            return None
        
        # 5. 检查是否包含 front-matter
        if not content.strip().startswith("---"):
            print("⚠️  检测到缺少 front-matter，尝试自动添加...")
            content = self._add_front_matter(content, topic, category)
        
        # 6. 保存文件
        filename = self._generate_filename(topic)
        filepath = os.path.join(Config.POSTS_DIR, filename)
        
        # 确保目录存在
        Path(Config.POSTS_DIR).mkdir(parents=True, exist_ok=True)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"✅ 成功生成：{filepath}")
        self.generated_count += 1
        
        return filepath
    
    def _add_front_matter(self, content, topic, category):
        """自动添加 front-matter"""
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d %H:%M:%S")
        
        # 选择标签
        tags = random.choice(Config.TAGS_POOL)
        
        front_matter = f"""---
title: {topic}
date: {date_str}
tags: [{', '.join(tags)}]
categories: [{category}]
---

"""
        return front_matter + content
    
    def _generate_filename(self, topic):
        """生成文件名"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        # 简化主题作为文件名
        safe_topic = topic.replace(" ", "-").replace("/", "-")[:50]
        random_id = random.randint(100, 999)
        return f"{date_str}-{safe_topic}-{random_id}.md"
    
    def batch_generate(self, count=3, templates=None):
        """批量生成"""
        if templates is None:
            templates = ["base"]
        
        print(f"\n🚀 开始批量生成 {count} 篇文章...")
        
        success = 0
        for i in range(count):
            print(f"\n{'='*60}")
            print(f"第 {i+1}/{count} 篇")
            print('='*60)
            
            template = random.choice(templates)
            filepath = self.generate_article(template=template)
            
            if filepath:
                success += 1
            
            # 避免频率限制
            if i < count - 1:
                print("⏳ 等待 3 秒...")
                import time
                time.sleep(3)
        
        print(f"\n{'='*60}")
        print(f"✅ 批量生成完成：成功 {success}/{count} 篇")
        print('='*60)
        
        return success


# ==================== 主函数 ====================

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AI 金融博客自动创作工具")
    parser.add_argument("--model", type=str, default=None, help="AI 模型名称")
    parser.add_argument("--count", type=int, default=1, help="生成文章数量")
    parser.add_argument("--template", type=str, choices=["base", "quick", "deep"], 
                       default="base", help="文章模板类型")
    parser.add_argument("--topic", type=str, default=None, help="指定主题（不随机）")
    parser.add_argument("--category", type=str, default=None, 
                       help="指定分类（macro/market/strategy/esg/tech/crypto/insurance/risk）")
    parser.add_argument("--list-topics", action="store_true", help="列出所有可用主题")
    
    args = parser.parse_args()
    
    # 列出所有主题
    if args.list_topics:
        print("\n📚 可用主题列表:\n")
        all_topics = TopicLibrary.get_all_topics()
        for i, (category, topic) in enumerate(all_topics, 1):
            print(f"{i:3d}. [{category:10s}] {topic}")
        print(f"\n共 {len(all_topics)} 个主题")
        return
    
    # 检查 API Key
    if not Config.API_KEY:
        print("❌ 错误：未设置 AI_API_KEY 环境变量")
        print("\n解决方法:")
        print("1. 临时设置：export AI_API_KEY='your-key-here'")
        print("2. 永久设置：添加到 ~/.bashrc 或 ~/.zshrc")
        print("3. 创建 .env 文件：见 scripts/.env.example")
        sys.exit(1)
    
    try:
        # 初始化 AI 客户端
        ai_client = AIClient(model=args.model)
        
        # 初始化生成器
        generator = ArticleGenerator(ai_client)
        
        # 生成文章
        if args.count > 1:
            # 批量生成
            templates = ["base"] * 7 + ["quick"] * 2 + ["deep"]  # 权重分配
            generator.batch_generate(count=args.count, templates=templates)
        else:
            # 单篇生成
            generator.generate_article(
                topic=args.topic,
                template=args.template,
                category=args.category
            )
        
        print(f"\n✨ 共生成 {generator.generated_count} 篇文章")
        print("\n💡 提示：运行以下命令预览和部署")
        print("   hexo clean && hexo generate")
        print("   hexo server  # 本地预览")
        print("   hexo deploy  # 部署到 GitHub Pages")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
