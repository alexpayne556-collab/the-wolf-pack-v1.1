"""
🐺 MASTER WOLF PACK SYSTEM 🐺

ONE COMMAND TO RUN EVERYTHING

This master script orchestrates all Wolf Pack modules:
- Autonomous brain (24/7 trading)
- Strategy coordinator (multi-strategy)
- Dashboard (real-time view)
- All scanners (biotech, premarket, compression, etc.)

USAGE:
    python master.py                    # Run full autonomous system
    python master.py --dashboard-only   # Just show dashboard
    python master.py --scan-now         # Run all scanners now
    python master.py --report           # Generate full intel report
    python master.py --test-setup       # Test all connections

AUTONOMOUS FEATURES:
✅ Auto-execute paper trades when confidence is high
✅ Learn from losses automatically
✅ Multi-strategy coordination
✅ Risk management (max 5 positions, max 3 biotech)
✅ 24/7 operation with smart sleep schedules
✅ All free data sources (Finnhub, NewsAPI, Polygon, Alpha Vantage, SEC)
"""

import sys
import argparse
import logging
import time
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from autonomous_brain import AutonomousBrain
from dashboard import WolfDashboard
from strategy_coordinator import StrategyCoordinator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)

log = logging.getLogger('Master')


def print_banner():
    """Print the Wolf Pack banner"""
    print("""
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║          🐺 M A S T E R   W O L F   P A C K   S Y S T E M 🐺          ║
║                                                                       ║
║                    ONE SYSTEM TO RULE THEM ALL                        ║
║                                                                       ║
║  ┌─────────────────────────────────────────────────────────────────┐ ║
║  │ AUTONOMOUS FEATURES:                                            │ ║
║  │ ✅ Auto-execute paper trades (70%+ confidence)                  │ ║
║  │ ✅ Learn from losses automatically                              │ ║
║  │ ✅ Multi-strategy coordination                                  │ ║
║  │ ✅ 24/7 operation with smart schedules                          │ ║
║  │ ✅ All free data sources integrated                             │ ║
║  │ ✅ Risk management (5 positions max, 3 biotech max)             │ ║
║  └─────────────────────────────────────────────────────────────────┘ ║
║                                                                       ║
║  STRATEGIES:                                                          ║
║  • PDUFA Runup (7-14 day window before FDA decisions)                ║
║  • Insider Buying (Follow smart money)                               ║
║  • Compression Breakout (Flat + catalyst)                            ║
║  • Gap and Go (Premarket runners)                                    ║
║  • Wounded Prey (Oversold + catalyst)                                ║
║  • Head Hunter (Low float + squeeze)                                 ║
║                                                                       ║
║  DATA SOURCES:                                                        ║
║  • Finnhub (News + Insider trades)                                   ║
║  • NewsAPI (Breaking news)                                           ║
║  • Polygon (Fundamentals + News)                                     ║
║  • Alpha Vantage (PE ratios + Analyst targets)                       ║
║  • SEC Edgar (Form 4 insider transactions)                           ║
║  • yfinance (Price data)                                             ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
    """)


def run_dashboard_only():
    """Just display the dashboard"""
    print_banner()
    print("\n📊 DASHBOARD MODE\n")
    
    dashboard = WolfDashboard()
    output = dashboard.render_terminal_dashboard()
    print(output)
    
    dashboard.save_dashboard_to_file()


def run_scan_now(brain: AutonomousBrain):
    """Run all scanners immediately"""
    print_banner()
    print("\n🔍 RUNNING ALL SCANNERS NOW\n")
    
    log.info("1️⃣  Scanning biotech catalysts...")
    biotech_opps = brain.scan_biotech_catalysts()
    
    log.info("\n2️⃣  Scanning premarket gainers...")
    gainers = brain.scan_real_premarket_gainers()
    
    log.info("\n3️⃣  Generating intel report...")
    report = brain.generate_intel_report()
    
    print("\n✅ All scans complete!")
    print(f"   • Biotech opportunities: {len(biotech_opps.get('pdufa_runup_plays', []))} PDUFA plays")
    print(f"   • Premarket gainers: {len(gainers)} tickers")
    print(f"   • Intel report saved to: data/wolf_brain/LATEST_INTEL_REPORT.txt")


def test_setup(brain: AutonomousBrain):
    """Test all connections and APIs"""
    print_banner()
    print("\n🧪 TESTING SYSTEM SETUP\n")
    
    # Check Alpaca
    if brain.alpaca_connected:
        print("✅ Alpaca Paper Trading: CONNECTED")
        try:
            account = brain.trading_client.get_account()
            print(f"   Portfolio: ${float(account.portfolio_value):,.2f}")
            print(f"   Buying Power: ${float(account.buying_power):,.2f}")
        except Exception as e:
            print(f"   ⚠️  Could not fetch account: {e}")
    else:
        print("❌ Alpaca: NOT CONNECTED")
    
    # Check Ollama
    if brain.ollama_connected:
        print("✅ Ollama (Fenrir): CONNECTED")
        # Model name stored in config, not as attribute
    else:
        print("❌ Ollama: NOT CONNECTED")
    
    # Check modules
    if brain.biotech_scanner:
        print("✅ Biotech Catalyst Scanner: LOADED")
        catalysts = brain.biotech_scanner.get_upcoming_catalysts(days_ahead=14)
        print(f"   Upcoming catalysts: {len(catalysts)}")
    else:
        print("❌ Biotech Scanner: NOT LOADED")
    
    # Test APIs
    print("\n🔌 Testing APIs...")
    test_ticker = "AAPL"
    
    try:
        news = brain._get_news(test_ticker)
        print(f"✅ News APIs: {len(news)} articles fetched")
    except Exception as e:
        print(f"❌ News APIs: {e}")
    
    try:
        polygon_data = brain._get_polygon_data(test_ticker)
        if polygon_data:
            print("✅ Polygon API: Working")
    except:
        print("⚠️  Polygon API: Issue")
    
    try:
        av_data = brain._get_alpha_vantage_data(test_ticker)
        if av_data:
            print("✅ Alpha Vantage API: Working")
    except:
        print("⚠️  Alpha Vantage API: Issue")
    
    print("\n📊 System Status:")
    print(f"   Database: {brain.db_path}")
    print(f"   Dry Run: {brain.dry_run}")
    print(f"   Daily Trades: {brain.daily_trades}/{brain.SAFETY['max_daily_trades']}")
    print(f"   Open Positions: {len(brain.positions)}")
    
    print("\n✅ Setup test complete!")


def run_full_autonomous():
    """Run the full autonomous system"""
    print_banner()
    print("\n🚀 STARTING FULL AUTONOMOUS MODE\n")
    
    print("CONFIGURATION:")
    print("  • Auto-execute: YES (70%+ confidence)")
    print("  • Loss learning: ENABLED")
    print("  • Position management: AUTO")
    print("  • Daily trade limit: 5")
    print("  • Max positions: 5")
    print("  • Max biotech: 3")
    print("")
    
    # Initialize brain
    log.info("Initializing Autonomous Brain...")
    brain = AutonomousBrain(dry_run=False)  # LIVE PAPER TRADING
    
    # Show initial status
    if brain.alpaca_connected:
        account = brain.trading_client.get_account()
        print(f"💰 Starting Portfolio: ${float(account.portfolio_value):,.2f}")
    
    if brain.ollama_connected:
        print(f"🧠 AI Brain: Fenrir (Ollama) READY")
    
    print("")
    print("🐺 Wolf Brain is now AUTONOMOUS")
    print("   Press Ctrl+C to stop")
    print("")
    print("SCHEDULE:")
    print("  4:00 AM - First premarket scan")
    print("  5:00 AM - Early movers")
    print("  6:00 AM - Volume confirmation")
    print("  7:00 AM - Peak action")
    print("  7:30 AM - Final scan")
    print("  9:30 AM - Market open trading")
    print("  During day - Position management + swing setups")
    print("  After hours - Light research")
    print("  Overnight - Deep research")
    print("")
    
    # Run forever
    try:
        brain.run_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutdown requested by user")
        print("Generating final dashboard...")
        
        dashboard = WolfDashboard()
        output = dashboard.render_terminal_dashboard()
        print(output)
        dashboard.save_dashboard_to_file()
        
        print("\n👋 Wolf Brain shutdown complete")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='🐺 Master Wolf Pack System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  python master.py                     # Run full autonomous system
  python master.py --dashboard-only    # Show dashboard
  python master.py --scan-now          # Run all scanners
  python master.py --test-setup        # Test connections
  python master.py --report            # Generate intel report
        """
    )
    
    parser.add_argument('--dashboard-only', action='store_true',
                       help='Only display the dashboard')
    parser.add_argument('--scan-now', action='store_true',
                       help='Run all scanners immediately')
    parser.add_argument('--test-setup', action='store_true',
                       help='Test all connections and APIs')
    parser.add_argument('--report', action='store_true',
                       help='Generate full intel report')
    parser.add_argument('--dry-run', action='store_true',
                       help='Run in dry-run mode (no actual trades)')
    parser.add_argument('--prepop', action='store_true',
                       help='Run pre-pop scanner (scores explosion potential)')
    
    args = parser.parse_args()
    
    # Dashboard only
    if args.dashboard_only:
        run_dashboard_only()
        return
    
    # Pre-pop scanner
    if args.prepop:
        print_banner()
        print("\n🔍 PRE-POP SCANNER MODE\n")
        from prepop_scanner import PrePopScorer
        
        # Biotech universe
        tickers = [
            "PALI", "ONCY", "RCAT", "AQST", "OCUL", "VNDA", "ASND",
            "ZURA", "LXRX", "NVAX", "IBRX", "MNMD", "XENE",
            "NTLA", "CRSP", "BEAM", "EDIT", "SRPT", "RARE"
        ]
        
        scanner = PrePopScorer()
        results = scanner.scan_universe(tickers)
        scanner.print_results(results)
        
        # Show actionable opportunities
        buy_now = [r for r in results if r.get('catalyst', {}).get('days_until', 999) <= 14 and r.get('catalyst', {}).get('days_until', 999) >= 7]
        if buy_now:
            print(f"\n🎯 ACTIONABLE NOW (7-14 day window):")
            for r in buy_now:
                print(f"   {r['ticker']} @ ${r['price']} - Score: {r['total_score']}")
        
        return
    
    # Initialize brain for other modes
    brain = AutonomousBrain(dry_run=args.dry_run)
    
    # Test setup
    if args.test_setup:
        test_setup(brain)
        return
    
    # Scan now
    if args.scan_now:
        run_scan_now(brain)
        return
    
    # Generate report
    if args.report:
        print_banner()
        print("\n📝 GENERATING INTEL REPORT\n")
        report = brain.generate_intel_report()
        print("✅ Report generated: data/wolf_brain/LATEST_INTEL_REPORT.txt")
        return
    
    # Default: Run full autonomous system
    run_full_autonomous()


if __name__ == '__main__':
    main()
