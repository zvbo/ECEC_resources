# Gemini Deep Research Agent 项目使用指南

本项目旨在利用 Google Gemini Deep Research Agent 进行纵向文献综述与证据地图构建。项目包含自动化脚本，用于将本地 PDF/文档上传至云端知识库，并调用 Deep Research 进行深度研究。

## 1. 环境准备

### 前置条件
*   拥有 Google Gemini API Key (需要支持 Deep Research 权限)。
*   本地安装 Python 3.8+。
*   准备好需要分析的文献文件夹（支持 PDF, DOCX, TXT 等）。

### 安装依赖
在终端中运行以下命令，自动创建虚拟环境并安装所需库：

```bash
bash setup_env.sh
```

或者手动安装：
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 2. 配置项目 (.env)

项目根目录会生成一个 `.env` 文件（如果没有请手动创建），请填入你的配置信息：

1.  打开 `.env` 文件。
2.  修改 `GOOGLE_API_KEY` 为你的真实 API Key。
3.  修改 `DOCS_DIR` 为你存放文献的**本地绝对路径**。

**.env 文件示例：**
```env
GOOGLE_API_KEY=AIzaSyDxxxxxxxxxxxxxxxxxxxxxxxx
DOCS_DIR=[需要进行云端储存的本地路径]
# 上传脚本运行后，会自动或手动填入 STORE NAME
FILE_STORE_NAME=
```

## 3. 自动化文档上传与知识库构建

本项目使用 `upload_knowledge_base.py` 脚本实现了从本地文件到 Gemini Knowledge Base 的全自动流程。

**核心机制：**
1.  **MIME 类型自动识别**：脚本内置了针对 PDF, CSV, DOCX, TXT 等常见学术格式的 MIME 映射，确保文件被正确解析。
2.  **原子化存储**：先将文件上传为 Google GenAI File 资源，然后创建 File Search Store，最后通过 `upload_to_file_search_store` 方法将文件与 Store 关联。
3.  **自动配置**：上传成功后，脚本会自动将生成的 `FILE_STORE_NAME` (例如 `fileSearchStores/xxx`) 写入 `.env` 文件。
4.  **元数据打标**：(实验性) 尝试为上传文件添加 `tags: "期刊类"`，配合 Deep Research 的过滤机制使用。

**运行命令：**

```bash
python upload_knowledge_base.py
```

*看到 "SUCCESS: Knowledge base ready" 提示即表示成功。*

## 4. 开始 Deep Research 研究

主程序 `run_research.py` 封装了 Google Gemini Deep Research Agent 的调用逻辑。

**工作流程：**
1.  **加载配置**：读取 `.env` 中的 API Key 和 `FILE_STORE_NAME`。
2.  **构建 Prompt**：使用内置的纵向研究 Prompt 模板，填入你的研究参数。
3.  **启动 Agent**：调用 `client.interactions.create`，并挂载 File Search 工具。配置中包含 `metadata_filter: "tags: \"期刊类\""`，确保 Agent 优先使用你的本地文献。
4.  **异步轮询**：脚本会在后台持续轮询任务状态 (`in_progress` -> `SUCCEEDED` / `FAILED`)，并打印实时进度。

**运行命令：**

```bash
python run_research.py
```

**查看结果：**

任务完成后，脚本会自动将最终的**Markdown 格式研究报告**保存到项目根目录下的 `final_report.md` 文件中。
同时，原始调试数据会保存到 `research_output_raw.txt`。

### 4.1 自定义研究课题 (重要)
**默认配置**是针对“儿童发展”领域的演示。在正式使用前，请务必修改 `run_research.py` 以适配您的研究：

1.  **修改 Prompt 模板**：打开 `run_research.py`，找到 `PROMPT_TEMPLATE` 变量。
2.  **修改角色设定**：将“儿童发展专家”改为适合您领域的角色（如“法律顾问”、“医学研究员”）。
3.  **修改任务要求**：调整 Prompt 中的 `研究任务说明` 和 `输出格式要求`，使其符合您的特定需求。
4.  **修改参数**：在 `main()` 函数中更新 `q` (问题), `age` (范围), `time_p` (时间) 等变量。

## 5. 项目完整研究流程

1.  **资料准备**：
    *   将您的 PDF/Word/TXT 文献放入本地文件夹 (例如 `docs/`)。
    *   在 `.env` 中配置 `DOCS_DIR` 指向该文件夹。
2.  **知识库构建** (`Data Layer`)：
    *   运行 `python upload_knowledge_base.py`。
    *   脚本会自动识别文件格式 -> 上传至 Google Cloud -> 创建/更新 File Search Store -> 自动更新 `.env` 中的 Store ID。
3.  **深度研究执行** (`Logic Layer`)：
    *   运行 `python run_research.py`。
    *   Agent 接收任务 -> 挂载 File Search 工具 -> 自动查询本地知识库 + 公开网络补全 -> 进行多步骤推理。
4.  **结果生成** (`Presentation Layer`)：
    *   任务完成后，脚本自动拉取结果，清洗格式，生成 `final_report.md`。

## 6. 项目参考架构

| 文件/目录 | 类型 | 说明 |
| :--- | :--- | :--- |
| `upload_knowledge_base.py` | **核心脚本** | **数据接入层**。负责扫描本地 `DOCS_DIR`，处理 MIME 类型，调用 SDK 上传文件并创建 File Search Store，最终更新环境配置。 |
| `run_research.py` | **核心脚本** | **业务逻辑层**。Deep Research Agent 的执行入口。包含 Prompt 模板管理、Interaction 会话创建、工具挂载配置以及结果轮询逻辑。 |
| `.env` | **配置文件** | **配置层**。存储敏感信息 (API Key) 和动态生成的资源 ID (Store Name)。**请勿提交到版本控制系统。** |
| `requirements.txt` | **依赖文件** | 定义项目运行所需的 Python 库 (`google-genai`, `python-dotenv`)。 |
| `setup_env.sh` | **工具脚本** | 一键环境初始化脚本。 |

## 常见问题

*   **报错 "GOOGLE_API_KEY not found"**: 请检查 `.env` 文件是否保存，并且变量名正确。
*   **上传报错 "unexpected keyword argument"**: 请确保使用最新版 `google-genai` SDK，本项目已针对 SDK 接口变化进行了适配 (使用 `file` 参数而非 `file_path`)。
*   **Deep Research 耗时**: 该 Agent 进行的是深度推理和多轮检索，任务运行可能耗时 5-30 分钟。脚本设计为长轮询模式，请保持终端开启或使用 `nohup` 后台运行。
