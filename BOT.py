import requests
import time
import re
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, Set, List, Optional, Tuple

# Configuration
CONFIG = {
    "telegram_token": "8402286199:AAEwsLGs7ZcLK2lvdaiYggqn3AJQNFdV94k",
    "group_id": -1002725332877,
    "admin_user_id": 7380687709,
    "api_urls": [
        "http://51.77.216.195/crapi/dgroup/viewstats",
    ],
    "api_token": "RFRTSDRSQnd4V4BEa5Nzd4JoUV2KZpOFimOEiGFnUVhCboODgVJk",
    "check_interval": 30,
    "records_per_request": 100,
    "max_retries": 2,
    "retry_delay": 5
}

# Country data
COUNTRIES = {
    "Kyrgyzstan": {"short": "KG", "flag": "🇰🇬"},  # 996 code
    "Kenya": {"short": "KE", "flag": "🇰🇪"},
    "Nigeria": {"short": "NG", "flag": "🇳🇬"},
    "India": {"short": "IN", "flag": "🇮🇳"},
    "Pakistan": {"short": "PK", "flag": "🇵🇰"},
    "Bangladesh": {"short": "BD", "flag": "🇧🇩"},
    "Indonesia": {"short": "ID", "flag": "🇮🇩"},
    "Vietnam": {"short": "VN", "flag": "🇻🇳"},
    "Brazil": {"short": "BR", "flag": "🇧🇷"},
    "Russia": {"short": "RU", "flag": "🇷🇺"},
    "USA": {"short": "US", "flag": "🇺🇸"},
    "Unknown": {"short": "XX", "flag": "🏳️"}
}

class OTPBot:
    def __init__(self):
        self.processed_messages: Set[str] = set()
        self.bot_active = True
        self.last_api_success = None
        self.api_error_count = 0
        self.current_api_index = 0
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Connection': 'keep-alive'
        })
        
    def log(self, message: str):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def handle_telegram_updates(self):
        """Handle Telegram updates"""
        self.log("📡 Starting Telegram update handler...")
        
        offset = 0
        while True:
            try:
                url = f"https://api.telegram.org/bot{CONFIG['telegram_token']}/getUpdates"
                params = {"offset": offset, "timeout": 30}
                
                response = requests.get(url, params=params, timeout=35)
                
                if response.status_code == 200:
                    updates = response.json().get("result", [])
                    
                    for update in updates:
                        offset = update["update_id"] + 1
                        
                        if "message" in update:
                            message = update["message"]
                            chat_id = message["chat"]["id"]
                            user_id = message["from"]["id"]
                            message_id = message.get("message_id", 0)
                            
                            if chat_id == CONFIG["group_id"] and "text" in message:
                                text = message["text"].strip()
                                self.handle_command(text, user_id, chat_id, message_id)
                
                time.sleep(1)
                
            except Exception as e:
                self.log(f"⚠️ Update handler error: {e}")
                time.sleep(5)
    
    def handle_command(self, command: str, user_id: int, chat_id: int, message_id: int = None):
        """Handle bot commands"""
        command = command.lower()
        
        if command == "/on":
            if user_id == CONFIG["admin_user_id"]:
                if not self.bot_active:
                    self.bot_active = True
                    self.send_group_message("Bot Started", reply_to=message_id)
                    self.log(f"Bot activated by admin {user_id}")
                else:
                    self.send_group_message("Bot is already active", reply_to=message_id)
            else:
                self.send_group_message("Admin only command", reply_to=message_id)
                
        elif command == "/off":
            if user_id == CONFIG["admin_user_id"]:
                if self.bot_active:
                    self.bot_active = False
                    self.send_group_message("Bot Stopped", reply_to=message_id)
                    self.log(f"Bot deactivated by admin {user_id}")
                else:
                    self.send_group_message("Bot is already inactive", reply_to=message_id)
            else:
                self.send_group_message("Admin only command", reply_to=message_id)
                
        elif command == "/status":
            status = "🟢 ACTIVE" if self.bot_active else "🔴 INACTIVE"
            last_check = f"Last API: {self.last_api_success}" if self.last_api_success else "API: Never"
            message = f"🤖 BOT STATUS\n\n{status}\n{last_check}"
            self.send_group_message(message, reply_to=message_id)
                
        elif command == "/clear":
            if user_id == CONFIG["admin_user_id"]:
                self.processed_messages.clear()
                self.send_group_message("Cache cleared", reply_to=message_id)
                self.log("Cleared processed messages cache")
    
    def send_group_message(self, message: str, reply_to: int = None):
        """Send message to Telegram group"""
        try:
            url = f"https://api.telegram.org/bot{CONFIG['telegram_token']}/sendMessage"
            payload = {
                "chat_id": CONFIG['group_id'],
                "text": message,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True
            }
            if reply_to:
                payload["reply_to_message_id"] = reply_to
                
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
                
        except Exception as e:
            self.log(f"Telegram send error: {e}")
            return False
    
    def get_otps_from_api(self) -> List[Dict]:
        """Fetch OTPs from API"""
        current_url = CONFIG["api_urls"][self.current_api_index]
        
        self.log(f"📡 Using API: {current_url}")
        
        try:
            # Wait if too many requests
            if self.api_error_count > 0:
                time.sleep(5)
            
            params = {
                "token": CONFIG["api_token"],
                "records": CONFIG["records_per_request"]
            }
            
            # Try POST
            response = self.session.post(current_url, data=params, timeout=15)
            
            if response.status_code == 200:
                response_text = response.text.strip()
                
                # Check if it's rate limit error
                if "too many times" in response_text:
                    self.log(f"⚠️ Rate limited, waiting 5 seconds...")
                    time.sleep(5)
                    return []
                
                # Try to parse JSON
                try:
                    data = json.loads(response_text)
                    
                    if isinstance(data, dict) and data.get("status") == "success":
                        records = data.get("data", [])
                        self.log(f"✅ Found {len(records)} records")
                        self.last_api_success = datetime.now().strftime("%H:%M:%S")
                        self.api_error_count = 0
                        return records
                    else:
                        self.log(f"⚠️ JSON but not success: {response_text[:100]}")
                        return []
                        
                except json.JSONDecodeError:
                    self.log(f"❌ Not JSON: {response_text[:100]}")
                    self.api_error_count += 1
                    return []
            else:
                self.log(f"❌ HTTP {response.status_code}")
                self.api_error_count += 1
                return []
                
        except Exception as e:
            self.log(f"❌ API Error: {type(e).__name__}: {str(e)}")
            self.api_error_count += 1
            return []
    
    def detect_country_from_number(self, phone_number: str) -> str:
        """Detect country from phone number"""
        if not phone_number or phone_number == "Unknown":
            return "Unknown"
            
        num_str = str(phone_number).strip()
        
        prefixes = {
            '996': 'Kyrgyzstan',  # WhatsApp code দেখেছি
            '254': 'Kenya',
            '91': 'India',
            '234': 'Nigeria',
            '92': 'Pakistan',
            '880': 'Bangladesh',
            '62': 'Indonesia',
            '84': 'Vietnam',
            '55': 'Brazil',
            '7': 'Russia',
            '1': 'USA'
        }
        
        for prefix, country in prefixes.items():
            if num_str.startswith(prefix):
                return country
        
        return "Unknown"
    
    def extract_otp_code(self, message: str) -> str:
        """Extract OTP code from message - IMPROVED VERSION"""
        if not message:
            return "N/A"
        
        # Log the message for debugging
        self.log(f"🔍 Extracting OTP from: {message[:50]}...")
        
        # WhatsApp Business pattern (আপনার পাওয়া মেসেজ থেকে)
        # "# Kode WhatsApp Business 848-843"
        whatsapp_patterns = [
            r'WhatsApp Business\s*(\d{3}[-]?\d{3})',  # 848-843
            r'Kode WhatsApp.*?(\d{3}[-]?\d{3})',  # Kode WhatsApp 848-843
            r'(\d{3}[-]?\d{3}).*?WhatsApp',  # 848-843 WhatsApp
            r'code.*?(\d{3}[-]?\d{3})',  # code 848-843
            r'kode.*?(\d{3}[-]?\d{3})',  # kode 848-843 (Indonesian)
        ]
        
        for pattern in whatsapp_patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            if matches:
                code = matches[0]
                self.log(f"✅ Found WhatsApp code: {code}")
                return code.replace("-", "")  # 848843 return করবে
        
        # Standard OTP patterns
        patterns = [
            r'\b\d{4,8}\b',  # 4-8 digit standalone
            r'code[\s:]*[#]?(\d{4,8})',
            r'kode[\s:]*[#]?(\d{4,8})',  # Indonesian "kode"
            r'otp[\s:]*[#]?(\d{4,8})',
            r'verification[\s:]*[#]?(\d{4,8})',
            r'password[\s:]*[#]?(\d{4,8})',
            r'pin[\s:]*[#]?(\d{4,8})',
            r'(\d{4,8})[\s]*is[\s]*your',
            r'your[\s]*code[\s]*is[\s]*(\d{4,8})'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            if matches:
                code = matches[0]
                self.log(f"✅ Found standard OTP: {code}")
                return code
        
        # Try to find any 3-8 digit number
        all_numbers = re.findall(r'\d+', message)
        for num in all_numbers:
            if 3 <= len(num) <= 8:
                # Check if it's not likely a phone number or date
                if not (len(num) >= 10 or num in ['2026', '2025', '2024']):
                    self.log(f"✅ Found potential OTP ({len(num)} digits): {num}")
                    return num
        
        self.log(f"❌ No OTP found in message")
        return "N/A"
    
    def format_phone_number(self, phone_number: str) -> str:
        """Format phone number for display"""
        if not phone_number or phone_number == "Unknown":
            return "N/A"
        
        digits = ''.join(filter(str.isdigit, str(phone_number)))
        
        if not digits:
            return "N/A"
        
        if len(digits) >= 9:
            return f"{digits[:5]}****{digits[-4:]}"
        elif 6 <= len(digits) <= 8:
            return f"{digits[:3]}****{digits[-3:]}"
        else:
            if len(digits) > 4:
                return f"{digits[:2]}****{digits[-2:]}"
            return digits
    
    def detect_platform(self, message: str, cli: str = "") -> str:
        """Detect platform from message and CLI"""
        message_lower = message.lower()
        cli_lower = cli.lower() if cli else ""
        
        # Check CLI first
        if 'whatsapp' in cli_lower:
            return "WhatsApp"
        elif 'facebook' in cli_lower or 'fb' in cli_lower:
            return "Facebook"
        elif 'telegram' in cli_lower or 'tg' in cli_lower:
            return "Telegram"
        
        # Check message content
        if 'whatsapp' in message_lower or 'wa' in message_lower:
            return "WhatsApp"
        elif 'facebook' in message_lower or 'fb' in message_lower:
            return "Facebook"
        elif 'telegram' in message_lower or 'tg' in message_lower:
            return "Telegram"
        elif 'google' in message_lower or 'gmail' in message_lower:
            return "Google"
        elif 'instagram' in message_lower or 'insta' in message_lower:
            return "Instagram"
        else:
            return "SMS"
    
    def create_otp_message(self, otp_data: Dict) -> Optional[str]:
        """Create formatted OTP message"""
        try:
            phone = otp_data.get("num", "")
            cli = otp_data.get("cli", "")
            message_text = otp_data.get("message", "")
            timestamp = otp_data.get("dt", "")
            
            if not message_text:
                return None
            
            # Extract OTP code - IMPORTANT: সবচেয়ে আগে
            otp_code = self.extract_otp_code(message_text)
            
            if otp_code == "N/A":
                self.log(f"❌ No OTP code found in message")
                return None
            
            # Detect platform and country
            platform = self.detect_platform(message_text, cli)
            country = self.detect_country_from_number(phone)
            country_info = COUNTRIES.get(country, COUNTRIES["Unknown"])
            formatted_phone = self.format_phone_number(phone)
            
            # Format timestamp
            if timestamp:
                try:
                    msg_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                    time_str = msg_time.strftime("%I:%M %p")
                except:
                    time_str = datetime.now().strftime("%I:%M %p")
            else:
                time_str = datetime.now().strftime("%I:%M %p")
            
            # Platform emoji
            platform_emoji = {
                "WhatsApp": "📱",
                "Facebook": "👤",
                "Telegram": "📨",
                "Google": "🔍",
                "Instagram": "📸",
                "SMS": "💬"
            }.get(platform, "📲")
            
            # Clean message text (remove excessive newlines)
            cleaned_message = message_text.replace('\n\n', '\n').strip()
            
            # Create message
            formatted_message = (
                f"══════════════════════\n"
                f"    🚨 *NEW OTP RECEIVED* 🚨\n"
                f"══════════════════════\n\n"
                f"{platform_emoji} *Platform:* {platform}\n"
                f"📱 *Number:* `{formatted_phone}`\n"
                f"🌍 *Country:* {country_info['flag']} #{country_info['short']}\n"
                f"⏰ *Time:* {time_str}\n\n"
                f"🔐 *OTP Code:* `{otp_code}`\n\n"
                f"💬 *Message:*\n"
                f"`{cleaned_message}`"
            )
            
            return formatted_message
            
        except Exception as e:
            self.log(f"❌ Error creating message: {e}")
            return None
    
    def send_otp_to_telegram(self, message: str) -> bool:
        """Send OTP message to Telegram"""
        try:
            url = f"https://api.telegram.org/bot{CONFIG['telegram_token']}/sendMessage"
            
            keyboard = {
                "inline_keyboard": [
                    [
                        {"text": "📞 Number Channel", "url": "https://t.me/jsworktg"},
                        {"text": "📢 Official Group", "url": "https://t.me/JSofficialgroup"}
                    ]
                ]
            }
            
            payload = {
                "chat_id": CONFIG['group_id'],
                "text": message,
                "parse_mode": "Markdown",
                "reply_markup": json.dumps(keyboard),
                "disable_web_page_preview": True
            }
            
            response = requests.post(url, json=payload, timeout=15)
            
            if response.status_code == 200:
                return True
            else:
                self.log(f"❌ Telegram error: {response.status_code}")
                return False
                
        except Exception as e:
            self.log(f"❌ Telegram send error: {e}")
            return False
    
    def process_otps(self):
        """Process OTPs - SIMPLIFIED"""
        if not self.bot_active:
            return 0
        
        otp_list = self.get_otps_from_api()
        
        if not otp_list:
            self.log("📭 No messages from API")
            return 0
        
        self.log(f"📨 Processing {len(otp_list)} messages")
        sent_count = 0
        
        for otp_data in otp_list:
            message_text = otp_data.get("message", "")
            phone = otp_data.get("num", "")
            cli = otp_data.get("cli", "")
            timestamp = otp_data.get("dt", "")
            
            # Create unique ID
            unique_id = f"{phone}_{message_text}_{timestamp}"
            
            if unique_id not in self.processed_messages:
                # Log the raw data
                self.log(f"📝 Raw data: {phone} | {cli} | {message_text[:50]}...")
                
                # Create and send message
                message = self.create_otp_message(otp_data)
                
                if message:
                    # Extract OTP code again for logging
                    otp_code = self.extract_otp_code(message_text)
                    platform = self.detect_platform(message_text, cli)
                    
                    self.log(f"  ✅ {platform} | {phone} | OTP: {otp_code}")
                    
                    if self.send_otp_to_telegram(message):
                        self.processed_messages.add(unique_id)
                        sent_count += 1
                        self.log(f"  📤 Sent to Telegram")
                    else:
                        self.log(f"  ❌ Failed to send")
                    
                    time.sleep(2)  # Avoid rate limiting
                else:
                    self.log(f"  ⚠️ Skipped - no OTP found")
        
        return sent_count
    
    def send_welcome_message(self):
        """Send welcome message"""
        try:
            self.send_group_message("Bot Started")
            self.log("✅ Welcome message sent")
            
        except Exception as e:
            self.log(f"⚠️ Welcome message error: {e}")
    
    def run(self):
        """Main bot loop"""
        print("=" * 60)
        print("🤖 JS OTP BOT - WORKING VERSION")
        print("=" * 60)
        print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        update_thread = threading.Thread(target=self.handle_telegram_updates, daemon=True)
        update_thread.start()
        time.sleep(2)
        
        self.send_welcome_message()
        
        total_sent = 0
        check_count = 0
        
        try:
            while True:
                check_count += 1
                
                if self.bot_active:
                    self.log(f"🔄 Check #{check_count}")
                    sent_now = self.process_otps()
                    total_sent += sent_now
                    
                    if sent_now > 0:
                        self.log(f"📤 Sent {sent_now} messages (Total: {total_sent})")
                    else:
                        self.log(f"📭 No new messages")
                    
                    self.log(f"⏳ Next check in {CONFIG['check_interval']}s")
                else:
                    self.log(f"⏸️ Check #{check_count} - Bot inactive")
                
                print("-" * 40)
                time.sleep(CONFIG['check_interval'])
                
        except KeyboardInterrupt:
            self.log("🛑 Bot stopped manually")
            self.send_group_message("Bot Stopped")
        except Exception as e:
            self.log(f"💥 Fatal error: {e}")
            import traceback
            traceback.print_exc()

def main():
    """Main function"""
    print("\n" + "="*60)
    print("JS OTP BOT - FINAL VERSION")
    print("="*60)
    print("🎯 Features:")
    print("• WhatsApp OTP detection (848-843 format)")
    print("• No dummy messages")
    print("• Real API data only")
    print("="*60 + "\n")
    
    bot = OTPBot()
    bot.run()

if __name__ == "__main__":
    main()
