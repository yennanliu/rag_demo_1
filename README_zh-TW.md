# 簡易 RAG 示範系統

一個極簡優雅的檢索增強生成（RAG）系統，使用 Python 與記憶體內向量儲存實作。

<p align="center">
  <img src="doc/pic/demo_1.png" width="80%" alt="Landing Page"/>
</p>

**✨ 新功能：互動式網頁介面，輕鬆展示！**

👉 請參閱 [快速入門指南](doc/QUICKSTART.md) 三步驟快速設定。

## 功能特色

- **🌐 互動式網頁介面** - 精美的 UI，適合展示和實驗
- **簡易記憶體內向量資料庫** - 無需外部資料庫設定
- **語意搜尋** - 使用句子轉換器（sentence transformers）進行嵌入
- **LLM 整合** - OpenAI API 生成回答
- **乾淨的提示工程** - 遵循文件中的 RAG 最佳實踐
- **最小化依賴** - 僅需 Flask、OpenAI、sentence-transformers 和 numpy

## 設定

### 1. 安裝 UV（如尚未安裝）

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 安裝依賴套件

```bash
cd /Users/jerryliu/rag_demo_1
uv sync
```

### 3. 設定環境變數

複製範例環境檔：

```bash
cp .env.example .env
```

編輯 `.env` 並加入你的 API 金鑰：

```bash
# 必填：OpenAI API 金鑰
OPENAI_API_KEY=sk-xxxxxxxxxxxxx

# 選填：使用不同的 OpenAI 模型
OPENAI_MODEL=gpt-3.5-turbo

# 選填：HuggingFace token 以加速模型下載
# 從此處取得：https://huggingface.co/settings/tokens
HF_TOKEN=hf_xxxxxxxxxxxxx
```

應用程式會在執行時自動載入 `.env` 中的所有變數。

## 使用方式

### 🌐 網頁應用程式（推薦）

啟動互動式網頁介面：

```bash
uv run python app.py
```

然後在瀏覽器開啟 http://localhost:5000

**功能特色：**
- 💬 **對話式聊天** - 完整對話歷史與上下文
- 💾 **對話歷史** - 儲存、載入和管理過去的對話
- 📚 **顯示來源文件** - 查看哪些文件被用於回答
- ➕ **文件管理** - 新增、查看、刪除個別文件
- 📥 **匯出/匯入** - 將知識庫和對話存為 JSON 檔案
- ⚙️ **設定範例** - 編輯啟動時載入的預設文件
- 🔄 **自動持久化** - 對話自動儲存至 localStorage
- 🎨 **現代化 UI** - 乾淨、響應式介面，流暢動畫
- ⌨️ **鍵盤快捷鍵** - 為進階使用者提供快速工作流程
- 🏗️ **乾淨架構** - 模組化程式碼，關注點分離

**鍵盤快捷鍵：**
- `Enter` 在聊天中傳送訊息
- `Shift+Enter` 換行
- `Ctrl+Enter` 在文件欄位中：新增文件

### 📟 命令列

**快速開始：**

```bash
uv run python demo/example.py
```

包含 3 種不同情境：
- 員工目錄
- 產品文件
- 使用中繼資料進行組織

### 在你的程式碼中使用

```python
from rag import SimpleRAG

# 建立 RAG 實例
rag = SimpleRAG()

# 新增文件至知識庫
rag.add_document("你的文件內容")
rag.add_document("另一個文件", metadata={"source": "api-docs"})

# 查詢知識庫
answer = rag.generate_answer("你的問題")
print(answer)
```

## 運作原理

1. **索引**：使用 `sentence-transformers` 將文件轉換為嵌入向量
2. **檢索**：使用者查詢被嵌入，然後使用餘弦相似度找出前 k 個相似文件
3. **生成**：將檢索到的文件格式化為提示，遵循 RAG 最佳實踐
4. **LLM 呼叫**：將提示傳送至 GPT-3.5-turbo 生成回答

## 架構

```
使用者查詢
    ↓
嵌入模型
    ↓
相似度搜尋（餘弦）
    ↓
檢索前 K 個文件
    ↓
格式化 RAG 提示
    ↓
OpenAI API
    ↓
生成回答
```

## RAG 提示範本

系統使用此提示結構（來自 `/doc/prompt_gpt.txt`）：

```
你是一個有幫助的助手。

遵循以下規則：
- 僅使用提供的上下文
- 簡潔且事實性
- 如果不確定，說「我不知道」
- 不要編造資訊

上下文：
{檢索到的文件}

問題：
{使用者查詢}

有用的回答：
```

## 檔案

**網頁應用程式：**
- `app.py` - Flask 後端與 REST API
- `templates/index.html` - 主要 HTML 範本
- `static/styles.css` - 現代白色主題 CSS
- `static/app.js` - 客戶端 JavaScript（聊天、文件管理）

**核心 RAG：**
- `rag.py` - 核心 RAG 實作與嵌入
- `demo/rag_local.py` - 選用的本地 LLM 變體（無 API 費用）
- `demo/example.py` - 命令列使用範例

**設定：**
- `pyproject.toml` - UV 專案依賴
- `config.json` - 範例文件（使用者可編輯，不提交）
- `config.example.json` - 範例設定範本
- `.env` - API 金鑰和設定（不提交）
- `.env.example` - 範例環境變數

**文件：**
- `README.md` - 完整文件（英文版）
- `README_zh-TW.md` - 本檔案（繁體中文版）
- `doc/QUICKSTART.md` - 快速 3 步驟設定指南
- `doc/ARCHITECTURE.md` - 完整架構文件
- `doc/WHATS_NEW.md` - 新功能使用指南
- `doc/ENHANCEMENTS_SUMMARY.md` - 詳細增強功能分析

## 設定

### 範例文件（`config.json`）

網頁應用程式在啟動時從 `config.json` 載入範例文件。你可以編輯：

1. **透過網頁 UI**：前往「範例文件設定」區段
2. **透過檔案**：直接編輯 `config.json`

範例 `config.json`：
```json
{
  "sample_documents": [
    "你的第一個範例文件",
    "你的第二個範例文件"
  ]
}
```

設定檔會在首次執行時自動建立。使用 `config.example.json` 作為範本。

### 對話歷史

對話會自動儲存至瀏覽器 localStorage，並可持久化至伺服器。

**自動儲存（LocalStorage）：**
- 對話在頁面重新整理後仍保留
- 僅儲存在瀏覽器
- 無需伺服器互動

**伺服器端儲存：**
1. 點擊 **「📥 儲存」** 將當前對話儲存至伺服器
2. 點擊 **「💾 歷史」** 查看所有已儲存的對話
3. 載入、匯出或刪除個別對話
4. 將所有對話匯出為單一 JSON 檔案
5. 匯入先前匯出的對話

**對話檔案：**
- 儲存在 `conversations/` 目錄
- 以時間戳記命名：`20260324_143022.json`
- 包含完整的訊息歷史與來源
- 可在使用者之間共享

## 環境變數

所有變數會自動從 `.env` 載入：

- **OPENAI_API_KEY**（必填）- 你的 OpenAI API 金鑰用於 GPT 模型
- **OPENAI_MODEL**（選填）- 預設為 `gpt-3.5-turbo`，可使用 `gpt-4` 或其他模型
- **HF_TOKEN**（選填）- HuggingFace token 以加速模型下載，無速率限制
  - 無 token：約 100 請求/小時限制
  - 有 token：顯著提高限制
  - 從此處取得 token：https://huggingface.co/settings/tokens

## 注意事項

- 嵌入模型（`all-MiniLM-L6-v2`）輕量且在 CPU 上執行
- 對於大型部署，請考慮使用外部向量資料庫如 Pinecone、Weaviate 或 Milvus
- 你可以透過傳遞 `embedding_model` 參數至 `SimpleRAG()` 來更換嵌入模型

## 單元測試

執行單元測試：

```bash
uv run pytest tests/
```

測試涵蓋：
- RAG 核心功能
- 設定管理
- 對話持久化
- API 端點

## 授權

MIT

---

**繁體中文版本 | Traditional Chinese Version**

如需英文版本，請參閱 [README.md](README.md)
