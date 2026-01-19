#!/usr/bin/env python
# 🐺 FENRIR SECRETARY - Simple wrapper with all commands

import sys
from risk_manager import RiskManager
from premarket_tracker import PremarketTracker
from afterhours_monitor import AfterHoursMonitor
from daily_briefing import DailyBriefing
from catalyst_calendar import CatalystCalendar
from key_levels import KeyLevelsTracker
from eod_report import EODReport
from correlation_tracker import CorrelationTracker
import failed_trades
from notifications import send_alert

def show_help():
    """Show available commands"""
    print("""
🐺 FENRIR SECRETARY COMMANDS:

python fenrir_secretary.py risk          - Risk check (PDT, concentration)
python fenrir_secretary.py premarket     - Pre-market gaps
python fenrir_secretary.py afterhours    - After-hours monitor
python fenrir_secretary.py briefing      - Daily briefing
python fenrir_secretary.py catalysts     - Upcoming events
python fenrir_secretary.py levels [TICK] - Key support/resistance
python fenrir_secretary.py eod           - End of day report
python fenrir_secretary.py correlation [TICKER] - Sympathy plays
python fenrir_secretary.py missed        - Missed opportunities

For full system:
python main.py chat    - Natural language mode
python main.py scan    - Market scanner
python main.py holdings - Show positions
    """)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        show_help()
        sys.exit(0)
    
    command = sys.argv[1].lower()
    
    if command == 'risk':
        print("🐺 RISK CHECK:\n")
        from risk_manager import format_risk_report
        import config
        print(format_risk_report(config.HOLDINGS))
    
    elif command == 'premarket':
        print("🐺 PRE-MARKET SCAN:\n")
        tracker = PremarketTracker()
        gaps = tracker.scan_for_gaps()
        if gaps:
            for gap in gaps:
                emoji = "🟢" if gap['gap_pct'] > 0 else "🔴"
                print(f"{emoji} {gap['ticker']}: ${gap['pm_price']:.2f} ({gap['gap_pct']:+.1f}% gap)")
        else:
            print("No significant gaps found")
    
    elif command == 'afterhours' or command == 'ah':
        print("🐺 AFTER-HOURS MONITOR:\n")
        import config
        monitor = AfterHoursMonitor()
        print(monitor.generate_ah_report(list(config.HOLDINGS.keys())))
    
    elif command == 'briefing':
        print("🐺 DAILY BRIEFING:\n")
        briefing = DailyBriefing()
        print(briefing.generate_briefing())
    
    elif command == 'catalysts':
        print("🐺 CATALYST CALENDAR:\n")
        from catalyst_calendar import quick_catalyst_check
        print(quick_catalyst_check())
    
    elif command == 'levels':
        tracker = KeyLevelsTracker()
        if len(sys.argv) > 2:
            ticker = sys.argv[2].upper()
            print(tracker.format_levels_report(ticker))
        else:
            print(tracker.scan_all_positions())
    
    elif command == 'eod':
        print("🐺 END OF DAY REPORT:\n")
        report = EODReport()
        print(report.generate_report())
    
    elif command == 'correlation' or command == 'corr':
        tracker = CorrelationTracker()
        if len(sys.argv) > 2:
            ticker = sys.argv[2].upper()
            print(f"\n🐺 STOCKS CORRELATED WITH {ticker}:\n")
            correlated = tracker.find_correlated_stocks(ticker, min_correlation=0.7)
            if correlated:
                for c in correlated[:10]:
                    print(f"  {c['ticker']}: {c['correlation']:.2f} correlation")
            else:
                print("  No strong correlations found")
        else:
            print(tracker.when_this_moves_watch())
    
    elif command == 'missed':
        print("🐺 MISSED OPPORTUNITIES:\n")
        print(failed_trades.analyze_missed_trades())
    
    else:
        print(f"Unknown command: {command}")
        show_help()
