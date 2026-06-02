"""
Workflow با قابلیت streaming رویدادها از طریق callback
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from typing import List, Dict, Any, TypedDict, Literal, Callable, Optional
import structlog
import asyncio
import time

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, BaseMessage

from agents.core.planner_agent import PlannerAgent, Task
from agents.memory.local_vector_store import LocalVectorMemory
from agents.policies.policy_engine import PolicyEngine, PolicyAction
from agents.core.executor_agent import ExecutorAgent
from api.schemas import StreamEvent, NodeStatus

logger = structlog.get_logger()


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
    session_id: str


class StreamingEconojinWorkflow:
    """Workflow با قابلیت streaming رویدادها"""

    def __init__(self, event_callback: Optional[Callable] = None):
        self.planner = PlannerAgent()
        self.memory = LocalVectorMemory()
        self.policy_engine = PolicyEngine()
        self.executor = ExecutorAgent()
        self.logger = logger.bind(component="streaming_workflow")
        self.event_callback = event_callback
        self.graph = self._build_graph()

    async def _emit_event(self, event: StreamEvent):
        """ارسال رویداد از طریق callback"""
        if self.event_callback:
            await self.event_callback(event)

    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(AgentState)

        workflow.add_node("planner", self._planner_node)
        workflow.add_node("retrieve_context", self._retrieve_context_node)
        workflow.add_node("executor", self._executor_node)
        workflow.add_node("reviewer", self._reviewer_node)
        workflow.add_node("finalizer", self._finalizer_node)

        workflow.set_entry_point("planner")
        workflow.add_edge("planner", "retrieve_context")
        workflow.add_edge("retrieve_context", "executor")
        workflow.add_conditional_edges(
            "executor",
            self._should_continue_execution,
            {"continue": "executor", "review": "reviewer"}
        )
        workflow.add_edge("reviewer", "finalizer")
        workflow.add_edge("finalizer", END)

        return workflow.compile()

    async def _planner_node(self, state: AgentState) -> AgentState:
        await self._emit_event(StreamEvent(
            event_type="node_start",
            node_name="planner",
            status=NodeStatus.started,
            message="در حال تحلیل درخواست و تولید برنامه..."
        ))

        tasks = await self.planner.plan(state["user_request"])

        await self._emit_event(StreamEvent(
            event_type="node_complete",
            node_name="planner",
            status=NodeStatus.completed,
            data={
                "task_count": len(tasks),
                "tasks": [{"id": t.id, "description": t.description, "tools": t.required_tools} for t in tasks]
            },
            message=f"✅ {len(tasks)} وظیفه تولید شد"
        ))

        return {**state, "tasks": tasks, "current_task_index": 0, "task_results": {}, "errors": []}

    async def _retrieve_context_node(self, state: AgentState) -> AgentState:
        await self._emit_event(StreamEvent(
            event_type="node_start",
            node_name="retrieve_context",
            status=NodeStatus.started,
            message="در حال بازیابی context از حافظه..."
        ))

        all_context = []
        for task in state["tasks"]:
            results = self.memory.search(task.description, limit=3)
            all_context.extend(results)

        await self._emit_event(StreamEvent(
            event_type="node_complete",
            node_name="retrieve_context",
            status=NodeStatus.completed,
            data={"context_count": len(all_context)},
            message=f"✅ {len(all_context)} context بازیابی شد"
        ))

        return {**state, "context": all_context}

    async def _executor_node(self, state: AgentState) -> AgentState:
        current_idx = state["current_task_index"]
        task = state["tasks"][current_idx]

        await self._emit_event(StreamEvent(
            event_type="node_start",
            node_name="executor",
            status=NodeStatus.started,
            data={"task_id": task.id, "task_description": task.description},
            message=f"🚀 در حال اجرای: {task.description[:60]}..."
        ))

        start_time = time.time()
        result = await self.executor.execute_task(task, state["user_request"], state.get("context", []))
        exec_time = (time.time() - start_time) * 1000

        task_results = state["task_results"].copy()

        if result.success:
            task_result = {
                "task_id": task.id,
                "status": "completed",
                "output": result.data.get("summary", "Executed successfully"),
                "tools_used": result.data.get("tools_used", []),
                "location": result.data.get("location", {}),
                "execution_time_ms": exec_time
            }

            # ارسال رویداد برای هر tool اجرا شده
            for tool_name, tool_result in result.data.get("results", {}).items():
                await self._emit_event(StreamEvent(
                    event_type="tool_executed",
                    node_name="executor",
                    status=NodeStatus.completed,
                    data={
                        "tool": tool_name,
                        "task_id": task.id,
                        "success": tool_result.get("success", False),
                        "exec_time_ms": tool_result.get("execution_time_ms", 0)
                    },
                    message=f"🛠️ ابزار {tool_name} اجرا شد"
                ))

            await self._emit_event(StreamEvent(
                event_type="task_complete",
                node_name="executor",
                status=NodeStatus.completed,
                data={
                    "task_id": task.id,
                    "task_description": task.description,
                    "summary": result.data.get("summary", ""),
                    "tools_used": task_result["tools_used"],
                    "location": task_result["location"]
                },
                message=f"✅ وظیفه {task.id} تکمیل شد"
            ))
        else:
            task_result = {
                "task_id": task.id,
                "status": "failed",
                "output": f"خطا: {result.error}",
                "error": result.error
            }

            await self._emit_event(StreamEvent(
                event_type="task_failed",
                node_name="executor",
                status=NodeStatus.failed,
                data={"task_id": task.id, "error": result.error},
                message=f"❌ خطا در {task.id}"
            ))

        task_results[task.id] = task_result
        return {**state, "current_task_index": current_idx + 1, "task_results": task_results}

    def _should_continue_execution(self, state: AgentState) -> Literal["continue", "review"]:
        return "continue" if state["current_task_index"] < len(state["tasks"]) else "review"

    async def _reviewer_node(self, state: AgentState) -> AgentState:
        await self._emit_event(StreamEvent(
            event_type="node_start",
            node_name="reviewer",
            status=NodeStatus.started,
            message="🔍 در حال بررسی کیفیت نتایج..."
        ))

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

        await self._emit_event(StreamEvent(
            event_type="node_complete",
            node_name="reviewer",
            status=NodeStatus.completed,
            data=review_summary,
            message=f"✅ امتیاز کیفیت: {review_summary['quality_score']:.2f}"
        ))

        return {**state, "review_summary": review_summary}

    async def _finalizer_node(self, state: AgentState) -> AgentState:
        await self._emit_event(StreamEvent(
            event_type="node_start",
            node_name="finalizer",
            status=NodeStatus.started,
            message="📝 در حال تولید گزارش نهایی..."
        ))

        task_results = state["task_results"]
        review_summary = state.get("review_summary", {})

        response_parts = [
            f"✅ درخواست شما با موفقیت پردازش شد!\n\n",
            f"📊 خلاصه اجرا:\n",
            f"  - تعداد وظایف: {review_summary.get('total_tasks', 0)}\n",
            f"  - موفق: {review_summary.get('successful', 0)}\n",
            f"  - ناموفق: {review_summary.get('failed', 0)}\n",
            f"  - امتیاز کیفیت: {review_summary.get('quality_score', 0):.2f}\n\n"
        ]

        if task_results:
            response_parts.append("📋 جزئیات وظایف:\n")
            for task_id, result in task_results.items():
                output = result.get('output', 'N/A')
                response_parts.append(f"\n  🔹 [{task_id}]:\n")
                for line in output.split('\n'):
                    if line.strip():
                        response_parts.append(f"      {line}\n")

        final_response = "".join(response_parts)

        await self._emit_event(StreamEvent(
            event_type="final",
            node_name="finalizer",
            status=NodeStatus.completed,
            data={
                "final_response": final_response,
                "review_summary": review_summary,
                "tasks": [
                    {
                        "task_id": tid,
                        "description": tr.get("output", "")[:100],
                        "status": tr.get("status"),
                        "tools_used": tr.get("tools_used", [])
                    }
                    for tid, tr in task_results.items()
                ]
            },
            message="🎉 تحلیل با موفقیت تکمیل شد"
        ))

        return {**state, "final_response": final_response}

    async def run(self, user_request: str, session_id: str = "default") -> Dict[str, Any]:
        """اجرای کامل workflow با streaming"""
        initial_state: AgentState = {
            "messages": [HumanMessage(content=user_request)],
            "user_request": user_request,
            "tasks": [],
            "current_task_index": 0,
            "task_results": {},
            "context": [],
            "final_response": "",
            "errors": [],
            "review_summary": {},
            "session_id": session_id
        }

        start_time = time.time()
        final_state = await self.graph.ainvoke(initial_state)
        total_time = (time.time() - start_time) * 1000

        return {
            "session_id": session_id,
            "final_response": final_state["final_response"],
            "tasks": final_state["task_results"],
            "review_summary": final_state.get("review_summary", {}),
            "total_execution_time_ms": total_time
        }