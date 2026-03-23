"""
HuggingFace Qwen 图像识别测试脚本
测试 Qwen/Qwen3.5-35B-A3B:novita 模型的图像识别能力
"""

from openai import OpenAI


def test_image_recognition(image_url: str = None, prompt: str = None):
    """
    测试 Qwen 模型的图像识别功能
    
    Args:
        image_url: 图片 URL 地址
        prompt: 提示词，默认为 "Describe this image in one sentence."
    """
    
    # 默认参数
    if image_url is None:
        image_url = "https://cdn.britannica.com/61/93061-050-99147DCE/Statue-of-Liberty-Island-New-York-Bay.jpg"
    
    if prompt is None:
        prompt = "Describe this image in one sentence."
    
    print("=" * 60)
    print("🔍 HuggingFace Qwen 图像识别测试")
    print("=" * 60)
    print(f"\n📷 测试图片：{image_url}")
    print(f"💬 提示词：{prompt}\n")
    
    try:
        # 直接使用 API 密钥
        hf_token = "YOUR_HF_TOKEN_HERE"
        
        # 初始化客户端
        client = OpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=hf_token,
        )
        
        print("⚙️  正在调用 Qwen/Qwen3.5-35B-A3B:novita 模型...\n")
        
        # 调用 API
        completion = client.chat.completions.create(
            model="Qwen/Qwen3.5-35B-A3B:novita",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        }
                    ]
                }
            ],
        )
        
        # 输出结果
        print("=" * 60)
        print("✅ 识别结果:\n")
        print(completion.choices[0].message.content)
        print("\n" + "=" * 60)
        
        return completion.choices[0].message.content
        
    except Exception as e:
        print("=" * 60)
        print(f"❌ 测试失败：{str(e)}")
        print("=" * 60)
        print("\n💡 可能的原因:")
        print("   1. HF_TOKEN 未设置或无效")
        print("   2. 网络连接问题")
        print("   3. 模型服务暂时不可用")
        print("   4. 图片 URL 无法访问\n")
        return None


def test_text_only(prompt: str = "你好，请介绍一下你自己"):
    """
    测试纯文本对话（不使用图像）
    
    Args:
        prompt: 提示词
    """
    
    print("=" * 60)
    print("💬 HuggingFace Qwen 文本对话测试")
    print("=" * 60)
    print(f"\n📝 问题：{prompt}\n")
    
    try:
        hf_token = "YOUR_HF_TOKEN_HERE"
        
        client = OpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=hf_token,
        )
        
        print("⚙️  正在调用 Qwen/Qwen3.5-35B-A3B:novita 模型...\n")
        
        completion = client.chat.completions.create(
            model="Qwen/Qwen3.5-35B-A3B:novita",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=1000
        )
        
        print("=" * 60)
        print("✅ 回复内容:\n")
        print(completion.choices[0].message.content)
        print("\n" + "=" * 60)
        
        return completion.choices[0].message.content
        
    except Exception as e:
        print("=" * 60)
        print(f"❌ 测试失败：{str(e)}")
        print("=" * 60)
        return None


def test_multiple_images():
    """
    测试多图片识别（如果模型支持）
    """
    
    print("=" * 60)
    print("🖼️  HuggingFace Qwen 多图识别测试")
    print("=" * 60)
    
    images = [
        "https://cdn.britannica.com/61/93061-050-99147DCE/Statue-of-Liberty-Island-New-York-Bay.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/Eiffel_Tower_-_Paris_2016_-_panoramio_%283%29.jpg/800px-Eiffel_Tower_-_Paris_2016_-_panoramio_%283%29.jpg"
    ]
    
    try:
        hf_token = "YOUR_HF_TOKEN_HERE"
        
        client = OpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=hf_token,
        )
        
        content = [
            {"type": "text", "text": "请比较这两张著名地标建筑的图片，它们分别是什么？"}
        ]
        
        for img_url in images:
            content.append({
                "type": "image_url",
                "image_url": {"url": img_url}
            })
        
        print("\n⚙️  正在调用模型分析多张图片...\n")
        
        completion = client.chat.completions.create(
            model="Qwen/Qwen3.5-35B-A3B:novita",
            messages=[{"role": "user", "content": content}],
            max_tokens=1000
        )
        
        print("=" * 60)
        print("✅ 分析结果:\n")
        print(completion.choices[0].message.content)
        print("\n" + "=" * 60)
        
        return completion.choices[0].message.content
        
    except Exception as e:
        print("=" * 60)
        print(f"❌ 测试失败：{str(e)}")
        print("=" * 60)
        return None


if __name__ == "__main__":
    import sys
    
    print("\n🤖 HuggingFace Qwen 模型测试工具\n")
    print("请选择测试模式:")
    print("1. 图像识别测试（单图）")
    print("2. 文本对话测试")
    print("3. 多图识别测试")
    print("4. 自定义图片 URL")
    print("0. 退出\n")
    
    choice = input("请输入选项 (1-4/0): ").strip()
    
    if choice == "0":
        print("👋 再见！")
        sys.exit(0)
    
    elif choice == "1":
        test_image_recognition()
    
    elif choice == "2":
        custom_prompt = input("\n请输入你的问题（直接回车使用默认问题）: ").strip()
        prompt = custom_prompt if custom_prompt else "你好，请介绍一下你自己"
        test_text_only(prompt)
    
    elif choice == "3":
        test_multiple_images()
    
    elif choice == "4":
        custom_url = input("\n请输入图片 URL: ").strip()
        custom_prompt = input("请输入描述提示词（直接回车使用默认）: ").strip()
        
        if not custom_url:
            print("❌ 错误：图片 URL 不能为空")
        else:
            test_image_recognition(
                image_url=custom_url,
                prompt=custom_prompt if custom_prompt else "Describe this image in one sentence."
            )
    
    else:
        print("❌ 无效的选项，请重新运行程序并选择正确的选项")
    
    print("\n✨ 测试完成！\n")
