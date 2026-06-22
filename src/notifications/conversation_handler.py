"""
Conversational AI Handler for StockPilot
Supports multiple FREE AI APIs with automatic fallback:
1. Groq (llama-3.3-70b-versatile) - BEST & FASTEST - 30 req/min free
2. Google Gemini (gemini-2.0-flash-exp) - EXCELLENT - 1500 req/day free
3. OpenRouter (meta-llama/llama-3.1-8b-instruct:free) - GOOD - Unlimited free

Phase 5 Feature - 100% FREE AI
"""
import os
from typing import Dict, Optional
from datetime import datetime
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

# Try to import AI libraries
GROQ_AVAILABLE = False
GOOGLE_AVAILABLE = False
OPENROUTER_AVAILABLE = False

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    pass

try:
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
except ImportError:
    pass

try:
    import requests
    OPENROUTER_AVAILABLE = True
except ImportError:
    pass


class ConversationHandler:
    """Handle natural language conversations with trading context using FREE AI APIs"""
    
    def __init__(self, groq_key: Optional[str] = None, google_key: Optional[str] = None, 
                 openrouter_key: Optional[str] = None):
        """
        Initialize conversation handler with multiple free AI options
        
        Args:
            groq_key: Groq API key (free from https://console.groq.com/)
            google_key: Google AI API key (free from https://aistudio.google.com/)
            openrouter_key: OpenRouter API key (free from https://openrouter.ai/)
        """
        # API keys
        self.groq_key = groq_key or os.getenv('GROQ_API_KEY')
        self.google_key = google_key or os.getenv('GOOGLE_API_KEY')
        self.openrouter_key = openrouter_key or os.getenv('OPENROUTER_API_KEY')
        
        # Clients
        self.groq_client = None
        self.google_model = None
        self.openrouter_available = False
        
        # Initialize available clients
        self._initialize_clients()
        
        # Track which AI is being used
        self.active_provider = None
    
    def _initialize_clients(self):
        """Initialize all available AI clients"""
        
        # 1. Try Groq (BEST - llama-3.3-70b-versatile, 30 req/min free)
        if GROQ_AVAILABLE and self.groq_key:
            try:
                self.groq_client = Groq(api_key=self.groq_key)
                self.active_provider = "Groq (llama-3.3-70b)"
                logger.info("✅ Groq AI initialized (BEST - 70B model, 30 req/min)")
                return
            except Exception as e:
                logger.warning(f"Groq initialization failed: {e}")
        
        # 2. Try Google Gemini (EXCELLENT - gemini-1.5-pro, 1500 req/day free)
        if GOOGLE_AVAILABLE and self.google_key:
            try:
                genai.configure(api_key=self.google_key)
                # Try gemini-1.5-pro first, fallback to gemini-pro
                try:
                    self.google_model = genai.GenerativeModel('gemini-1.5-pro')
                    self.active_provider = "Google Gemini 1.5 Pro"
                except:
                    self.google_model = genai.GenerativeModel('gemini-pro')
                    self.active_provider = "Google Gemini Pro"
                logger.info("✅ Google Gemini AI initialized (EXCELLENT - 1500 req/day)")
                return
            except Exception as e:
                logger.warning(f"Google Gemini initialization failed: {e}")
        
        # 3. Try OpenRouter (GOOD - llama-3.1-8b, unlimited free)
        if OPENROUTER_AVAILABLE and self.openrouter_key:
            self.openrouter_available = True
            self.active_provider = "OpenRouter (llama-3.1-8b)"
            logger.info("✅ OpenRouter AI initialized (GOOD - unlimited free)")
            return
        
        # No AI available
        logger.warning("⚠️ No AI providers available. Install packages:")
        logger.warning("  pip install groq google-generativeai requests")
        logger.warning("  Get free API keys:")
        logger.warning("  - Groq: https://console.groq.com/ (BEST)")
        logger.warning("  - Google: https://aistudio.google.com/ (EXCELLENT)")
        logger.warning("  - OpenRouter: https://openrouter.ai/ (GOOD)")
    
    def is_available(self) -> bool:
        """Check if any conversational AI is available"""
        return (self.groq_client is not None or 
                self.google_model is not None or 
                self.openrouter_available)
    
    async def handle_message(self, message: str, context: Dict) -> str:
        """
        Handle a conversational message with trading context
        
        Args:
            message: User's message
            context: Trading context (portfolio, trades, performance, etc.)
            
        Returns:
            AI-generated response
        """
        if not self.is_available():
            return self._fallback_response(message, context)
        
        try:
            # Build system prompt with trading context
            system_prompt = self._build_system_prompt(context)
            
            # Try Groq first (BEST)
            if self.groq_client:
                return await self._call_groq(message, system_prompt)
            
            # Try Google Gemini second (EXCELLENT)
            elif self.google_model:
                return await self._call_google(message, system_prompt)
            
            # Try OpenRouter third (GOOD)
            elif self.openrouter_available:
                return await self._call_openrouter(message, system_prompt)
            
            # Fallback
            return self._fallback_response(message, context)
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return self._fallback_response(message, context)
    
    async def _call_groq(self, message: str, system_prompt: str) -> str:
        """Call Groq API (BEST - llama-3.3-70b-versatile)"""
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # Best free model
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                temperature=0.7,
                max_tokens=1000,
                top_p=1,
                stream=False
            )
            
            ai_response = response.choices[0].message.content
            logger.info(f"✅ Groq response generated for: {message[:50]}...")
            return ai_response
            
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            # Try next provider
            if self.google_model:
                return await self._call_google(message, system_prompt)
            elif self.openrouter_available:
                return await self._call_openrouter(message, system_prompt)
            raise
    
    async def _call_google(self, message: str, system_prompt: str) -> str:
        """Call Google Gemini API (EXCELLENT - gemini-1.5-pro)"""
        try:
            # Combine system prompt and message for Gemini
            full_prompt = f"{system_prompt}\n\nUser: {message}\n\nAssistant:"
            
            # Use the correct generation config
            response = self.google_model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=1000,
                )
            )
            
            ai_response = response.text
            logger.info(f"✅ Google Gemini response generated for: {message[:50]}...")
            return ai_response
            
        except Exception as e:
            logger.error(f"Google Gemini API error: {e}")
            # Try next provider
            if self.openrouter_available:
                return await self._call_openrouter(message, system_prompt)
            raise
    
    async def _call_openrouter(self, message: str, system_prompt: str) -> str:
        """Call OpenRouter API (GOOD - llama-3.1-8b-instruct:free)"""
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openrouter_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "meta-llama/llama-3.1-8b-instruct:free",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": message}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                timeout=30
            )
            
            response.raise_for_status()
            ai_response = response.json()['choices'][0]['message']['content']
            logger.info(f"✅ OpenRouter response generated for: {message[:50]}...")
            return ai_response
            
        except Exception as e:
            logger.error(f"OpenRouter API error: {e}")
            raise
    
    def _build_system_prompt(self, context: Dict) -> str:
        """Build system prompt with trading context"""
        
        # Extract context data
        portfolio = context.get('portfolio', {})
        recent_trades = context.get('recent_trades', [])
        performance = context.get('performance', {})
        strategies = context.get('strategies', {})
        preferences = context.get('preferences', {})
        
        prompt = f"""You are StockPilot AI, a professional trading assistant helping a trader manage their portfolio.

CURRENT DATE: {datetime.now().strftime('%Y-%m-%d %H:%M')}

PERSONALITY:
- Professional but friendly
- Data-driven and analytical
- Encouraging but realistic
- Provide specific numbers and insights
- Use emojis sparingly but effectively
- Keep responses concise (under 300 words)

USER'S PORTFOLIO:
"""
        
        # Add portfolio info
        if portfolio:
            prompt += f"""
• Open Positions: {portfolio.get('open_trades', 0)}
• Total Value: ${portfolio.get('total_value', 0):,.2f}
• Unrealized P&L: ${portfolio.get('unrealized_pnl', 0):+,.2f} ({portfolio.get('unrealized_pnl_percent', 0):+.1f}%)
"""
        
        # Add performance info
        if performance:
            prompt += f"""
PERFORMANCE METRICS:
• Total Trades: {performance.get('total_trades', 0)}
• Win Rate: {performance.get('win_rate', 0):.1f}%
• Total P&L: ${performance.get('total_pnl', 0):+,.2f}
• Average Profit: ${performance.get('avg_profit', 0):.2f}
• Average Loss: ${performance.get('avg_loss', 0):.2f}
• Best Trade: ${performance.get('best_trade', 0):+,.2f}
• Worst Trade: ${performance.get('worst_trade', 0):+,.2f}
"""
        
        # Add recent trades
        if recent_trades:
            prompt += f"\nRECENT TRADES (Last 5):\n"
            for i, trade in enumerate(recent_trades[:5], 1):
                status = "🟢" if trade.get('pnl', 0) > 0 else "🔴"
                prompt += f"{i}. {status} {trade.get('ticker', 'N/A')} - ${trade.get('pnl', 0):+,.2f} ({trade.get('pnl_percent', 0):+.1f}%)\n"
        
        # Add strategy performance
        if strategies:
            prompt += f"\nSTRATEGY PERFORMANCE:\n"
            for strategy, stats in strategies.items():
                prompt += f"• {strategy}: {stats.get('win_rate', 0):.1f}% win rate, {stats.get('trades', 0)} trades\n"
        
        # Add user preferences
        if preferences:
            prompt += f"\nUSER PREFERENCES:\n"
            if preferences.get('favorite_strategy'):
                prompt += f"• Favorite Strategy: {preferences.get('favorite_strategy')}\n"
            if preferences.get('min_confidence'):
                prompt += f"• Min Confidence: {preferences.get('min_confidence')}%\n"
            if preferences.get('risk_tolerance'):
                prompt += f"• Risk Tolerance: {preferences.get('risk_tolerance')}\n"
        
        prompt += """
GUIDELINES:
1. Answer questions based on the data provided above
2. If asked about specific stocks, provide analysis if you have market knowledge
3. Suggest relevant commands when appropriate (e.g., "/portfolio", "/trades", "/research TICKER")
4. Be encouraging about wins, constructive about losses
5. Focus on learning and improvement
6. If you don't have specific data, say so honestly
7. Use markdown formatting for better readability

AVAILABLE COMMANDS YOU CAN SUGGEST:
• /status - Bot status
• /portfolio - Portfolio summary
• /trades - Open trades
• /performance - Detailed stats
• /research TICKER - Company analysis
• /watchlist - User's watchlist
• /learn - Trigger learning
• /optimize - Optimize strategies
• /help - All commands

Remember: You're helping a real trader make real money. Be accurate, helpful, and professional.
"""
        
        return prompt
    
    def _fallback_response(self, message: str, context: Dict) -> str:
        """Fallback response when AI is not available"""
        
        message_lower = message.lower()
        
        # Portfolio queries
        if any(word in message_lower for word in ['portfolio', 'positions', 'holdings']):
            portfolio = context.get('portfolio', {})
            return f"""📊 **Portfolio Summary**

• Open Positions: {portfolio.get('open_trades', 0)}
• Total Value: ${portfolio.get('total_value', 0):,.2f}
• Unrealized P&L: ${portfolio.get('unrealized_pnl', 0):+,.2f}

Use /portfolio for detailed view or /trades for open positions."""
        
        # Performance queries
        elif any(word in message_lower for word in ['performance', 'stats', 'results']):
            performance = context.get('performance', {})
            return f"""📈 **Performance Stats**

• Win Rate: {performance.get('win_rate', 0):.1f}%
• Total Trades: {performance.get('total_trades', 0)}
• Total P&L: ${performance.get('total_pnl', 0):+,.2f}

Use /performance for detailed analytics."""
        
        # Help queries
        elif any(word in message_lower for word in ['help', 'commands', 'what can you do']):
            return """🤖 **I'm your StockPilot AI assistant!**

I can help you with:
• Portfolio analysis and insights
• Trade performance review
• Strategy recommendations
• Stock research and analysis

**Available Commands:**
• /status - Check bot status
• /portfolio - View portfolio
• /trades - See open trades
• /performance - Detailed stats
• /research TICKER - Analyze stocks
• /help - All commands

Just ask me anything about your trading!"""
        
        # Default response
        else:
            return f"""I'm here to help! You can ask me about:

• Your portfolio and positions
• Trading performance and stats
• Specific stocks or strategies
• Any trading-related questions

Or use commands like /portfolio, /trades, /performance

**Note:** For full AI conversations, set up a free API key:
• Groq (BEST): https://console.groq.com/
• Google (EXCELLENT): https://aistudio.google.com/
• OpenRouter (GOOD): https://openrouter.ai/

Current provider: {self.active_provider or 'None - using fallback'}"""
    
    def _extract_ticker(self, message: str) -> Optional[str]:
        """Extract ticker symbol from message"""
        import re
        # Look for 1-5 uppercase letters
        match = re.search(r'\b([A-Z]{1,5})\b', message)
        return match.group(1) if match else None


def create_conversation_handler(groq_key: Optional[str] = None,
                                google_key: Optional[str] = None,
                                openrouter_key: Optional[str] = None) -> ConversationHandler:
    """
    Create a conversation handler instance
    
    Args:
        groq_key: Groq API key (optional, will use env var if not provided)
        google_key: Google AI API key (optional, will use env var if not provided)
        openrouter_key: OpenRouter API key (optional, will use env var if not provided)
        
    Returns:
        ConversationHandler instance
    """
    return ConversationHandler(groq_key=groq_key, google_key=google_key, openrouter_key=openrouter_key)
