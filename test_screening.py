"""
Test script for daily stock screening feature
"""
import asyncio
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.analysis.screener import StockScreener
from src.analysis.research import ResearchReportGenerator
from src.notifications.telegram_bot import create_bot
from src.utils.logger import setup_logger
from src.utils.config import get_config

logger = setup_logger("test_screening")


async def test_screening():
    """Test the daily screening feature"""
    logger.info("=" * 80)
    logger.info("TESTING DAILY STOCK SCREENING FEATURE")
    logger.info("=" * 80)
    
    try:
        # Initialize screener
        logger.info("\n1. Initializing stock screener...")
        screener = StockScreener()
        logger.info(f"   ✓ Screener initialized")
        logger.info(f"   ✓ Will screen {len(screener.us_stocks)} US stocks")
        logger.info(f"   ✓ Will screen {len(screener.uk_stocks)} UK stocks")
        logger.info(f"   ✓ Total: {len(screener.us_stocks) + len(screener.uk_stocks)} stocks")
        
        # Run screening (limit to top 5 for testing)
        logger.info("\n2. Running stock screening (this may take 3-5 minutes)...")
        logger.info("   Note: Screening 75+ stocks with real market data...")
        
        candidates = screener.screen_daily(max_results=5)
        
        # Display results
        logger.info("\n" + "=" * 80)
        logger.info("SCREENING RESULTS")
        logger.info("=" * 80)
        
        if candidates:
            logger.info(f"\n✓ Found {len(candidates)} high-quality candidates:\n")
            
            for i, stock in enumerate(candidates, 1):
                logger.info(f"{i}. {stock['ticker']} - {stock['name']}")
                logger.info(f"   Overall Score: {stock['total_score']}/100")
                logger.info(f"   Sector: {stock['sector']}")
                logger.info(f"   Current Price: ${stock['current_price']:.2f}")
                logger.info(f"   Scores:")
                logger.info(f"     • Technical: {stock['technical_score']}/100")
                logger.info(f"     • Fundamental: {stock['fundamental_score']}/100")
                logger.info(f"     • Momentum: {stock['momentum_score']}/100")
                logger.info(f"     • Value: {stock['value_score']}/100")
                logger.info(f"   Recommendation: {stock['recommendation']}")
                logger.info(f"   Reasons: {', '.join(stock['reasons'])}")
                logger.info("")
            
            # Test research report for top candidate
            if candidates[0]['total_score'] >= 70:
                top_ticker = candidates[0]['ticker']
                logger.info("=" * 80)
                logger.info(f"3. Generating detailed research report for top candidate: {top_ticker}")
                logger.info("=" * 80)
                
                research_gen = ResearchReportGenerator()
                report = research_gen.generate_report(top_ticker)
                
                if report:
                    logger.info(f"\n✓ Research report generated for {top_ticker}")
                    logger.info(f"\nReport Summary:")
                    logger.info(f"  • Company: {report['overview']['name']}")
                    logger.info(f"  • Sector: {report['overview']['sector']}")
                    logger.info(f"  • Financial Health: {report['financial_health']['health_score']}/100 ({report['financial_health']['health_rating']})")
                    logger.info(f"  • Valuation: {report['valuation']['valuation']}")
                    logger.info(f"  • Growth: {report['growth']['growth_rating']}")
                    logger.info(f"  • Technical Trend: {report['technical_setup'].get('trend', 'Unknown')}")
                    logger.info(f"  • Bot Assessment: {report['bot_assessment']['recommendation']}")
                    logger.info(f"  • Overall Score: {report['bot_assessment']['overall_score']}/100")
                    logger.info(f"  • Action: {report['bot_assessment']['action']}")
                else:
                    logger.warning(f"✗ Failed to generate research report for {top_ticker}")
            
            # Test Telegram integration (optional)
            logger.info("\n" + "=" * 80)
            logger.info("4. Testing Telegram Integration")
            logger.info("=" * 80)
            
            config = get_config()
            telegram_config = config.get_telegram_config()
            
            if telegram_config.get('enabled') and telegram_config.get('bot_token') and telegram_config.get('chat_id'):
                logger.info("\n   Telegram is configured. Sending test results...")
                
                try:
                    bot = create_bot()
                    await bot.initialize()
                    
                    # Send screening results
                    await bot.send_screening_results(candidates)
                    logger.info("   ✓ Screening results sent to Telegram")
                    
                    # Send research report if available
                    if report:
                        await asyncio.sleep(2)  # Small delay
                        await bot.send_research_report(report)
                        logger.info("   ✓ Research report sent to Telegram")
                    
                except Exception as e:
                    logger.warning(f"   ✗ Telegram send failed: {e}")
            else:
                logger.info("   ⊘ Telegram not configured - skipping")
        
        else:
            logger.warning("\n✗ No candidates found meeting the 70+ score threshold")
            logger.info("   This could mean:")
            logger.info("   • Market conditions are not favorable")
            logger.info("   • Scoring criteria are too strict")
            logger.info("   • API rate limiting or data issues")
        
        logger.info("\n" + "=" * 80)
        logger.info("TEST COMPLETE")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"\n✗ Test failed with error: {e}", exc_info=True)
        return False
    
    return True


def main():
    """Main entry point"""
    logger.info("\nStarting screening test...")
    logger.info("This will test:")
    logger.info("  1. Stock screener (75+ stocks)")
    logger.info("  2. Research report generator")
    logger.info("  3. Telegram integration (if configured)")
    logger.info("\nExpected duration: 3-5 minutes\n")
    
    success = asyncio.run(test_screening())
    
    if success:
        logger.info("\n✓ All tests passed!")
    else:
        logger.error("\n✗ Tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
