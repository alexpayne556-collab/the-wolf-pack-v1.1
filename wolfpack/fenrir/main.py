# 🐺 FENRIR V2 - MAIN
# Command Line Interface for Fenrir Trading AI

import argparse
import sys
from datetime import datetime

from config import ALL_WATCHLIST, HOLDINGS, MOVE_THRESHOLD_PCT, VOLUME_THRESHOLD_RATIO
from database import init_database, log_trade, log_alert, get_all_trades, get_recent_alerts
from market_data import get_stock_data, scan_movers, scan_volume_spikes, get_sector_performance
from news_fetcher import get_company_news
from ollama_brain import (
    ask_fenrir, quick_opinion, should_i_buy, should_i_sell,
    check_ollama_running, list_models, analyze_mover
)
from alerts import alert_big_mover, alert_volume_spike, console_alert

# Import new secretary features
from risk_manager import RiskManager
from premarket_tracker import PremarketTracker
from afterhours_monitor import AfterHoursMonitor
from daily_briefing import DailyBriefing
from catalyst_calendar import CatalystCalendar
from key_levels import KeyLevelsTracker
from eod_report import EODReport
from notifications import NotificationSystem, send_alert
from correlation_tracker import CorrelationTracker
from failed_trades import FailedTradesLog


def cmd_test():
    """Test that Fenrir is working"""
    print("🐺 Testing Fenrir...\n")
    
    # Check Ollama
    if check_ollama_running():
        print("✅ Ollama is running")
        models = list_models()
        print(f"   Models: {models}")
        
        if 'fenrir' in models or 'fenrir:latest' in models:
            print("✅ Fenrir model found")
        else:
            print("❌ Fenrir model not found. Create it with:")
            print("   ollama create fenrir -f Modelfile")
            return
    else:
        print("❌ Ollama not running. Start with: ollama serve")
        return
    
    # Test a basic question
    print("\n🐺 Asking Fenrir a question...\n")
    response = ask_fenrir("Give me your current read on the market. Keep it brief.")
    print(response)


def cmd_ask(question: str, ticker: str = None):
    """Ask Fenrir a question"""
    print(f"🐺 Asking Fenrir...\n")
    response = ask_fenrir(question, ticker=ticker, include_sectors=True)
    print(response)


def cmd_scan():
    """Scan watchlist for movers and volume spikes"""
    print(f"🐺 Scanning {len(ALL_WATCHLIST)} stocks...\n")
    
    # Find big movers
    movers = scan_movers(ALL_WATCHLIST, threshold=MOVE_THRESHOLD_PCT)
    
    if movers:
        print(f"📈 BIG MOVERS (>{MOVE_THRESHOLD_PCT}%):\n")
        for m in movers[:10]:
            emoji = "🟢" if m['change_pct'] > 0 else "🔴"
            owned = "⭐" if m['ticker'] in HOLDINGS else ""
            print(f"  {emoji} {m['ticker']}{owned}: ${m['price']:.2f} ({m['change_pct']:+.2f}%) vol:{m['volume_ratio']:.1f}x")
        
        # Get Fenrir's take on the top mover
        top = movers[0]
        print(f"\n🐺 Fenrir's take on {top['ticker']}:\n")
        response = analyze_mover(top['ticker'], top['change_pct'])
        print(response)
    else:
        print("No big movers found today.")
    
    # Find volume spikes
    print(f"\n📊 VOLUME SPIKES (>{VOLUME_THRESHOLD_RATIO}x average):\n")
    spikes = scan_volume_spikes(ALL_WATCHLIST, threshold=VOLUME_THRESHOLD_RATIO)
    
    if spikes:
        for s in spikes[:10]:
            emoji = "🟢" if s['change_pct'] > 0 else "🔴"
            owned = "⭐" if s['ticker'] in HOLDINGS else ""
            print(f"  {emoji} {s['ticker']}{owned}: {s['volume_ratio']:.1f}x volume (${s['price']:.2f}, {s['change_pct']:+.2f}%)")
    else:
        print("No unusual volume detected.")


def cmd_holdings():
    """Show current holdings with live data"""
    print("🐺 YOUR HOLDINGS:\n")
    
    total_value = 0
    total_cost = 0
    
    for ticker, info in HOLDINGS.items():
        data = get_stock_data(ticker)
        if data:
            value = info['shares'] * data['price']
            cost = info['shares'] * info['avg_cost']
            total_value += value
            total_cost += cost
            
            pnl_pct = ((data['price'] - info['avg_cost']) / info['avg_cost']) * 100
            pnl_dollar = value - cost
            
            emoji = "🟢" if data['change_pct'] > 0 else "🔴"
            
            print(f"{emoji} {ticker}")
            print(f"   {info['shares']} shares @ ${info['avg_cost']:.2f}")
            print(f"   Now: ${data['price']:.2f} ({data['change_pct']:+.2f}% today)")
            print(f"   P/L: ${pnl_dollar:+.2f} ({pnl_pct:+.2f}%)")
            print(f"   Thesis: {info.get('thesis', 'N/A')}")
            print()
    
    total_pnl = total_value - total_cost
    total_pnl_pct = ((total_value - total_cost) / total_cost) * 100 if total_cost > 0 else 0
    
    print(f"{'='*40}")
    print(f"TOTAL VALUE: ${total_value:,.2f}")
    print(f"TOTAL COST:  ${total_cost:,.2f}")
    print(f"TOTAL P/L:   ${total_pnl:+,.2f} ({total_pnl_pct:+.2f}%)")


def cmd_sectors():
    """Show sector performance"""
    from config import WATCHLIST
    
    print("🐺 SECTOR PERFORMANCE TODAY:\n")
    
    perf = get_sector_performance(WATCHLIST)
    
    for sector, change in perf.items():
        emoji = "🟢" if change > 0 else "🔴"
        bar = "█" * int(abs(change))
        print(f"  {emoji} {sector:12} {change:+6.2f}% {bar}")


def cmd_analyze(ticker: str):
    """Deep analysis of a specific ticker"""
    print(f"🐺 Analyzing {ticker}...\n")
    
    # Get data
    data = get_stock_data(ticker)
    if not data:
        print(f"Couldn't fetch data for {ticker}")
        return
    
    # Display data
    print(f"{'='*40}")
    print(f"{ticker} ANALYSIS")
    print(f"{'='*40}")
    print(f"Price:    ${data['price']:.2f}")
    print(f"Today:    {data['change_pct']:+.2f}%")
    print(f"Volume:   {data['volume_ratio']:.1f}x average")
    print(f"52w High: ${data['high_52w']:.2f} ({data['from_high']:+.1f}%)")
    print(f"52w Low:  ${data['low_52w']:.2f} ({data['from_low']:+.1f}%)")
    
    # News
    print(f"\n📰 RECENT NEWS:")
    news = get_company_news(ticker, days=7)
    if news:
        for item in news[:5]:
            print(f"  [{item['datetime']}] {item['headline'][:70]}")
    else:
        print("  No recent news found.")
    
    # Fenrir's opinion
    print(f"\n🐺 FENRIR'S TAKE:\n")
    response = quick_opinion(ticker)
    print(response)


def cmd_buy_check(ticker: str):
    """Should I buy this?"""
    print(f"🐺 Checking if you should buy {ticker}...\n")
    response = should_i_buy(ticker)
    print(response)


def cmd_sell_check(ticker: str):
    """Should I sell this?"""
    print(f"🐺 Checking if you should sell {ticker}...\n")
    response = should_i_sell(ticker)
    print(response)


def cmd_log_trade(ticker: str, action: str, shares: float, price: float, account: str = None):
    """Log a trade"""
    init_database()
    
    # Get Fenrir's take
    fenrir_opinion = quick_opinion(ticker)
    
    trade_id = log_trade(
        ticker=ticker,
        action=action,
        shares=shares,
        price=price,
        account=account,
        thesis=HOLDINGS.get(ticker, {}).get('thesis'),
        fenrir_said=fenrir_opinion[:500]
    )
    
    print(f"✅ Trade logged (ID: {trade_id})")
    print(f"   {action} {shares} {ticker} @ ${price:.2f}")
    if account:
        print(f"   Account: {account}")


def cmd_trades():
    """Show recent trades"""
    init_database()
    trades = get_all_trades()
    
    if not trades:
        print("No trades logged yet.")
        return
    
    print("🐺 YOUR TRADES:\n")
    for t in trades[:20]:
        emoji = "🟢" if t['action'] == 'BUY' else "🔴"
        print(f"{emoji} [{t['timestamp'][:10]}] {t['action']} {t['shares']} {t['ticker']} @ ${t['price']:.2f}")
        if t.get('outcome'):
            print(f"   Outcome: {t['outcome']}")


def cmd_risk():
    """Show risk analysis"""
    print("🐺 RISK CHECK:\n")
    manager = RiskManager()
    print(manager.generate_risk_report())


def cmd_premarket():
    """Check pre-market activity"""
    print("🐺 PRE-MARKET SCAN:\n")
    tracker = PremarketTracker()
    gaps = tracker.scan_for_gaps()
    
    if gaps:
        for gap in gaps:
            emoji = "🟢" if gap['gap_pct'] > 0 else "🔴"
            print(f"{emoji} {gap['ticker']}: ${gap['pm_price']:.2f} ({gap['gap_pct']:+.1f}% gap)")
    else:
        print("No significant gaps found")


def cmd_afterhours():
    """Check after-hours activity"""
    print("🐺 AFTER-HOURS MONITOR:\n")
    monitor = AfterHoursMonitor()
    print(monitor.generate_ah_report())


def cmd_briefing():
    """Generate daily briefing"""
    print("🐺 Generating morning briefing...\n")
    briefing = DailyBriefing()
    print(briefing.generate_briefing())


def cmd_catalysts():
    """Show upcoming catalysts"""
    print("🐺 CATALYST CALENDAR:\n")
    calendar = CatalystCalendar()
    print(calendar.format_calendar())


def cmd_levels(ticker: str = None):
    """Show key levels"""
    tracker = KeyLevelsTracker()
    
    if ticker:
        print(tracker.format_levels_report(ticker))
    else:
        print(tracker.scan_all_positions())


def cmd_eod():
    """Generate end of day report"""
    print("🐺 Generating EOD report...\n")
    report = EODReport()
    print(report.generate_report())


def cmd_correlation(ticker: str = None):
    """Show correlated stocks"""
    tracker = CorrelationTracker()
    
    if ticker:
        print(f"\n🐺 STOCKS CORRELATED WITH {ticker}:\n")
        correlated = tracker.find_correlated_stocks(ticker, min_correlation=0.7)
        if correlated:
            for c in correlated[:10]:
                print(f"  {c['ticker']}: {c['correlation']:.2f} correlation")
        else:
            print("  No strong correlations found")
    else:
        print(tracker.when_this_moves_watch())


def cmd_missed():
    """Show missed opportunities"""
    print("🐺 MISSED OPPORTUNITIES:\n")
    log = FailedTradesLog()
    print(log.analyze_missed_trades())


def main():
    parser = argparse.ArgumentParser(
        description="🐺 Fenrir - Personal AI Trading Companion",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  BASIC:
    test              Test that Fenrir is working
    ask               Ask Fenrir a question
    scan              Scan watchlist for movers
    holdings          Show your holdings with live data
    sectors           Show sector performance
    analyze TICKER    Deep analysis of a ticker
    buy TICKER        Should I buy this?
    sell TICKER       Should I sell this?
    log               Log a trade
    trades            Show recent trades
    
  SECRETARY FEATURES:
    risk              Show risk analysis (PDT, concentration)
    premarket         Check pre-market gaps
    afterhours        Check after-hours activity
    briefing          Generate daily briefing (run at 6 AM)
    catalysts         Show upcoming earnings/events
    levels [TICKER]   Show key support/resistance levels
    eod               Generate end of day report (run at 4:15 PM)
    correlation [T]   Show correlated stocks / sympathy plays
    missed            Analyze missed opportunities
    
  INTERACTIVE:
    chat              Natural language chat mode (RECOMMENDED)

Examples:
  python main.py chat
    Then type naturally:
      - how's ibrx doing
      - show my positions
      - what's moving today
      - any catalysts coming up
      - what do i need to know
        """
    )
    
    parser.add_argument('command', 
                       choices=['test', 'ask', 'scan', 'holdings', 'sectors', 
                               'analyze', 'buy', 'sell', 'log', 'trades', 'chat',
                               'risk', 'premarket', 'afterhours', 'briefing', 
                               'catalysts', 'levels', 'eod', 'correlation', 'missed'],
                       help='Command to run')
    parser.add_argument('-t', '--ticker', help='Ticker symbol')
    parser.add_argument('-q', '--question', help='Question for ask command')
    parser.add_argument('-s', '--shares', type=float, help='Number of shares (for log)')
    parser.add_argument('-p', '--price', type=float, help='Price (for log)')
    parser.add_argument('-a', '--action', choices=['BUY', 'SELL'], help='Action (for log)')
    parser.add_argument('--account', help='Account (robinhood/fidelity)')
    
    args = parser.parse_args()
    
    # Route to command
    if args.command == 'test':
        cmd_test()
    
    elif args.command == 'ask':
        question = args.question or input("Ask Fenrir: ")
        cmd_ask(question, ticker=args.ticker)
    
    elif args.command == 'scan':
        cmd_scan()
    
    elif args.command == 'holdings':
        cmd_holdings()
    
    elif args.command == 'sectors':
        cmd_sectors()
    
    elif args.command == 'analyze':
        ticker = args.ticker or input("Ticker: ").upper()
        cmd_analyze(ticker)
    
    elif args.command == 'buy':
        ticker = args.ticker or input("Ticker: ").upper()
        cmd_buy_check(ticker)
    
    elif args.command == 'sell':
        ticker = args.ticker or input("Ticker: ").upper()
        cmd_sell_check(ticker)
    
    elif args.command == 'log':
        ticker = args.ticker or input("Ticker: ").upper()
        action = args.action or input("Action (BUY/SELL): ").upper()
        shares = args.shares or float(input("Shares: "))
        price = args.price or float(input("Price: "))
        account = args.account or input("Account (robinhood/fidelity): ") or None
        cmd_log_trade(ticker, action, shares, price, account)
    
    elif args.command == 'trades':
        cmd_trades()
    
    elif args.command == 'risk':
        cmd_risk()
    
    elif args.command == 'premarket':
        cmd_premarket()
    
    elif args.command == 'afterhours':
        cmd_afterhours()
    
    elif args.command == 'briefing':
        cmd_briefing()
    
    elif args.command == 'catalysts':
        cmd_catalysts()
    
    elif args.command == 'levels':
        cmd_levels(args.ticker)
    
    elif args.command == 'eod':
        cmd_eod()
    
    elif args.command == 'correlation':
        cmd_correlation(args.ticker)
    
    elif args.command == 'missed':
        cmd_misseduy' in text or 'buy?' in text:
        return ('buy', ticker, {})
    
    if 'should i sell' in text or 'sell?' in text:
        return ('sell', ticker, {})
    
    if any(phrase in text for phrase in ['risk', 'risks', 'danger']):
        return ('risk', None, {})
    
    if any(phrase in text for phrase in ['premarket', 'pre-market', 'gaps']):
        return ('premarket', None, {})
    
    if any(phrase in text for phrase in ['after hours', 'afterhours', 'ah']):
        return ('afterhours', None, {})
    
    if any(phrase in text for phrase in ['briefing', 'morning', 'what do i need', 'summary']):
        return ('briefing', None, {})
    
    if any(phrase in text for phrase in ['catalyst', 'earnings', 'events']):
        return ('catalysts', None, {})
    
    if any(phrase in text for phrase in ['levels', 'support', 'resistance']):
        return ('levels', ticker, {})
    
    if any(phrase in text for phrase in ['eod', 'end of day', 'today summary']):
        return ('eod', None, {})
    
    if any(phrase in text for phrase in ['correlation', 'sympathy', 'related']):
        return ('correlation', ticker, {})
    
    if any(phrase in text for phrase in ['missed', 'opportunities', 'failed']):
        return ('missed', None, {})
    
    # Default: treat as question
    return ('ask', ticker, {'question': text})


def cmd_interactive():
    """Interactive chat mode with natural language"""
    print("🐺 FENRIR INTERACTIVE MODE")
    print("="*40)
    print("Just type naturally. Examples:")
    print("  - how's ibrx doing")
    print("  - show my positions")
    print("  - what's moving today")
    print("  - should i buy ktos")
    print("  - what do i need to know")
    print("  - any catalysts coming up")
    print("Type 'quit' to exit.")
    print("="*40 + "\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("🐺 Later, boss. LLHR.")
                break
            
            # Parse natural language
            command, ticker, args = parse_natural_language(user_input)
            
            print()  # Blank line
            
            # Execute command
            if command == 'analyze' and ticker:
                cmd_analyze(ticker)
            elif command == 'holdings':
                cmd_holdings()
            elif command == 'scan':
                cmd_scan()
            elif command == 'buy' and ticker:
                cmd_buy_check(ticker)
            elif command == 'sell' and ticker:
                cmd_sell_check(ticker)
            elif command == 'risk':
                cmd_risk()
            elif command == 'premarket':
                cmd_premarket()
            elif command == 'afterhours':
                cmd_afterhours()
            elif command == 'briefing':
                cmd_briefing()
            elif command == 'catalysts':
                cmd_catalysts()
            elif command == 'levels':
                cmd_levels(ticker)
            elif command == 'eod':
                cmd_eod()
            elif command == 'correlation':
                cmd_correlation(ticker)
            elif command == 'missed':
                cmd_missed()
            elif command == 'ask':
                question = args.get('question', user_input)
                response = ask_fenrir(question, ticker=ticker)
                print(f"🐺 Fenrir: {response}")
            else:
                # Fallback to Fenrir
                response = ask_fenrir(user_input, ticker=ticker)
                print(f"🐺 Fenrir: {response}")
            
            print()  # Blank line after response
            
        except KeyboardInterrupt:
            print("\n🐺 Later, boss. LLHR.")
            break
        except Exception as e:
            print(f"❌ Error: {e}\n")


def main():
    parser = argparse.ArgumentParser(
        description="🐺 Fenrir - Personal AI Trading Companion",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  test              Test that Fenrir is working
  ask               Ask Fenrir a question
  scan              Scan watchlist for movers
  holdings          Show your holdings with live data
  sectors           Show sector performance
  analyze TICKER    Deep analysis of a ticker
  buy TICKER        Should I buy this?
  sell TICKER       Should I sell this?
  log               Log a trade
  trades            Show recent trades
  chat              Interactive chat mode

Examples:
  python main.py test
  python main.py scan
  python main.py analyze IBRX
  python main.py ask -q "What's your read on nuclear stocks?"
  python main.py buy KTOS
  python main.py chat
        """
    )
    
    parser.add_argument('command', 
                       choices=['test', 'ask', 'scan', 'holdings', 'sectors', 
                               'analyze', 'buy', 'sell', 'log', 'trades', 'chat'],
                       help='Command to run')
    parser.add_argument('-t', '--ticker', help='Ticker symbol')
    parser.add_argument('-q', '--question', help='Question for ask command')
    parser.add_argument('-s', '--shares', type=float, help='Number of shares (for log)')
    parser.add_argument('-p', '--price', type=float, help='Price (for log)')
    parser.add_argument('-a', '--action', choices=['BUY', 'SELL'], help='Action (for log)')
    parser.add_argument('--account', help='Account (robinhood/fidelity)')
    
    args = parser.parse_args()
    
    # Route to command
    if args.command == 'test':
        cmd_test()
    
    elif args.command == 'ask':
        question = args.question or input("Ask Fenrir: ")
        cmd_ask(question, ticker=args.ticker)
    
    elif args.command == 'scan':
        cmd_scan()
    
    elif args.command == 'holdings':
        cmd_holdings()
    
    elif args.command == 'sectors':
        cmd_sectors()
    
    elif args.command == 'analyze':
        ticker = args.ticker or input("Ticker: ").upper()
        cmd_analyze(ticker)
    
    elif args.command == 'buy':
        ticker = args.ticker or input("Ticker: ").upper()
        cmd_buy_check(ticker)
    
    elif args.command == 'sell':
        ticker = args.ticker or input("Ticker: ").upper()
        cmd_sell_check(ticker)
    
    elif args.command == 'log':
        ticker = args.ticker or input("Ticker: ").upper()
        action = args.action or input("Action (BUY/SELL): ").upper()
        shares = args.shares or float(input("Shares: "))
        price = args.price or float(input("Price: "))
        account = args.account or input("Account (robinhood/fidelity): ") or None
        cmd_log_trade(ticker, action, shares, price, account)
    
    elif args.command == 'trades':
        cmd_trades()
    
    elif args.command == 'chat':
        cmd_interactive()


if __name__ == "__main__":
    main()
