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
    "api_url": "http://51.77.216.195/crapi/dgroup/viewstats",
    "api_token": "RFRTSDRSQnd4V4BEa5Nzd4JoUV2KZpOFimOEiGFnUVhCboODgVJk",
    "check_interval": 10,
    "records_per_request": 50,
    "max_retries": 2,
    "retry_delay": 3
}

# Country data
COUNTRIES = {
    "Kyrgyzstan": {"short": "KG", "flag": "🇰🇬"},
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
        self.bot_start_time = datetime.now()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Connection': 'keep-alive',
            'Accept-Language': 'en-US,en;q=0.9',
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
                    self.bot_start_time = datetime.now()
                    self.send_group_message("Bot Started - Only new OTPs will be sent", reply_to=message_id)
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
            bot_uptime = (datetime.now() - self.bot_start_time).seconds
            uptime_str = f"{bot_uptime // 60}m {bot_uptime % 60}s"
            message = f"🤖 BOT STATUS\n\n{status}\n⏰ Uptime: {uptime_str}\n📊 Processed: {len(self.processed_messages)}\n{last_check}"
            self.send_group_message(message, reply_to=message_id)
                
        elif command == "/clear":
            if user_id == CONFIG["admin_user_id"]:
                self.processed_messages.clear()
                self.bot_start_time = datetime.now()
                self.send_group_message("Cache cleared - Bot will send only new OTPs", reply_to=message_id)
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
    
    def test_api_connection(self):
        """Test API connection with different parameters"""
        self.log("🔍 Testing API connection...")
        
        # Different parameter combinations to try
        param_combinations = [
            # Format 1: With time range
            {
                "token": CONFIG["api_token"],
                "dt1": (datetime.now() - timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S"),
                "dt2": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "records": 10
            },
            # Format 2: Without time range
            {
                "token": CONFIG["api_token"],
                "records": 10
            },
            # Format 3: Minimal
            {
                "token": CONFIG["api_token"]
            },
            # Format 4: Alternative
            {
                "token": CONFIG["api_token"],
                "limit": 10
            }
        ]
        
        for i, params in enumerate(param_combinations):
            self.log(f"  Trying parameter set {i+1}: {list(params.keys())}")
            
            try:
                # Try POST
                response = self.session.post(CONFIG["api_url"], data=params, timeout=10)
                self.log(f"    POST Status: {response.status_code}")
                if response.status_code == 200:
                    self.log(f"    POST Response: {response.text[:200]}...")
                    
                    # Try to parse
                    try:
                        data = json.loads(response.text)
                        self.log(f"    ✅ JSON parsed: {data.get('status', 'No status')}")
                        if data.get("status") == "success":
                            self.log(f"    🎯 SUCCESS with set {i+1}")
                            return True, params
                    except:
                        self.log(f"    ⚠️ Not JSON")
                
                # Try GET
                response = self.session.get(CONFIG["api_url"], params=params, timeout=10)
                self.log(f"    GET Status: {response.status_code}")
                if response.status_code == 200:
                    self.log(f"    GET Response: {response.text[:200]}...")
                    
                    try:
                        data = json.loads(response.text)
                        self.log(f"    ✅ JSON parsed: {data.get('status', 'No status')}")
                        if data.get("status") == "success":
                            self.log(f"    🎯 SUCCESS with set {i+1} (GET)")
                            return True, params
                    except:
                        self.log(f"    ⚠️ Not JSON")
                
                time.sleep(1)
                
            except Exception as e:
                self.log(f"    ❌ Error: {e}")
        
        return False, None
    
    def get_otps_from_api(self) -> List[Dict]:
        """Fetch OTPs from API - Improved version"""
        self.log("📡 Fetching OTPs...")
        
        # If too many errors, test connection first
        if self.api_error_count >= 3:
            self.log("⚠️ Too many errors, testing API...")
            success, working_params = self.test_api_connection()
            if not success:
                self.log("❌ API test failed")
                return []
        
        try:
            # Try different time windows
            time_windows = [5, 10, 30]  # 5, 10, 30 minutes
            
            for minutes in time_windows:
                dt2 = datetime.now()
                dt1 = dt2 - timedelta(minutes=minutes)
                
                # Try different parameter formats
                param_formats = [
                    # Standard format
                    {
                        "token": CONFIG["api_token"],
                        "dt1": dt1.strftime("%Y-%m-%d %H:%M:%S"),
                        "dt2": dt2.strftime("%Y-%m-%d %H:%M:%S"),
                        "records": CONFIG["records_per_request"]
                    },
                    # Alternative format
                    {
                        "token": CONFIG["api_token"],
                        "start": dt1.strftime("%Y-%m-%d %H:%M:%S"),
                        "end": dt2.strftime("%Y-%m-%d %H:%M:%S"),
                        "limit": CONFIG["records_per_request"]
                    },
                    # Simple format
                    {
                        "token": CONFIG["api_token"],
                        "limit": CONFIG["records_per_request"]
                    }
                ]
                
                for params in param_formats:
                    self.log(f"  Trying {minutes}min window with params: {list(params.keys())}")
                    
                    try:
                        # Try POST first
                        response = self.session.post(CONFIG["api_url"], data=params, timeout=15)
                        
                        if response.status_code == 200:
                            response_text = response.text.strip()
                            
                            # Check for rate limiting
                            if "too many times" in response_text.lower():
                                self.log(f"  ⏰ Rate limited, waiting 5s...")
                                time.sleep(5)
                                continue
                            
                            # Try to parse response
                            try:
                                data = json.loads(response_text)
                                self.log(f"  ✅ Got JSON response")
                                
                                # Check different response formats
                                if isinstance(data, dict):
                                    # Format 1: status = "success"
                                    if data.get("status") == "success":
                                        records = data.get("data", [])
                                        self.log(f"  🎯 Found {len(records)} records (status: success)")
                                        self.last_api_success = datetime.now().strftime("%H:%M:%S")
                                        self.api_error_count = 0
                                        return self.filter_new_records(records)
                                    
                                    # Format 2: has "data" key
                                    elif "data" in data and isinstance(data["data"], list):
                                        records = data.get("data", [])
                                        self.log(f"  🎯 Found {len(records)} records (has data key)")
                                        self.last_api_success = datetime.now().strftime("%H:%M:%S")
                                        self.api_error_count = 0
                                        return self.filter_new_records(records)
                                    
                                    # Format 3: direct array in dict
                                    elif any(isinstance(data.get(k), list) for k in data):
                                        for key, value in data.items():
                                            if isinstance(value, list) and value:
                                                # Check if it looks like OTP data
                                                if all(isinstance(item, dict) and any(f in item for f in ["num", "message", "phone"]) for item in value[:2]):
                                                    self.log(f"  🎯 Found {len(value)} records in key '{key}'")
                                                    self.last_api_success = datetime.now().strftime("%H:%M:%S")
                                                    self.api_error_count = 0
                                                    return self.filter_new_records(value)
                                    
                                    else:
                                        self.log(f"  ⚠️ Dict but no recognized format: {list(data.keys())}")
                                
                                # If response is a list directly
                                elif isinstance(data, list):
                                    self.log(f"  🎯 Found {len(data)} records (direct list)")
                                    self.last_api_success = datetime.now().strftime("%H:%M:%S")
                                    self.api_error_count = 0
                                    return self.filter_new_records(data)
                                
                            except json.JSONDecodeError:
                                self.log(f"  ⚠️ Response not JSON: {response_text[:100]}")
                                # Check if it's HTML error page
                                if "<html" in response_text.lower() or "<!doctype" in response_text.lower():
                                    self.log(f"  ❌ Got HTML page, API might be down")
                                continue
                        
                        else:
                            self.log(f"  ❌ HTTP {response.status_code}")
                    
                    except Exception as e:
                        self.log(f"  ⚠️ Request error: {e}")
                    
                    time.sleep(1)  # Small delay between attempts
            
            self.api_error_count += 1
            self.log(f"❌ All attempts failed")
            return []
                
        except Exception as e:
            self.log(f"❌ API Error: {type(e).__name__}: {str(e)}")
            self.api_error_count += 1
            return []
    
    def filter_new_records(self, records: List[Dict]) -> List[Dict]:
        """Filter only records that arrived after bot started"""
        filtered = []
        
        for record in records:
            record_time_str = record.get("dt", "")
            
            if record_time_str:
                try:
                    record_time = datetime.strptime(record_time_str, "%Y-%m-%d %H:%M:%S")
                    # Only include records after bot started
                    if record_time > self.bot_start_time:
                        filtered.append(record)
                    else:
                        self.log(f"  ⏰ Skipping old record from {record_time_str}")
                except:
                    # If can't parse time, include it
                    filtered.append(record)
            else:
                # If no timestamp, include it
                filtered.append(record)
        
        self.log(f"  📊 After filtering: {len(filtered)} new records")
        return filtered
    
    def detect_country_from_number(self, phone_number: str) -> str:
        """Detect country from phone number"""
        if not phone_number or phone_number == "Unknown":
            return "Unknown"
            
        num_str = str(phone_number).strip()
        
        prefixes = {
            '996': 'Kyrgyzstan',
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
        """Extract OTP code from message"""
        if not message:
            return "N/A"
        
        # WhatsApp patterns
        patterns = [
            r'WhatsApp Business\s*(\d{3}[-]?\d{3})',
            r'Kode WhatsApp.*?(\d{3}[-]?\d{3})',
            r'(\d{3}[-]?\d{3}).*?WhatsApp',
            r'code.*?(\d{3}[-]?\d{3})',
            r'kode.*?(\d{3}[-]?\d{3})',
            r'\b\d{4,8}\b',
            r'code[\s:]*[#]?(\d{4,8})',
            r'kode[\s:]*[#]?(\d{4,8})',
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
                if "-" in code:
                    return code.replace("-", "")
                return code
        
        # Any 3-8 digit number
        all_numbers = re.findall(r'\d+', message)
        for num in all_numbers:
            if 3 <= len(num) <= 8:
                if not (len(num) >= 10 or num in ['2026', '2025', '2024']):
                    return num
        
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
        
        if 'whatsapp' in cli_lower or 'whatsapp' in message_lower or 'wa' in message_lower:
            return "WhatsApp"
        elif 'facebook' in cli_lower or 'facebook' in message_lower or 'fb' in message_lower:
            return "Facebook"
        elif 'telegram' in cli_lower or 'telegram' in message_lower or 'tg' in message_lower:
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
            
            otp_code = self.extract_otp_code(message_text)
            
            if otp_code == "N/A":
                return None
            
            platform = self.detect_platform(message_text, cli)
            country = self.detect_country_from_number(phone)
            country_info = COUNTRIES.get(country, COUNTRIES["Unknown"])
            formatted_phone = self.format_phone_number(phone)
            
            # Calculate how fresh
            freshness = ""
            if timestamp:
                try:
                    msg_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                    seconds_ago = (datetime.now() - msg_time).seconds
                    if seconds_ago < 60:
                        freshness = f" ({seconds_ago}s ago)"
                    else:
                        freshness = f" ({seconds_ago//60}m ago)"
                except:
                    pass
            
            platform_emoji = {
                "WhatsApp": "📱",
                "Facebook": "👤",
                "Telegram": "📨",
                "Google": "🔍",
                "Instagram": "📸",
                "SMS": "💬"
            }.get(platform, "📲")
            
            formatted_message = (
                f"══════════════════════\n"
                f"    🚨 *LIVE OTP RECEIVED* 🚨\n"
                f"══════════════════════\n\n"
                f"{platform_emoji} *Platform:* {platform}\n"
                f"📱 *Number:* `{formatted_phone}`\n"
                f"🌍 *Country:* {country_info['flag']} #{country_info['short']}\n"
                f"⏰ *Freshness:* Just now{freshness}\n\n"
                f"🔐 *OTP Code:* `{otp_code}`\n\n"
                f"💬 *Message:*\n"
                f"`{message_text}`"
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
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                return True
            else:
                self.log(f"❌ Telegram error: {response.status_code}")
                return False
                
        except Exception as e:
            self.log(f"❌ Telegram send error: {e}")
            return False
    
    def process_otps(self):
        """Process OTPs"""
        if not self.bot_active:
            return 0
        
        otp_list = self.get_otps_from_api()
        
        if not otp_list:
            return 0
        
        self.log(f"📨 Processing {len(otp_list)} new OTPs")
        sent_count = 0
        
        for otp_data in otp_list:
            message_text = otp_data.get("message", "")
            phone = otp_data.get("num", "")
            timestamp = otp_data.get("dt", "")
            
            unique_id = f"{phone}_{timestamp}_{hash(message_text[:100])}"
            
            if unique_id not in self.processed_messages:
                otp_code = self.extract_otp_code(message_text)
                
                if otp_code != "N/A":
                    message = self.create_otp_message(otp_data)
                    
                    if message:
                        platform = self.detect_platform(message_text, otp_data.get("cli", ""))
                        
                        self.log(f"  🚀 SENDING: {platform} | {phone} | OTP: {otp_code}")
                        
                        if self.send_otp_to_telegram(message):
                            self.processed_messages.add(unique_id)
                            sent_count += 1
                            self.log(f"  ✅ INSTANT DELIVERY")
                        
                        time.sleep(0.5)
        
        return sent_count
    
    def send_welcome_message(self):
        """Send welcome message"""
        try:
            message = (
                "🤖 *LIVE OTP BOT STARTED*\n\n"
                "✅ Bot is now **ACTIVE**\n"
                "⚡ *Real-time monitoring* enabled\n"
                "⏰ Checking every *10 seconds*\n\n"
                "🚨 **Only NEW OTPs will be sent**\n"
                "(OTPs before bot start are ignored)\n\n"
                "🔔 OTPs will appear here instantly!"
            )
            self.send_group_message(message)
            self.log("✅ Welcome message sent")
            
        except Exception as e:
            self.log(f"⚠️ Welcome message error: {e}")
    
    def run(self):
        """Main bot loop"""
        print("=" * 60)
        print("🤖 JS OTP BOT - REAL TIME")
        print("=" * 60)
        print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⚡ Check interval: {CONFIG['check_interval']}s")
        print("=" * 60)
        
        # Test API connection first
        self.log("🔍 Testing API connection on startup...")
        success, params = self.test_api_connection()
        if success:
            self.log("✅ API connection successful")
        else:
            self.log("⚠️ API connection test failed, but continuing...")
        
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
                    self.log(f"🔄 Quick Check #{check_count}")
                    sent_now = self.process_otps()
                    total_sent += sent_now
                    
                    if sent_now > 0:
                        self.log(f"⚡ Delivered: {sent_now} OTPs (Total: {total_sent})")
                    
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
    print("JS OTP BOT - WORKING VERSION")
    print("="*60)
    print("🎯 Features:")
    print("• Multiple API parameter tests")
    print("• Only new OTPs after bot start")
    print("• Real-time delivery")
    print("• Better error handling")
    print("="*60 + "\n")
    
    bot = OTPBot()
    bot.run()

if __name__ == "__main__":
    main()
