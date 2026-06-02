"""
LangGraph Workflow: اتصال Planner، Executor، Reviewer با RAG و Policy Engine
"""
import sys
from pathlib import Path

# افزودن ریشه پروژه به sys.path برای حل مشکل import
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from typing import List, Dict, Any, TypedDict, Literal
from dataclasses import dataclass
import structlog
import asyncio

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

# Import اجزای سیستم
from agents.core.planner_agent import PlannerAgent, Task
from agents.memory.local_vector_store import LocalVectorMemory
from agents.policies.policy_engine import PolicyEngine, PolicyAction

logger = structlog.get_logger()


# تعریف State برای LangGraph
class AgentState(TypedDict):
    messages: List[BaseMessage]
    user_request: str
    tasks: List[Task]
    current_task_index: int
    task_results: Dict[str, Any]
    context: List[Dict[str, Any]]
    final_response: str
    errors: List[str]
    review_summary: Dict[str, Any]


class EconojinWorkflow:
    """Workflow اصلی با LangGraph"""
    
    def __init__(self):
        self.planner = PlannerAgent()
        self.memory = LocalVectorMemory()
        self.policy_engine = PolicyEngine()
        self.logger = logger.bind(component="workflow")
        
        # ساخت گراف
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """ساخت StateGraph با nodes و edges"""
        
        workflow = StateGraph(AgentState)
        
        # افزودن nodes
        workflow.add_node("planner", self._planner_node)
        workflow.add_node("retrieve_context", self._retrieve_context_node)
        workflow.add_node("executor", self._executor_node)
        workflow.add_node("reviewer", self._reviewer_node)
        workflow.add_node("finalizer", self._finalizer_node)
        
        # تعریف entry point
        workflow.set_entry_point("planner")
        
        # تعریف edges
        workflow.add_edge("planner", "retrieve_context")
        workflow.add_edge("retrieve_context", "executor")
        workflow.add_conditional_edges(
            "executor",
            self._should_continue_execution,
            {
                "continue": "executor",
                "review": "reviewer"
            }
        )
        workflow.add_edge("reviewer", "finalizer")
        workflow.add_edge("finalizer", END)
        
        return workflow.compile()
    
    async def _planner_node(self, state: AgentState) -> AgentState:
        """Node 1: برنامه‌ریزی و تقسیم وظایف"""
        self.logger.info("planner_start", request=state["user_request"][:100])
        
        tasks = await self.planner.plan(state["user_request"])
        
        self.logger.info("planner_complete", task_count=len(tasks))
        
        return {
            **state,
            "tasks": tasks,
            "current_task_index": 0,
            "task_results": {},
            "errors": []
        }
    
    async def _retrieve_context_node(self, state: AgentState) -> AgentState:
        """Node 2: بازیابی context مرتبط با RAG"""
        self.logger.info("retrieve_context_start")
        
        all_context = []
        for task in state["tasks"]:
            results = self.memory.search(task.description, limit=3)
            all_context.extend(results)
        
        self.logger.info("retrieve_context_complete", context_count=len(all_context))
        
        return {
            **state,
            "context": all_context
        }
    
    async def _executor_node(self, state: AgentState) -> AgentState:
        """Node 3: اجرای واقعی task با ابزارهای Domain-Specific"""
        from agents.core.executor_agent import ExecutorAgent
        
        current_idx = state["current_task_index"]
        task = state["tasks"][current_idx]
        
        self.logger.info("executor_start", task_id=task.id, task_desc=task.description[:50])
        
        # استفاده از Executor واقعی
        executor = ExecutorAgent()
        result = await executor.execute_task(task, state["user_request"], state.get("context", []))
        
        # ذخیره نتیجه
        task_results = state["task_results"].copy()
        
        if result.success:
            task_result = {
                "task_id": task.id,
                "status": "completed",
                "output": result.data.get("summary", "Executed successfully"),
                "tools_used": result.data.get("tools_used", []),
                "location": result.data.get("location", {}),
                "detailed_data": result.data.get("results", {})
            }
            self.logger.info("executor_complete", task_id=task.id, tools=task_result["tools_used"])
        else:
            task_result = {
                "task_id": task.id,
                "status": "failed",
                "output": f"خطا: {result.error}",
                "error": result.error
            }
            self.logger.error("executor_failed", task_id=task.id, error=result.error)
        
        task_results[task.id] = task_result
        
        return {
            **state,
            "current_task_index": current_idx + 1,
            "task_results": task_results
        }
    
    def _should_continue_execution(self, state: AgentState) -> Literal["continue", "review"]:
        """تصمیم‌گیری برای ادامه اجرا یا رفتن به review"""
        current_idx = state["current_task_index"]
        total_tasks = len(state["tasks"])
        
        if current_idx < total_tasks:
            return "continue"
        else:
            return "review"
    
    async def _reviewer_node(self, state: AgentState) -> AgentState:
        """Node 4: بررسی کیفیت نتایج"""
        self.logger.info("reviewer_start")
        
        task_results = state["task_results"]
        errors = state["errors"]
        
        success_count = sum(1 for r in task_results.values() if r.get("status") == "completed")
        total_count = len(state["tasks"])
        
        review_summary = {
            "total_tasks": total_count,
            "successful": success_count,
            "failed": len(errors),
            "quality_score": success_count / total_count if total_count > 0 else 0
        }
        
        self.logger.info("reviewer_complete", **review_summary)
        
        return {
            **state,
            "review_summary": review_summary
        }
    
    async def _finalizer_node(self, state: AgentState) -> AgentState:
        """Node 5: تولید پاسخ نهایی"""
        self.logger.info("finalizer_start")
        
        task_results = state["task_results"]
        review_summary = state.get("review_summary", {})
        errors = state["errors"]
        
        response_parts = []
        response_parts.append(f"✅ درخواست شما با موفقیت پردازش شد!\n\n")
        response_parts.append(f"📊 خلاصه اجرا:\n")
        response_parts.append(f"  - تعداد وظایف: {review_summary.get('total_tasks', 0)}\n")
        response_parts.append(f"  - موفق: {review_summary.get('successful', 0)}\n")
        response_parts.append(f"  - ناموفق: {review_summary.get('failed', 0)}\n")
        response_parts.append(f"  - امتیاز کیفیت: {review_summary.get('quality_score', 0):.2f}\n\n")
        
        if task_results:
            response_parts.append("📋 جزئیات وظایف:\n")
            for task_id, result in task_results.items():
                output = result.get('output', 'N/A')
                response_parts.append(f"\n  🔹 [{task_id}]:\n")
                # هر خط از output را با indent نمایش بده
                for line in output.split('\n'):
                    if line.strip():
                        response_parts.append(f"      {line}\n")
        
        if errors:
            response_parts.append(f"\n⚠️ خطاها:\n")
            for error in errors:
                response_parts.append(f"  - {error}\n")
        
        final_response = "".join(response_parts)
        
        self.logger.info("finalizer_complete", response_length=len(final_response))
        
        return {
            **state,
            "final_response": final_response
        }
    
    async def run(self, user_request: str) -> str:
        """اجرای کامل workflow"""
        self.logger.info("workflow_start", request=user_request[:100])
        
        initial_state: AgentState = {
            "messages": [HumanMessage(content=user_request)],
            "user_request": user_request,
            "tasks": [],
            "current_task_index": 0,
            "task_results": {},
            "context": [],
            "final_response": "",
            "errors": [],
            "review_summary": {}
        }
        
        final_state = await self.graph.ainvoke(initial_state)
        
        self.logger.info("workflow_complete")
        
        return final_state["final_response"]


async def main():
    """تست Workflow"""
    print("\n" + "="*60)
    print("🚀 Econojin Workflow Test (با Executor واقعی)")
    print("="*60 + "\n")
    
    workflow = EconojinWorkflow()
    
    user_request = "تحلیل داده‌های ماهواره‌ای NDVI برای منطقه خراسان در ۶ ماه گذشته"
    
    print(f"📝 User Request: {user_request}\n")
    
    response = await workflow.run(user_request)
    
    print("\n" + "="*60)
    print("📤 Final Response:")
    print("="*60)
    print(response)
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())