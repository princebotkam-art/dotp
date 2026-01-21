import requests
import time
import re
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, Set, List, Optional, Tuple

# Configuration - Ultra Real-time monitoring
CONFIG = {
    "telegram_token": "8402286199:AAEwsLGs7ZcLK2lvdaiYggqn3AJQNFdV94k",
    "group_id": -1002725332877,
    "admin_user_id": 7380687709,
    "api_url": "http://51.77.216.195/crapi/dgroup/viewstats",
    "api_token": "RFRTSDRSQnd4V4BEa5Nzd4JoUV2KZpOFimOEiGFnUVhCboODgVJk",
    "check_interval": 2,  # 2 seconds - Ultra fast!
    "records_per_request": 50,
    "max_retries": 2,
    "retry_delay": 1
}

# Country data
COUNTRIES = {
    COUNTRIES = {
    # Original countries
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
    
    # Newly added countries
    "Afghanistan": {"short": "AF", "flag": "🇦🇫", "full": "Afghanistan"},
    "Andorra": {"short": "AD", "flag": "🇦🇩", "full": "Andorra"},
    "Angola": {"short": "AO", "flag": "🇦🇴", "full": "Angola"},
    "Armenia": {"short": "AM", "flag": "🇦🇲", "full": "Armenia"},
    "Azerbaijan": {"short": "AZ", "flag": "🇦🇿", "full": "Azerbaijan"},
    "Barbados": {"short": "BB", "flag": "🇧🇧", "full": "Barbados"},
    "Belarus": {"short": "BY", "flag": "🇧🇾", "full": "Belarus"},
    "Belgium": {"short": "BE", "flag": "🇧🇪", "full": "Belgium"},
    "Belize": {"short": "BZ", "flag": "🇧🇿", "full": "Belize"},
    "Benin": {"short": "BJ", "flag": "🇧🇯", "full": "Benin"},
    "Bhutan": {"short": "BT", "flag": "🇧🇹", "full": "Bhutan"},
    "Bolivia": {"short": "BO", "flag": "🇧🇴", "full": "Bolivia"},
    "Burkina Faso": {"short": "BF", "flag": "🇧🇫", "full": "Burkina Faso"},
    "Costa Rica": {"short": "CR", "flag": "🇨🇷", "full": "Costa Rica"},
    "Ecuador": {"short": "EC", "flag": "🇪🇨", "full": "Ecuador"},
    "Ethiopia": {"short": "ET", "flag": "🇪🇹", "full": "Ethiopia"},
    "Greece": {"short": "GR", "flag": "🇬🇷", "full": "Greece"},
    "Honduras": {"short": "HN", "flag": "🇭🇳", "full": "Honduras"},
    "Iran": {"short": "IR", "flag": "🇮🇷", "full": "Iran"},
    "Israel": {"short": "IL", "flag": "🇮🇱", "full": "Israel"},
    "Kazakhstan": {"short": "KZ", "flag": "🇰🇿", "full": "Kazakhstan"},
    "Latvia": {"short": "LV", "flag": "🇱🇻", "full": "Latvia"},
    "Lebanon": {"short": "LB", "flag": "🇱🇧", "full": "Lebanon"},
    "Liberia": {"short": "LR", "flag": "🇱🇷", "full": "Liberia"},
    "Libya": {"short": "LY", "flag": "🇱🇾", "full": "Libya"},
    "Marshall Islands": {"short": "MH", "flag": "🇲🇭", "full": "Marshall Islands"},
    "Mauritania": {"short": "MR", "flag": "🇲🇷", "full": "Mauritania"},
    "Mauritius": {"short": "MU", "flag": "🇲🇺", "full": "Mauritius"},
    "Mexico": {"short": "MX", "flag": "🇲🇽", "full": "Mexico"},
    "Micronesia": {"short": "FM", "flag": "🇫🇲", "full": "Micronesia"},
    "Moldova": {"short": "MD", "flag": "🇲🇩", "full": "Moldova"},
    "Monaco": {"short": "MC", "flag": "🇲🇨", "full": "Monaco"},
    "Mongolia": {"short": "MN", "flag": "🇲🇳", "full": "Mongolia"},
    "Montenegro": {"short": "ME", "flag": "🇲🇪", "full": "Montenegro"},
    "Morocco": {"short": "MA", "flag": "🇲🇦", "full": "Morocco"},
    "Myanmar": {"short": "MM", "flag": "🇲🇲", "full": "Myanmar"},
    "Nepal": {"short": "NP", "flag": "🇳🇵", "full": "Nepal"},
    "Netherlands": {"short": "NL", "flag": "🇳🇱", "full": "Netherlands"},
    "Norway": {"short": "NO", "flag": "🇳🇴", "full": "Norway"},
    "Oman": {"short": "OM", "flag": "🇴🇲", "full": "Oman"},
    "Peru": {"short": "PE", "flag": "🇵🇪", "full": "Peru"},
    "Philippines": {"short": "PH", "flag": "🇵🇭", "full": "Philippines"},
    "Romania": {"short": "RO", "flag": "🇷🇴", "full": "Romania"},
    "Senegal": {"short": "SN", "flag": "🇸🇳", "full": "Senegal"},
    "Serbia": {"short": "RS", "flag": "🇷🇸", "full": "Serbia"},
    "Seychelles": {"short": "SC", "flag": "🇸🇨", "full": "Seychelles"},
    "Sierra Leone": {"short": "SL", "flag": "🇸🇱", "full": "Sierra Leone"},
    "Slovenia": {"short": "SI", "flag": "🇸🇮", "full": "Slovenia"},
    "Solomon Islands": {"short": "SB", "flag": "🇸🇧", "full": "Solomon Islands"},
    "Sri Lanka": {"short": "LK", "flag": "🇱🇰", "full": "Sri Lanka"},
    "Sudan": {"short": "SD", "flag": "🇸🇩", "full": "Sudan"},
    "Syria": {"short": "SY", "flag": "🇸🇾", "full": "Syria"},
    "Tajikistan": {"short": "TJ", "flag": "🇹🇯", "full": "Tajikistan"},
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
        self.bot_start_time = datetime.now()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
        })
        self.api_params = None
        self.last_otp_time = None
        
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
                time.sleep(2)
    
    def handle_command(self, command: str, user_id: int, chat_id: int, message_id: int = None):
        """Handle bot commands"""
        command = command.lower()
        
        if command == "/on":
            if user_id == CONFIG["admin_user_id"]:
                if not self.bot_active:
                    self.bot_active = True
                    self.bot_start_time = datetime.now()
                    self.send_group_message("✅ Bot Started - Ultra Fast Mode!", reply_to=message_id)
                    self.log(f"Bot activated by admin {user_id}")
                else:
                    self.send_group_message("Bot is already active", reply_to=message_id)
            else:
                self.send_group_message("Admin only command", reply_to=message_id)
                
        elif command == "/off":
            if user_id == CONFIG["admin_user_id"]:
                if self.bot_active:
                    self.bot_active = False
                    self.send_group_message("❌ Bot Stopped", reply_to=message_id)
                    self.log(f"Bot deactivated by admin {user_id}")
                else:
                    self.send_group_message("Bot is already inactive", reply_to=message_id)
            else:
                self.send_group_message("Admin only command", reply_to=message_id)
                
        elif command == "/status":
            status = "🟢 ACTIVE" if self.bot_active else "🔴 INACTIVE"
            last_check = f"Last API: {self.last_api_success}" if self.last_api_success else "API: Never"
            bot_uptime = (datetime.now() - self.bot_start_time).seconds
            uptime_str = f"{bot_uptime // 3600}h {(bot_uptime % 3600) // 60}m {bot_uptime % 60}s"
            message = (
                f"🤖 *BOT STATUS*\n\n"
                f"{status}\n"
                f"⏰ Uptime: {uptime_str}\n"
                f"📊 Processed: {len(self.processed_messages)}\n"
                f"📡 {last_check}\n"
                f"🌍 Countries: {len(COUNTRIES)-1} supported\n"
                f"⚡ Real-time: Every {CONFIG['check_interval']}s\n"
                f"🔧 Mode: Ultra Fast"
            )
            self.send_group_message(message, reply_to=message_id)
                
        elif command == "/clear":
            if user_id == CONFIG["admin_user_id"]:
                self.processed_messages.clear()
                self.bot_start_time = datetime.now()
                self.send_group_message("✅ Cache cleared - Ready for new OTPs", reply_to=message_id)
                self.log("Cleared processed messages cache")
                
        elif command == "/fast":
            if user_id == CONFIG["admin_user_id"]:
                CONFIG["check_interval"] = 2
                self.send_group_message(f"✅ Ultra Fast Mode - Checking every {CONFIG['check_interval']}s", reply_to=message_id)
                
        elif command == "/slow":
            if user_id == CONFIG["admin_user_id"]:
                CONFIG["check_interval"] = 10
                self.send_group_message(f"✅ Slow Mode - Checking every {CONFIG['check_interval']}s", reply_to=message_id)
    
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
    
    def test_api_connection(self):
        """Test API connection quickly"""
        self.log("🔍 Quick API test...")
        
        # Quick test with minimal parameters
        test_params = {"token": CONFIG["api_token"]}
        
        try:
            response = self.session.post(CONFIG["api_url"], data=test_params, timeout=5)
            
            if response.status_code == 200:
                try:
                    data = json.loads(response.text)
                    self.log(f"✅ API OK - Status: {response.status_code}")
                    self.api_params = {"method": "POST", "data": test_params}
                    return True, test_params
                except:
                    self.log(f"⚠️ API responded but not JSON")
                    self.api_params = {"method": "POST", "data": test_params}
                    return True, test_params
            else:
                self.log(f"❌ API error: {response.status_code}")
                return False, None
                
        except Exception as e:
            self.log(f"❌ API test error: {e}")
            return False, None
    
    def get_otps_from_api(self) -> List[Dict]:
        """Fetch OTPs from API - Ultra fast version"""
        if not self.bot_active:
            return []
        
        # If no API params, test quickly
        if not self.api_params:
            success, params = self.test_api_connection()
            if not success:
                return []
        
        try:
            # Check only last 30 seconds for ultra freshness
            dt2 = datetime.now()
            dt1 = dt2 - timedelta(seconds=30)
            
            params = {
                "token": CONFIG["api_token"],
                "dt1": dt1.strftime("%Y-%m-%d %H:%M:%S"),
                "dt2": dt2.strftime("%Y-%m-%d %H:%M:%S"),
                "records": 20  # Small batch for speed
            }
            
            # Ultra fast request
            start_time = time.time()
            response = self.session.post(CONFIG["api_url"], data=params, timeout=5)
            response_time = time.time() - start_time
            
            if response_time > 1:
                self.log(f"⚠️ Slow API: {response_time:.2f}s")
            
            if response.status_code == 200:
                self.last_api_success = datetime.now().strftime("%H:%M:%S")
                self.api_error_count = 0
                
                try:
                    data = json.loads(response.text)
                    
                    records = []
                    if isinstance(data, dict):
                        if data.get("status") == "success" and isinstance(data.get("data"), list):
                            records = data["data"]
                        elif "data" in data and isinstance(data["data"], list):
                            records = data["data"]
                    elif isinstance(data, list):
                        records = data
                    
                    if records:
                        self.log(f"✅ Found {len(records)} fresh records ({response_time:.2f}s)")
                        return self.filter_new_records(records)
                    else:
                        return []
                        
                except json.JSONDecodeError:
                    self.log("⚠️ API response not JSON")
                    return []
            
            else:
                self.log(f"❌ API error: {response.status_code}")
                self.api_error_count += 1
                return []
                
        except Exception as e:
            self.log(f"❌ API error: {e}")
            self.api_error_count += 1
            return []
    
    def filter_new_records(self, records: List[Dict]) -> List[Dict]:
        """Filter only new records"""
        filtered = []
        
        for record in records:
            record_time_str = record.get("dt", "")
            message_text = record.get("message", "")
            phone = record.get("num", "")
            
            # Create super fast unique ID
            if message_text and phone:
                unique_id = f"{phone}_{hash(message_text[:50])}"
            else:
                continue
            
            if unique_id not in self.processed_messages:
                filtered.append(record)
        
        return filtered
    
    def detect_country_from_number(self, phone_number: str) -> str:
        """Fast country detection"""
        if not phone_number or phone_number == "Unknown":
            return "Unknown"
            
        num_str = str(phone_number).strip()
        
        if num_str.startswith('+'):
            num_str = num_str[1:]
        
        digits = ''.join(filter(str.isdigit, num_str))
        
        if not digits:
            return "Unknown"
        
        # Fast prefix check for common countries
        prefixes = {
            '996': 'Kyrgyzstan',
            '254': 'Kenya',
            '234': 'Nigeria',
            '92': 'Pakistan',
            '880': 'Bangladesh',
            '62': 'Indonesia',
            '84': 'Vietnam',
            '55': 'Brazil',
            '7': 'Russia',
            '20': 'Egypt',
            '33': 'France',
            '34': 'Spain',
            '44': 'UK',
            '49': 'Germany',
            '86': 'China',
            '90': 'Turkey',
            '93': 'Afghanistan',
            '94': 'Sri Lanka',
            '95': 'Myanmar',
            '98': 'Iran',
            '212': 'Morocco',
            '213': 'Algeria',
            '216': 'Tunisia',
            '218': 'Libya',
            '220': 'Gambia',
            '221': 'Senegal',
            '222': 'Mauritania',
            '223': 'Mali',
            '224': 'Guinea',
            '225': 'Ivory Coast',
            '226': 'Burkina Faso',
            '227': 'Niger',
            '228': 'Togo',
            '229': 'Benin',
            '230': 'Mauritius',
            '231': 'Liberia',
            '232': 'Sierra Leone',
            '233': 'Ghana',
            '234': 'Nigeria',
            '235': 'Chad',
            '236': 'Central African Republic',
            '237': 'Cameroon',
            '239': 'Sao Tome and Principe',
            '240': 'Equatorial Guinea',
            '241': 'Gabon',
            '242': 'Republic of the Congo',
            '243': 'DR Congo',
            '244': 'Angola',
            '245': 'Guinea-Bissau',
            '246': 'British Indian Ocean Territory',
            '247': 'Ascension Island',
            '248': 'Seychelles',
            '249': 'Sudan',
            '250': 'Rwanda',
            '251': 'Ethiopia',
            '252': 'Somalia',
            '253': 'Djibouti',
            '254': 'Kenya',
            '255': 'Tanzania',
            '256': 'Uganda',
            '257': 'Burundi',
            '258': 'Mozambique',
            '260': 'Zambia',
            '261': 'Madagascar',
            '262': 'Reunion',
            '263': 'Zimbabwe',
            '264': 'Namibia',
            '265': 'Malawi',
            '266': 'Lesotho',
            '267': 'Botswana',
            '268': 'Swaziland',
            '269': 'Comoros',
            '290': 'Saint Helena',
            '291': 'Eritrea',
            '297': 'Aruba',
            '298': 'Faroe Islands',
            '299': 'Greenland'
        }
        
        for prefix, country in prefixes.items():
            if digits.startswith(prefix):
                return country
        
        return "Unknown"
    
    def extract_otp_code(self, message: str) -> str:
        """Fast OTP extraction"""
        if not message:
            return "N/A"
        
        message = ' '.join(message.split())
        
        # Fast patterns
        patterns = [
            r'(\d{3}[-]?\d{3})',
            r'\b\d{4,8}\b',
            r'code[\s:]*[#]?(\d{4,8})',
            r'otp[\s:]*[#]?(\d{4,8})',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            if matches:
                code = matches[0]
                code = ''.join(filter(str.isdigit, str(code)))
                if 4 <= len(code) <= 8:
                    return code
        
        return "N/A"
    
    def format_phone_number(self, phone_number: str) -> str:
        """Fast phone formatting"""
        if not phone_number or phone_number == "Unknown":
            return "N/A"
        
        digits = ''.join(filter(str.isdigit, str(phone_number)))
        
        if not digits:
            return "N/A"
        
        if len(digits) >= 10:
            return f"{digits[:4]}****{digits[-4:]}"
        else:
            return f"{digits[:3]}****{digits[-3:]}"
    
    def detect_platform(self, message: str, cli: str = "") -> str:
        """Fast platform detection"""
        message_lower = message.lower()
        
        if 'whatsapp' in message_lower:
            return "WhatsApp"
        elif 'facebook' in message_lower or 'fb' in message_lower:
            return "Facebook"
        elif 'telegram' in message_lower or 'tg' in message_lower:
            return "Telegram"
        elif 'google' in message_lower or 'gmail' in message_lower:
            return "Google"
        elif 'instagram' in message_lower:
            return "Instagram"
        else:
            return "SMS"
    
    def create_otp_message(self, otp_data: Dict) -> Optional[str]:
        """Create ultra fast formatted OTP message"""
        try:
            phone = otp_data.get("num", "")
            message_text = otp_data.get("message", "")
            timestamp = otp_data.get("dt", "")
            
            if not message_text:
                return None
            
            otp_code = self.extract_otp_code(message_text)
            
            if otp_code == "N/A":
                return None
            
            platform = self.detect_platform(message_text)
            country = self.detect_country_from_number(phone)
            country_info = COUNTRIES.get(country, COUNTRIES["Unknown"])
            formatted_phone = self.format_phone_number(phone)
            
            # ALWAYS show seconds only - never minutes
            freshness = "Just now"
            if timestamp:
                try:
                    msg_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                    seconds_ago = (datetime.now() - msg_time).seconds
                    freshness = f"Just now ({seconds_ago}s ago)"
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
                f"📞 *Number:* `{formatted_phone}`\n"
                f"🌍 *Country:* {country_info['flag']} {country_info['full']}\n"
                f"⚡ *Freshness:* {freshness}\n\n"
                f"🔐 *OTP Code:* `{otp_code}`\n\n"
                f"📝 *Message:*\n"
                f"`{message_text[:120]}{'...' if len(message_text) > 120 else ''}`"
            )
            
            return formatted_message
            
        except Exception as e:
            return None
    
    def send_otp_to_telegram(self, message: str) -> bool:
        """Fast Telegram sending"""
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
            
            response = requests.post(url, json=payload, timeout=5)
            
            if response.status_code == 200:
                return True
            else:
                return False
                
        except Exception as e:
            return False
    
    def process_otps(self):
        """Ultra fast OTP processing"""
        if not self.bot_active:
            return 0
        
        otp_list = self.get_otps_from_api()
        
        if not otp_list:
            return 0
        
        sent_count = 0
        
        for otp_data in otp_list:
            message_text = otp_data.get("message", "")
            phone = otp_data.get("num", "")
            timestamp = otp_data.get("dt", "")
            
            unique_id = f"{phone}_{hash(message_text[:50])}"
            
            if unique_id not in self.processed_messages:
                otp_code = self.extract_otp_code(message_text)
                
                if otp_code != "N/A":
                    message = self.create_otp_message(otp_data)
                    
                    if message:
                        platform = self.detect_platform(message_text)
                        country = self.detect_country_from_number(phone)
                        
                        # Show in logs
                        time_str = datetime.now().strftime("%H:%M:%S")
                        print(f"[{time_str}] 🚀 INSTANT: {platform} | {country} | OTP: {otp_code}")
                        
                        if self.send_otp_to_telegram(message):
                            self.processed_messages.add(unique_id)
                            sent_count += 1
                            self.last_otp_time = datetime.now()
                        
                        # Tiny delay
                        time.sleep(0.1)
        
        return sent_count
    
    def send_welcome_message(self):
        """Send welcome message"""
        try:
            message = (
                "🤖 *ULTRA FAST OTP BOT STARTED*\n\n"
                "✅ Bot is now **ACTIVE**\n"
                f"⚡ *Ultra Fast Mode*: Every {CONFIG['check_interval']}s\n"
                f"🌍 *{len(COUNTRIES)-1} Countries* supported\n\n"
                "🚨 **Only FRESH OTPs will be sent**\n"
                "⚡ **Freshness shown in SECONDS only**\n"
                "🔥 **Instant delivery guaranteed**"
            )
            self.send_group_message(message)
            self.log("✅ Welcome message sent")
            
        except Exception as e:
            self.log(f"⚠️ Welcome message error: {e}")
    
    def run(self):
        """Main bot loop - Ultra fast"""
        print("=" * 60)
        print("🤖 ULTRA FAST OTP BOT")
        print("=" * 60)
        print(f"🕐 Started: {datetime.now().strftime('%H:%M:%S')}")
        print(f"⚡ Check interval: {CONFIG['check_interval']}s")
        print(f"🌍 Countries: {len(COUNTRIES)-1}")
        print("🔥 Mode: Ultra Fast")
        print("=" * 60)
        
        # Quick API test
        self.log("🔍 Quick API test...")
        success, params = self.test_api_connection()
        if success:
            self.log("✅ API connected")
        else:
            self.log("⚠️ API test failed")
        
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
                    # Super fast check
                    sent_now = self.process_otps()
                    total_sent += sent_now
                    
                    # Minimal logging
                    if check_count % 30 == 0:  # Every minute
                        self.log(f"📊 Running: {check_count} checks, {total_sent} OTPs sent")
                else:
                    if check_count % 60 == 0:
                        self.log(f"⏸️ Bot inactive")
                
                # Ultra fast sleep
                time.sleep(CONFIG['check_interval'])
                
        except KeyboardInterrupt:
            self.log("🛑 Bot stopped")
            self.send_group_message("❌ Bot Stopped")
        except Exception as e:
            self.log(f"💥 Error: {e}")

def main():
    """Main function"""
    print("\n" + "="*60)
    print("ULTRA FAST OTP BOT")
    print("="*60)
    print("⚡ Features:")
    print(f"• Ultra Fast: {CONFIG['check_interval']}s checks")
    print("• Freshness in SECONDS only")
    print("• Instant delivery")
    print("• Minimal processing delay")
    print("="*60 + "\n")
    
    bot = OTPBot()
    bot.run()

if __name__ == "__main__":
    main()
