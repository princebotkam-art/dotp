import requests
import time
import re
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, Set, List, Optional, Tuple

# Configuration - Real-time monitoring
CONFIG = {
    "telegram_token": "8402286199:AAEwsLGs7ZcLK2lvdaiYggqn3AJQNFdV94k",
    "group_id": -1002725332877,
    "admin_user_id": 7380687709,
    "api_url": "http://51.77.216.195/crapi/dgroup/viewstats",
    "api_token": "RFRTSDRSQnd4V4BEa5Nzd4JoUV2KZpOFimOEiGFnUVhCboODgVJk",
    "check_interval": 3,
    "records_per_request": 100,
    "max_retries": 2,
    "retry_delay": 2
}

# Country data - Full English names only (Extended list)
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
            'Connection': 'keep-alive',
            'Accept-Language': 'en-US,en;q=0.9',
        })
        self.last_check_time = datetime.now() - timedelta(minutes=5)
        
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
                    self.send_group_message("✅ Bot Started - Only new OTPs will be sent", reply_to=message_id)
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
                f"🌍 Countries: {len(COUNTRIES)} supported\n"
                f"⚡ Real-time: Every {CONFIG['check_interval']}s"
            )
            self.send_group_message(message, reply_to=message_id)
                
        elif command == "/clear":
            if user_id == CONFIG["admin_user_id"]:
                self.processed_messages.clear()
                self.bot_start_time = datetime.now()
                self.send_group_message("✅ Cache cleared - Bot will send only new OTPs", reply_to=message_id)
                self.log("Cleared processed messages cache")
                
        elif command == "/countries":
            # Show supported countries count
            message = f"🌍 *Supported Countries:* {len(COUNTRIES)-1}\n⚡ Major countries detected automatically"
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
                
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
                
        except Exception as e:
            self.log(f"Telegram send error: {e}")
            return False
    
    def test_api_connection(self):
        """Test API connection with different parameters"""
        self.log("🔍 Testing API connection...")
        
        param_combinations = [
            {
                "token": CONFIG["api_token"],
                "dt1": (datetime.now() - timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S"),
                "dt2": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "records": 10
            },
            {
                "token": CONFIG["api_token"],
                "records": 10
            }
        ]
        
        for i, params in enumerate(param_combinations):
            self.log(f"  Trying parameter set {i+1}: {list(params.keys())}")
            
            try:
                # Try POST
                response = self.session.post(CONFIG["api_url"], data=params, timeout=5)
                if response.status_code == 200:
                    try:
                        data = json.loads(response.text)
                        if data.get("status") == "success":
                            self.log(f"    ✅ SUCCESS with set {i+1}")
                            return True, params
                    except:
                        pass
                
                time.sleep(1)
                
            except Exception as e:
                self.log(f"    ❌ Error: {e}")
        
        return False, None
    
    def get_otps_from_api(self) -> List[Dict]:
        """Fetch OTPs from API - Real-time optimized version"""
        if not self.bot_active:
            return []
        
        try:
            # Always check last 1 minute for real-time updates
            dt2 = datetime.now()
            dt1 = dt2 - timedelta(seconds=60)
            
            params = {
                "token": CONFIG["api_token"],
                "dt1": dt1.strftime("%Y-%m-%d %H:%M:%S"),
                "dt2": dt2.strftime("%Y-%m-%d %H:%M:%S"),
                "records": CONFIG["records_per_request"]
            }
            
            # Try POST first
            response = self.session.post(CONFIG["api_url"], data=params, timeout=8)
            
            if response.status_code == 200:
                try:
                    data = json.loads(response.text)
                    
                    if isinstance(data, dict):
                        if data.get("status") == "success":
                            records = data.get("data", [])
                            self.log(f"✅ Found {len(records)} records")
                            self.last_api_success = datetime.now().strftime("%H:%M:%S")
                            self.api_error_count = 0
                            return self.filter_new_records(records)
                        
                        elif "data" in data and isinstance(data["data"], list):
                            records = data.get("data", [])
                            self.log(f"✅ Found {len(records)} records")
                            self.last_api_success = datetime.now().strftime("%H:%M:%S")
                            self.api_error_count = 0
                            return self.filter_new_records(records)
                    
                    elif isinstance(data, list):
                        self.log(f"✅ Found {len(data)} records")
                        self.last_api_success = datetime.now().strftime("%H:%M:%S")
                        self.api_error_count = 0
                        return self.filter_new_records(data)
                        
                except json.JSONDecodeError:
                    self.log("⚠️ Response not JSON")
            
            self.api_error_count += 1
            return []
                
        except Exception as e:
            self.log(f"❌ API Error: {e}")
            self.api_error_count += 1
            return []
    
    def filter_new_records(self, records: List[Dict]) -> List[Dict]:
        """Filter only records that arrived after bot started"""
        filtered = []
        
        for record in records:
            record_time_str = record.get("dt", "")
            message_text = record.get("message", "")
            phone = record.get("num", "")
            
            # Create unique ID for each message
            unique_id = f"{phone}_{record_time_str}_{hash(message_text[:50])}"
            
            if unique_id not in self.processed_messages:
                filtered.append(record)
        
        return filtered
    
    def detect_country_from_number(self, phone_number: str) -> str:
        """Detect country from phone number - Enhanced with all countries"""
        if not phone_number or phone_number == "Unknown":
            return "Unknown"
            
        num_str = str(phone_number).strip()
        
        # Remove any plus sign and non-digits
        if num_str.startswith('+'):
            num_str = num_str[1:]
        
        num_str = ''.join(filter(str.isdigit, num_str))
        
        if not num_str:
            return "Unknown"
        
        # Extended country prefixes
        country_prefixes = {
            # Asia
            '93': 'Afghanistan',
            '91': 'India',
            '92': 'Pakistan',
            '880': 'Bangladesh',
            '62': 'Indonesia',
            '84': 'Vietnam',
            '95': 'Myanmar',
            '977': 'Nepal',
            '94': 'Sri Lanka',
            '66': 'Thailand',
            '98': 'Iran',
            '972': 'Israel',
            '961': 'Lebanon',
            '63': 'Philippines',
            '81': 'Japan',
            '82': 'South Korea',
            '86': 'China',
            '60': 'Malaysia',
            '65': 'Singapore',
            '7': 'Kazakhstan',  # Also Russia, but Kazakhstan priority
            '996': 'Kyrgyzstan',
            '992': 'Tajikistan',
            '998': 'Uzbekistan',
            '855': 'Cambodia',
            '856': 'Laos',
            '880': 'Bangladesh',
            
            # Africa
            '254': 'Kenya',
            '234': 'Nigeria',
            '27': 'South Africa',
            '20': 'Egypt',
            '212': 'Morocco',
            '216': 'Tunisia',
            '251': 'Ethiopia',
            '255': 'Tanzania',
            '233': 'Ghana',
            '229': 'Benin',
            '226': 'Burkina Faso',
            '257': 'Burundi',
            '235': 'Chad',
            '242': 'Congo',
            '243': 'DR Congo',
            '240': 'Equatorial Guinea',
            '291': 'Eritrea',
            '220': 'Gambia',
            '233': 'Ghana',
            '224': 'Guinea',
            '245': 'Guinea-Bissau',
            '225': 'Ivory Coast',
            '231': 'Liberia',
            '218': 'Libya',
            '261': 'Madagascar',
            '265': 'Malawi',
            '223': 'Mali',
            '222': 'Mauritania',
            '230': 'Mauritius',
            '258': 'Mozambique',
            '227': 'Niger',
            '250': 'Rwanda',
            '221': 'Senegal',
            '232': 'Sierra Leone',
            '252': 'Somalia',
            '211': 'South Sudan',
            '249': 'Sudan',
            '255': 'Tanzania',
            '228': 'Togo',
            '256': 'Uganda',
            '260': 'Zambia',
            '263': 'Zimbabwe',
            
            # Europe
            '376': 'Andorra',
            '375': 'Belarus',
            '32': 'Belgium',
            '359': 'Bulgaria',
            '385': 'Croatia',
            '357': 'Cyprus',
            '420': 'Czech Republic',
            '45': 'Denmark',
            '372': 'Estonia',
            '358': 'Finland',
            '33': 'France',
            '995': 'Georgia',
            '49': 'Germany',
            '30': 'Greece',
            '36': 'Hungary',
            '354': 'Iceland',
            '353': 'Ireland',
            '39': 'Italy',
            '371': 'Latvia',
            '370': 'Lithuania',
            '352': 'Luxembourg',
            '356': 'Malta',
            '373': 'Moldova',
            '377': 'Monaco',
            '382': 'Montenegro',
            '31': 'Netherlands',
            '47': 'Norway',
            '48': 'Poland',
            '351': 'Portugal',
            '40': 'Romania',
            '7': 'Russia',
            '381': 'Serbia',
            '421': 'Slovakia',
            '386': 'Slovenia',
            '34': 'Spain',
            '46': 'Sweden',
            '41': 'Switzerland',
            '90': 'Turkey',
            '380': 'Ukraine',
            '44': 'United Kingdom',
            '379': 'Vatican City',
            
            # North America
            '1': 'USA',  # Also Canada, but USA priority
            '1': 'Canada',
            '506': 'Costa Rica',
            '53': 'Cuba',
            '1809': 'Dominican Republic',
            '1829': 'Dominican Republic',
            '1849': 'Dominican Republic',
            '502': 'Guatemala',
            '504': 'Honduras',
            '1876': 'Jamaica',
            '52': 'Mexico',
            '505': 'Nicaragua',
            '507': 'Panama',
            '1787': 'Puerto Rico',
            '1939': 'Puerto Rico',
            '1868': 'Trinidad and Tobago',
            '501': 'Belize',
            
            # South America
            '54': 'Argentina',
            '591': 'Bolivia',
            '55': 'Brazil',
            '56': 'Chile',
            '57': 'Colombia',
            '593': 'Ecuador',
            '592': 'Guyana',
            '595': 'Paraguay',
            '51': 'Peru',
            '597': 'Suriname',
            '598': 'Uruguay',
            '58': 'Venezuela',
            
            # Oceania
            '61': 'Australia',
            '672': 'Norfolk Island',
            '677': 'Solomon Islands',
            '679': 'Fiji',
            '682': 'Cook Islands',
            '685': 'Samoa',
            '686': 'Kiribati',
            '687': 'New Caledonia',
            '689': 'French Polynesia',
            '691': 'Micronesia',
            '692': 'Marshall Islands',
            '850': 'North Korea',
            '852': 'Hong Kong',
            '853': 'Macau',
            '670': 'Timor-Leste',
            '680': 'Palau',
            '683': 'Niue',
            '688': 'Tuvalu',
            '690': 'Tokelau',
            '676': 'Tonga',
            '678': 'Vanuatu',
            
            # Middle East
            '973': 'Bahrain',
            '20': 'Egypt',
            '98': 'Iran',
            '964': 'Iraq',
            '962': 'Jordan',
            '965': 'Kuwait',
            '961': 'Lebanon',
            '968': 'Oman',
            '974': 'Qatar',
            '966': 'Saudi Arabia',
            '963': 'Syria',
            '971': 'United Arab Emirates',
            '967': 'Yemen',
            '972': 'Israel',
            '970': 'Palestine',
        }
        
        # Check for exact matches first (longer prefixes first)
        sorted_prefixes = sorted(country_prefixes.items(), key=lambda x: len(x[0]), reverse=True)
        
        for prefix, country in sorted_prefixes:
            if num_str.startswith(prefix):
                return country
        
        # If no match found
        return "Unknown"
    
    def extract_otp_code(self, message: str) -> str:
        """Extract OTP code from message"""
        if not message:
            return "N/A"
        
        # Remove extra spaces
        message = ' '.join(message.split())
        
        # Common patterns
        patterns = [
            r'(\d{3}[-]?\d{3})',  # 123-456 or 123456
            r'\b\d{4,8}\b',  # 4-8 digit codes
            r'code[\s:]*[#]?(\d{4,8})',
            r'kode[\s:]*[#]?(\d{4,8})',
            r'otp[\s:]*[#]?(\d{4,8})',
            r'verification[\s:]*[#]?(\d{4,8})',
            r'password[\s:]*[#]?(\d{4,8})',
            r'pin[\s:]*[#]?(\d{4,8})',
            r'(\d{4,8})[\s]*is[\s]*your',
            r'your[\s]*code[\s]*is[\s]*(\d{4,8})',
            r'(\d{4,8})[\s]*code',
            r'code[\s]*is[\s]*(\d{4,8})'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            if matches:
                code = matches[0]
                if "-" in code:
                    return code.replace("-", "")
                return code
        
        return "N/A"
    
    def format_phone_number(self, phone_number: str) -> str:
        """Format phone number for display"""
        if not phone_number or phone_number == "Unknown":
            return "N/A"
        
        digits = ''.join(filter(str.isdigit, str(phone_number)))
        
        if not digits:
            return "N/A"
        
        if len(digits) >= 10:
            return f"{digits[:4]}****{digits[-4:]}"
        elif len(digits) >= 7:
            return f"{digits[:3]}****{digits[-3:]}"
        else:
            return f"{digits[:2]}****{digits[-2:]}"
    
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
        elif 'tiktok' in message_lower or '抖音' in message_lower:
            return "TikTok"
        elif 'twitter' in message_lower or 'x.com' in message_lower:
            return "Twitter"
        elif 'amazon' in message_lower:
            return "Amazon"
        elif 'paypal' in message_lower:
            return "PayPal"
        elif 'snapchat' in message_lower:
            return "Snapchat"
        elif 'linkedin' in message_lower:
            return "LinkedIn"
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
            
            # Calculate freshness
            freshness = ""
            if timestamp:
                try:
                    msg_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                    seconds_ago = (datetime.now() - msg_time).seconds
                    if seconds_ago < 60:
                        freshness = f" ({seconds_ago}s ago)"
                    else:
                        minutes_ago = seconds_ago // 60
                        freshness = f" ({minutes_ago}m ago)"
                except:
                    pass
            
            platform_emoji = {
                "WhatsApp": "📱",
                "Facebook": "👤",
                "Telegram": "📨",
                "Google": "🔍",
                "Instagram": "📸",
                "TikTok": "🎵",
                "Twitter": "🐦",
                "Amazon": "🛒",
                "PayPal": "💳",
                "Snapchat": "👻",
                "LinkedIn": "💼",
                "SMS": "💬"
            }.get(platform, "📲")
            
            formatted_message = (
                f"══════════════════════\n"
                f"    🚨 *LIVE OTP RECEIVED* 🚨\n"
                f"══════════════════════\n\n"
                f"{platform_emoji} *Platform:* {platform}\n"
                f"📞 *Number:* `{formatted_phone}`\n"
                f"🌍 *Country:* {country_info['flag']} {country_info['full']}\n"
                f"⚡ *Freshness:* Just now{freshness}\n\n"
                f"🔐 *OTP Code:* `{otp_code}`\n\n"
                f"📝 *Message Preview:*\n"
                f"`{message_text[:120]}{'...' if len(message_text) > 120 else ''}`"
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
            
            if response.status_code == 200:
                return True
            else:
                self.log(f"❌ Telegram error: {response.status_code}")
                return False
                
        except Exception as e:
            self.log(f"❌ Telegram send error: {e}")
            return False
    
    def process_otps(self):
        """Process OTPs - Real-time optimized"""
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
            
            # Create unique ID
            unique_id = f"{phone}_{timestamp}_{hash(message_text[:50])}"
            
            if unique_id not in self.processed_messages:
                otp_code = self.extract_otp_code(message_text)
                
                if otp_code != "N/A":
                    message = self.create_otp_message(otp_data)
                    
                    if message:
                        platform = self.detect_platform(message_text, otp_data.get("cli", ""))
                        country = self.detect_country_from_number(phone)
                        
                        self.log(f"⚡ INSTANT: {platform} | {phone[:12]}... | {country} | OTP: {otp_code}")
                        
                        if self.send_otp_to_telegram(message):
                            self.processed_messages.add(unique_id)
                            sent_count += 1
                            self.log(f"✅ DELIVERED")
                        
                        time.sleep(0.3)
        
        if sent_count > 0:
            self.log(f"📊 Total delivered this cycle: {sent_count}")
        
        return sent_count
    
    def send_welcome_message(self):
        """Send welcome message"""
        try:
            message = (
                "🤖 *ULTIMATE OTP BOT STARTED*\n\n"
                "✅ Bot is now **ACTIVE**\n"
                "⚡ *Ultra Real-time monitoring* enabled\n"
                f"⏰ Checking every *{CONFIG['check_interval']} seconds*\n"
                f"🌍 *{len(COUNTRIES)-1} Countries* supported\n\n"
                "🚨 **Only NEW OTPs will be sent**\n"
                "🌍 **Country names in full English**\n\n"
                "🔔 OTPs will appear here INSTANTLY!\n"
                "⚡ Lightning fast delivery guaranteed"
            )
            self.send_group_message(message)
            self.log("✅ Welcome message sent")
            
        except Exception as e:
            self.log(f"⚠️ Welcome message error: {e}")
    
    def run(self):
        """Main bot loop - Real-time optimized"""
        print("=" * 60)
        print("🤖 JS OTP BOT - ULTIMATE REAL-TIME")
        print("=" * 60)
        print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⚡ Check interval: {CONFIG['check_interval']}s (Real-time)")
        print(f"🌍 Countries supported: {len(COUNTRIES)-1}")
        print("=" * 60)
        
        # Test API connection first
        self.log("🔍 Testing API connection...")
        success, params = self.test_api_connection()
        if success:
            self.log("✅ API connection successful")
        else:
            self.log("⚠️ API connection test failed, but continuing...")
        
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
                    self.log(f"🔄 Quick Check #{check_count}")
                    sent_now = self.process_otps()
                    total_sent += sent_now
                    
                    if sent_now == 0:
                        self.log(f"⏳ No new OTPs, next check in {CONFIG['check_interval']}s")
                    
                    # Print status every 20 checks
                    if check_count % 20 == 0:
                        self.log(f"📈 Stats: {total_sent} total OTPs | {len(self.processed_messages)} processed")
                else:
                    self.log(f"⏸️ Check #{check_count} - Bot inactive")
                
                time.sleep(CONFIG['check_interval'])
                
        except KeyboardInterrupt:
            self.log("🛑 Bot stopped manually")
            self.send_group_message("❌ Bot Stopped Manually")
        except Exception as e:
            self.log(f"💥 Fatal error: {e}")
            import traceback
            traceback.print_exc()

def main():
    """Main function"""
    print("\n" + "="*60)
    print("JS OTP BOT - ULTIMATE REAL-TIME VERSION")
    print("="*60)
    print("🎯 Features:")
    print(f"• Ultra-fast {CONFIG['check_interval']}-second checks")
    print(f"• {len(COUNTRIES)-1} Countries supported")
    print("• Full English country names")
    print("• Instant delivery to group")
    print("• Real-time monitoring")
    print("• Advanced country detection")
    print("="*60 + "\n")
    
    bot = OTPBot()
    bot.run()

if __name__ == "__main__":
    main()
