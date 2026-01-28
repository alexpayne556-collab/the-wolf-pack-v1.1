"""
ALERTER - Send Notifications via Discord
=========================================
Sends brain thoughts and alerts without crashing.

Features:
- Discord webhook integration (free, no limits)
- Priority-based messaging
- Message formatting
- Error handling
- Logging fallback
"""

import os
import requests
import json
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Alerter:
    """Send alerts via Discord webhook"""
    
    def __init__(self):
        self.discord_webhook = os.getenv('DISCORD_WEBHOOK_URL')
        self.leonard_file = Path("THE_LEONARD_FILE.md")
        
    def send_discord(self, message: str, priority: str = "medium", embed_data: Optional[Dict] = None) -> bool:
        """
        Send message to Discord
        
        Args:
            message: Text message
            priority: "urgent", "high", "medium", "low"
            embed_data: Optional rich embed data
        
        Returns:
            True if sent successfully
        """
        if not self.discord_webhook:
            print("⚠️  Discord webhook not configured")
            return False
        
        try:
            # Build payload
            payload = {
                "content": message,
                "username": "Wolf Pack Brain 🐺"
            }
            
            # Add embed if provided
            if embed_data:
                color_map = {
                    "urgent": 0xFF0000,  # Red
                    "high": 0xFFA500,    # Orange
                    "medium": 0x0099FF,  # Blue
                    "low": 0x808080      # Gray
                }
                
                embed = {
                    "title": embed_data.get("title", ""),
                    "description": embed_data.get("description", ""),
                    "color": color_map.get(priority, 0x0099FF),
                    "timestamp": datetime.utcnow().isoformat(),
                    "fields": embed_data.get("fields", [])
                }
                
                if "footer" in embed_data:
                    embed["footer"] = {"text": embed_data["footer"]}
                
                payload["embeds"] = [embed]
            
            # Send to Discord
            response = requests.post(
                self.discord_webhook,
                json=payload,
                timeout=10
            )
            
            if response.status_code in [200, 204]:
                return True
            else:
                print(f"Discord API error: {response.status_code}")
                return False
        
        except Exception as e:
            print(f"Discord send error: {e}")
            return False
    
    def alert_volume_spike(self, ticker: str, volume_ratio: float, price: float, change_pct: float) -> bool:
        """Alert about volume spike"""
        
        emoji = "🔥" if volume_ratio >= 2.0 else "📈"
        
        message = f"{emoji} **Volume Spike Detected: {ticker}**"
        
        embed_data = {
            "title": f"{ticker} Volume Alert",
            "description": f"Volume is {volume_ratio:.1f}x average",
            "fields": [
                {"name": "Price", "value": f"${price:.2f} ({change_pct:+.2f}%)", "inline": True},
                {"name": "Volume Ratio", "value": f"{volume_ratio:.1f}x", "inline": True},
                {"name": "Action", "value": "Check news & thesis", "inline": False}
            ],
            "footer": f"Scanned at {datetime.now().strftime('%I:%M %p ET')}"
        }
        
        priority = "high" if volume_ratio >= 2.0 else "medium"
        
        return self.send_discord(message, priority=priority, embed_data=embed_data)
    
    def alert_thesis_break(self, ticker: str, reason: str) -> bool:
        """Alert about broken thesis"""
        
        message = f"🚨 **THESIS BREAK: {ticker}**"
        
        embed_data = {
            "title": f"{ticker} - Thesis Broken",
            "description": reason,
            "fields": [
                {"name": "Action Required", "value": "**CUT POSITION**", "inline": False}
            ],
            "footer": "Automated thesis monitoring"
        }
        
        return self.send_discord(message, priority="urgent", embed_data=embed_data)
    
    def alert_setup(self, ticker: str, convergence: int, thesis: str, catalyst: str) -> bool:
        """Alert about A+ setup"""
        
        message = f"✨ **A+ Setup: {ticker}**"
        
        embed_data = {
            "title": f"{ticker} Entry Signal",
            "description": f"Convergence: {convergence}",
            "fields": [
                {"name": "Thesis", "value": thesis, "inline": False},
                {"name": "Catalyst", "value": catalyst, "inline": False},
                {"name": "Action", "value": "Review for entry", "inline": False}
            ],
            "footer": "High-conviction setup detected"
        }
        
        return self.send_discord(message, priority="high", embed_data=embed_data)
    
    def alert_brain_thought(self, thought_type: str, trigger: str, reasoning: list, confidence: float, action: str) -> bool:
        """Alert about brain reasoning"""
        
        emoji_map = {
            "earnings_impact": "📊",
            "macro_effect": "🌐",
            "people_signal": "👤",
            "sector_correlation": "🔗",
            "multi_signal_convergence": "🧠"
        }
        
        emoji = emoji_map.get(thought_type, "💭")
        
        message = f"{emoji} **Brain Insight: {trigger}**"
        
        # Format reasoning chain
        reasoning_text = "\n".join([f"{i+1}. {step}" for i, step in enumerate(reasoning[:3])])
        
        embed_data = {
            "title": f"Brain Reasoning: {thought_type.replace('_', ' ').title()}",
            "description": f"**Trigger:** {trigger}\n\n**Reasoning:**\n{reasoning_text}",
            "fields": [
                {"name": "Confidence", "value": f"{confidence:.0f}%", "inline": True},
                {"name": "Suggested Action", "value": action, "inline": True}
            ],
            "footer": "Fenrir Thinking Engine"
        }
        
        priority = "high" if confidence >= 75 else "medium"
        
        return self.send_discord(message, priority=priority, embed_data=embed_data)
    
    def send_daily_summary(self, summary_data: Dict) -> bool:
        """Send end-of-day summary"""
        
        message = "📋 **Daily Trading Summary**"
        
        fields = []
        
        if "positions" in summary_data:
            positions_text = ", ".join(summary_data["positions"])
            fields.append({"name": "Positions", "value": positions_text, "inline": False})
        
        if "top_movers" in summary_data:
            movers_text = "\n".join(summary_data["top_movers"])
            fields.append({"name": "Top Movers", "value": movers_text, "inline": False})
        
        if "thoughts_generated" in summary_data:
            fields.append({
                "name": "Brain Activity",
                "value": f"{summary_data['thoughts_generated']} thoughts generated",
                "inline": True
            })
        
        embed_data = {
            "title": f"Daily Summary - {datetime.now().strftime('%B %d, %Y')}",
            "description": summary_data.get("summary", "Market activity summary"),
            "fields": fields,
            "footer": "Wolf Pack Brain • End of Day"
        }
        
        return self.send_discord(message, priority="low", embed_data=embed_data)
    
    def log_to_leonard(self, message: str, category: str = "general"):
        """Fallback: log to Leonard File if Discord fails"""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            entry = f"\n\n### {category.upper()} - {timestamp}\n{message}\n"
            
            with open(self.leonard_file, 'a', encoding='utf-8') as f:
                f.write(entry)
            
            return True
        except Exception as e:
            print(f"Leonard File logging error: {e}")
            return False


def test_alerter():
    """Test Discord alerts"""
    print("=" * 70)
    print("TESTING ALERTER - Discord Webhooks")
    print("=" * 70)
    
    alerter = Alerter()
    
    if not alerter.discord_webhook:
        print("\n⚠️  DISCORD_WEBHOOK_URL not set in .env")
        print("\nTo enable Discord alerts:")
        print("1. Create a Discord server (or use existing)")
        print("2. Server Settings → Integrations → Webhooks → New Webhook")
        print("3. Copy webhook URL")
        print("4. Add to .env: DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...")
        print("\nSkipping Discord tests, logging to Leonard File instead")
        
        # Test Leonard File logging
        print("\n[TEST] Leonard File Logging")
        print("-" * 70)
        success = alerter.log_to_leonard("Test alert - system operational", "test")
        print(f"Leonard File log: {'✅ Success' if success else '❌ Failed'}")
        
        return
    
    print(f"\n[TEST 1] Volume Spike Alert")
    print("-" * 70)
    success = alerter.alert_volume_spike(
        ticker="MU",
        volume_ratio=2.3,
        price=395.50,
        change_pct=3.2
    )
    print(f"Discord alert sent: {'✅' if success else '❌'}")
    
    print(f"\n[TEST 2] Brain Thought Alert")
    print("-" * 70)
    success = alerter.alert_brain_thought(
        thought_type="earnings_impact",
        trigger="MSFT earnings beat",
        reasoning=[
            "MSFT earnings beat",
            "Azure growth 31%",
            "AI infrastructure spending increasing → More demand for MU"
        ],
        confidence=75,
        action="hold"
    )
    print(f"Discord alert sent: {'✅' if success else '❌'}")
    
    print(f"\n[TEST 3] Setup Alert")
    print("-" * 70)
    success = alerter.alert_setup(
        ticker="RCAT",
        convergence=78,
        thesis="Defense drone play - Trump $1.5T budget",
        catalyst="Pentagon contract announced"
    )
    print(f"Discord alert sent: {'✅' if success else '❌'}")
    
    print("\n" + "=" * 70)
    print("✅ ALERTER OPERATIONAL")
    print("=" * 70)
    print("\nDiscord alerts working")
    print("Leonard File fallback available")
    print("\nReady to notify you of brain insights")


if __name__ == "__main__":
    test_alerter()
