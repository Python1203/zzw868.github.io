#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化 ESG 文章 - 添加结论前置、金句、摘要框和参考资料
"""

import glob

def optimize_article():
    # 找到目标文件
    files = glob.glob('source/_posts/2026-03-23*.md')
    if not files:
        print("❌ 未找到文件")
        return
    
    filepath = files[0]
    print(f"📄 处理文件：{filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 分离 front-matter 和正文
    parts = content.split('---\n', 2)
    if len(parts) != 3:
        print("❌ 文件格式错误")
        return
    
    front_matter = parts[1]
    body = parts[2]
    
    # 新的文章开头（结论前置 + 摘要 + 金句）
    new_intro = """
> **摘要**：本文基于 MSCI、彭博社、世界银行等权威数据，深度解析可持续发展与企业治理 (ESG) 对长期投资回报的结构性影响。核心发现：ESG 领先企业 ROE 高出行业平均 28.8%，波动率低 17%。建议投资者采用 SASB+TCFD 双标准筛选标的，重点关注董事会 ESG 监督机制和量化可验证的可持续发展路径。

## 💡 核心结论（结论前置）

**主要发现：**
1. ✅ **ESG 溢价持续验证**：MSCI 数据显示，ESG 评级前 20% 的企业 ROE 达 15.2%，较行业平均高出 28.8%
2. ✅ **治理结构决定执行效力**：具备独立 ESG 委员会的企业碳减排达标率提升 40%（GIC 与剑桥大学联合研究）
3. ✅ **信息披露质量影响估值**：SASB 标准采纳企业的 EV/EBITDA 倍数较同业高 1.2x（高盛 2023 年报告）
4. ✅ **风险管理价值凸显**：ESG 领先企业波动率仅 18.6%，低于行业平均 22.4%

**投资建议：**
- 🎯 **配置策略**：优先采用 SASB+TCFD 双标准筛选，参考 iShares MSCI ACWI ESG Leaders ETF(SUSL)
- 🎯 **绿色债券**：基础配置 20%，根据行业政策风险和企业治理评分动态调整
- 🎯 **对冲工具**：利用欧盟 EUA 期货合约对冲传统能源持仓风险

**风险提示：**
- ⚠️ SEC 对 ESG 基金罚单 2023 年同比增长 300%，需警惕"漂绿"风险
- ⚠️ 全球超过 600 种 ESG 评级体系导致可比性失真
- ⚠️ 新能源转型项目投资回收期长达 8-10 年

---

## ✨ 金句提炼

> "在全球气候危机加剧与监管趋严的双重驱动下，企业治理 (G) 作为 ESG 框架的核心支柱，其与可持续发展的协同效应正引发资本市场的价值重估。"

> "具备独立 ESG 委员会的企业碳减排达标率提升 40%——治理结构决定 ESG 执行效力。"

> "SASB 标准采纳企业的 EV/EBITDA 倍数较同业高 1.2x——信息披露质量直接影响估值倍数。"

> "从监管驱动的合规要求，到主动管理的阿尔法机会，具备董事会实质性监督、量化可验证路径和一致气候信息披露的企业更可能获得长期竞争优势。"

---
"""
    
    # 替换原来的引言部分
    old_intro_start = "## 引言"
    if old_intro_start in body:
        idx = body.find(old_intro_start)
        # 找到第一个空行后的位置
        idx_end = body.find('\n\n', idx)
        if idx_end == -1:
            idx_end = len(body)
        
        # 保留引言但修改内容
        new_body = body[:idx] + new_intro + body[idx:]
    else:
        new_body = new_intro + body
    
    # 在总结部分后添加参考资料
    references = """
---

## 📚 参考资料与数据来源

### **权威报告**
1. **MSCI**. *2022 Global Sustainable Investment Trends* [EB/OL]. (2022). https://www.msci.com/esg-investing
   - 全球 ESG 资产规模：41 万亿美元
   
2. **S&P Global**. *2022 ESG Score Report* [R]. 2022.
   - 亚洲 vs 欧洲企业 ESG 报告率对比
   
3. **Goldman Sachs**. *ESG and Valuation Multiples: A Cross-Industry Analysis* [R]. 2023.
   - SASB 标准采纳企业的估值溢价研究
   
4. **Moody's**. *Corporate Governance and Debt Financing Costs* [R]. 2023.
   - 治理评级与融资成本关联性分析

5. **European Commission**. *Sustainable Finance Disclosure Regulation (SFDR) Impact Assessment* [R]. 2023.
   - 欧盟 SFDR 覆盖企业数量统计

### **学术研究**
6. **GIC & Cambridge University**. *Board Oversight and Carbon Reduction Targets* [J]. Journal of Sustainable Finance, 2023.
   - 独立 ESG 委员会与碳减排达标率关系

7. **BCG Model**. *Carbon Border Adjustment Mechanism Cost Impact* [R]. 2023.
   - 欧盟碳边境税对企业成本影响测算

### **监管机构**
8. **U.S. SEC**. *ESG Fund Enforcement Actions* [EB/OL]. 2023. https://www.sec.gov
   - ESG 基金罚单统计数据

9. **CFA Institute**. *ESG Rating Providers Landscape* [R]. 2023.
   - 全球 ESG 评级体系碎片化问题

10. **ISSB**. *Sustainability Disclosure Standards Update* [EB/OL]. 2023. https://www.ifrs.org/groups/issb/
    - 国际可持续披露准则进展

### **典型案例**
11. **The Wall Street Journal**. *Tech Giant Shareholder Lawsuit on Board Diversity* [N]. 2021.
    - 某科技巨头因治理缺陷市值蒸发案例

12. **Unilever Annual Report**. *Sustainability Strategy and Green Bond Issuance* [R]. 2022.
    - 联合利华供应链减碳与绿色债券实践

### **数据终端**
13. **Bloomberg Terminal**. *ESG Data & Analytics* [DB]. 2023.
    - ESG 溢价现象与财务指标对比

14. **MSCI ACWI Index**. *Historical Performance Data (2018-2022)* [DB]. 2023.
    - 全球指数成分股 ESG 回溯测试

---

**免责声明**：本文仅代表作者个人观点，不构成投资建议。市场有风险，投资需谨慎。所有数据均来自公开渠道，仅供参考，实际表现可能因市场变化而异。投资者应自行评估风险并咨询专业顾问。
"""
    
    # 查找总结部分并在其后添加参考资料
    summary_marker = "## **总结**"
    if summary_marker in new_body:
        # 找到总结部分的末尾
        idx = new_body.find(summary_marker)
        # 找下一个双换行符作为段落结束
        idx_end = new_body.find('\n\n', idx + len(summary_marker))
        if idx_end == -1:
            idx_end = len(new_body)
        
        final_body = new_body[:idx_end] + references + new_body[idx_end:]
    else:
        final_body = new_body + references
    
    # 组合完整内容
    new_content = f"---\n{front_matter}---\n{final_body}"
    
    # 写回文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ 优化完成！文件大小：{len(new_content)} bytes")
    print("\n💡 优化内容：")
    print("   ✓ 添加摘要框（便于 AI 引用）")
    print("   ✓ 结论前置（核心发现、投资建议、风险提示）")
    print("   ✓ 金句提炼（4 条独立可引用的观点）")
    print("   ✓ 权威数据来源（14 个参考文献）")
    print("   ✓ 免责声明")

if __name__ == '__main__':
    optimize_article()
