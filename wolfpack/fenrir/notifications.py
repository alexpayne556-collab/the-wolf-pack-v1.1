# 🐺 FENRIR V2 - NOTIFICATION SYSTEM
# Desktop alerts with sound for urgent situations

import sys
from typing import Optional

# Try to import Windows toast notifications
try:
    from win10toast import ToastNotifier
    toaster = ToastNotifier()
    HAS_TOAST = True
except ImportError:
    HAS_TOAST = False
    print("⚠️  win10toast not installed - install with: pip install win10toast")

# Sound support
try:
    import winsound
    HAS_SOUND = True
except ImportError:
    HAS_SOUND = False

class NotificationSystem:
    """Send notifications with different urgency levels"""
    
    def __init__(self):
        self.sound_enabled = True
        self.toast_enabled = HAS_TOAST
    
    def notify(self, title: str, message: str, severity: str = 'info'):
        """
        Send notification
        
        severity: 'info', 'warning', 'urgent'
        """
        
        # Console output (always)
        self._console_notify(title, message, severity)
        
        # Sound
        if self.sound_enabled and severity == 'urgent':
            self._play_alert_sound()
        
        # Toast notification
        if self.toast_enabled:
            self._toast_notify(title, message, severity)
    
    def _console_notify(self, title: str, message: str, severity: str):
        """Print to console"""
        
        emoji_map = {
            'info': 'ℹ️',
            'warning': '⚠️',
            'urgent': '🚨',
        }
        
        emoji = emoji_map.get(severity, 'ℹ️')
        
        print(f"\n{emoji} {severity.upper()}: {title}")
        print(f"  {message}\n")
    
    def _toast_notify(self, title: str, message: str, severity: str):
        """Windows toast notification"""
        
        if not HAS_TOAST:
            return
        
        try:
            # Duration based on severity
            duration = 5 if severity == 'info' else 10
            
            toaster.show_toast(
                title=f"🐺 {title}",
                msg=message,
                duration=duration,
                threaded=True
            )
        except Exception as e:
            print(f"Toast error: {e}")
    
    def _play_alert_sound(self):
        """Play alert sound for urgent notifications"""
        
        if not HAS_SOUND:
            return
        
        try:
            # Play Windows system sound
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        except:
            pass
    
    def alert_position_bleeding(self, ticker: str, price: float, change_pct: float):
        """URGENT: Position down 5%+"""
        
        self.notify(
            title=f"{ticker} BLEEDING",
            message=f"Down {change_pct:.1f}% to ${price:.2f}",
            severity='urgent'
        )
    
    def alert_position_running(self, ticker: str, price: float, change_pct: float):
        """WARNING: Position up 5%+"""
        
        self.notify(
            title=f"{ticker} RUNNING",
            message=f"Up {change_pct:+.1f}% to ${price:.2f}",
            severity='warning'
        )
    
    def alert_news(self, ticker: str, headline: str):
        """WARNING: News on position"""
        
        self.notify(
            title=f"{ticker} NEWS",
            message=headline[:100],
            severity='warning'
        )
    
    def alert_volume_spike(self, ticker: str, volume_ratio: float):
        """INFO: Volume spike"""
        
        self.notify(
            title=f"{ticker} VOLUME",
            message=f"Volume {volume_ratio:.1f}x average",
            severity='info'
        )
    
    def alert_level_approach(self, ticker: str, level_type: str, level: float):
        """INFO: Approaching key level"""
        
        self.notify(
            title=f"{ticker} LEVEL",
            message=f"Approaching {level_type} at ${level:.2f}",
            severity='info'
        )
    
    def alert_ah_move(self, ticker: str, ah_change: float):
        """WARNING: After-hours move"""
        
        self.notify(
            title=f"{ticker} AFTER HOURS",
            message=f"Moving {ah_change:+.1f}% AH",
            severity='warning'
        )
    
    def alert_pdt_warning(self):
        """WARNING: Low on day trades"""
        
        self.notify(
            title="PDT WARNING",
            message="Only 1 day trade left this week",
            severity='warning'
        )
    
    def alert_custom(self, title: str, message: str, urgent: bool = False):
        """Send custom alert"""
        
        self.notify(
            title=title,
            message=message,
            severity='urgent' if urgent else 'info'
        )


# Global instance
_notifier = None

def get_notifier() -> NotificationSystem:
    """Get global notifier instance"""
    global _notifier
    if _notifier is None:
        _notifier = NotificationSystem()
    return _notifier


def send_alert(title: str, message: str, urgent: bool = False):
    """Quick function to send alert"""
    notifier = get_notifier()
    notifier.alert_custom(title, message, urgent)


# Test
if __name__ == '__main__':
    print("\n🐺 Testing Notification System\n")
    
    notifier = NotificationSystem()
    
    print("Test 1: Info notification")
    notifier.alert_volume_spike('IBRX', 3.5)
    
    print("\nTest 2: Warning notification")
    notifier.alert_position_running('KTOS', 130.72, 5.2)
    
    print("\nTest 3: URGENT notification (with sound)")
    notifier.alert_position_bleeding('BBAI', 6.12, -5.8)
    
    print("\n🐺 Notification test complete\n")
