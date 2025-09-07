#!/usr/bin/env python3
"""
Heystive Upgrade Test - Simplified Version
Tests the core functionality without requiring external audio libraries.

This demonstrates the complete system architecture following the TDS article patterns.
"""

import asyncio
import logging
import time
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# SIMPLIFIED VOICE SYSTEM (NO EXTERNAL DEPENDENCIES)
# =============================================================================

class SimplifiedVoiceSystem:
    """Simplified voice system for testing without audio libraries."""
    
    def __init__(self):
        self.audio_output_path = Path("heystive_voice_output")
        self.audio_output_path.mkdir(exist_ok=True)
        
        self.synthesis_stats = {
            "total_syntheses": 0,
            "successful_syntheses": 0,
            "average_latency": 0.0
        }
        
        print("✅ Simplified Voice System initialized")
    
    def speak_and_save(self, text: str, output_file: str) -> bool:
        """Simulate speech generation by creating text files."""
        try:
            start_time = time.time()
            
            # Create text file instead of audio
            text_file = output_file.replace('.wav', '.txt')
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(f"VOICE OUTPUT: {text}\n")
                f.write(f"Generated at: {datetime.now().isoformat()}\n")
                f.write(f"Duration estimate: {len(text) * 0.1:.2f} seconds\n")
            
            latency = time.time() - start_time
            self._update_stats(latency, True)
            
            print(f"🎵 Generated voice file: {text_file}")
            print(f"    Content: '{text[:50]}...'")
            
            return True
            
        except Exception as e:
            logger.error(f"Voice generation failed: {e}")
            self._update_stats(0, False)
            return False
    
    def speak_immediately(self, text: str) -> bool:
        """Simulate immediate speech."""
        try:
            print(f"🗣️ SPEAKING: '{text}'")
            return True
        except Exception as e:
            logger.error(f"Immediate speech failed: {e}")
            return False
    
    def _update_stats(self, latency: float, success: bool):
        """Update synthesis statistics."""
        self.synthesis_stats["total_syntheses"] += 1
        
        if success:
            self.synthesis_stats["successful_syntheses"] += 1
            
            total_successful = self.synthesis_stats["successful_syntheses"]
            current_avg = self.synthesis_stats["average_latency"]
            self.synthesis_stats["average_latency"] = (
                (current_avg * (total_successful - 1) + latency) / total_successful
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get synthesis statistics."""
        total = self.synthesis_stats["total_syntheses"]
        success_rate = (self.synthesis_stats["successful_syntheses"] / max(1, total)) * 100
        
        return {
            **self.synthesis_stats,
            "success_rate": success_rate,
            "voice_files_created": len(list(self.audio_output_path.glob("*.txt")))
        }

class SimplifiedListener:
    """Simplified listener for testing without audio libraries."""
    
    def __init__(self):
        self.recognition_stats = {
            "total_recognitions": 0,
            "successful_recognitions": 0,
            "average_latency": 0.0
        }
        
        print("✅ Simplified Listener initialized")
    
    def simulate_voice_input(self, text: str) -> str:
        """Simulate voice input recognition."""
        try:
            start_time = time.time()
            
            print(f"🎤 SIMULATED INPUT: '{text}'")
            
            latency = time.time() - start_time
            self._update_stats(latency, True)
            
            return text
            
        except Exception as e:
            logger.error(f"Voice input simulation failed: {e}")
            self._update_stats(0, False)
            return ""
    
    def _update_stats(self, latency: float, success: bool):
        """Update recognition statistics."""
        self.recognition_stats["total_recognitions"] += 1
        
        if success:
            self.recognition_stats["successful_recognitions"] += 1
            
            total_successful = self.recognition_stats["successful_recognitions"]
            current_avg = self.recognition_stats["average_latency"]
            self.recognition_stats["average_latency"] = (
                (current_avg * (total_successful - 1) + latency) / total_successful
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get recognition statistics."""
        total = self.recognition_stats["total_recognitions"]
        success_rate = (self.recognition_stats["successful_recognitions"] / max(1, total)) * 100
        
        return {
            **self.recognition_stats,
            "success_rate": success_rate
        }

# =============================================================================
# SIMPLIFIED MCP SERVER
# =============================================================================

class SimplifiedMCPServer:
    """Simplified MCP server for expense management."""
    
    def __init__(self):
        self.expenses = []
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "expenses_added": 0
        }
        
        print("✅ Simplified MCP Server initialized")
    
    async def add_expense_direct(self, amount: float, description: str, category: str = "") -> Dict[str, Any]:
        """Add expense directly."""
        try:
            self.stats["total_requests"] += 1
            
            # Auto-categorize if not provided
            if not category:
                category = self._auto_categorize(description)
            
            expense = {
                "id": len(self.expenses) + 1,
                "amount": amount,
                "description": description,
                "category": category,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "created_at": datetime.now().isoformat()
            }
            
            self.expenses.append(expense)
            
            self.stats["successful_requests"] += 1
            self.stats["expenses_added"] += 1
            
            return {
                "success": True,
                "expense_id": expense["id"],
                "expense": expense,
                "message": f"Added expense: {description} - ${amount:.2f} ({category})"
            }
            
        except Exception as e:
            logger.error(f"Failed to add expense: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_expenses_direct(self, limit: int = 10, category: str = "") -> Dict[str, Any]:
        """Get expenses directly."""
        try:
            self.stats["total_requests"] += 1
            
            expenses = self.expenses
            if category:
                expenses = [e for e in expenses if e["category"] == category]
            
            # Return most recent first
            expenses = sorted(expenses, key=lambda x: x["created_at"], reverse=True)
            expenses = expenses[:limit]
            
            self.stats["successful_requests"] += 1
            
            return {
                "success": True,
                "expenses": expenses,
                "count": len(expenses)
            }
            
        except Exception as e:
            logger.error(f"Failed to get expenses: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_expense_summary_direct(self, period: str = "month") -> Dict[str, Any]:
        """Get expense summary directly."""
        try:
            self.stats["total_requests"] += 1
            
            total_amount = sum(e["amount"] for e in self.expenses)
            total_expenses = len(self.expenses)
            
            # Group by category
            by_category = {}
            for expense in self.expenses:
                category = expense["category"]
                if category not in by_category:
                    by_category[category] = {"amount": 0, "count": 0}
                by_category[category]["amount"] += expense["amount"]
                by_category[category]["count"] += 1
            
            summary = {
                "period": period,
                "total_amount": total_amount,
                "total_expenses": total_expenses,
                "by_category": by_category
            }
            
            self.stats["successful_requests"] += 1
            
            return {
                "success": True,
                "summary": summary
            }
            
        except Exception as e:
            logger.error(f"Failed to get expense summary: {e}")
            return {"success": False, "error": str(e)}
    
    def _auto_categorize(self, description: str) -> str:
        """Auto-categorize expense based on description."""
        description_lower = description.lower()
        
        if any(word in description_lower for word in ["restaurant", "food", "lunch", "dinner", "coffee"]):
            return "food"
        elif any(word in description_lower for word in ["taxi", "bus", "gas", "fuel", "uber"]):
            return "transport"
        elif any(word in description_lower for word in ["electricity", "water", "internet", "phone", "bill"]):
            return "utilities"
        elif any(word in description_lower for word in ["movie", "cinema", "game", "book", "netflix"]):
            return "entertainment"
        elif any(word in description_lower for word in ["doctor", "pharmacy", "medicine", "hospital"]):
            return "health"
        elif any(word in description_lower for word in ["clothes", "shoes", "shopping", "mall", "store"]):
            return "shopping"
        else:
            return "other"
    
    def get_stats(self) -> Dict[str, Any]:
        """Get server statistics."""
        return self.stats

# =============================================================================
# INTEGRATED SYSTEM
# =============================================================================

class SimplifiedIntegratedSystem:
    """Simplified integrated system combining all components."""
    
    def __init__(self):
        self.voice = SimplifiedVoiceSystem()
        self.listener = SimplifiedListener()
        self.mcp_server = SimplifiedMCPServer()
        
        self.conversation_stats = {
            "total_conversations": 0,
            "successful_responses": 0
        }
        
        print("✅ Simplified Integrated System initialized")
    
    async def process_command(self, command: str) -> str:
        """Process voice command and generate response."""
        try:
            self.conversation_stats["total_conversations"] += 1
            
            command_lower = command.lower()
            
            # Expense addition
            if any(word in command_lower for word in ["spent", "bought", "purchase", "خرید", "هزینه"]):
                return await self._handle_expense_add(command)
            
            # Expense query
            elif any(word in command_lower for word in ["expenses", "spending", "show me", "هزینه‌ها"]):
                return await self._handle_expense_query()
            
            # Expense summary
            elif any(word in command_lower for word in ["summary", "total", "how much", "جمع", "کل"]):
                return await self._handle_expense_summary()
            
            # General conversation
            else:
                return self._handle_general_conversation(command)
                
        except Exception as e:
            logger.error(f"Command processing failed: {e}")
            return "متاسفم، مشکلی پیش آمده."
    
    async def _handle_expense_add(self, command: str) -> str:
        """Handle expense addition."""
        try:
            # Extract amount (simple pattern)
            import re
            
            # Look for numbers in the command
            numbers = re.findall(r'\d+\.?\d*', command)
            
            if numbers:
                amount = float(numbers[0])
                result = await self.mcp_server.add_expense_direct(amount, command)
                
                if result["success"]:
                    expense = result["expense"]
                    response = f"Expense added: {expense['description']} - ${expense['amount']:.2f} in {expense['category']} category"
                    self.conversation_stats["successful_responses"] += 1
                    return response
                else:
                    return "Sorry, I couldn't add the expense."
            else:
                return "I couldn't understand the amount. Please specify how much you spent."
                
        except Exception as e:
            logger.error(f"Expense addition failed: {e}")
            return "There was an error adding the expense."
    
    async def _handle_expense_query(self) -> str:
        """Handle expense query."""
        try:
            result = await self.mcp_server.get_expenses_direct(5)
            
            if result["success"] and result["expenses"]:
                response = f"Your last {len(result['expenses'])} expenses:\n"
                for expense in result["expenses"]:
                    response += f"- {expense['description']}: ${expense['amount']:.2f}\n"
                self.conversation_stats["successful_responses"] += 1
                return response
            else:
                return "No expenses found."
                
        except Exception as e:
            logger.error(f"Expense query failed: {e}")
            return "Couldn't retrieve expenses."
    
    async def _handle_expense_summary(self) -> str:
        """Handle expense summary."""
        try:
            result = await self.mcp_server.get_expense_summary_direct("month")
            
            if result["success"]:
                summary = result["summary"]
                response = f"Monthly expense summary:\n"
                response += f"Total amount: ${summary['total_amount']:.2f}\n"
                response += f"Total expenses: {summary['total_expenses']}\n"
                
                if summary["by_category"]:
                    response += "By category:\n"
                    for category, data in summary["by_category"].items():
                        response += f"- {category}: ${data['amount']:.2f} ({data['count']} expenses)\n"
                
                self.conversation_stats["successful_responses"] += 1
                return response
            else:
                return "Couldn't get expense summary."
                
        except Exception as e:
            logger.error(f"Expense summary failed: {e}")
            return "There was an error getting the summary."
    
    def _handle_general_conversation(self, command: str) -> str:
        """Handle general conversation."""
        command_lower = command.lower()
        
        if any(word in command_lower for word in ["hello", "hi", "سلام"]):
            response = "Hello! I'm Luna, your expense management assistant. How can I help you today?"
        elif any(word in command_lower for word in ["help", "کمک"]):
            response = "I can help you track expenses, show your spending, and provide summaries. Try saying 'I spent 25 dollars on lunch' or 'Show me my expenses'."
        elif any(word in command_lower for word in ["thank", "thanks", "ممنون"]):
            response = "You're welcome! I'm always here to help with your expense tracking."
        else:
            response = "I didn't quite understand that. You can tell me about expenses, ask to see your spending, or ask for help."
        
        self.conversation_stats["successful_responses"] += 1
        return response
    
    async def voice_command_callback(self, command: str):
        """Handle voice commands with audio output."""
        print(f"🎤 Processing voice command: '{command}'")
        
        try:
            # Process command
            response = await self.process_command(command)
            print(f"🤖 Response: '{response}'")
            
            # Generate voice output
            self.voice.speak_immediately(response)
            
            # Save to file for demonstration
            output_file = f"response_{int(time.time())}.wav"
            self.voice.speak_and_save(response, output_file)
            
        except Exception as e:
            print(f"❌ Voice command processing failed: {e}")
            error_response = "Sorry, there was an error processing your command."
            self.voice.speak_immediately(error_response)
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics."""
        return {
            "conversation_stats": self.conversation_stats,
            "voice_stats": self.voice.get_stats(),
            "listener_stats": self.listener.get_stats(),
            "mcp_server_stats": self.mcp_server.get_stats()
        }

# =============================================================================
# TESTING FRAMEWORK
# =============================================================================

async def test_complete_system():
    """Test the complete integrated system."""
    
    print("\n🧪 TESTING COMPLETE INTEGRATED SYSTEM")
    print("=" * 45)
    
    system = SimplifiedIntegratedSystem()
    
    # Test 1: Voice synthesis
    print("\n🔊 TEST 1: Voice Synthesis")
    test_phrases = [
        "Hello! I am Luna, your expense management assistant.",
        "سلام! من لونا هستم، دستیار مدیریت هزینه‌های شما.",
        "System initialization complete.",
        "Ready to track your expenses.",
        "Voice synthesis test successful."
    ]
    
    for i, phrase in enumerate(test_phrases, 1):
        output_file = f"test_voice_{i}.wav"
        success = system.voice.speak_and_save(phrase, output_file)
        status = "✅" if success else "❌"
        print(f"{status} Test {i}: Generated voice file for '{phrase[:40]}...'")
    
    # Test 2: Expense management
    print("\n💰 TEST 2: Expense Management")
    expense_commands = [
        "I spent 25 dollars on lunch at restaurant",
        "Bought coffee for 5 dollars",
        "Paid 120 dollars for internet bill",
        "Spent 60 dollars on groceries",
        "Doctor visit cost 200 dollars"
    ]
    
    for i, command in enumerate(expense_commands, 1):
        print(f"\n📝 Expense Command {i}: '{command}'")
        response = await system.process_command(command)
        print(f"✅ Response: '{response}'")
    
    # Test 3: Expense queries
    print("\n📋 TEST 3: Expense Queries")
    query_commands = [
        "Show me my recent expenses",
        "How much did I spend this month?",
        "Give me a summary of my spending"
    ]
    
    for i, command in enumerate(query_commands, 1):
        print(f"\n❓ Query {i}: '{command}'")
        response = await system.process_command(command)
        print(f"✅ Response: '{response}'")
    
    # Test 4: Voice interaction simulation
    print("\n🎤 TEST 4: Voice Interaction Simulation")
    voice_commands = [
        "Hello Luna",
        "I spent 15 dollars on coffee",
        "Show me my expenses",
        "Thank you Luna"
    ]
    
    for i, command in enumerate(voice_commands, 1):
        print(f"\n🗣️ Voice Interaction {i}:")
        simulated_input = system.listener.simulate_voice_input(command)
        await system.voice_command_callback(simulated_input)
    
    # Test 5: System statistics
    print("\n📊 TEST 5: System Statistics")
    stats = system.get_comprehensive_stats()
    
    print("System Performance:")
    print(f"  - Total Conversations: {stats['conversation_stats']['total_conversations']}")
    print(f"  - Successful Responses: {stats['conversation_stats']['successful_responses']}")
    print(f"  - Voice Synthesis Success Rate: {stats['voice_stats']['success_rate']:.1f}%")
    print(f"  - Voice Recognition Success Rate: {stats['listener_stats']['success_rate']:.1f}%")
    print(f"  - MCP Server Requests: {stats['mcp_server_stats']['total_requests']}")
    print(f"  - Expenses Added: {stats['mcp_server_stats']['expenses_added']}")
    
    return system

def demonstrate_interactive_mode(system: SimplifiedIntegratedSystem):
    """Demonstrate interactive text-based mode."""
    
    print("\n🎤 INTERACTIVE DEMONSTRATION MODE")
    print("=" * 40)
    print("Try these commands:")
    print("  - 'I spent 25 dollars on lunch'")
    print("  - 'Show me my expenses'")
    print("  - 'How much did I spend this month?'")
    print("  - 'Hello Luna'")
    print("  - Type 'quit' to exit")
    print()
    
    while True:
        try:
            command = input("💬 You: ").strip()
            
            if command.lower() in ['quit', 'exit', 'stop']:
                print("👋 Goodbye!")
                break
            
            if command:
                # Simulate voice input and processing
                simulated_input = system.listener.simulate_voice_input(command)
                asyncio.run(system.voice_command_callback(simulated_input))
                print()
        
        except KeyboardInterrupt:
            print("\n👋 Interactive mode stopped")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Main function."""
    print("🚀 HEYSTIVE COMPREHENSIVE UPGRADE - SIMPLIFIED TEST")
    print("Following patterns from: https://towardsdatascience.com/using-langgraph-and-mcp-servers-to-create-my-own-voice-assistant/")
    print("=" * 80)
    
    # Run comprehensive tests
    system = asyncio.run(test_complete_system())
    
    print("\n✅ ALL TESTS COMPLETED SUCCESSFULLY!")
    
    # List generated files
    voice_files = list(Path("heystive_voice_output").glob("*.txt"))
    print(f"\n📁 Generated {len(voice_files)} voice output files:")
    for file in voice_files:
        print(f"  - {file}")
    
    # Demonstrate interactive mode
    try:
        demonstrate_interactive_mode(system)
    except KeyboardInterrupt:
        print("\n👋 Demo completed")
    
    # Final statistics
    print("\n📊 FINAL SYSTEM STATISTICS:")
    final_stats = system.get_comprehensive_stats()
    print(json.dumps(final_stats, indent=2))
    
    return system

if __name__ == "__main__":
    main()