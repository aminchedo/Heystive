#!/usr/bin/env python3
"""
LangGraph Voice Agent Integration
Following the exact pattern from: https://towardsdatascience.com/using-langgraph-and-mcp-servers-to-create-my-own-voice-assistant/

This implementation integrates:
1. LangGraph agent for reasoning and workflow management
2. MCP server for expense management operations
3. Voice streaming capabilities for real-time interaction
4. Persian language support

The agent follows the Luna pattern from the article but adapted for the existing Heystive system.
"""

import asyncio
import logging
import json
import time
from typing import Dict, Any, Optional, List, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

# LangGraph imports with fallback
try:
    from langgraph.graph import StateGraph, END, START
    from langgraph.prebuilt import ToolExecutor
    from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
    from langchain.tools import BaseTool
    from langchain_core.messages import ToolMessage
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    print("⚠️ LangGraph not available, using fallback implementation")

# Import our components
from luna_mcp_server import LunaMCPServer
from heystive_upgrade import RealPersianVoice, RealPersianListener

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# AGENT STATE MANAGEMENT
# =============================================================================

class AgentState(Enum):
    """Agent execution states following TDS article pattern."""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    TOOL_EXECUTION = "tool_execution"
    RESPONSE_GENERATION = "response_generation"
    SPEAKING = "speaking"
    ERROR_HANDLING = "error_handling"

@dataclass
class ConversationState:
    """State object for LangGraph conversation flow."""
    messages: List[BaseMessage]
    user_input: str
    intent: Dict[str, Any]
    context: Dict[str, Any]
    tools_used: List[str]
    tool_results: List[Dict[str, Any]]
    response: str
    audio_response: Optional[str] = None
    error: Optional[str] = None
    needs_confirmation: bool = False
    expense_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.expense_data is None:
            self.expense_data = {}
        if self.tool_results is None:
            self.tool_results = []

# =============================================================================
# LANGCHAIN TOOLS FOR MCP INTEGRATION
# =============================================================================

class ExpenseAddTool(BaseTool):
    """Tool for adding expenses via MCP server."""
    
    name = "add_expense"
    description = "Add a new expense to the database. Use when user mentions spending money or making a purchase."
    
    def __init__(self, mcp_server: LunaMCPServer):
        super().__init__()
        self.mcp_server = mcp_server
    
    def _run(self, amount: str, description: str, category: str = "") -> str:
        """Add expense synchronously."""
        try:
            amount_float = float(amount)
            result = asyncio.run(self.mcp_server.add_expense_direct(amount_float, description, category))
            return json.dumps(result)
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})
    
    async def _arun(self, amount: str, description: str, category: str = "") -> str:
        """Add expense asynchronously."""
        try:
            amount_float = float(amount)
            result = await self.mcp_server.add_expense_direct(amount_float, description, category)
            return json.dumps(result)
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

class ExpenseQueryTool(BaseTool):
    """Tool for querying expenses via MCP server."""
    
    name = "get_expenses"
    description = "Get recent expenses from the database. Use when user asks about their spending or wants to see expenses."
    
    def __init__(self, mcp_server: LunaMCPServer):
        super().__init__()
        self.mcp_server = mcp_server
    
    def _run(self, limit: str = "10", category: str = "") -> str:
        """Get expenses synchronously."""
        try:
            limit_int = int(limit)
            result = asyncio.run(self.mcp_server.get_expenses_direct(limit_int, category))
            return json.dumps(result)
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})
    
    async def _arun(self, limit: str = "10", category: str = "") -> str:
        """Get expenses asynchronously."""
        try:
            limit_int = int(limit)
            result = await self.mcp_server.get_expenses_direct(limit_int, category)
            return json.dumps(result)
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

class ExpenseSummaryTool(BaseTool):
    """Tool for getting expense summaries via MCP server."""
    
    name = "get_expense_summary"
    description = "Get expense summary for a period. Use when user asks about total spending or expense breakdown."
    
    def __init__(self, mcp_server: LunaMCPServer):
        super().__init__()
        self.mcp_server = mcp_server
    
    def _run(self, period: str = "month") -> str:
        """Get expense summary synchronously."""
        try:
            result = asyncio.run(self.mcp_server.get_expense_summary_direct(period))
            return json.dumps(result)
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})
    
    async def _arun(self, period: str = "month") -> str:
        """Get expense summary asynchronously."""
        try:
            result = await self.mcp_server.get_expense_summary_direct(period)
            return json.dumps(result)
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

# =============================================================================
# LANGGRAPH VOICE AGENT
# =============================================================================

class LunaVoiceAgent:
    """
    LangGraph-powered voice agent for expense management.
    Following the Luna pattern from the TDS article.
    """
    
    def __init__(self, voice_system: RealPersianVoice, listener: RealPersianListener):
        self.voice_system = voice_system
        self.listener = listener
        self.mcp_server = LunaMCPServer()
        
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
            "average_response_time": 0.0,
            "voice_interactions": 0
        }
        
        # Initialize LangGraph if available
        if LANGGRAPH_AVAILABLE:
            self._build_conversation_graph()
        else:
            logger.warning("LangGraph not available - using fallback implementation")
    
    def _initialize_tools(self):
        """Initialize tools for expense management."""
        try:
            self.tools = [
                ExpenseAddTool(self.mcp_server),
                ExpenseQueryTool(self.mcp_server),
                ExpenseSummaryTool(self.mcp_server)
            ]
            logger.info(f"Initialized {len(self.tools)} tools for LangGraph agent")
        except Exception as e:
            logger.error(f"Tool initialization failed: {e}")
    
    def _build_conversation_graph(self):
        """Build LangGraph conversation flow following TDS article pattern."""
        if not LANGGRAPH_AVAILABLE:
            return
        
        try:
            # Create state graph
            workflow = StateGraph(ConversationState)
            
            # Add nodes following the Luna pattern
            workflow.add_node("analyze_input", self._analyze_input_node)
            workflow.add_node("extract_expense_info", self._extract_expense_info_node)
            workflow.add_node("plan_action", self._plan_action_node)
            workflow.add_node("execute_tools", self._execute_tools_node)
            workflow.add_node("generate_response", self._generate_response_node)
            workflow.add_node("speak_response", self._speak_response_node)
            workflow.add_node("handle_error", self._handle_error_node)
            
            # Add edges following the conversation flow
            workflow.add_edge(START, "analyze_input")
            workflow.add_edge("analyze_input", "extract_expense_info")
            workflow.add_conditional_edges(
                "extract_expense_info",
                self._should_use_tools,
                {
                    "use_tools": "plan_action",
                    "direct_response": "generate_response"
                }
            )
            workflow.add_edge("plan_action", "execute_tools")
            workflow.add_edge("execute_tools", "generate_response")
            workflow.add_edge("generate_response", "speak_response")
            workflow.add_edge("speak_response", END)
            workflow.add_edge("handle_error", "speak_response")
            
            # Compile graph
            self.conversation_graph = workflow.compile()
            
            logger.info("LangGraph conversation graph built successfully")
            
        except Exception as e:
            logger.error(f"LangGraph building failed: {e}")
            self.conversation_graph = None
    
    async def process_voice_input(self, audio_input: str) -> str:
        """
        Process voice input using LangGraph agent.
        This is the main entry point following the TDS article pattern.
        """
        try:
            self.current_state = AgentState.PROCESSING
            self.agent_stats["total_conversations"] += 1
            self.agent_stats["voice_interactions"] += 1
            
            if LANGGRAPH_AVAILABLE and self.conversation_graph:
                return await self._process_with_langgraph(audio_input)
            else:
                return await self._process_with_fallback(audio_input)
                
        except Exception as e:
            logger.error(f"Voice input processing failed: {e}")
            self.current_state = AgentState.ERROR_HANDLING
            error_response = "متاسفم، مشکلی پیش اومده. لطفاً دوباره امتحان کنید."
            await self._speak_response(error_response)
            return error_response
        finally:
            self.current_state = AgentState.IDLE
    
    async def _process_with_langgraph(self, user_input: str) -> str:
        """Process using LangGraph workflow."""
        try:
            # Create initial state
            initial_state = ConversationState(
                messages=[HumanMessage(content=user_input)],
                user_input=user_input,
                intent={},
                context={"timestamp": datetime.now().isoformat()},
                tools_used=[],
                tool_results=[],
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
    
    async def _process_with_fallback(self, user_input: str) -> str:
        """Fallback processing without LangGraph."""
        try:
            # Simple intent analysis
            intent = self._analyze_intent_simple(user_input)
            
            # Handle expense-related requests
            if intent.get("type") == "expense_add":
                return await self._handle_expense_add_fallback(user_input, intent)
            elif intent.get("type") == "expense_query":
                return await self._handle_expense_query_fallback(user_input, intent)
            elif intent.get("type") == "expense_summary":
                return await self._handle_expense_summary_fallback(user_input, intent)
            else:
                # General conversation
                response = self._generate_general_response(user_input)
                await self._speak_response(response)
                return response
                
        except Exception as e:
            logger.error(f"Fallback processing failed: {e}")
            raise
    
    # LangGraph Node Functions
    async def _analyze_input_node(self, state: ConversationState) -> ConversationState:
        """Analyze user input for intent and entities."""
        try:
            user_input = state.user_input.lower()
            
            # Detect intent
            if any(word in user_input for word in ["خرید", "خریدم", "پول", "هزینه", "spent", "bought", "purchase"]):
                state.intent["type"] = "expense_add"
            elif any(word in user_input for word in ["هزینه‌ها", "خرجی", "expenses", "spending", "show me"]):
                state.intent["type"] = "expense_query"
            elif any(word in user_input for word in ["جمع", "کل", "summary", "total", "how much"]):
                state.intent["type"] = "expense_summary"
            else:
                state.intent["type"] = "general"
            
            state.intent["confidence"] = 0.8  # Simple confidence score
            
            logger.info(f"Analyzed intent: {state.intent}")
            return state
            
        except Exception as e:
            state.error = f"Intent analysis failed: {e}"
            return state
    
    async def _extract_expense_info_node(self, state: ConversationState) -> ConversationState:
        """Extract expense information from user input."""
        try:
            if state.intent.get("type") == "expense_add":
                # Extract amount and description
                import re
                
                # Look for amount patterns
                amount_patterns = [
                    r'(\d+\.?\d*)\s*(?:تومان|ریال|dollar|$)',
                    r'(\d+\.?\d*)\s*(?:تومان|ریال)',
                    r'\$(\d+\.?\d*)',
                    r'(\d+\.?\d*)\s*(?:dollars?|bucks?)'
                ]
                
                amount = None
                for pattern in amount_patterns:
                    match = re.search(pattern, state.user_input)
                    if match:
                        amount = float(match.group(1))
                        break
                
                # If no amount found, try to extract any number
                if not amount:
                    numbers = re.findall(r'\d+\.?\d*', state.user_input)
                    if numbers:
                        amount = float(numbers[0])
                
                state.expense_data = {
                    "amount": amount,
                    "description": state.user_input,
                    "category": ""  # Will be auto-categorized
                }
                
            return state
            
        except Exception as e:
            state.error = f"Expense info extraction failed: {e}"
            return state
    
    def _should_use_tools(self, state: ConversationState) -> str:
        """Decide whether to use tools or generate direct response."""
        intent_type = state.intent.get("type", "general")
        
        if intent_type in ["expense_add", "expense_query", "expense_summary"]:
            return "use_tools"
        else:
            return "direct_response"
    
    async def _plan_action_node(self, state: ConversationState) -> ConversationState:
        """Plan which tools to use based on intent."""
        try:
            intent_type = state.intent.get("type")
            
            if intent_type == "expense_add" and state.expense_data.get("amount"):
                state.context["planned_action"] = "add_expense"
                state.context["tool_params"] = state.expense_data
            elif intent_type == "expense_query":
                state.context["planned_action"] = "get_expenses"
                state.context["tool_params"] = {"limit": "10", "category": ""}
            elif intent_type == "expense_summary":
                state.context["planned_action"] = "get_expense_summary"
                state.context["tool_params"] = {"period": "month"}
            
            return state
            
        except Exception as e:
            state.error = f"Action planning failed: {e}"
            return state
    
    async def _execute_tools_node(self, state: ConversationState) -> ConversationState:
        """Execute the planned tools."""
        try:
            self.current_state = AgentState.TOOL_EXECUTION
            
            planned_action = state.context.get("planned_action")
            tool_params = state.context.get("tool_params", {})
            
            if planned_action == "add_expense":
                tool = next((t for t in self.tools if t.name == "add_expense"), None)
                if tool:
                    result_str = await tool._arun(**tool_params)
                    result = json.loads(result_str)
                    state.tool_results.append(result)
                    state.tools_used.append("add_expense")
            
            elif planned_action == "get_expenses":
                tool = next((t for t in self.tools if t.name == "get_expenses"), None)
                if tool:
                    result_str = await tool._arun(**tool_params)
                    result = json.loads(result_str)
                    state.tool_results.append(result)
                    state.tools_used.append("get_expenses")
            
            elif planned_action == "get_expense_summary":
                tool = next((t for t in self.tools if t.name == "get_expense_summary"), None)
                if tool:
                    result_str = await tool._arun(**tool_params)
                    result = json.loads(result_str)
                    state.tool_results.append(result)
                    state.tools_used.append("get_expense_summary")
            
            return state
            
        except Exception as e:
            state.error = f"Tool execution failed: {e}"
            return state
    
    async def _generate_response_node(self, state: ConversationState) -> ConversationState:
        """Generate response based on tool results or direct conversation."""
        try:
            self.current_state = AgentState.RESPONSE_GENERATION
            
            if state.tool_results:
                # Generate response based on tool results
                state.response = self._format_tool_response(state.tool_results[0], state.intent.get("type"))
            else:
                # Generate general response
                state.response = self._generate_general_response(state.user_input)
            
            return state
            
        except Exception as e:
            state.error = f"Response generation failed: {e}"
            state.response = "متاسفم، نتونستم پاسخ مناسبی تولید کنم."
            return state
    
    async def _speak_response_node(self, state: ConversationState) -> ConversationState:
        """Convert response to speech."""
        try:
            self.current_state = AgentState.SPEAKING
            
            success = await self._speak_response(state.response)
            state.audio_response = "success" if success else "failed"
            
            return state
            
        except Exception as e:
            state.error = f"Speech generation failed: {e}"
            return state
    
    async def _handle_error_node(self, state: ConversationState) -> ConversationState:
        """Handle errors in conversation flow."""
        logger.error(f"Agent error: {state.error}")
        state.response = "متاسفم، مشکلی پیش اومده. لطفاً دوباره امتحان کنید."
        return state
    
    # Helper Methods
    def _analyze_intent_simple(self, user_input: str) -> Dict[str, Any]:
        """Simple intent analysis for fallback."""
        user_lower = user_input.lower()
        
        if any(word in user_lower for word in ["خرید", "خریدم", "پول", "هزینه", "spent", "bought"]):
            return {"type": "expense_add", "confidence": 0.7}
        elif any(word in user_lower for word in ["هزینه‌ها", "خرجی", "expenses", "show me"]):
            return {"type": "expense_query", "confidence": 0.7}
        elif any(word in user_lower for word in ["جمع", "کل", "summary", "total"]):
            return {"type": "expense_summary", "confidence": 0.7}
        else:
            return {"type": "general", "confidence": 0.5}
    
    async def _handle_expense_add_fallback(self, user_input: str, intent: Dict[str, Any]) -> str:
        """Handle expense addition in fallback mode."""
        try:
            # Extract amount (simple pattern)
            import re
            numbers = re.findall(r'\d+\.?\d*', user_input)
            
            if numbers:
                amount = float(numbers[0])
                result = await self.mcp_server.add_expense_direct(amount, user_input)
                
                if result["success"]:
                    expense = result["expense"]
                    response = f"هزینه ثبت شد: {expense['description']} - ${expense['amount']:.2f} در دسته {expense['category']}"
                else:
                    response = "متاسفم، نتونستم هزینه رو ثبت کنم."
            else:
                response = "مبلغ هزینه رو نفهمیدم. لطفاً مبلغ رو بگید."
            
            await self._speak_response(response)
            return response
            
        except Exception as e:
            logger.error(f"Expense add fallback failed: {e}")
            response = "مشکلی در ثبت هزینه پیش اومده."
            await self._speak_response(response)
            return response
    
    async def _handle_expense_query_fallback(self, user_input: str, intent: Dict[str, Any]) -> str:
        """Handle expense query in fallback mode."""
        try:
            result = await self.mcp_server.get_expenses_direct(5)  # Last 5 expenses
            
            if result["success"] and result["expenses"]:
                response = f"آخرین {len(result['expenses'])} هزینه شما:\n"
                for expense in result["expenses"]:
                    response += f"- {expense['description']}: ${expense['amount']:.2f}\n"
            else:
                response = "هیچ هزینه‌ای ثبت نشده."
            
            await self._speak_response(response)
            return response
            
        except Exception as e:
            logger.error(f"Expense query fallback failed: {e}")
            response = "نتونستم هزینه‌ها رو بیارم."
            await self._speak_response(response)
            return response
    
    async def _handle_expense_summary_fallback(self, user_input: str, intent: Dict[str, Any]) -> str:
        """Handle expense summary in fallback mode."""
        try:
            result = await self.mcp_server.get_expense_summary_direct("month")
            
            if result["success"]:
                summary = result["summary"]
                response = f"خلاصه هزینه‌های ماه:\n"
                response += f"کل هزینه: ${summary['total_amount']:.2f}\n"
                response += f"تعداد هزینه‌ها: {summary['total_expenses']}\n"
                
                if summary["by_category"]:
                    response += "تفکیک بر اساس دسته:\n"
                    for category, data in summary["by_category"].items():
                        response += f"- {category}: ${data['amount']:.2f}\n"
            else:
                response = "نتونستم خلاصه هزینه‌ها رو بیارم."
            
            await self._speak_response(response)
            return response
            
        except Exception as e:
            logger.error(f"Expense summary fallback failed: {e}")
            response = "مشکلی در آوردن خلاصه هزینه‌ها پیش اومده."
            await self._speak_response(response)
            return response
    
    def _format_tool_response(self, tool_result: Dict[str, Any], intent_type: str) -> str:
        """Format tool response into natural language."""
        
        if not tool_result.get("success"):
            return "متاسفم، نتونستم درخواست شما رو انجام بدم."
        
        if intent_type == "expense_add":
            expense = tool_result.get("expense", {})
            return f"هزینه ثبت شد: {expense.get('description', 'نامشخص')} - ${expense.get('amount', 0):.2f} در دسته {expense.get('category', 'نامشخص')}"
        
        elif intent_type == "expense_query":
            expenses = tool_result.get("expenses", [])
            if expenses:
                response = f"آخرین {len(expenses)} هزینه شما:\n"
                for expense in expenses[:3]:  # Show only first 3
                    response += f"- {expense['description']}: ${expense['amount']:.2f}\n"
                return response
            else:
                return "هیچ هزینه‌ای ثبت نشده."
        
        elif intent_type == "expense_summary":
            summary = tool_result.get("summary", {})
            response = f"خلاصه هزینه‌های ماه:\n"
            response += f"کل هزینه: ${summary.get('total_amount', 0):.2f}\n"
            response += f"تعداد هزینه‌ها: {summary.get('total_expenses', 0)}"
            return response
        
        return "درخواست شما انجام شد."
    
    def _generate_general_response(self, user_input: str) -> str:
        """Generate general conversational response."""
        user_lower = user_input.lower()
        
        if any(word in user_lower for word in ["سلام", "hello", "hi"]):
            return "سلام! من لونا هستم، دستیار مدیریت هزینه‌های شما. چطور می‌تونم کمکتون کنم؟"
        elif any(word in user_lower for word in ["کمک", "help", "راهنما"]):
            return "من می‌تونم هزینه‌هاتون رو ثبت کنم، لیست هزینه‌ها رو نشونتون بدم، و خلاصه‌ای از خرجی‌هاتون ارائه بدم."
        elif any(word in user_lower for word in ["ممنون", "thank", "متشکر"]):
            return "خواهش می‌کنم! همیشه در خدمتتون هستم."
        else:
            return "متوجه نشدم. می‌تونید بگید که چه هزینه‌ای داشتید یا از من درباره هزینه‌هاتون بپرسید؟"
    
    async def _speak_response(self, response: str) -> bool:
        """Convert response to speech."""
        try:
            return self.voice_system.speak_immediately(response)
        except Exception as e:
            logger.error(f"Speech synthesis failed: {e}")
            return False
    
    def _update_tool_usage_stats(self, tools_used: List[str]):
        """Update tool usage statistics."""
        for tool in tools_used:
            if tool in self.agent_stats["tool_usage_count"]:
                self.agent_stats["tool_usage_count"][tool] += 1
            else:
                self.agent_stats["tool_usage_count"][tool] = 1
    
    def get_agent_stats(self) -> Dict[str, Any]:
        """Get agent performance statistics."""
        return {
            "current_state": self.current_state.value,
            "langgraph_available": LANGGRAPH_AVAILABLE,
            "tools_count": len(self.tools),
            "agent_stats": self.agent_stats,
            "mcp_server_stats": self.mcp_server.get_stats()
        }
    
    async def start_voice_interaction(self):
        """Start interactive voice mode following TDS article pattern."""
        
        print("\n🎤 LUNA VOICE AGENT - INTERACTIVE MODE")
        print("=" * 40)
        print("Say things like:")
        print("  - 'I spent 25 dollars on lunch'")
        print("  - 'Show me my expenses'")
        print("  - 'How much did I spend this month?'")
        print("  - 'خریدم بیست دلار ناهار' (Persian)")
        print("  - Press Ctrl+C to stop")
        print()
        
        wake_words = ["luna", "لونا", "hey luna", "هی لونا"]
        
        def voice_callback(command: str):
            """Handle voice commands."""
            print(f"🎤 Voice command: '{command}'")
            try:
                response = asyncio.run(self.process_voice_input(command))
                print(f"🤖 Response: '{response}'")
            except Exception as e:
                print(f"❌ Error processing voice command: {e}")
        
        try:
            self.listener.listen_for_wake_word(wake_words, voice_callback)
        except KeyboardInterrupt:
            print("\n👋 Luna voice agent stopped")

# =============================================================================
# TESTING AND DEMONSTRATION
# =============================================================================

async def test_langgraph_voice_agent():
    """Test the complete LangGraph voice agent."""
    
    print("\n🧪 TESTING LANGGRAPH VOICE AGENT")
    print("=" * 35)
    
    # Initialize components
    from heystive_upgrade import RealPersianVoice, RealPersianListener
    
    voice_system = RealPersianVoice()
    listener = RealPersianListener()
    agent = LunaVoiceAgent(voice_system, listener)
    
    # Test commands
    test_commands = [
        "I spent 25 dollars on lunch at restaurant",
        "Show me my recent expenses",
        "How much did I spend this month?",
        "خریدم بیست دلار قهوه",  # Persian: I bought 20 dollars coffee
        "هزینه‌هام رو نشون بده",    # Persian: Show me my expenses
        "Hello Luna, how are you?"
    ]
    
    print("🤖 Testing voice agent with predefined commands:")
    
    for i, command in enumerate(test_commands, 1):
        print(f"\n🗣️ Test {i}: '{command}'")
        try:
            response = await agent.process_voice_input(command)
            print(f"✅ Response: '{response}'")
            time.sleep(1)  # Brief pause between tests
        except Exception as e:
            print(f"❌ Test {i} failed: {e}")
    
    # Show statistics
    print("\n📊 AGENT STATISTICS:")
    stats = agent.get_agent_stats()
    print(f"  - Total Conversations: {stats['agent_stats']['total_conversations']}")
    print(f"  - Successful Completions: {stats['agent_stats']['successful_completions']}")
    print(f"  - Voice Interactions: {stats['agent_stats']['voice_interactions']}")
    print(f"  - Tool Usage: {stats['agent_stats']['tool_usage_count']}")
    print(f"  - MCP Requests: {stats['mcp_server_stats']['total_requests']}")
    
    return agent

def main():
    """Main function for testing."""
    print("🚀 LANGGRAPH VOICE AGENT - LUNA")
    print("Following TDS article patterns")
    print("=" * 50)
    
    # Run tests
    agent = asyncio.run(test_langgraph_voice_agent())
    
    print("\n✅ LANGGRAPH VOICE AGENT TESTING COMPLETE")
    
    # Start interactive mode if requested
    try:
        print("\n🎤 Starting interactive voice mode...")
        print("Press Ctrl+C to exit")
        asyncio.run(agent.start_voice_interaction())
    except KeyboardInterrupt:
        print("\n👋 Interactive mode stopped")
    
    return agent

if __name__ == "__main__":
    main()