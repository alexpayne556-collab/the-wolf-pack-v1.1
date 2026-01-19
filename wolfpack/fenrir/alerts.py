# 🐺 FENRIR V2 - ALERTS
# Desktop notifications for Windows

import sys
from typing import Optional

# Try to import Windows notification library
try:
    from win10toast import ToastNotifier
    TOAST_AVAILABLE = True
except ImportError:
    TOAST_AVAILABLE = False
    print("Note: win10toast not installed. Install with: pip install win10toast")


class FenrirAlerts:
    """Handle desktop notifications for Fenrir"""
    
    def __init__(self):
        if TOAST_AVAILABLE:
            self.toaster = ToastNotifier()
        else:
            self.toaster = None
    
    def notify(self, title: str, message: str, duration: int = 5):
        """Send a desktop notification"""
        if self.toaster:
            try:
                self.toaster.show_toast(
                    title=f"🐺 {title}",
                    msg=message,
                    duration=duration,
                    threaded=True  # Don't block
                )
            except Exception as e:
                print(f"Toast error: {e}")
                self._fallback_notify(title, message)
        else:
            self._fallback_notify(title, message)
    
    def _fallback_notify(self, title: str, message: str):
        """Fallback to console notification"""
        print(f"\n{'='*50}")
        print(f"🐺 FENRIR ALERT: {title}")
        print(f"{'='*50}")
        print(message)
        print(f"{'='*50}\n")
    
    def big_mover(self, ticker: str, price: float, change_pct: float, catalyst: str = None):
        """Alert for big price move"""
        direction = "🟢 UP" if change_pct > 0 else "🔴 DOWN"
        title = f"{ticker} {direction} {abs(change_pct):.1f}%"
        
        msg = f"${price:.2f}"
        if catalyst:
            msg += f"\n{catalyst}"
        
        self.notify(title, msg)
    
    def volume_spike(self, ticker: str, volume_ratio: float, price: float):
        """Alert for unusual volume"""
        title = f"{ticker} Volume Spike"
        msg = f"{volume_ratio:.1f}x average volume\nPrice: ${price:.2f}"
        self.notify(title, msg)
    
    def catalyst_alert(self, ticker: str, catalyst_type: str, headline: str):
        """Alert for news catalyst"""
        title = f"{ticker} {catalyst_type}"
        self.notify(title, headline[:100])
    
    def position_alert(self, ticker: str, message: str):
        """Alert about a position you hold"""
        title = f"Position Alert: {ticker}"
        self.notify(title, message)


# Global instance
alerts = FenrirAlerts()


def alert_big_mover(ticker: str, price: float, change_pct: float, catalyst: str = None):
    """Quick function to send big mover alert"""
    alerts.big_mover(ticker, price, change_pct, catalyst)


def alert_volume_spike(ticker: str, volume_ratio: float, price: float):
    """Quick function to send volume alert"""
    alerts.volume_spike(ticker, volume_ratio, price)


def alert_news(ticker: str, headline: str):
    """Quick function to send news alert"""
    alerts.catalyst_alert(ticker, "NEWS", headline)


def console_alert(message: str):
    """Simple console alert"""
    print(f"\n🐺 FENRIR: {message}\n")


# =============================================================================
# TEST
# =============================================================================
if __name__ == "__main__":
    print("Testing Fenrir alerts...\n")
    
    # Test big mover
    alert_big_mover("IBRX", 5.27, 33.42, "Q4 revenue beat 700% YoY")
    
    import time
    time.sleep(2)
    
    # Test volume spike
    alert_volume_spike("KTOS", 3.5, 130.46)
    
    time.sleep(2)
    
    # Test news
    alert_news("MU", "Micron wins major AI contract with hyperscaler")
    
    print("\nAlerts sent! Check your notifications.")
