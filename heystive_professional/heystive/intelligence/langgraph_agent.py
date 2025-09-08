"""
LangGraph Agent for Persian Voice Assistant
Advanced agent orchestration using LangGraph for complex task handling
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Callable
import json
from dataclasses import dataclass
from enum import Enum

try:
    from langgraph.graph import StateGraph, END
    from langgraph.prebuilt import ToolExecutor, ToolInvocation
    from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
    from langchain.tools import BaseTool
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    logger.warning("LangGraph not available. Install with: pip install langgraph")

logger = logging.getLogger(__name__)

class AgentState(Enum):
    """Agent execution states"""
    IDLE = "idle"
    PROCESSING = "processing"
    TOOL_EXECUTION = "tool_execution"
    RESPONSE_GENERATION = "response_generation"
    ERROR_HANDLING = "error_handling"

@dataclass
class ConversationState:
    """State object for LangGraph conversation flow"""
    messages: List[BaseMessage]
    user_input: str
    intent: Dict[str, Any]
    context: Dict[str, Any]
    tools_used: List[str]
    response: str
    error: Optional[str] = None
    needs_confirmation: bool = False
    device_actions: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.device_actions is None:
            self.device_actions = []

class PersianSmartHomeTool(BaseTool):
    """Smart home control tool for Persian commands"""
    
    name = "persian_smart_home"
    description = "Control smart home devices using Persian commands"
    
    def __init__(self, smart_home_controller):
        super().__init__()
        self.smart_home_controller = smart_home_controller
    
    def _run(self, persian_command: str) -> str:
        """Execute smart home command"""
        try:
            if not self.smart_home_controller:
                return "کنترل خانه هوشمند در دسترس نیست"
            
            # This would be async in real implementation
            import asyncio
            loop = asyncio.get_event_loop()
            result = loop.run_until_complete(
                self.smart_home_controller.control_device_by_persian_command(persian_command)
            )
            return result
        except Exception as e:
            return f"خطا در کنترل دستگاه: {str(e)}"
    
    async def _arun(self, persian_command: str) -> str:
        """Async execute smart home command"""
        try:
            if not self.smart_home_controller:
                return "کنترل خانه هوشمند در دسترس نیست"
            
            result = await self.smart_home_controller.control_device_by_persian_command(persian_command)
            return result
        except Exception as e:
            return f"خطا در کنترل دستگاه: {str(e)}"

class PersianTimeInfoTool(BaseTool):
    """Time and date information tool in Persian"""
    
    name = "persian_time_info"
    description = "Get current time and date information in Persian"
    
    def _run(self, query: str = "") -> str:
        """Get time information"""
        import datetime
        import jdatetime  # Persian calendar
        
        now = datetime.datetime.now()
        persian_now = jdatetime.datetime.now()
        
        if "ساعت" in query or "زمان" in query:
            return f"ساعت {now.strftime('%H:%M')} است"
        elif "تاریخ" in query:
            return f"امروز {persian_now.strftime('%d %B %Y')} است"
        else:
            return f"ساعت {now.strftime('%H:%M')} - تاریخ {persian_now.strftime('%d %B %Y')}"
    
    async def _arun(self, query: str = "") -> str:
        """Async get time information"""
        return self._run(query)

class PersianLangGraphAgent:
    """
    Advanced Persian conversation agent using LangGraph
    Orchestrates complex multi-step conversations and tool usage
    """
    
    def __init__(self, llm_manager, smart_home_controller=None):
        self.llm_manager = llm_manager
        self.smart_home_controller = smart_home_controller
        
        # Agent state
        self.current_state = AgentState.IDLE
        self.conversation_graph = None
        
        # Tools
        self.tools = []
        self._initialize_tools()
        
        # Performance tracking
        self.agent_stats = {
            "total_conversations": 0,
            "successful_completions": 0,
            "tool_usage_count": {},
            "average_steps": 0.0
        }
        
        # Initialize LangGraph if available
        if LANGGRAPH_AVAILABLE:
            self._build_conversation_graph()
        else:
            logger.warning("LangGraph not available - using fallback implementation")
    
    def _initialize_tools(self):
        """Initialize available tools for the agent"""
        try:
            # Smart home control tool
            if self.smart_home_controller:
                self.tools.append(PersianSmartHomeTool(self.smart_home_controller))
            
            # Time information tool
            self.tools.append(PersianTimeInfoTool())
            
            logger.info(f"Initialized {len(self.tools)} tools for LangGraph agent")
            
        except Exception as e:
            logger.error(f"Tool initialization failed: {e}")
    
    def _build_conversation_graph(self):
        """Build LangGraph conversation flow"""
        if not LANGGRAPH_AVAILABLE:
            return
        
        try:
            # Create state graph
            workflow = StateGraph(ConversationState)
            
            # Add nodes
            workflow.add_node("analyze_input", self._analyze_input_node)
            workflow.add_node("plan_response", self._plan_response_node)
            workflow.add_node("execute_tools", self._execute_tools_node)
            workflow.add_node("generate_response", self._generate_response_node)
            workflow.add_node("handle_error", self._handle_error_node)
            
            # Add edges
            workflow.add_edge("analyze_input", "plan_response")
            workflow.add_conditional_edges(
                "plan_response",
                self._should_use_tools,
                {
                    "use_tools": "execute_tools",
                    "direct_response": "generate_response"
                }
            )
            workflow.add_edge("execute_tools", "generate_response")
            workflow.add_edge("generate_response", END)
            workflow.add_edge("handle_error", END)
            
            # Set entry point
            workflow.set_entry_point("analyze_input")
            
            # Compile graph
            self.conversation_graph = workflow.compile()
            
            logger.info("LangGraph conversation graph built successfully")
            
        except Exception as e:
            logger.error(f"LangGraph building failed: {e}")
            self.conversation_graph = None
    
    async def process_conversation(self, user_input: str, context: Dict[str, Any] = None) -> str:
        """
        Process conversation using LangGraph agent
        
        Args:
            user_input: Persian user input
            context: Conversation context
            
        Returns:
            Persian response
        """
        try:
            self.current_state = AgentState.PROCESSING
            self.agent_stats["total_conversations"] += 1
            
            if LANGGRAPH_AVAILABLE and self.conversation_graph:
                return await self._process_with_langgraph(user_input, context)
            else:
                return await self._process_with_fallback(user_input, context)
                
        except Exception as e:
            logger.error(f"Conversation processing failed: {e}")
            self.current_state = AgentState.ERROR_HANDLING
            return "متاسفم، مشکلی پیش اومده. لطفاً دوباره امتحان کنید."
        finally:
            self.current_state = AgentState.IDLE
    
    async def _process_with_langgraph(self, user_input: str, context: Dict[str, Any] = None) -> str:
        """Process using LangGraph workflow"""
        try:
            # Create initial state
            initial_state = ConversationState(
                messages=[HumanMessage(content=user_input)],
                user_input=user_input,
                intent={},
                context=context or {},
                tools_used=[],
                response=""
            )
            
            # Run the graph
            result = await self.conversation_graph.ainvoke(initial_state)
            
            # Update stats
            self.agent_stats["successful_completions"] += 1
            self._update_tool_usage_stats(result.tools_used)
            
            return result.response
            
        except Exception as e:
            logger.error(f"LangGraph processing failed: {e}")
            raise
    
    async def _process_with_fallback(self, user_input: str, context: Dict[str, Any] = None) -> str:
        """Fallback processing without LangGraph"""
        try:
            # Simple intent analysis
            intent = await self._analyze_intent_fallback(user_input)
            
            # Check if we need tools
            if intent.get("needs_tools", False):
                tool_result = await self._execute_tools_fallback(user_input, intent)
                if tool_result:
                    return tool_result
            
            # Generate response using LLM
            response = await self.llm_manager.generate_persian_response(user_input, context)
            
            self.agent_stats["successful_completions"] += 1
            return response
            
        except Exception as e:
            logger.error(f"Fallback processing failed: {e}")
            raise
    
    async def _analyze_input_node(self, state: ConversationState) -> ConversationState:
        """Analyze user input and extract intent"""
        try:
            # Use LLM manager for intent analysis
            intent = await self.llm_manager.analyze_intent(state.user_input)
            state.intent = intent
            
            # Add system message for context
            state.messages.insert(0, SystemMessage(content="""
شما استیو هستید، دستیار صوتی فارسی. شما می‌توانید:
1. دستگاه‌های خانه هوشمند را کنترل کنید
2. اطلاعات زمان و تاریخ ارائه دهید  
3. به سوالات عمومی پاسخ دهید

همیشه به فارسی پاسخ دهید و طبیعی صحبت کنید.
"""))
            
            return state
            
        except Exception as e:
            state.error = f"Intent analysis failed: {e}"
            return state
    
    async def _plan_response_node(self, state: ConversationState) -> ConversationState:
        """Plan response strategy based on intent"""
        try:
            intent = state.intent.get("intent", "other")
            
            # Determine if tools are needed
            if intent == "device_control":
                state.needs_confirmation = False  # For now, no confirmation needed
                # Plan device action
                device = state.intent.get("device", "")
                action = state.intent.get("action", "")
                if device and action:
                    state.device_actions.append({
                        "device": device,
                        "action": action,
                        "command": f"{device} را {action} کن"
                    })
            
            return state
            
        except Exception as e:
            state.error = f"Response planning failed: {e}"
            return state
    
    def _should_use_tools(self, state: ConversationState) -> str:
        """Decide whether to use tools or generate direct response"""
        intent = state.intent.get("intent", "other")
        
        if intent == "device_control" and state.device_actions:
            return "use_tools"
        elif intent == "question" and any(word in state.user_input.lower() for word in ["ساعت", "زمان", "تاریخ"]):
            return "use_tools"
        else:
            return "direct_response"
    
    async def _execute_tools_node(self, state: ConversationState) -> ConversationState:
        """Execute required tools"""
        try:
            self.current_state = AgentState.TOOL_EXECUTION
            
            # Execute device control tools
            if state.device_actions:
                for action in state.device_actions:
                    tool_result = await self._execute_smart_home_tool(action["command"])
                    state.tools_used.append("persian_smart_home")
                    
                    # Add tool result to messages
                    state.messages.append(AIMessage(content=f"نتیجه کنترل دستگاه: {tool_result}"))
            
            # Execute time info tool if needed
            if any(word in state.user_input.lower() for word in ["ساعت", "زمان", "تاریخ"]):
                time_result = await self._execute_time_tool(state.user_input)
                state.tools_used.append("persian_time_info")
                
                # Add tool result to messages
                state.messages.append(AIMessage(content=f"اطلاعات زمان: {time_result}"))
            
            return state
            
        except Exception as e:
            state.error = f"Tool execution failed: {e}"
            return state
    
    async def _generate_response_node(self, state: ConversationState) -> ConversationState:
        """Generate final response"""
        try:
            self.current_state = AgentState.RESPONSE_GENERATION
            
            # If we have tool results, use them to generate response
            if state.tools_used:
                # Extract tool results from messages
                tool_results = []
                for msg in state.messages:
                    if isinstance(msg, AIMessage) and ("نتیجه" in msg.content or "اطلاعات" in msg.content):
                        tool_results.append(msg.content)
                
                if tool_results:
                    # Generate response based on tool results
                    context = state.context.copy()
                    context["tool_results"] = tool_results
                    
                    response = await self.llm_manager.generate_persian_response(
                        state.user_input, context
                    )
                    state.response = response
                else:
                    # Fallback to direct tool result
                    if state.device_actions:
                        state.response = "دستور انجام شد."
                    else:
                        state.response = tool_results[0] if tool_results else "انجام شد."
            else:
                # Generate response using LLM without tools
                response = await self.llm_manager.generate_persian_response(
                    state.user_input, state.context
                )
                state.response = response
            
            return state
            
        except Exception as e:
            state.error = f"Response generation failed: {e}"
            return state
    
    async def _handle_error_node(self, state: ConversationState) -> ConversationState:
        """Handle errors in conversation flow"""
        logger.error(f"Agent error: {state.error}")
        state.response = "متاسفم، مشکلی پیش اومده. لطفاً دوباره امتحان کنید."
        return state
    
    async def _execute_smart_home_tool(self, command: str) -> str:
        """Execute smart home tool"""
        try:
            for tool in self.tools:
                if isinstance(tool, PersianSmartHomeTool):
                    return await tool._arun(command)
            return "ابزار کنترل خانه هوشمند در دسترس نیست"
        except Exception as e:
            return f"خطا در اجرای دستور: {e}"
    
    async def _execute_time_tool(self, query: str) -> str:
        """Execute time information tool"""
        try:
            for tool in self.tools:
                if isinstance(tool, PersianTimeInfoTool):
                    return await tool._arun(query)
            return "ابزار اطلاعات زمان در دسترس نیست"
        except Exception as e:
            return f"خطا در دریافت اطلاعات زمان: {e}"
    
    async def _analyze_intent_fallback(self, user_input: str) -> Dict[str, Any]:
        """Fallback intent analysis without LangGraph"""
        try:
            return await self.llm_manager.analyze_intent(user_input)
        except Exception as e:
            logger.error(f"Fallback intent analysis failed: {e}")
            return {"intent": "other", "confidence": 0.0}
    
    async def _execute_tools_fallback(self, user_input: str, intent: Dict[str, Any]) -> Optional[str]:
        """Fallback tool execution"""
        try:
            intent_type = intent.get("intent", "")
            
            if intent_type == "device_control":
                # Execute smart home control
                device = intent.get("device", "")
                action = intent.get("action", "")
                if device and action:
                    command = f"{device} را {action} کن"
                    return await self._execute_smart_home_tool(command)
            
            elif "ساعت" in user_input or "زمان" in user_input or "تاریخ" in user_input:
                # Execute time tool
                return await self._execute_time_tool(user_input)
            
            return None
            
        except Exception as e:
            logger.error(f"Fallback tool execution failed: {e}")
            return None
    
    def _update_tool_usage_stats(self, tools_used: List[str]):
        """Update tool usage statistics"""
        for tool in tools_used:
            if tool in self.agent_stats["tool_usage_count"]:
                self.agent_stats["tool_usage_count"][tool] += 1
            else:
                self.agent_stats["tool_usage_count"][tool] = 1
    
    def get_agent_stats(self) -> Dict[str, Any]:
        """Get agent performance statistics"""
        return {
            "current_state": self.current_state.value,
            "langgraph_available": LANGGRAPH_AVAILABLE,
            "tools_count": len(self.tools),
            "agent_stats": self.agent_stats
        }
    
    def reset_agent(self):
        """Reset agent state"""
        self.current_state = AgentState.IDLE
        logger.info("LangGraph agent reset")