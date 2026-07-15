from typing import TypedDict, Annotated, Sequence, Any, List, AsyncGenerator
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
import logging

logger = logging.getLogger(__name__)

# ==========================================
# State Definition
# ==========================================
class AgentState(TypedDict):
    """وضعیت مرکزی ایجنت."""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    context: dict

# ==========================================
# Base Agent Builder
# ==========================================
class ModularAgentBuilder:
    """سازنده ماژولار ایجنت‌های LangGraph."""
    
    def __init__(self, llm: Any, tools: List[Any], system_prompt: str = ""):
        self.llm = llm.bind_tools(tools) if tools else llm
        self.tools = {t.name: t for t in tools}
        self.system_prompt = system_prompt
        self.graph = None

    def _call_model(self, state: AgentState) -> AgentState:
        """نود اصلی: فراخوانی مدل زبانی."""
        logger.info("🧠 [Agent] Processing...")
        messages = state["messages"]
        
        if self.system_prompt and len(messages) == 1:
            from langchain_core.messages import SystemMessage
            messages = [SystemMessage(content=self.system_prompt)] + list(messages)
        
        response = self.llm.invoke(messages)
        return {"messages": [response], "context": state.get("context", {})}

    async def _call_tool(self, state: AgentState) -> AgentState:
        """نود ابزار: اجرای ابزار درخواست شده."""
        logger.info("🛠️ [Agent] Executing tool...")
        messages = state["messages"]
        last_message = messages[-1]
        
        tool_calls = last_message.tool_calls
        tool_results = []
        
        for tc in tool_calls:
            tool_func = self.tools.get(tc["name"])
            if not tool_func:
                tool_results.append(
                    ToolMessage(content=f"❌ ابزار '{tc['name']}' یافت نشد.", tool_call_id=tc["id"])
                )
                continue
            
            try:
                if hasattr(tool_func, 'ainvoke'):
                    result = await tool_func.ainvoke(tc["args"])
                else:
                    result = tool_func.invoke(tc["args"])
                
                tool_results.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))
            except Exception as e:
                logger.error(f"Error executing tool {tc['name']}: {e}")
                tool_results.append(
                    ToolMessage(content=f"❌ خطا در اجرای ابزار: {str(e)}", tool_call_id=tc["id"])
                )
        
        return {"messages": tool_results, "context": state.get("context", {})}

    def _should_continue(self, state: AgentState) -> str:
        """تصمیم‌گیری برای ادامه یا پایان."""
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return END

    def build(self, recursion_limit: int = 25) -> StateGraph:
        """ساخت و کامپایل گراف ایجنت."""
        workflow = StateGraph(AgentState)

        workflow.add_node("agent", self._call_model)
        if self.tools:
            workflow.add_node("tools", self._call_tool)

        workflow.add_edge(START, "agent")
        
        if self.tools:
            workflow.add_conditional_edges(
                "agent",
                self._should_continue,
                {"tools": "tools", END: END}
            )
            workflow.add_edge("tools", "agent")
        else:
            workflow.add_edge("agent", END)

        self.graph = workflow.compile()
        return self.graph

    async def run(self, user_input: str, context: dict = None) -> str:
        """اجرای ایجنت با یک پیام (non-streaming)."""
        if not self.graph:
            self.build()
        
        initial_state = {
            "messages": [HumanMessage(content=user_input)],
            "context": context or {}
        }
        
        final_state = await self.graph.ainvoke(
            initial_state,
            config={"recursion_limit": 25}
        )
        
        for msg in reversed(final_state["messages"]):
            if isinstance(msg, AIMessage) and msg.content:
                return msg.content
        
        return "متأسفانه پاسخی تولید نشد."

    async def run_stream(self, user_input: str, context: dict = None) -> AsyncGenerator[str, None]:
        """
        اجرای ایجنت با streaming (chunk by chunk).
        
        Yields:
            str: هر chunk از پاسخ
        """
        if not self.graph:
            self.build()
        
        initial_state = {
            "messages": [HumanMessage(content=user_input)],
            "context": context or {}
        }
        
        logger.info("🌊 Starting streaming execution...")
        
        try:
            # اجرای گراف به صورت streaming
            async for event in self.graph.astream_events(
                initial_state,
                config={"recursion_limit": 25},
                version="v2"
            ):
                kind = event["event"]
                
                # پردازش رویدادهای LLM streaming
                if kind == "on_chat_model_stream":
                    content = event["data"]["chunk"].content
                    if content:
                        yield content
                
                # پردازش tool calls
                elif kind == "on_tool_start":
                    tool_name = event["name"]
                    yield f"\n\n🛠️ **اجرای ابزار: {tool_name}**\n\n"
                
                elif kind == "on_tool_end":
                    tool_output = event["data"].get("output", "")
                    if tool_output:
                        yield f"\n\n📊 **نتیجه ابزار:**\n{str(tool_output)[:500]}...\n\n"
        
        except Exception as e:
            logger.error(f"❌ Streaming error: {e}")
            # ارسال خطا به صورت chunk
            yield f"❌ خطا در پردازش: {str(e)}"

# ============================================================
# Compatibility Aliases (Added by Phase 2 Fix)
# ============================================================

BaseAgent = ModularAgentBuilder
