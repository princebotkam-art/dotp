import requests
import time
import re
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, Set, List, Optional, Tuple

# Configuration - UPDATED WITH FASTER TIMING
CONFIG = {
    "telegram_token": "8402286199:AAEwsLGs7ZcLK2lvdaiYggqn3AJQNFdV94k",
    "group_id": -1002725332877,
    "admin_user_id": 7380687709,
    "api_urls": [
        "http://51.77.216.195/crapi/dgroup/viewstats",
    ],
    "api_token": "RFRTSDRSQnd4V4BEa5Nzd4JoUV2KZpOFimOEiGFnUVhCboODgVJk",
    "check_interval": 10,  # 10 seconds
    "records_per_request": 100,
    "max_retries": 2,
    "retry_delay": 3
}

# Country data with FULL NAMES
COUNTRIES = {
    "Kyrgyzstan": {"short": "KG", "flag": "🇰🇬", "full": "Kyrgyzstan"},
    "Kenya": {"short": "KE", "flag": "🇰🇪", "full": "Kenya"},
    "Nigeria": {"short": "NG", "flag": "🇳🇬", "full": "Nigeria"},
    "India": {"short": "IN", "flag": "🇮🇳", "full": "India"},
    "Pakistan": {"short": "PK", "flag": "🇵🇰", "full": "Pakistan"},
    "Bangladesh": {"short": "BD", "flag": "🇧🇩", "full": "Bangladesh"},
    "Indonesia": {"short": "ID", "flag": "🇮🇩", "full": "Indonesia"},
    "Vietnam": {"short": "VN", "flag": "🇻🇳", "full": "Vietnam"},
    "Brazil": {"short": "BR", "flag": "🇧🇷", "full": "Brazil"},
    "Russia": {"short": "RU", "flag": "🇷🇺", "full": "Russia"},
    "USA": {"short": "US", "flag": "🇺🇸", "full": "USA"},
    "Afghanistan": {"short": "AF", "flag": "🇦🇫", "full": "Afghanistan"},
    "Tanzania": {"short": "TZ", "flag": "🇹🇿", "full": "Tanzania"},
    "Thailand": {"short": "TH", "flag": "🇹🇭", "full": "Thailand"},
    "Togo": {"short": "TG", "flag": "🇹🇬", "full": "Togo"},
    "Tunisia": {"short": "TN", "flag": "🇹🇳", "full": "Tunisia"},
    "Uruguay": {"short": "UY", "flag": "🇺🇾", "full": "Uruguay"},
    "Uzbekistan": {"short": "UZ", "flag": "🇺🇿", "full": "Uzbekistan"},
    "Vanuatu": {"short": "VU", "flag": "🇻🇺", "full": "Vanuatu"},
    "Vatican City": {"short": "VA", "flag": "🇻🇦", "full": "Vatican City"},
    "Venezuela": {"short": "VE", "flag": "🇻🇪", "full": "Venezuela"},
    "Yemen": {"short": "YE", "flag": "🇾🇪", "full": "Yemen"},
    "Zambia": {"short": "ZM", "flag": "🇿🇲", "full": "Zambia"},
    "Unknown": {"short": "XX", "flag": "🏳️", "full": "Unknown"}
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
        self.last_check_time = datetime.now()
        self.continuous_mode = True
        
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
                params = {"offset": offset, "timeout": 10}
                
                response = requests.get(url, params=params, timeout=15)
                
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
                
                time.sleep(0.5)
                
            except Exception as e:
                self.log(f"⚠️ Update handler error: {e}")
                time.sleep(3)
    
    def handle_command(self, command: str, user_id: int, chat_id: int, message_id: int = None):
        """Handle bot commands"""
        command = command.lower()
        
        if command == "/on":
            if user_id == CONFIG["admin_user_id"]:
                if not self.bot_active:
                    self.bot_active = True
                    self.send_group_message("🚀 Bot Started", reply_to=message_id)
                    self.log(f"Bot activated by admin {user_id}")
                else:
                    self.send_group_message("Bot is already active", reply_to=message_id)
            else:
                self.send_group_message("Admin only command", reply_to=message_id)
                
        elif command == "/off":
            if user_id == CONFIG["admin_user_id"]:
                if self.bot_active:
                    self.bot_active = False
                    self.send_group_message("🛑 Bot Stopped", reply_to=message_id)
                    self.log(f"Bot deactivated by admin {user_id}")
                else:
                    self.send_group_message("Bot is already inactive", reply_to=message_id)
            else:
                self.send_group_message("Admin only command", reply_to=message_id)
                
        elif command == "/status":
            status = "🟢 ACTIVE" if self.bot_active else "🔴 INACTIVE"
            last_check = f"Last API: {self.last_api_success}" if self.last_api_success else "API: Never"
            mode = "⚡ FAST MODE" if self.continuous_mode else "🐢 NORMAL MODE"
            message = f"🤖 BOT STATUS\n\n{status}\n{mode}\n{last_check}"
            self.send_group_message(message, reply_to=message_id)
                
        elif command == "/clear":
            if user_id == CONFIG["admin_user_id"]:
                self.processed_messages.clear()
                self.send_group_message("🧹 Cache cleared", reply_to=message_id)
                self.log("Cleared processed messages cache")
        
        elif command == "/fast":
            if user_id == CONFIG["admin_user_id"]:
                self.continuous_mode = True
                CONFIG["check_interval"] = 5
                self.send_group_message("⚡ Fast mode activated", reply_to=message_id)
                
        elif command == "/normal":
            if user_id == CONFIG["admin_user_id"]:
                self.continuous_mode = False
                CONFIG["check_interval"] = 10
                self.send_group_message("🐢 Normal mode activated", reply_to=message_id)
        
        elif command == "/countries":
            countries_list = []
            for i, (name, info) in enumerate(COUNTRIES.items()):
                if name != "Unknown":
                    countries_list.append(f"{info['flag']} {name}")
            
            # Split into chunks of 8 countries each
            chunks = [countries_list[i:i + 8] for i in range(0, len(countries_list), 8)]
            
            for chunk in chunks:
                message = "🌍 **Supported Countries:**\n" + "\n".join(chunk)
                self.send_group_message(message, reply_to=message_id)
    
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
                
            response = requests.post(url, json=payload, timeout=5)
            return response.status_code == 200
                
        except Exception as e:
            self.log(f"Telegram send error: {e}")
            return False
    
    def get_otps_from_api(self) -> List[Dict]:
        """Fetch OTPs from API"""
        current_url = CONFIG["api_urls"][self.current_api_index]
        
        self.log(f"📡 Checking API...")
        
        try:
            params = {
                "token": CONFIG["api_token"],
                "records": CONFIG["records_per_request"]
            }
            
            response = self.session.post(current_url, data=params, timeout=8)
            
            if response.status_code == 200:
                response_text = response.text.strip()
                
                if "too many times" in response_text:
                    self.log(f"⚠️ Rate limited")
                    time.sleep(2)
                    return []
                
                try:
                    data = json.loads(response_text)
                    
                    if isinstance(data, dict) and data.get("status") == "success":
                        records = data.get("data", [])
                        if records:
                            self.log(f"✅ Found {len(records)} records")
                        self.last_api_success = datetime.now().strftime("%H:%M:%S")
                        self.api_error_count = 0
                        return records
                    else:
                        return []
                        
                except json.JSONDecodeError:
                    self.api_error_count += 1
                    return []
            else:
                self.api_error_count += 1
                return []
                
        except Exception as e:
            self.log(f"❌ API Error: {type(e).__name__}")
            self.api_error_count += 1
            return []
    
    def detect_country_from_number(self, phone_number: str) -> str:
        """Detect country from phone number"""
        if not phone_number or phone_number == "Unknown":
            return "Unknown"
            
        num_str = str(phone_number).strip()
        
        # Remove any non-digit characters
        num_str = ''.join(filter(str.isdigit, num_str))
        
        if not num_str:
            return "Unknown"
        
        # Country prefixes
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
            '1': 'USA',
            '93': 'Afghanistan',
            '255': 'Tanzania',
            '66': 'Thailand',
            '228': 'Togo',
            '216': 'Tunisia',
            '598': 'Uruguay',
            '998': 'Uzbekistan',
            '678': 'Vanuatu',
            '379': 'Vatican City',
            '58': 'Venezuela',
            '967': 'Yemen',
            '260': 'Zambia'
        }
        
        for prefix, country in prefixes.items():
            if num_str.startswith(prefix):
                return country
        
        return "Unknown"
    
    def extract_otp_code(self, message: str) -> str:
        """Extract OTP code from message - FIXED FOR WHATSAPP"""
        if not message:
            return "N/A"
        
        # 🔴 FIRST PRIORITY: WhatsApp Business OTP (848-843 format)
        # WhatsApp messages like: "# Kode WhatsApp Business 848-843"
        # or "Your WhatsApp code: 848-843"
        
        whatsapp_patterns = [
            r'WhatsApp Business[\s:]*(\d{3}[-]?\d{3})',
            r'Kode WhatsApp[\s:]*(\d{3}[-]?\d{3})',
            r'WhatsApp code[\s:]*(\d{3}[-]?\d{3})',
            r'kode WhatsApp[\s:]*(\d{3}[-]?\d{3})',
            r'code WhatsApp[\s:]*(\d{3}[-]?\d{3})',
            r'(\d{3}[-]\d{3})[\s]*WhatsApp',
            r'WhatsApp[\s:]*(\d{3}[-]?\d{3})',
            r'(\d{6})[\s]*WhatsApp',  # 848843 without dash
        ]
        
        for pattern in whatsapp_patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            if matches:
                code = matches[0]
                # Remove dash if present
                code = code.replace("-", "")
                self.log(f"✅ Found WhatsApp OTP: {code}")
                return code
        
        # 🔴 SECOND PRIORITY: Standard OTP patterns
        patterns = [
            r'\b\d{4,8}\b',  # Standalone 4-8 digits
            r'code[\s:]*[#]?(\d{4,8})',
            r'kode[\s:]*[#]?(\d{4,8})',
            r'otp[\s:]*[#]?(\d{4,8})',
            r'verification[\s:]*[#]?(\d{4,8})',
            r'password[\s:]*[#]?(\d{4,8})',
            r'pin[\s:]*[#]?(\d{4,8})',
            r'(\d{4,8})[\s]*is[\s]*your',
            r'your[\s]*code[\s]*is[\s]*(\d{4,8})',
            r'code[\s:]*(\d{4,8})',
            r'kode[\s:]*(\d{4,8})',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            if matches:
                code = matches[0]
                self.log(f"✅ Found standard OTP: {code}")
                return code
        
        # 🔴 THIRD PRIORITY: Any 3-8 digit number
        all_numbers = re.findall(r'\d+', message)
        for num in all_numbers:
            if 3 <= len(num) <= 8:
                # Exclude phone numbers and dates
                if not (len(num) >= 10 or num in ['2026', '2025', '2024', '2023', '2022']):
                    self.log(f"✅ Found potential OTP: {num}")
                    return num
        
        self.log(f"❌ No OTP found")
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
        
        # WhatsApp detection (highest priority)
        if 'whatsapp' in cli_lower or 'wa' in cli_lower:
            return "WhatsApp"
        
        if 'whatsapp' in message_lower or 'wa' in message_lower:
            return "WhatsApp"
        
        # Check for WhatsApp code pattern in message
        if re.search(r'\d{3}[-]?\d{3}.*whatsapp', message_lower) or \
           re.search(r'whatsapp.*\d{3}[-]?\d{3}', message_lower):
            return "WhatsApp"
        
        # Other platforms
        if 'facebook' in cli_lower or 'fb' in cli_lower:
            return "Facebook"
        elif 'telegram' in cli_lower or 'tg' in cli_lower:
            return "Telegram"
        elif 'google' in cli_lower or 'gmail' in cli_lower:
            return "Google"
        elif 'instagram' in cli_lower or 'insta' in cli_lower:
            return "Instagram"
        
        if 'facebook' in message_lower or 'fb' in message_lower:
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
        """Create formatted OTP message with FULL COUNTRY NAMES"""
        try:
            phone = otp_data.get("num", "")
            cli = otp_data.get("cli", "")
            message_text = otp_data.get("message", "")
            timestamp = otp_data.get("dt", "")
            
            if not message_text:
                return None
            
            # 🔴 Extract OTP code
            otp_code = self.extract_otp_code(message_text)
            
            if otp_code == "N/A":
                return None
            
            # Detect platform
            platform = self.detect_platform(message_text, cli)
            
            # 🔴 Detect country with FULL NAME
            country = self.detect_country_from_number(phone)
            country_info = COUNTRIES.get(country, COUNTRIES["Unknown"])
            
            # 🔴 Use FULL country name from dictionary
            country_name = country_info["full"]
            country_flag = country_info["flag"]
            country_code = country_info["short"]
            
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
            
            # Special formatting for WhatsApp
            if platform == "WhatsApp":
                platform_display = "WhatsApp Business"
            else:
                platform_display = platform
            
            # Clean message
            cleaned_message = message_text.replace('\n\n', '\n').strip()
            
            # 🔴 Create message with FULL COUNTRY NAME
            formatted_message = (
                f"══════════════════════\n"
                f"    🚨 *NEW OTP RECEIVED* 🚨\n"
                f"══════════════════════\n\n"
                f"{platform_emoji} *Platform:* {platform_display}\n"
                f"📱 *Number:* `{formatted_phone}`\n"
                f"🌍 *Country:* {country_flag} {country_name} (#{country_code})\n"
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
            
            response = requests.post(url, json=payload, timeout=8)
            return response.status_code == 200
                
        except Exception as e:
            return False
    
    def process_otps(self):
        """Process OTPs"""
        if not self.bot_active:
            return 0
        
        otp_list = self.get_otps_from_api()
        
        if not otp_list:
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
                # Create and send message
                message = self.create_otp_message(otp_data)
                
                if message:
                    # Extract OTP for logging
                    otp_code = self.extract_otp_code(message_text)
                    platform = self.detect_platform(message_text, cli)
                    country = self.detect_country_from_number(phone)
                    
                    self.log(f"  ✅ {platform} | {country} | {phone} | OTP: {otp_code}")
                    
                    if self.send_otp_to_telegram(message):
                        self.processed_messages.add(unique_id)
                        sent_count += 1
                        self.log(f"  📤 Sent to Telegram")
                    else:
                        self.log(f"  ❌ Failed to send")
                    
                    time.sleep(1)
        
        return sent_count
    
    def send_welcome_message(self):
        """Send welcome message"""
        try:
            welcome_msg = (
                "🤖 *JS OTP BOT STARTED*\n\n"
                "✅ *Features:*\n"
                "• ⚡ Fast OTP delivery (5-10 seconds)\n"
                "• 🌍 Full country names\n"
                "• 📱 WhatsApp OTP support\n"
                "• 🔍 Smart OTP detection\n\n"
                "📋 *Commands:*\n"
                "/on - Start bot\n"
                "/off - Stop bot\n"
                "/status - Check status\n"
                "/fast - Fast mode (5s)\n"
                "/normal - Normal mode (10s)\n"
                "/countries - Show supported countries"
            )
            self.send_group_message(welcome_msg)
            self.log("✅ Welcome message sent")
            
        except Exception as e:
            self.log(f"⚠️ Welcome message error: {e}")
    
    def run(self):
        """Main bot loop"""
        print("=" * 60)
        print("🤖 JS OTP BOT - ENHANCED VERSION")
        print("=" * 60)
        print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⚡ Mode: Fast (Check every {CONFIG['check_interval']}s)")
        print(f"🌍 Countries: {len(COUNTRIES)-1} supported")
        print("=" * 60)
        
        update_thread = threading.Thread(target=self.handle_telegram_updates, daemon=True)
        update_thread.start()
        time.sleep(1)
        
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
                    
                    sleep_time = 5 if self.continuous_mode else CONFIG["check_interval"]
                    self.log(f"⏳ Next check in {sleep_time}s")
                    time.sleep(sleep_time)
                else:
                    self.log(f"⏸️ Bot inactive")
                    time.sleep(10)
                
        except KeyboardInterrupt:
            self.log("🛑 Bot stopped manually")
            self.send_group_message("🛑 Bot Stopped")
        except Exception as e:
            self.log(f"💥 Fatal error: {e}")
            import traceback
            traceback.print_exc()

def main():
    """Main function"""
    print("\n" + "="*60)
    print("JS OTP BOT - ENHANCED VERSION")
    print("="*60)
    print("🎯 **ENHANCED FEATURES:**")
    print("• 🌍 FULL Country names in messages")
    print("• 📱 WhatsApp OTP detection (848-843 format)")
    print("• ⚡ OTPs delivered in 5-10 seconds")
    print("• 🇰🇬 23+ countries supported")
    print("• 📊 Better OTP extraction")
    print("="*60 + "\n")
    
    bot = OTPBot()
    bot.run()

if __name__ == "__main__":
    main()
