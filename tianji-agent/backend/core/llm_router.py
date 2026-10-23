"""
天机智能体 - LLM 多模型路由引擎
支持 GPT-4o/Claude/文心一言/通义千问/DeepSeek
"""

from typing import Optional, List, Dict, Any, AsyncGenerator
from enum import Enum
import openai
from openai import AsyncOpenAI
import httpx

from core.config import settings


class ModelType(str, Enum):
    """支持的模型类型"""
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    CLAUDE_3_5_SONNET = "claude-3-5-sonnet-20241022"
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"
    DEEPSEEK_CHAT = "deepseek-chat"
    DEEPSEEK_CODER = "deepseek-coder"
    QWEN_MAX = "qwen-max"
    QWEN_PLUS = "qwen-plus"
    WENXIN_4 = "ernie-4.0"


class TaskType(str, Enum):
    """任务类型 - 用于模型路由决策"""
    CREATIVE_WRITING = "creative_writing"  # 长文案创作
    DATA_ANALYSIS = "data_analysis"        # 数据分析
    CHINESE_CONTENT = "chinese_content"    # 中文内容
    CODE_GENERATION = "code_generation"    # 代码/脚本
    QUICK_CHAT = "quick_chat"              # 快速问答
    MULTIMODAL = "multimodal"              # 多模态


# 模型路由映射：根据任务类型推荐最优模型
MODEL_ROUTING = {
    TaskType.CREATIVE_WRITING: (ModelType.CLAUDE_3_5_SONNET, 0.7),
    TaskType.DATA_ANALYSIS: (ModelType.GPT_4O, 0.2),
    TaskType.CHINESE_CONTENT: (ModelType.QWEN_MAX, 0.6),
    TaskType.CODE_GENERATION: (ModelType.DEEPSEEK_CODER, 0.1),
    TaskType.QUICK_CHAT: (ModelType.GPT_4O_MINI, 0.5),
    TaskType.MULTIMODAL: (ModelType.GPT_4O, 0.4),
}


class LLMRouter:
    """LLM 模型路由器"""
    
    def __init__(self):
        self.clients: Dict[str, Any] = {}
        self._init_clients()
    
    def _init_clients(self):
        """初始化各模型客户端"""
        # OpenAI
        if settings.OPENAI_API_KEY=[已移除]openai"] = AsyncOpenAI(
                api_key=[已移除]
                base_url=settings.OPENAI_BASE_URL
            )
        
        # Claude (通过OpenAI兼容接口或原生API)
        if settings.ANTHROPIC_API_KEY=[已移除]claude"] = AsyncOpenAI(
                api_key=[已移除]
                base_url="https://api.anthropic.com/v1"
            )
        
        # DeepSeek
        if settings.DEEPSEEK_API_KEY=[已移除]deepseek"] = AsyncOpenAI(
                api_key=[已移除]
                base_url="https://api.deepseek.com/v1"
            )
        
        # 通义千问
        if settings.QWEN_API_KEY=[已移除]qwen"] = AsyncOpenAI(
                api_key=[已移除]
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
            )
    
    def route(self, task_type: TaskType, user_preference: Optional[ModelType] = None) -> tuple:
        """
        根据任务类型路由到最优模型
        
        Returns:
            (model_name, temperature, client)
        """
        if user_preference:
            model_name = user_preference
        else:
            model_name, temperature = MODEL_ROUTING.get(task_type, (ModelType.GPT_4O, 0.5))
        
        # 根据模型名称选择客户端
        client = self._get_client_for_model(model_name)
        _, temperature = MODEL_ROUTING.get(task_type, (model_name, 0.5))
        
        return model_name, temperature, client
    
    def _get_client_for_model(self, model: ModelType) -> Any:
        """获取模型对应的客户端"""
        if "gpt" in model.value:
            return self.clients.get("openai")
        elif "claude" in model.value:
            return self.clients.get("claude")
        elif "deepseek" in model.value:
            return self.clients.get("deepseek")
        elif "qwen" in model.value:
            return self.clients.get("qwen")
        return self.clients.get("openai")  # 默认
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[ModelType] = None,
        task_type: TaskType = TaskType.QUICK_CHAT,
        temperature: Optional[float] = None,
        stream: bool = False,
        tools: Optional[List[Dict]] = None
    ) -> Any:
        """
        统一的聊天完成接口
        
        Args:
            messages: 消息列表
            model: 指定模型（可选）
            task_type: 任务类型（用于自动路由）
            temperature: 温度参数
            stream: 是否流式输出
            tools: 工具/函数调用定义
        """
        model_name, default_temp, client = self.route(task_type, model)
        temp = temperature if temperature is not None else default_temp
        
        if not client:
            raise ValueError(f"模型 {model_name} 未配置API密钥")
        
        params = {
            "model": model_name.value,
            "messages": messages,
            "temperature": temp,
            "stream": stream
        }
        
        if tools:
            params["tools"] = tools
            params["tool_choice"] = "auto"
        
        try:
            response = await client.chat.completions.create(**params)
            return response
        except Exception as e:
            print(f"LLM调用失败: {e}")
            raise
    
    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        model: Optional[ModelType] = None,
        task_type: TaskType = TaskType.QUICK_CHAT
    ) -> AsyncGenerator[str, None]:
        """流式聊天响应"""
        model_name, temperature, client = self.route(task_type, model)
        
        if not client:
            raise ValueError(f"模型 {model_name} 未配置API密钥")
        
        try:
            stream = await client.chat.completions.create(
                model=model_name.value,
                messages=messages,
                temperature=temperature,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            print(f"流式调用失败: {e}")
            raise
    
    async def create_embedding(self, text: str, model: str = "text-embedding-3-small") -> List[float]:
        """创建文本向量嵌入"""
        client = self.clients.get("openai")
        if not client:
            raise ValueError("OpenAI API密钥未配置")
        
        try:
            response = await client.embeddings.create(
                model=model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Embedding创建失败: {e}")
            raise


# 全局路由器实例
llm_router = LLMRouter()
