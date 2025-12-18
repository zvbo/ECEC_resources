import os
import time
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURATION ---
# Replace with the Store ID from upload_knowledge_base.py (or AI Studio)
FILE_STORE_NAME = os.getenv("FILE_STORE_NAME", "fileSearchStores/my-child-dev-store")

# Prompt Template
PROMPT_TEMPLATE = """
你是一个严谨的儿童发展与方法论研究助手，专门针对 0–8 岁儿童的纵向研究，进行系统性文献综述和证据地图构建。

一、研究任务说明
我现在要围绕如下核心问题做“纵向文献综述 + 证据地图”：

研究问题：
{research_question}

年龄范围：
{age_range}

时间范围：
{time_range}

研究设计优先级：先纵向/队列，其次随机对照试验，再考虑高质量横断研究。

二、数据来源要求（非常重要）
优先使用我提供的本地文献知识库（File Search），这些文献包括：
我自己整理的 0–8 岁执行功能、语言发展、家庭环境相关论文与报告
我整理的中文/英文政策文件与综述
当本地文献不足以回答子问题时，再使用公开网络搜索。

所有结论必须明确区分：
基于“本地知识库文献”的证据
基于“公开网络检索”的补充证据

三、工作流要求（对 Deep Research 的过程约束）
请严格按以下步骤工作：

1. 问题分解与检索策略设计
把核心问题拆成 3–6 个子问题（例如：样本特征、测量工具、效应方向和大小、调节/中介变量、关键方法差异等）。
为每个子问题设计检索式（英文为主，必要时含中文或其他语言关键词）。
明确哪些子问题优先用本地文献就能回答，哪些需要外部检索。

2. 文献筛选与结构化抽取
对候选文献进行题目+摘要层面的快速筛选，并在内部记录纳入/排除的主要理由。
对纳入文献抽取以下字段，形成“证据表格”：
作者与年份
国家/地区
样本量与样本特征（年龄段、风险群体与否）
研究设计类型（纵向/队列/RCT/横断等）
主要测量工具（执行功能、语言、家庭环境、其他协变量）
跟踪时长与测量次数
主要结果方向（正向/负向/无显著关系）
效应大小或可比指标（如相关系数、标准化回归系数，如果有的话）

3. 证据综合与证据地图
按子问题组织“叙述性综述”，清楚说明：
哪些结果在不同研究间一致
哪些结果存在冲突及可能原因（测量工具不同、样本不同等）
构造一张“证据地图”的文字版：
维度 A：年龄段或发展阶段
维度 B：环境因素类型（如家庭语言环境、亲子互动质量、教育机构质量）
维度 C：结果类型（执行功能子构念、语言、情绪行为等）
在地图中标注：证据数量、质量大致水平、主要发现方向。

4. 研究设计与测量工具建议（方法学部分）
基于现有证据，总结目前该领域常用的研究设计范式：
常见测量时间点、常见样本规模、典型协变量控制方式。
列出适用于 {target_age} 的常用测量工具清单：
对每个工具，只描述：名称、适用年龄、测量维度、条目量级、是否有本土化版本与已报道信效度；不要复制或生成量表内容本身，以避免版权问题。
在此基础上，为“未来一项新纵向研究”给出 2–3 个候选设计方案（简要列出优点与局限）。

四、输出格式要求
请以结构化方式输出：
「研究问题与分解子问题」
「检索与纳入原则简述」（说明本地文献与外部网络的占比）
「证据表格（文字描述形式）」
「证据地图的文字说明」
「主要结论 + 尚不确定/有争议的领域」
「未来研究设计与测量工具建议」

在报告中保持“研究者口吻”，严谨、中性，需要准确（不可以无中生有，美化结果）遇到证据不足时要明确写出“不足之处”，而不是进行想象性推断。
如果用户2026年及以后的数据不可获得，请直接说明“暂无相关文献或暂未检索到”，不要编造未来研究。
"""

def generate_prompt(question, age, time_period, target):
    return PROMPT_TEMPLATE.format(
        research_question=question,
        age_range=age,
        time_range=time_period,
        target_age=target
    )

def main():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY must be set in .env or environment variables.")
        return

    client = genai.Client(api_key=api_key)

    # Example Input Defaults
    q = "2-3岁儿童的执行功能发展的误区和研究重点"
    age = "0–8岁，重点 2-3 岁"
    time_p = "2015–2025年发表"
    target = "目标年龄段 (2-3岁)"

    prompt = generate_prompt(q, age, time_p, target)

    print(f"Starting Deep Research Interaction (Background Mode)...")
    print(f"Using Store: {FILE_STORE_NAME}")
    
    try:
        interaction = client.interactions.create(
            input=prompt,
            agent="deep-research-pro-preview-12-2025",
            background=True,
            tools=[
                {
                    "type": "file_search",
                    "file_search_store_names": [FILE_STORE_NAME],
                    # Metadata Filtering based on user request ("期刊类")
                    # Syntax: Key-Value filtering.
                    # Assuming we tagged files with 'tags': ['期刊类']
                    # Using Python SDK filter syntax (might need adjustment based on exact backend version)
                    # "metadata_filter" or "filter" depending on SDK structure for tool config
                    "metadata_filter": "tags: \"期刊类\"" 
                }
            ],
            agent_config={
                "type": "deep-research",
                "thinking_summaries": "auto"
            }
        )
        
        print("\nInteraction created successfully!")
        
        # DEBUG: Print structure
        print("DEBUG: Interaction Object Attributes:", dir(interaction)) 
        
        # Try to get ID safely
        interaction_name = getattr(interaction, 'name', None) or getattr(interaction, 'id', None)
        print(f"Interaction Name/ID: {interaction_name}")
        
        if not interaction_name:
             print("Could not determine interaction name/ID. Exiting.")
             return
        
        # Poll for results
        print("\nWaiting for results (this may take a while)...")
        while True:
            # Fix: Use 'id' parameter as per inspection
            current_state = client.interactions.get(id=interaction_name)
            
            # Fix: Use 'status' property as per inspection of Interaction object
            status = current_state.status 
            
            # Map status string if needed (assuming 'SUCCEEDED', 'FAILED' are values)
            # If status is an enum, we might need str(status) or status.name
            print(f"Status: {status}...", end="\r")
            
            if str(status).lower() in ["succeeded", "completed"]:
                print("\n\nResearch Completed!")
                # Extract output
                # The output format depends on the API response structure
                # Typically loop through messages or filtered outputs
                # Extract Output Content
                print(current_state) 
                
                # Extract and save the clean markdown report
                report_content = ""
                
                # Iterate through outputs to find text content
                # The structure is usually interaction.outputs -> list of Content items
                if hasattr(current_state, 'outputs') and current_state.outputs:
                    for item in current_state.outputs:
                         # Find TextContent items (the actual report)
                        if hasattr(item, 'text') and item.text:
                            report_content += item.text + "\n"
                
                if report_content:
                    with open("final_report.md", "w") as f:
                        f.write(report_content)
                    print("\nSuccess! Clean report saved to 'final_report.md'")
                else: 
                     print("\nWarning: No text content found in outputs. Saving raw state.")
                
                # Also save raw state for debug
                with open("research_output_raw.txt", "w") as f:
                    f.write(str(current_state))
                print("Raw debug data saved to 'research_output_raw.txt'")
                
                break
            elif str(status).lower() == "failed":
                print("\nResearch Failed.")
                if hasattr(current_state, 'error'):
                    print(current_state.error)
                else:
                    print("Error details not available directly on object.")
                break
            
            time.sleep(10) # Wait 10 seconds before polling again

    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()
