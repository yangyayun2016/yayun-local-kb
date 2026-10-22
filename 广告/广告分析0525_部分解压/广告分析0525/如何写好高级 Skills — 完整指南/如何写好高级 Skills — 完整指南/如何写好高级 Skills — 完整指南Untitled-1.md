如何写好高级 Skills — 完整指南
# 🧠 高级 Skills 深度研究：知识库 + 向量库 + RAG + MiniLM + 提示词工程

--- 怎么写skills，写出高级Skills---

## 一、整体架构全景图

先看清楚这几个组件之间的关系：

```
用户提问 / 任务触发
        │
        ▼
┌───────────────────────────────────────────────────────────────────┐
│                        Skill 执行引擎                              │
│                                                                   │
│  ┌─────────────┐     ┌──────────────────────────────────────┐    │
│  │  提示词模板   │     │         RAG 检索增强管线              │    │
│  │             │     │                                      │    │
│  │ • 批注       │     │  用户Query ──▶ MiniLM 编码 ──▶ 向量  │    │
│  │ • 背景交代   │     │                                │     │    │
│  │ • 上下文注入 │     │              ┌─────────────────┘     │    │
│  │ • 单一任务   │     │              ▼                       │    │
│  │ • 输出合同   │     │  ┌────────────────┐  ┌──────────┐   │    │
│  └──────┬──────┘     │  │   向量数据库     │  │ 知识图谱  │   │    │
│         │            │  │ (ChromaDB/FAISS)│  │ (Neo4j)  │   │    │
│         │            │  │   语义相似检索   │  │  精确关系  │   │    │
│         │            │  └───────┬────────┘  └────┬─────┘   │    │
│         │            │          │                 │         │    │
│         │            │          └────────┬────────┘         │    │
│         │            │                   ▼                  │    │
│         │            │           检索到的上下文 Chunks        │    │
│         │            └───────────────────┬──────────────────┘    │
│         │                                │                       │
│         └───────────────┬────────────────┘                       │
│                         ▼                                        │
│              ┌─────────────────────┐                             │
│              │    LLM 推理生成      │                             │
│              │ (GPT-4 / Claude)    │                             │
│              └──────────┬──────────┘                             │
│                         ▼                                        │
│              结构化输出 (JSON + 元数据 + 置信度)                    │
└───────────────────────────────────────────────────────────────────┘
```

---

## 二、Microsoft MiniLM 深度使用

### 2.1 为什么选 MiniLM？

```
┌──────────────────┬──────────────┬───────────────┬───────────────┐
│      模型         │   维度       │   速度        │   适用场景     │
├──────────────────┼──────────────┼───────────────┼───────────────┤
│ all-MiniLM-L6-v2 │   384维      │  ⚡ 极快      │ 实时检索/边缘  │
│ all-MiniLM-L12-v2│   384维      │  🔵 快        │ 精度优先      │
│ OpenAI ada-002   │   1536维     │  🔴 慢(API)   │ 通用高精度    │
│ BGE-large-zh     │   1024维     │  🟡 中等      │ 中文专用      │
└──────────────────┴──────────────┴───────────────┴───────────────┘

✅ MiniLM 优势：本地运行、零成本、低延迟、384维够用
```

### 2.2 MiniLM 完整集成代码

```python
# ============================================================
# 第一步：安装依赖
# pip install sentence-transformers chromadb langchain tiktoken
# ============================================================

from sentence_transformers import SentenceTransformer
import numpy as np

class MiniLMEmbedder:
    """基于微软 MiniLM 的嵌入引擎 —— Skills 的"感知层" """
    
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        # ✅ 首次运行自动从 HuggingFace 下载（约 80MB）
        # ✅ 之后完全本地离线运行
        self.model = SentenceTransformer(model_name)
        self.dimension = 384  # MiniLM-L6 输出维度
        
    def encode(self, texts: list[str], batch_size=64) -> np.ndarray:
        """
        批量编码文本为向量
        
        参数:
            texts: 文本列表（可以是句子、段落、整篇文档）
            batch_size: 批处理大小（GPU显存不够时调小）
        返回:
            numpy数组, shape = (len(texts), 384)
        """
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            normalize_embeddings=True  # ✅ L2归一化，余弦相似度 = 点积
        )
        return embeddings
    
    def similarity(self, query: str, candidates: list[str]) -> list[dict]:
        """计算 query 与候选文本的语义相似度"""
        query_vec = self.model.encode([query], normalize_embeddings=True)
        cand_vecs = self.model.encode(candidates, normalize_embeddings=True)
        
        # 归一化后点积 = 余弦相似度
        scores = np.dot(cand_vecs, query_vec.T).flatten()
        
        results = [
            {"text": t, "score": float(s)} 
            for t, s in zip(candidates, scores)
        ]
        return sorted(results, key=lambda x: x["score"], reverse=True)


# ============================================================
# 使用示例
# ============================================================
embedder = MiniLMEmbedder()

# 测试语义理解能力
query = "电池续航太短了"
candidates = [
    "这个充电宝容量不够，用半天就没电了",      # ✅ 语义相关
    "产品外观非常漂亮，颜色很好看",             # ❌ 不相关
    "电量消耗太快，出门必须带充电器",            # ✅ 语义相关
    "包装盒有破损，但产品本身没问题",            # ❌ 不相关
]

results = embedder.similarity(query, candidates)
for r in results:
    print(f"  [{r['score']:.4f}] {r['text']}")

# 输出：
#   [0.8234] 电量消耗太快，出门必须带充电器
#   [0.7891] 这个充电宝容量不够，用半天就没电了
#   [0.1245] 包装盒有破损，但产品本身没问题
#   [0.0987] 产品外观非常漂亮，颜色很好看
```

---

## 三、知识库 + 向量库 构建

### 3.1 文档切分策略（关键中的关键）

```python
class SmartChunker:
    """
    智能文档切分器
    
    ❌ 错误做法：按固定字数硬切（会切断语义）
    ✅ 正确做法：按语义边界切分 + 重叠窗口
    """
    
    def __init__(self, chunk_size=512, overlap=64):
        self.chunk_size = chunk_size   # 每个chunk的token数
        self.overlap = overlap          # 重叠token数（防止边界丢失信息）
    
    def chunk_document(self, document: dict) -> list[dict]:
        """
        参数:
            document: {"title": "...", "content": "...", "metadata": {...}}
        返回:
            [{"chunk_id": "doc1_chunk_0", "text": "...", "metadata": {...}}, ...]
        """
        text = document["content"]
        
        # ✅ 策略1：优先按自然段落切分
        paragraphs = text.split("\n\n")
        
        chunks = []
        current_chunk = ""
        chunk_idx = 0
        
        for para in paragraphs:
            # 如果加上这一段不超限，就合并
            if len(current_chunk) + len(para) < self.chunk_size:
                current_chunk += para + "\n\n"
            else:
                # 保存当前chunk
                if current_chunk.strip():
                    chunks.append(self._make_chunk(
                        document, current_chunk.strip(), chunk_idx
                    ))
                    chunk_idx += 1
                
                # ✅ 策略2：重叠窗口 —— 保留上一段最后N个字符
                overlap_text = current_chunk[-self.overlap:] if len(current_chunk) > self.overlap else ""
                current_chunk = overlap_text + para + "\n\n"
        
        # 最后一个chunk
        if current_chunk.strip():
            chunks.append(self._make_chunk(document, current_chunk.strip(), chunk_idx))
        
        return chunks
    
    def _make_chunk(self, doc, text, idx):
        return {
            "chunk_id": f"{doc.get('doc_id', 'unknown')}_chunk_{idx}",
            "text": text,
            "metadata": {
                **doc.get("metadata", {}),
                "source_title": doc.get("title", ""),
                "chunk_index": idx,
                "char_count": len(text),
                # ✅ 关键：保留来源信息，供后续"证据链"追溯
            }
        }
```

### 切分策略可视化对比

```
原始文档：
┌──────────────────────────────────────────────────┐
│ 第一段：产品A的电池采用锂聚合物技术...             │
│ 第二段：续航测试结果显示在连续使用场景下...         │
│ 第三段：与竞品B对比，A的充电速度快30%...           │
│ 第四段：用户反馈中，85%提到了续航满意度...          │
└──────────────────────────────────────────────────┘

❌ 硬切（固定200字）：
┌────────────┐┌────────────┐┌────────────┐
│产品A的电池采│用锂聚合物...│续航测试结果显│  ← 把"采用"切断了！
└────────────┘└────────────┘└────────────┘

✅ 语义切分 + 重叠：
┌──────────────────────┐
│ Chunk 0:              │
│ 第一段 + 第二段       │  ← 按段落边界
│                       │
│  ...连续使用场景下... │  ← 保留尾部64字符
└──────────────────────┘
          ┌──────────── overlap ──┐
┌──────────────────────┐          │
│ Chunk 1:              │          │
│ ...连续使用场景下...  │  ← 重叠区│
│ 第三段 + 第四段       │
└──────────────────────┘
```

### 3.2 向量数据库构建（ChromaDB）

```python
import chromadb
from chromadb.utils import embedding_functions

class VectorKnowledgeBase:
    """
    向量知识库 —— Skills 的"长期语义记忆"
    
    知识库(文档) ──切分──▶ Chunks ──MiniLM编码──▶ 向量 ──存入──▶ ChromaDB
    """
    
    def __init__(self, collection_name="skill_knowledge"):
        # ✅ 使用 MiniLM 作为嵌入函数
        self.ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # 持久化存储（重启不丢失）
        self.client = chromadb.PersistentClient(path="./chroma_db")
        
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.ef,
            metadata={"hnsw:space": "cosine"}  # ✅ 余弦距离
        )
    
    def ingest(self, chunks: list[dict]):
        """批量写入知识chunks"""
        self.collection.add(
            ids=[c["chunk_id"] for c in chunks],
            documents=[c["text"] for c in chunks],
            metadatas=[c["metadata"] for c in chunks]
        )
        print(f"✅ 已写入 {len(chunks)} 个chunks，总计 {self.collection.count()} 条")
    
    def search(self, query: str, top_k=5, filters: dict = None) -> list[dict]:
        """
        语义检索
        
        参数:
            query: 自然语言查询
            top_k: 返回前K条最相关结果
            filters: 元数据过滤（如 {"source": "competitor_report"}）
        """
        where_filter = filters if filters else None
        
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where_filter,
            include=["documents", "metadatas", "distances"]
        )
        
        retrieved = []
        for i in range(len(results["ids"][0])):
            retrieved.append({
                "chunk_id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "relevance_score": 1 - results["distances"][0][i],  # 距离→相似度
            })
        
        return retrieved


# ============================================================
# 完整流程演示
# ============================================================

# 1. 准备知识文档
documents = [
    {
        "doc_id": "competitor_report_2024",
        "title": "2024年Q3竞品分析报告",
        "content": """
            竞品A（ASIN: B0XXXXX）在7月进行了大幅降价，从$49.99降至$34.99。
            分析认为这是一次清库存行为，因为其供应商（东莞XX工厂）同期发布了新模具。
            
            竞品B的广告策略转向了长尾词，放弃了核心大词"wireless charger"的竞价，
            转而主攻"wireless charger for iphone 15 magsafe"等精确匹配词。
            其ACOS从45%降至22%。
            
            市场整体趋势：消费者对"快充"需求增长了67%，但Top 10竞品中
            仅有3家在Listing中提及"65W快充"功能。这是一个明显的内容差距。
        """,
        "metadata": {"type": "report", "quarter": "2024Q3", "category": "charger"}
    },
    {
        "doc_id": "review_analysis_001",
        "title": "消费者评论痛点汇总",
        "content": """
            通过分析Top 20竞品的共计15,000条评论，提取出以下高频痛点：
            1. 充电速度慢（提及率38%）——消费者期望至少30W以上
            2. 发热严重（提及率25%）——尤其是夏天使用场景
            3. 不兼容新款手机（提及率18%）——iPhone 15 MagSafe适配问题
            4. 外观廉价感（提及率12%）——对比Anker等品牌
            5. 数据线质量差（提及率7%）——容易断裂
        """,
        "metadata": {"type": "review_analysis", "category": "charger"}
    }
]

# 2. 切分
chunker = SmartChunker(chunk_size=400, overlap=50)
all_chunks = []
for doc in documents:
    all_chunks.extend(chunker.chunk_document(doc))

# 3. 写入向量库
kb = VectorKnowledgeBase(collection_name="amazon_competitor_intel")
kb.ingest(all_chunks)

# 4. 语义检索
results = kb.search("竞品为什么降价", top_k=3)
for r in results:
    print(f"\n[相似度: {r['relevance_score']:.4f}]")
    print(f"来源: {r['metadata']['source_title']}")
    print(f"内容: {r['text'][:100]}...")
```

---

## 四、RAG Skill 完整实现

### 4.1 RAG 管线架构

```
用户 Query
    │
    ▼
┌─────────────────────┐
│  Step 1: 查询改写    │  ← 把模糊问题变精确
│  "价格怎么了"        │
│  → "竞品近期价格异动  │
│     原因是什么"       │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐     ┌─────────────────┐
│  Step 2: 双路检索    │     │                 │
│                     │────▶│  向量库 (语义)    │ → 相似内容chunks
│  同时发起            │     │  MiniLM cosine   │
│  两路检索            │     └─────────────────┘
│                     │     ┌─────────────────┐
│                     │────▶│  知识图谱 (精确)  │ → 关系/实体
│                     │     │  Cypher 查询     │
└─────────┬───────────┘     └─────────────────┘
          │
          ▼
┌─────────────────────┐
│  Step 3: 重排序      │  ← 对检索结果按相关性重新排序
│  Cross-Encoder      │
│  或 LLM 打分        │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Step 4: 提示词组装  │  ← 将检索到的上下文注入Prompt
│  背景 + 批注 +       │
│  上下文 + 任务指令   │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Step 5: LLM 生成    │  ← 基于证据生成答案
│  + 置信度打分        │
│  + 证据引用标注      │
└─────────────────────┘
```

### 4.2 完整 RAG Skill 代码

```python
class RAGSkill:
    """
    检索增强生成 Skill —— 知识库 + 向量库 + MiniLM + LLM
    
    这是一个"组合型高级Skill"，内部包含多个子步骤
    """
    
    def __init__(self, vector_kb, kg_client, llm):
        self.vector_kb = vector_kb      # 向量知识库（ChromaDB + MiniLM）
        self.kg = kg_client             # 知识图谱（Neo4j）
        self.llm = llm                  # 大语言模型
        self.embedder = MiniLMEmbedder()
    
    def execute(self, input_data: dict) -> dict:
        """
        输入: {"query": "...", "context": {...}, "step_info": {"current": 2, "total": 5}}
        输出: {"status": "...", "answer": "...", "evidence": [...], "confidence": 0.85}
        """
        
        query = input_data["query"]
        context = input_data.get("context", {})
        
        # ═══════════════════════════════════════
        # Step 1: 查询改写（Query Rewriting）
        # ═══════════════════════════════════════
        rewritten_query = self._rewrite_query(query, context)
        
        # ═══════════════════════════════════════
        # Step 2: 双路检索（Hybrid Retrieval）
        # ═══════════════════════════════════════
        
        # 路径A：向量语义检索
        vector_results = self.vector_kb.search(
            query=rewritten_query,
            top_k=8,
            filters=context.get("search_filters")  # 可按类目/时间过滤
        )
        
        # 路径B：知识图谱精确检索
        kg_results = self._query_knowledge_graph(rewritten_query, context)
        
        # ═══════════════════════════════════════
        # Step 3: 重排序（Re-ranking）
        # ═══════════════════════════════════════
        reranked = self._rerank(query, vector_results, top_k=5)
        
        # ═══════════════════════════════════════
        # Step 4: 组装提示词 + 生成
        # ═══════════════════════════════════════
        answer = self._generate_answer(
            query=query,
            retrieved_chunks=reranked,
            kg_context=kg_results,
            task_context=context
        )
        
        return answer
    
    # --------------------------------------------------
    # 内部方法
    # --------------------------------------------------
    
    def _rewrite_query(self, query: str, context: dict) -> str:
        """将用户模糊查询改写为精确检索查询"""
        prompt = f"""请将以下用户问题改写为更适合知识库检索的查询语句。
保留核心意图，补充必要的限定词。

用户问题: {query}
当前上下文: {json.dumps(context, ensure_ascii=False)}

只输出改写后的查询，不要其他内容。"""
        
        return self.llm.invoke(prompt).strip()
    
    def _query_knowledge_graph(self, query: str, context: dict) -> dict:
        """从知识图谱检索结构化信息"""
        # 先用 LLM 将自然语言转为 Cypher 查询
        cypher_prompt = f"""你是Neo4j Cypher专家。根据问题生成查询语句。

图谱Schema:
- (:ASIN)-[:CompetesWith]->(:ASIN)
- (:ASIN)-[:HasIssue]->(:PainPoint)
- (:ASIN)-[:Dominates]->(:Keyword)
- (:ASIN)-[:DerivedFrom]->(:Supplier)
- (:ASIN)-[:BelongsTo]->(:Brand)

问题: {query}
只输出Cypher语句:"""
        
        cypher = self.llm.invoke(cypher_prompt).strip()
        
        try:
            results = self.kg.query(cypher)
            return {"status": "success", "data": results, "cypher": cypher}
        except Exception as e:
            return {"status": "error", "reason": str(e), "cypher": cypher}
    
    def _rerank(self, query: str, results: list, top_k=5) -> list:
        """用 Cross-Encoder 或 LLM 对检索结果重排序"""
        
        # 方法1：用 MiniLM 快速重排（计算 query 与每个 chunk 的精确相似度）
        texts = [r["text"] for r in results]
        scores = self.embedder.similarity(query, texts)
        
        # 按新分数排序，取 top_k
        score_map = {s["text"]: s["score"] for s in scores}
        for r in results:
            r["rerank_score"] = score_map.get(r["text"], 0)
        
        reranked = sorted(results, key=lambda x: x["rerank_score"], reverse=True)
        return reranked[:top_k]
    
    def _generate_answer(self, query, retrieved_chunks, kg_context, task_context):
        """组装最终提示词并生成答案"""
        
        # ✅ 构建带编号的证据文本（用于引用标注）
        evidence_text = ""
        for i, chunk in enumerate(retrieved_chunks, 1):
            source = chunk["metadata"].get("source_title", "未知来源")
            evidence_text += f"\n[证据{i}] (来源: {source}, 相关度: {chunk['rerank_score']:.2f})\n"
            evidence_text += f"{chunk['text']}\n"
        
        # ✅ 构建知识图谱上下文
        kg_text = ""
        if kg_context.get("status") == "success" and kg_context.get("data"):
            kg_text = f"\n知识图谱查询结果:\n{json.dumps(kg_context['data'], ensure_ascii=False, indent=2)}"
        
        # ══════════════════════════════════════════
        #  核心：高质量提示词模板
        # ══════════════════════════════════════════
        
        prompt = f"""\
# 角色与背景（批注：告诉AI它是谁）
你是一位资深的亚马逊运营分析专家，拥有10年跨境电商经验。
你擅长从多维数据中发现竞争机会。

# 上下文（批注：交代当前状态）
当前分析阶段: {task_context.get('phase', '通用分析')}
目标类目: {task_context.get('category', '未指定')}
关注的ASIN: {task_context.get('target_asin', '未指定')}

# 检索到的知识库证据
{evidence_text}

# 知识图谱关系数据
{kg_text}

# 任务（批注：单一明确任务）
请基于以上证据，回答以下问题：
{query}

# 输出要求（批注：严格约束格式）
必须按以下JSON格式输出：
{{
    "answer": "你的分析结论（必须引用证据编号，如[证据1]）",
    "key_findings": ["发现1", "发现2", "发现3"],
    "evidence_used": [1, 3],
    "confidence_score": 0.85,
    "reasoning_chain": [
        "第一步推理...",
        "第二步推理...",
        "因此得出结论..."
    ],
    "limitations": "数据不足或不确定的地方",
    "suggested_next_skill": "建议下一步调用的Skill名称（如需要）"
}}

# 约束（批注：防止幻觉）
- 只基于提供的证据作答，不要编造数据
- 没有证据支撑的观点必须标注"推测"
- confidence_score < 0.6 时，在limitations中说明原因
"""
        
        response = self.llm.invoke(prompt)
        
        try:
            result = json.loads(response)
            result["status"] = "success"
            result["source_chunks"] = [c["chunk_id"] for c in retrieved_chunks]
            return result
        except json.JSONDecodeError:
            return {
                "status": "error",
                "reason": "LLM输出不是有效JSON",
                "raw_output": response,
                "suggestion": "retry_with_stricter_prompt"
            }
```

---

## 五、提示词工程四大法则（深度展开）

### 法则 1：批注（Annotations）

```python
# ❌ 没有批注 —— AI 不理解你为什么这样要求
prompt = """分析竞品，输出JSON。"""

# ✅ 有批注 —— AI 理解每个要求背后的原因
prompt = """
# 角色定义（批注：限定专业领域，减少通用废话）
你是亚马逊广告优化专家。

# 数据输入（批注：明确告诉AI数据的含义和时间范围）
以下是过去30天的广告数据，ACOS=广告销售成本比。

# 分析要求（批注：为什么要求这样做——因为运营需要可执行的建议）
请找出ACOS > 40%的关键词，并给出具体的"降低出价"或"否定关键词"建议。
不要给笼统建议（如"优化广告"），必须具体到词级别操作。

# 输出格式（批注：下游Skill需要解析JSON，所以格式必须严格）
输出严格JSON格式，因为该输出将被自动化管线中的下一个Skill解析。
"""
```

### 法则 2：交代背景（Background Context）

```python
# ✅ 背景交代模板 —— 分三层
BACKGROUND_TEMPLATE = """
┌─────────────────────────────────────────────┐
│  Layer 1: 业务背景（这个任务是什么）          │
│  "我们是一家跨境电商公司，主营3C配件类目，    │
│   目前在美国站的市场份额约3%。"               │
│                                             │
│  Layer 2: 当前状态（现在到了哪一步）          │
│  "这是我们每周竞品监控流程的第3步，            │
│   前两步已经完成了数据采集和实体提取。"        │
│                                             │
│  Layer 3: 期望结果（你要什么产出）             │
│  "我需要一份可以直接发给运营团队执行的         │
│   竞品应对方案，包含具体的价格调整建议。"      │
│                                             │
└─────────────────────────────────────────────┘
"""
```

### 法则 3：上下文注入（Context Injection）

```python
def build_context_aware_prompt(query, skill_context):
    """
    上下文不是越多越好，而是越"相关"越好
    
    ✅ 上下文选择策略：
    1. 从向量库检索的 top-5 chunks（语义相关）
    2. 从知识图谱获取的实体关系（结构化事实）
    3. 前序 Skill 的输出（流程状态）
    4. 历史对话/决策记录（避免重复）
    """
    
    context_block = f"""
## 前序 Skill 产出（上游数据）
{json.dumps(skill_context.get('previous_skill_output', {}), ensure_ascii=False)}

## 知识图谱实体关系
{skill_context.get('kg_entities', '无相关实体')}

## 向量库检索结果（按相关度排序）
{skill_context.get('retrieved_chunks', '无检索结果')}

## 当前流程状态
步骤: {skill_context.get('current_step', '?')}/{skill_context.get('total_steps', '?')}
已尝试次数: {skill_context.get('retry_count', 0)}
上次失败原因: {skill_context.get('last_failure_reason', '无')}
"""
    return context_block
```

### 法则 4：单一任务（Single Task）

```python
# ❌ 多任务混合 —— AI 会顾此失彼
bad_prompt = """
分析竞品价格，同时写一篇Listing文案，顺便给出广告投放建议。
"""

# ✅ 单一任务 —— 一个 Skill 一个任务，清晰专注
# 拆成3个独立 Skill:

SKILL_1_PROMPT = """
【唯一任务】分析以下竞品的价格变化趋势，判断降价原因。
不要做其他任何事情。
"""

SKILL_2_PROMPT = """
【唯一任务】基于上一步的竞品分析结果，撰写差异化的Listing标题和五点描述。
不要分析价格，不要给广告建议。
"""

SKILL_3_PROMPT = """
【唯一任务】基于前两步的分析和文案，生成广告关键词投放方案。
只关注广告层面，不要修改文案。
"""
```

---

## 六、完整的多 Skill 组合示例

### 场景：「竞品防守薄弱点挖掘」全自动化工作流

```python
class CompetitorWeaknessWorkflow:
    """
    完整工作流：4个Skill闭环组合
    
    Step 1: MarketMapper    → 扫描Top50竞品
    Step 2: GraphLinker     → 连接知识图谱，找共同痛点
    Step 3: GapAnalyzer     → RAG分析需求差距
    Step 4: ContentGenerator→ 生成优化方案
    
    + CriticSkill 在每步之后验证质量
    """
    
    def __init__(self):
        self.embedder = MiniLMEmbedder()
        self.vector_kb = VectorKnowledgeBase("competitor_intel")
        self.kg = Neo4jClient(...)
        self.llm = ChatOpenAI(model="gpt-4")
        
        # 初始化所有 Skills
        self.skills = {
            "market_mapper":     MarketMapperSkill(self.llm),
            "graph_linker":      GraphLinkerSkill(self.kg),
            "gap_analyzer":      GapAnalyzerSkill(self.vector_kb, self.kg, self.llm, self.embedder),
            "content_generator": ContentGeneratorSkill(self.llm),
            "critic":            CriticSkill(self.kg, self.llm),
        }
    
    def run(self, category: str, target_asin: str):
        state = {
            "category": category,
            "target_asin": target_asin,
            "total_steps": 4,
            "results": {},
            "evidence_chain": []
        }
        
        workflow_steps = [
            ("market_mapper",     "扫描市场"),
            ("graph_linker",      "图谱关联"),
            ("gap_analyzer",      "差距分析"),
            ("content_generator", "方案生成"),
        ]
        
        for step_idx, (skill_name, description) in enumerate(workflow_steps, 1):
            print(f"\n{'='*60}")
            print(f"📍 Step {step_idx}/{state['total_steps']}: {description}")
            print(f"{'='*60}")
            
            skill = self.skills[skill_name]
            
            # ✅ 注入上下文 + 流程状态
            skill_input = {
                **state,
                "current_step": step_idx,
                "previous_output": state["results"].get(workflow_steps[step_idx-2][0]) if step_idx > 1 else None
            }
            
            # 执行 + 闭环验证（最多重试3次）
            for attempt in range(3):
                output = skill.execute(skill_input)
                
                # ✅ Critic 验证
                critique = self.skills["critic"].execute({
                    "worker_output": output,
                    "step_name": skill_name,
                    "attempt": attempt + 1
                })
                
                if critique["status"] == "approved":
                    print(f"  ✅ 通过验证 (第{attempt+1}次尝试)")
                    state["results"][skill_name] = output
                    state["evidence_chain"].append({
                        "step": step_idx,
                        "skill": skill_name,
                        "confidence": output.get("confidence_score", "N/A")
                    })
                    break
                else:
                    print(f"  ❌ 验证失败: {critique['issues']}")
                    skill_input["last_failure_reason"] = critique["issues"]
                    skill_input["retry_count"] = attempt + 1
            else:
                print(f"  ⚠️ 达到最大重试次数，使用最后一次输出")
                state["results"][skill_name] = output
        
        # 生成最终报告
        return self._compile_report(state)
    
    def _compile_report(self, state):
        return {
            "status": "workflow_complete",
            "results": state["results"],
            "evidence_chain": state["evidence_chain"],
            "total_confidence": np.mean([
                e["confidence"] for e in state["evidence_chain"] 
                if isinstance(e["confidence"], (int, float))
            ])
        }


# ============================================================
# 运行
# ============================================================
workflow = CompetitorWeaknessWorkflow()
report = workflow.run(
    category="wireless_charger",
    target_asin="B0XXXXXXX"
)

print(json.dumps(report, ensure_ascii=False, indent=2))
```

---

## 七、总结速查表

```
┌──────────────────────────────────────────────────────────────────┐
│                    高级 Skill 写作检查清单                        │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  知识库 + 向量库 + RAG                                           │
│  ─────────────────                                               │
│  □ 文档按语义边界切分（不要硬切）                                  │
│  □ 切分时保留重叠窗口（overlap 50-100 字符）                      │
│  □ 每个chunk携带完整metadata（来源、时间、类目）                   │
│  □ MiniLM 编码时开启 normalize_embeddings=True                   │
│  □ 检索后做重排序（Re-ranking）                                   │
│  □ 向量检索 + 知识图谱 双路并行                                   │
│                                                                  │
│  提示词四法则                                                     │
│  ────────────                                                    │
│  □ 批注：每个要求标注"为什么"                                     │
│  □ 背景：三层（业务→状态→期望）                                   │
│  □ 上下文：注入前序输出 + 图谱实体 + 检索chunks                   │
│  □ 单一任务：一个Prompt只做一件事                                  │
│                                                                  │
│  Skill 工程规范                                                   │
│  ──────────────                                                  │
│  □ JSON Schema 定义输入输出合同                                   │
│  □ 显式错误处理（status + reason + suggestion）                   │
│  □ 元数据透传（来源节点、证据链、置信度）                          │
│  □ 状态意识（Step N/M + retry_count）                             │
│  □ Critic 闭环验证 + 自动重试                                     │
│                                                                  │
│  技术栈                                                          │
│  ──────                                                          │
│  □ 嵌入: all-MiniLM-L6-v2 (384维, 本地运行)                      │
│  □ 向量库: ChromaDB (轻量) / Pinecone (生产)                     │
│  □ 知识图谱: Neo4j / Amazon Neptune                              │
│  □ 编排: LangGraph (状态循环) / AWS Step Functions                │
│  □ LLM: GPT-4 / Claude (推理核心)                                │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

> 💡 **核心记忆点**：高级 Skill = **MiniLM感知** + **知识图谱推理** + **批注式提示词** + **闭环验证**。它们不是孤立的函数，而是能相互校验、自动重试、带着证据链输出的**智能协作单元**。

# 🚀 如何写好高级 Skills — 完整指南

根据你提供的文档，我将系统性地拆解**如何编写高级 Skills**，并配上实际代码示例和架构图。

---

## 一、核心理念：从"函数"到"智能单元"

> **高级 Skill ≠ 一个函数调用**，而是一个具备 **感知、决策、执行** 能力的独立模块。

```
传统 Skill:    输入 → 处理 → 输出（线性）
高级 Skill:    输入 + 上下文 + 知识图谱 → 推理 → 输出 + 元数据 + 置信度（网络化）
```

---

## 二、Skill 的结构化定义（JSON Schema）

每个 Skill 必须有**严格的输入输出合同**，确保工作流引擎能准确调度：

```json
{
  "skill_name": "CompetitorPriceAnalyzer",
  "version": "1.2.0",
  "description": "分析竞品价格异动并结合知识图谱推理原因",
  "input_schema": {
    "type": "object",
    "required": ["asin", "current_price", "history_context"],
    "properties": {
      "asin":            { "type": "string", "description": "目标ASIN" },
      "current_price":   { "type": "number", "description": "当前价格" },
      "history_context": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "date":  { "type": "string" },
            "price": { "type": "number" },
            "bsr":   { "type": "integer" }
          }
        }
      },
      "kg_context": { "type": "object", "description": "知识图谱注入的上下文（可选）" }
    }
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "status":           { "enum": ["success", "error", "need_more_data"] },
      "analysis":         { "type": "string" },
      "confidence_score": { "type": "number", "minimum": 0, "maximum": 1 },
      "affected_nodes":   { "type": "array", "items": { "type": "string" } },
      "evidence_chain":   { "type": "array", "description": "推理证据链" },
      "suggestion":       { "type": "string" }
    }
  }
}
```

### ✅ 三大设计原则

| 原则 | 说明 | 反面教材 |
|------|------|----------|
| **单一职责** | 一个 Skill 只解决一个具体问题 | ❌ 一个 Skill 又提取实体又查图谱又打分 |
| **上下文注入** | 允许接收外部 Context，不仅仅是原始输入 | ❌ Skill 内部硬编码上下文 |
| **显式错误处理** | 返回结构化错误+建议 | ❌ 出错只返回 `null` |

---

## 三、5 种高级 Skill 模式（附代码）

### 模式 1️⃣：实体提取 Skill（原子型）

```python
class EntityExtractorSkill:
    """从非结构化文本中提取结构化实体"""
    
    def __init__(self, llm, kg_client):
        self.llm = llm
        self.kg = kg_client
    
    def execute(self, input_data: dict) -> dict:
        text = input_data["raw_text"]
        
        prompt = f"""你是一个精准的实体提取器。
从以下文本中提取：公司名、金额、日期、风险标签。

文本：{text}

输出格式（严格JSON）：
{{"entities": [{{"type": "COMPANY", "value": "...", "confidence": 0.95}}]}}
"""
        result = self.llm.invoke(prompt)
        
        # ✅ 关键：与知识图谱交叉验证
        validated = []
        for entity in result["entities"]:
            kg_match = self.kg.query(f"MATCH (n) WHERE n.name =~ '{entity['value']}' RETURN n")
            validated.append({
                **entity,
                "kg_verified": bool(kg_match),
                "kg_node_id": kg_match[0]["id"] if kg_match else None
            })
        
        return {
            "status": "success",
            "entities": validated,
            "source_skill": "EntityExtractor_v1.2",  # ✅ 元数据透传
            "step": f"{input_data.get('current_step', '?')}/{input_data.get('total_steps', '?')}"
        }
```

### 模式 2️⃣：知识图谱探索 Skill（推理型）

```python
class GraphExplorerSkill:
    """在知识图谱中进行多跳推理"""
    
    def execute(self, input_data: dict) -> dict:
        entity_id = input_data["entity_id"]
        query_type = input_data["query_type"]  # "risk_check" | "competitor_link" | "supply_chain"
        
        queries = {
            "risk_check": f"""
                MATCH (c:Company {{id: '{entity_id}'}})-[:SANCTIONED_BY|OWNED_BY*1..3]-(risk:RiskEntity)
                RETURN c, risk, relationships(c) as path
            """,
            "competitor_link": f"""
                MATCH (a:ASIN {{id: '{entity_id}'}})-[:CompetesWith]->(b:ASIN)
                MATCH (b)-[:HasIssue]->(p:PainPoint)
                MATCH (b)-[:Dominates]->(k:Keyword)
                RETURN b.name, collect(p.description) as pain_points, 
                       collect(k.term) as dominated_keywords
            """,
            "supply_chain": f"""
                MATCH (a:ASIN {{id: '{entity_id}'}})-[:DerivedFrom]->(s:Supplier)
                MATCH (s)<-[:DerivedFrom]-(other:ASIN)
                WHERE other.id <> '{entity_id}'
                RETURN s.name as shared_supplier, collect(other.name) as related_products
            """
        }
        
        results = self.kg.query(queries[query_type])
        
        return {
            "status": "success",
            "graph_paths": results,
            "reasoning": self._generate_reasoning(results, query_type),  # LLM 解读图谱路径
            "affected_nodes": [r["id"] for r in results],
            "confidence_score": self._calculate_confidence(results)
        }
```

### 模式 3️⃣：闭环验证 Skill（Critic 型）

```python
class CriticSkill:
    """验证其他 Skill 的输出质量，失败则打回重做"""
    
    def execute(self, worker_output: dict, rules_from_kg: list) -> dict:
        issues = []
        
        # ✅ 规则 1：输出完整性检查
        required_fields = ["analysis", "confidence_score", "evidence_chain"]
        for field in required_fields:
            if field not in worker_output:
                issues.append(f"缺少必要字段: {field}")
        
        # ✅ 规则 2：知识图谱事实校验
        for claim in worker_output.get("evidence_chain", []):
            kg_verified = self.kg.verify_fact(claim)
            if not kg_verified:
                issues.append(f"事实校验失败: {claim}")
        
        # ✅ 规则 3：置信度阈值
        if worker_output.get("confidence_score", 0) < 0.7:
            issues.append(f"置信度过低: {worker_output['confidence_score']}")
        
        if issues:
            return {
                "status": "rejected",
                "issues": issues,
                "action": "retry",             # 告诉工作流引擎：打回重做
                "max_retries": 3,
                "suggestion": "请补充更多上下文数据后重试"
            }
        
        return {"status": "approved", "final_output": worker_output}
```

### 模式 4️⃣：规划器 Skill（Planner 型）

```python
class PlannerSkill:
    """分析复杂任务，拆解为子任务序列并路由"""
    
    def execute(self, task: dict) -> dict:
        prompt = f"""你是一个任务规划专家。
        
任务描述：{task['description']}
可用 Skills：{json.dumps(task['available_skills'])}
知识图谱状态：{json.dumps(task['kg_state'])}

请拆解为最优子任务序列。考虑：
1. 哪些 Skill 可以并行执行？
2. 哪些 Skill 有依赖关系？
3. 是否需要知识图谱预热？

输出格式：
{{
  "plan": [
    {{"step": 1, "skill": "...", "parallel_group": "A", "input_mapping": {{...}}}},
    {{"step": 2, "skill": "...", "depends_on": [1], "input_mapping": {{...}}}}
  ],
  "estimated_steps": 4,
  "fallback_plan": [...]
}}
"""
        return self.llm.invoke(prompt)
```

### 模式 5️⃣：差距分析 Skill（Gap Analyzer，亚马逊场景）

```python
class GapAnalyzerSkill:
    """挖掘竞品防守薄弱点"""
    
    def execute(self, input_data: dict) -> dict:
        # 从知识图谱获取消费者需求 vs 竞品功能
        consumer_needs = self.kg.query("""
            MATCH (n:ConsumerNeed)<-[:MENTIONS]-(r:Review)
            WHERE r.category = $category
            WITH n, count(r) as mention_count
            ORDER BY mention_count DESC
            RETURN n.name, mention_count
        """, category=input_data["category"])
        
        top10_features = self.kg.query("""
            MATCH (a:ASIN)-[:HasFeature]->(f:Feature)
            WHERE a.bsr_rank <= 10 AND a.category = $category
            RETURN f.name, count(a) as coverage
        """, category=input_data["category"])
        
        # 🎯 核心逻辑：高需求 + 低覆盖 = 机会点
        feature_set = {f["name"] for f in top10_features}
        gaps = []
        for need in consumer_needs:
            if need["name"] not in feature_set and need["mention_count"] > 50:
                gaps.append({
                    "need": need["name"],
                    "demand_score": need["mention_count"],
                    "competitor_coverage": 0,
                    "opportunity_level": "HIGH"
                })
        
        return {
            "status": "success",
            "gaps": sorted(gaps, key=lambda x: x["demand_score"], reverse=True),
            "recommendation": self._generate_listing_advice(gaps)
        }
```

---

## 四、多 Skills 组合的工作流架构

### 🔄 闭环工作流（LangGraph 风格）

```
┌─────────────────────────────────────────────────────────────┐
│                    高级自动化工作流                           │
│                                                             │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐             │
│   │ Planner  │───▶│ Router   │───▶│ Worker   │             │
│   │ Skill A  │    │ Skill B  │    │ Skill C  │             │
│   └──────────┘    └──────────┘    └────┬─────┘             │
│        ▲                               │                    │
│        │          ┌──────────┐         │                    │
│        │          │  Critic  │◀────────┘                    │
│        │          │ Skill D  │                              │
│        │          └────┬─────┘                              │
│        │               │                                    │
│        │     ┌─────────┴─────────┐                         │
│        │     │                   │                          │
│        │  [REJECTED]          [APPROVED]                    │
│        │     │                   │                          │
│        └─────┘           ┌───────┴──────┐                  │
│                          │ Decision     │                   │
│                          │ Maker Skill  │──▶ 📄 最终报告    │
│                          └──────────────┘                   │
│                                                             │
│   ══════════════════════════════════════════                │
│   ║         知识图谱 (Knowledge Graph)     ║  ◀── 全程参与  │
│   ══════════════════════════════════════════                │
└─────────────────────────────────────────────────────────────┘
```

### 代码实现（LangGraph）

```python
from langgraph.graph import StateGraph, END

# 定义工作流状态
class WorkflowState(TypedDict):
    task: str
    plan: list
    current_step: int
    total_steps: int
    results: dict
    retry_count: int
    kg_context: dict

# 构建工作流图
workflow = StateGraph(WorkflowState)

workflow.add_node("planner",    planner_skill.execute)
workflow.add_node("router",     router_skill.execute)
workflow.add_node("worker",     worker_skill.execute)
workflow.add_node("critic",     critic_skill.execute)
workflow.add_node("decision",   decision_skill.execute)

# 定义边和条件
workflow.add_edge("planner", "router")
workflow.add_edge("router", "worker")
workflow.add_edge("worker", "critic")

workflow.add_conditional_edges(
    "critic",
    lambda state: "worker" if state["retry_count"] < 3 and state.get("rejected") else "decision",
    {"worker": "worker", "decision": "decision"}
)

workflow.add_edge("decision", END)
workflow.set_entry_point("planner")

app = workflow.compile()
```

---

## 五、Skill Prompt 的编写秘诀

### ❌ 低质量 Prompt
```
"分析这个竞品的价格变化"
```

### ✅ 高质量 Prompt（带思维链路 + 数据合同）
```python
SKILL_PROMPT = """
你是一个亚马逊资深运营 Agent。

## 身份与背景
你负责竞品价格异动分析，已在该类目积累 5 年经验。

## 输入数据合同
- Current_State: {current_state}       # 当前价格/BSR/库存
- History_Context: {history_context}   # 过去30天数据
- KG_Context: {kg_context}            # 知识图谱提供的关联信息

## 执行逻辑（Chain of Thought）
1. 首先，对比价格与 BSR 的相关性（皮尔逊系数 > 0.7 则强相关）
2. 其次，检查 KG_Context 中该竞品是否正在进行 Seasonality_Promotion
3. 如果排除季节性因素，检查是否有站外引流信号（TikTok/红人合作）
4. 最后，结合供应链图谱判断是否为"清库存→上新款"策略

## 输出要求（严格JSON）
{{
    "status": "success",
    "analysis": "结构化分析文本",
    "root_cause": "seasonal | clearance | external_traffic | competitive_response",
    "confidence_score": 0.85,
    "evidence_chain": ["依据1", "依据2", "依据3"],
    "affected_kg_nodes": ["node_id_1", "node_id_2"],
    "recommended_action": "具体行动建议"
}}

## 约束
- 置信度 < 0.6 时必须标记 status 为 "need_more_data"
- 不要猜测，没有数据支撑的结论不要给出
"""
```

---

## 六、知识图谱架构（亚马逊竞品场景）

```
                    ┌──────────┐
            ┌──────▶│ Keyword  │◀── Dominates ──┐
            │       └──────────┘                 │
      RanksFor                                   │
            │       ┌──────────┐          ┌──────┴───┐
            └───────│  ASIN A  │──Competes│  ASIN B  │
                    └────┬─────┘  With    └────┬─────┘
                         │                     │
                   HasIssue               DerivedFrom
                         │                     │
                    ┌────┴─────┐          ┌────┴──────┐
                    │PainPoint │          │ Supplier  │
                    │"电池寿命短"│          │ "工厂X"   │
                    └──────────┘          └───────────┘
```

**推理示例：**
> 🧠 Skill A 发现竞品 B 降价 → 知识图谱告诉 Skill B：「竞品 B 与你的产品共享同一个供应商（工厂X），且它正在清空 '旧款' 节点下的库存 → **推测即将发布升级款**」

---

## 七、落地技术栈推荐

| 层级 | 推荐方案 | 说明 |
|------|---------|------|
| **图数据库** | Neo4j / Amazon Neptune | 存储知识图谱 |
| **向量库** | ChromaDB / Pinecone + MiniLM | RAG 语义检索 |
| **工作流编排** | LangGraph / AWS Step Functions | 支持状态循环 |
| **Skill 定义** | JSON Schema + OpenAPI | 让 LLM 像调函数一样调度 |
| **LLM** | GPT-4 / Claude | 推理核心 |
| **嵌入模型** | all-MiniLM-L6-v2 | 轻量高效的语义向量化 |

---

## 八、总结：高级 Skill 的 7 条黄金法则

```
1. 📦 单一职责 ——— 一个 Skill 只做一件事
2. 📋 严格合同 ——— JSON Schema 定义输入输出
3. 🧠 上下文感知 ——— 注入外部 Context + KG 数据
4. 🔗 元数据透传 ——— 输出包含来源、证据链、置信度
5. ❌ 显式错误 ——— 返回结构化错误 + 建议 + 重试策略
6. 🔄 闭环验证 ——— Critic Skill 校验 + 打回机制
7. 🏗️ 状态意识 ——— 知道自己在流程的第几步 (Step N/M)
```

> **记住：优秀的 Skill 应该像乐高积木一样——标准接口、独立功能、自由拼装。** 🧱我需要更深入研究下skills的高级用法
知识库  +向量库  RAG 利用微软 minilm
提示词，需要批注，交代背景，做 上下文，  单一任务

 怎么写skills，写出高级Skills