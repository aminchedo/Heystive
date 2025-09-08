#!/usr/bin/env python3
"""
Luna MCP Server - Expense Management
Following the exact pattern from: https://towardsdatascience.com/using-langgraph-and-mcp-servers-to-create-my-own-voice-assistant/

This MCP server provides CRUD operations for expense tracking, similar to the Luna assistant
described in the article. It integrates with the existing Heystive system to add expense
management capabilities.
"""

import asyncio
import logging
import json
import sqlite3
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

# MCP imports (fallback if not available)
try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
    from mcp.server.stdio import stdio_server
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("⚠️ MCP not available, using fallback implementation")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# DATA MODELS
# =============================================================================

class ExpenseCategory(Enum):
    """Expense categories for automatic categorization."""
    FOOD = "food"
    TRANSPORT = "transport"
    UTILITIES = "utilities"
    ENTERTAINMENT = "entertainment"
    HEALTH = "health"
    SHOPPING = "shopping"
    EDUCATION = "education"
    OTHER = "other"

@dataclass
class Expense:
    """Expense data model."""
    id: Optional[int] = None
    amount: float = 0.0
    description: str = ""
    category: str = ExpenseCategory.OTHER.value
    date: str = ""
    created_at: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Expense':
        """Create from dictionary."""
        return cls(**data)

# =============================================================================
# DATABASE MANAGER
# =============================================================================

class ExpenseDatabase:
    """SQLite database manager for expenses."""
    
    def __init__(self, db_path: str = "luna_expenses.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the expense database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS expenses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        amount REAL NOT NULL,
                        description TEXT NOT NULL,
                        category TEXT NOT NULL,
                        date TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    )
                """)
                conn.commit()
            logger.info(f"Expense database initialized: {self.db_path}")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    def add_expense(self, expense: Expense) -> int:
        """Add a new expense."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    INSERT INTO expenses (amount, description, category, date, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    expense.amount,
                    expense.description,
                    expense.category,
                    expense.date or datetime.now().strftime("%Y-%m-%d"),
                    expense.created_at or datetime.now().isoformat()
                ))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Failed to add expense: {e}")
            raise
    
    def get_expenses(self, limit: int = 100, category: Optional[str] = None) -> List[Expense]:
        """Get expenses with optional filtering."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                if category:
                    cursor = conn.execute("""
                        SELECT * FROM expenses WHERE category = ? 
                        ORDER BY created_at DESC LIMIT ?
                    """, (category, limit))
                else:
                    cursor = conn.execute("""
                        SELECT * FROM expenses ORDER BY created_at DESC LIMIT ?
                    """, (limit,))
                
                rows = cursor.fetchall()
                return [Expense(**dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"Failed to get expenses: {e}")
            return []
    
    def update_expense(self, expense_id: int, updates: Dict[str, Any]) -> bool:
        """Update an existing expense."""
        try:
            # Build dynamic update query
            set_clauses = []
            values = []
            
            for field, value in updates.items():
                if field in ['amount', 'description', 'category', 'date']:
                    set_clauses.append(f"{field} = ?")
                    values.append(value)
            
            if not set_clauses:
                return False
            
            values.append(expense_id)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(f"""
                    UPDATE expenses SET {', '.join(set_clauses)} WHERE id = ?
                """, values)
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Failed to update expense: {e}")
            return False
    
    def delete_expense(self, expense_id: int) -> bool:
        """Delete an expense."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Failed to delete expense: {e}")
            return False
    
    def get_expense_summary(self, period: str = "month") -> Dict[str, Any]:
        """Get expense summary by period."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Get date filter based on period
                if period == "day":
                    date_filter = datetime.now().strftime("%Y-%m-%d")
                    date_condition = "date = ?"
                elif period == "week":
                    # Last 7 days
                    from datetime import timedelta
                    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
                    date_condition = "date >= ?"
                    date_filter = week_ago
                elif period == "month":
                    month_filter = datetime.now().strftime("%Y-%m")
                    date_condition = "date LIKE ?"
                    date_filter = f"{month_filter}%"
                else:
                    # All time
                    date_condition = "1=1"
                    date_filter = None
                
                # Get total and by category
                if date_filter:
                    cursor = conn.execute(f"""
                        SELECT 
                            SUM(amount) as total,
                            category,
                            COUNT(*) as count
                        FROM expenses 
                        WHERE {date_condition}
                        GROUP BY category
                    """, (date_filter,))
                else:
                    cursor = conn.execute("""
                        SELECT 
                            SUM(amount) as total,
                            category,
                            COUNT(*) as count
                        FROM expenses 
                        GROUP BY category
                    """)
                
                results = cursor.fetchall()
                
                summary = {
                    "period": period,
                    "total_amount": 0.0,
                    "total_expenses": 0,
                    "by_category": {}
                }
                
                for row in results:
                    summary["total_amount"] += row["total"] or 0
                    summary["total_expenses"] += row["count"] or 0
                    summary["by_category"][row["category"]] = {
                        "amount": row["total"] or 0,
                        "count": row["count"] or 0
                    }
                
                return summary
                
        except Exception as e:
            logger.error(f"Failed to get expense summary: {e}")
            return {"error": str(e)}

# =============================================================================
# EXPENSE CATEGORIZER
# =============================================================================

class ExpenseCategorizer:
    """Automatic expense categorization using keywords."""
    
    def __init__(self):
        self.category_keywords = {
            ExpenseCategory.FOOD: [
                "restaurant", "food", "grocery", "coffee", "lunch", "dinner", "breakfast",
                "رستوران", "غذا", "ناهار", "شام", "صبحانه", "قهوه", "کافه", "سوپرمارکت"
            ],
            ExpenseCategory.TRANSPORT: [
                "taxi", "bus", "metro", "gas", "fuel", "parking", "uber", "lyft",
                "تاکسی", "اتوبوس", "مترو", "بنزین", "سوخت", "پارکینگ", "اسنپ"
            ],
            ExpenseCategory.UTILITIES: [
                "electricity", "water", "gas", "internet", "phone", "bill",
                "برق", "آب", "گاز", "اینترنت", "تلفن", "قبض"
            ],
            ExpenseCategory.ENTERTAINMENT: [
                "movie", "cinema", "concert", "game", "book", "music", "netflix",
                "فیلم", "سینما", "کنسرت", "بازی", "کتاب", "موسیقی"
            ],
            ExpenseCategory.HEALTH: [
                "doctor", "pharmacy", "medicine", "hospital", "dental", "medical",
                "دکتر", "داروخانه", "دارو", "بیمارستان", "دندانپزشک", "پزشکی"
            ],
            ExpenseCategory.SHOPPING: [
                "clothes", "shoes", "shopping", "mall", "store", "amazon",
                "لباس", "کفش", "خرید", "فروشگاه", "مغازه"
            ],
            ExpenseCategory.EDUCATION: [
                "school", "university", "course", "book", "tuition", "education",
                "مدرسه", "دانشگاه", "کورس", "آموزش", "شهریه"
            ]
        }
    
    def categorize(self, description: str) -> str:
        """Categorize expense based on description."""
        description_lower = description.lower()
        
        # Check each category for keyword matches
        for category, keywords in self.category_keywords.items():
            if any(keyword in description_lower for keyword in keywords):
                return category.value
        
        return ExpenseCategory.OTHER.value

# =============================================================================
# MCP SERVER IMPLEMENTATION
# =============================================================================

class LunaMCPServer:
    """Luna MCP Server for expense management."""
    
    def __init__(self):
        self.db = ExpenseDatabase()
        self.categorizer = ExpenseCategorizer()
        
        # Server stats
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "expenses_added": 0,
            "expenses_queried": 0
        }
        
        if MCP_AVAILABLE:
            self.server = Server("luna-expense-server")
            self._register_tools()
        else:
            self.server = None
            logger.warning("MCP not available, using direct function calls")
    
    def _register_tools(self):
        """Register MCP tools."""
        if not self.server:
            return
        
        # Add Expense Tool
        @self.server.call_tool()
        async def add_expense(amount: float, description: str, category: str = "") -> List[TextContent]:
            """Add a new expense to the database."""
            try:
                self.stats["total_requests"] += 1
                
                # Auto-categorize if not provided
                if not category:
                    category = self.categorizer.categorize(description)
                
                expense = Expense(
                    amount=amount,
                    description=description,
                    category=category,
                    date=datetime.now().strftime("%Y-%m-%d"),
                    created_at=datetime.now().isoformat()
                )
                
                expense_id = self.db.add_expense(expense)
                expense.id = expense_id
                
                self.stats["successful_requests"] += 1
                self.stats["expenses_added"] += 1
                
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "expense_id": expense_id,
                        "expense": expense.to_dict(),
                        "message": f"Added expense: {description} - ${amount:.2f} ({category})"
                    })
                )]
                
            except Exception as e:
                logger.error(f"Failed to add expense: {e}")
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": str(e)
                    })
                )]
        
        # Get Expenses Tool
        @self.server.call_tool()
        async def get_expenses(limit: int = 10, category: str = "") -> List[TextContent]:
            """Get recent expenses from the database."""
            try:
                self.stats["total_requests"] += 1
                
                expenses = self.db.get_expenses(
                    limit=limit,
                    category=category if category else None
                )
                
                self.stats["successful_requests"] += 1
                self.stats["expenses_queried"] += len(expenses)
                
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "expenses": [expense.to_dict() for expense in expenses],
                        "count": len(expenses)
                    })
                )]
                
            except Exception as e:
                logger.error(f"Failed to get expenses: {e}")
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": str(e)
                    })
                )]
        
        # Get Expense Summary Tool
        @self.server.call_tool()
        async def get_expense_summary(period: str = "month") -> List[TextContent]:
            """Get expense summary for a specific period."""
            try:
                self.stats["total_requests"] += 1
                
                summary = self.db.get_expense_summary(period)
                
                self.stats["successful_requests"] += 1
                
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "summary": summary
                    })
                )]
                
            except Exception as e:
                logger.error(f"Failed to get expense summary: {e}")
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": str(e)
                    })
                )]
        
        # Update Expense Tool
        @self.server.call_tool()
        async def update_expense(expense_id: int, **updates) -> List[TextContent]:
            """Update an existing expense."""
            try:
                self.stats["total_requests"] += 1
                
                success = self.db.update_expense(expense_id, updates)
                
                if success:
                    self.stats["successful_requests"] += 1
                
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": success,
                        "expense_id": expense_id,
                        "updates": updates,
                        "message": "Expense updated successfully" if success else "Expense not found"
                    })
                )]
                
            except Exception as e:
                logger.error(f"Failed to update expense: {e}")
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": str(e)
                    })
                )]
        
        # Delete Expense Tool
        @self.server.call_tool()
        async def delete_expense(expense_id: int) -> List[TextContent]:
            """Delete an expense from the database."""
            try:
                self.stats["total_requests"] += 1
                
                success = self.db.delete_expense(expense_id)
                
                if success:
                    self.stats["successful_requests"] += 1
                
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": success,
                        "expense_id": expense_id,
                        "message": "Expense deleted successfully" if success else "Expense not found"
                    })
                )]
                
            except Exception as e:
                logger.error(f"Failed to delete expense: {e}")
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": str(e)
                    })
                )]
    
    # Direct function call methods (fallback when MCP not available)
    async def add_expense_direct(self, amount: float, description: str, category: str = "") -> Dict[str, Any]:
        """Direct function call to add expense."""
        try:
            self.stats["total_requests"] += 1
            
            if not category:
                category = self.categorizer.categorize(description)
            
            expense = Expense(
                amount=amount,
                description=description,
                category=category,
                date=datetime.now().strftime("%Y-%m-%d"),
                created_at=datetime.now().isoformat()
            )
            
            expense_id = self.db.add_expense(expense)
            expense.id = expense_id
            
            self.stats["successful_requests"] += 1
            self.stats["expenses_added"] += 1
            
            return {
                "success": True,
                "expense_id": expense_id,
                "expense": expense.to_dict(),
                "message": f"Added expense: {description} - ${amount:.2f} ({category})"
            }
            
        except Exception as e:
            logger.error(f"Failed to add expense: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_expenses_direct(self, limit: int = 10, category: str = "") -> Dict[str, Any]:
        """Direct function call to get expenses."""
        try:
            self.stats["total_requests"] += 1
            
            expenses = self.db.get_expenses(
                limit=limit,
                category=category if category else None
            )
            
            self.stats["successful_requests"] += 1
            self.stats["expenses_queried"] += len(expenses)
            
            return {
                "success": True,
                "expenses": [expense.to_dict() for expense in expenses],
                "count": len(expenses)
            }
            
        except Exception as e:
            logger.error(f"Failed to get expenses: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_expense_summary_direct(self, period: str = "month") -> Dict[str, Any]:
        """Direct function call to get expense summary."""
        try:
            self.stats["total_requests"] += 1
            
            summary = self.db.get_expense_summary(period)
            
            self.stats["successful_requests"] += 1
            
            return {
                "success": True,
                "summary": summary
            }
            
        except Exception as e:
            logger.error(f"Failed to get expense summary: {e}")
            return {"success": False, "error": str(e)}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get server statistics."""
        return {
            **self.stats,
            "mcp_available": MCP_AVAILABLE,
            "database_path": self.db.db_path
        }
    
    async def run_server(self):
        """Run the MCP server."""
        if self.server:
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options()
                )
        else:
            logger.warning("MCP server not available, running in direct mode")

# =============================================================================
# TESTING AND DEMONSTRATION
# =============================================================================

async def test_luna_mcp_server():
    """Test the Luna MCP server functionality."""
    
    print("\n🧪 TESTING LUNA MCP SERVER")
    print("=" * 35)
    
    server = LunaMCPServer()
    
    # Test 1: Add expenses
    print("\n📝 TEST 1: Adding Expenses")
    test_expenses = [
        {"amount": 25.50, "description": "Lunch at Persian restaurant"},
        {"amount": 60.00, "description": "Grocery shopping at supermarket"},
        {"amount": 15.00, "description": "Coffee and pastry"},
        {"amount": 120.00, "description": "Monthly internet bill"},
        {"amount": 45.00, "description": "Gas for car"},
        {"amount": 200.00, "description": "Doctor visit"},
        {"amount": 80.00, "description": "New shoes from mall"}
    ]
    
    for expense_data in test_expenses:
        result = await server.add_expense_direct(**expense_data)
        if result["success"]:
            expense = result["expense"]
            print(f"✅ Added: {expense['description']} - ${expense['amount']:.2f} ({expense['category']})")
        else:
            print(f"❌ Failed to add: {expense_data}")
    
    # Test 2: Get expenses
    print("\n📋 TEST 2: Retrieving Expenses")
    result = await server.get_expenses_direct(limit=5)
    if result["success"]:
        print(f"✅ Retrieved {result['count']} expenses:")
        for expense in result["expenses"]:
            print(f"   - {expense['description']}: ${expense['amount']:.2f} ({expense['category']})")
    else:
        print(f"❌ Failed to retrieve expenses: {result.get('error')}")
    
    # Test 3: Get expenses by category
    print("\n🍽️ TEST 3: Food Expenses")
    result = await server.get_expenses_direct(category="food")
    if result["success"]:
        print(f"✅ Retrieved {result['count']} food expenses:")
        for expense in result["expenses"]:
            print(f"   - {expense['description']}: ${expense['amount']:.2f}")
    else:
        print(f"❌ Failed to retrieve food expenses: {result.get('error')}")
    
    # Test 4: Get expense summary
    print("\n📊 TEST 4: Expense Summary")
    result = await server.get_expense_summary_direct("month")
    if result["success"]:
        summary = result["summary"]
        print(f"✅ Monthly Summary:")
        print(f"   - Total Amount: ${summary['total_amount']:.2f}")
        print(f"   - Total Expenses: {summary['total_expenses']}")
        print(f"   - By Category:")
        for category, data in summary["by_category"].items():
            print(f"     {category}: ${data['amount']:.2f} ({data['count']} expenses)")
    else:
        print(f"❌ Failed to get summary: {result.get('error')}")
    
    # Test 5: Server stats
    print("\n📈 TEST 5: Server Statistics")
    stats = server.get_stats()
    print(f"✅ Server Stats:")
    print(f"   - Total Requests: {stats['total_requests']}")
    print(f"   - Successful Requests: {stats['successful_requests']}")
    print(f"   - Expenses Added: {stats['expenses_added']}")
    print(f"   - Expenses Queried: {stats['expenses_queried']}")
    print(f"   - MCP Available: {stats['mcp_available']}")
    
    return server

def main():
    """Main function for testing."""
    print("🚀 LUNA MCP SERVER - EXPENSE MANAGEMENT")
    print("Following patterns from TDS article")
    print("=" * 50)
    
    # Run tests
    server = asyncio.run(test_luna_mcp_server())
    
    print("\n✅ LUNA MCP SERVER TESTING COMPLETE")
    print(f"Database created: {server.db.db_path}")
    
    return server

if __name__ == "__main__":
    main()