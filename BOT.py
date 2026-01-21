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
    "check_interval": 5,
    "records_per_request": 50,
    "max_retries": 3,
    "retry_delay": 2
}

# Country data
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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
        })
        self.api_params = None
        
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
                f"🌍 Countries: {len(COUNTRIES)-1} supported\n"
                f"⚡ Real-time: Every {CONFIG['check_interval']}s\n"
                f"🔧 API Status: {'Connected' if self.last_api_success else 'Not Connected'}"
            )
            self.send_group_message(message, reply_to=message_id)
                
        elif command == "/clear":
            if user_id == CONFIG["admin_user_id"]:
                self.processed_messages.clear()
                self.bot_start_time = datetime.now()
                self.send_group_message("✅ Cache cleared - Bot will send only new OTPs", reply_to=message_id)
                self.log("Cleared processed messages cache")
                
        elif command == "/testapi":
            if user_id == CONFIG["admin_user_id"]:
                self.send_group_message("🔍 Testing API connection...", reply_to=message_id)
                success, params = self.test_api_connection(True)
                if success:
                    self.send_group_message("✅ API connection successful!", reply_to=message_id)
                else:
                    self.send_group_message("❌ API connection failed", reply_to=message_id)
    
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
    
    def test_api_connection(self, detailed=False):
        """Test API connection with different parameters"""
        self.log("🔍 Testing API connection...")
        
        if detailed:
            self.send_group_message("🔍 Testing API connection with different methods...")
        
        # Try different endpoints and parameters
        test_cases = [
            # Case 1: Basic token only
            {
                "method": "POST",
                "data": {"token": CONFIG["api_token"]}
            },
            # Case 2: With time range
            {
                "method": "POST",
                "data": {
                    "token": CONFIG["api_token"],
                    "dt1": (datetime.now() - timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S"),
                    "dt2": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            },
            # Case 3: GET request
            {
                "method": "GET",
                "params": {"token": CONFIG["api_token"]}
            },
            # Case 4: Different parameter names
            {
                "method": "POST",
                "data": {
                    "token": CONFIG["api_token"],
                    "start_date": (datetime.now() - timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S"),
                    "end_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "limit": 10
                }
            }
        ]
        
        for i, test_case in enumerate(test_cases):
            method = test_case["method"]
            self.log(f"  Test {i+1}: {method} request")
            
            try:
                if method == "POST":
                    response = self.session.post(
                        CONFIG["api_url"],
                        data=test_case["data"],
                        timeout=10
                    )
                else:  # GET
                    response = self.session.get(
                        CONFIG["api_url"],
                        params=test_case.get("params", test_case["data"]),
                        timeout=10
                    )
                
                self.log(f"    Status: {response.status_code}")
                
                if response.status_code == 200:
                    self.log(f"    Response length: {len(response.text)} chars")
                    
                    # Try to parse JSON
                    try:
                        data = json.loads(response.text)
                        self.log(f"    JSON parsed successfully")
                        
                        # Check if response contains expected data
                        if isinstance(data, dict):
                            if "status" in data and data["status"] == "success":
                                self.log(f"    ✅ SUCCESS: status='success'")
                                self.api_params = test_case
                                return True, test_case
                            elif "data" in data:
                                self.log(f"    ✅ SUCCESS: has 'data' key")
                                self.api_params = test_case
                                return True, test_case
                            elif len(data) > 0:
                                self.log(f"    ✅ SUCCESS: non-empty dict")
                                self.api_params = test_case
                                return True, test_case
                        elif isinstance(data, list) and len(data) > 0:
                            self.log(f"    ✅ SUCCESS: non-empty list")
                            self.api_params = test_case
                            return True, test_case
                        
                        # If we got here but have valid JSON, still consider it success
                        self.log(f"    ⚠️ Valid JSON but unexpected format")
                        self.api_params = test_case
                        return True, test_case
                        
                    except json.JSONDecodeError:
                        # Check if response might be plain text with data
                        if len(response.text) > 10 and not "<html" in response.text.lower():
                            self.log(f"    ⚠️ Not JSON but might contain data")
                            self.api_params = test_case
                            return True, test_case
                        else:
                            self.log(f"    ❌ Invalid response format")
                
                elif response.status_code == 404:
                    self.log(f"    ❌ 404 - Endpoint not found")
                elif response.status_code == 403:
                    self.log(f"    ❌ 403 - Forbidden (check token)")
                elif response.status_code == 500:
                    self.log(f"    ❌ 500 - Server error")
                    
            except requests.exceptions.Timeout:
                self.log(f"    ❌ Timeout")
            except requests.exceptions.ConnectionError:
                self.log(f"    ❌ Connection error")
            except Exception as e:
                self.log(f"    ❌ Error: {type(e).__name__}: {str(e)}")
            
            time.sleep(1)
        
        self.log("❌ All API tests failed")
        return False, None
    
    def get_otps_from_api(self) -> List[Dict]:
        """Fetch OTPs from API"""
        if not self.bot_active:
            return []
        
        # If we don't have working params, try to find them
        if not self.api_params:
            self.log("⚠️ No API parameters, testing connection...")
            success, params = self.test_api_connection()
            if not success:
                self.log("❌ API test failed, cannot fetch OTPs")
                return []
        
        try:
            # Use last 5 minutes for real-time updates
            dt2 = datetime.now()
            dt1 = dt2 - timedelta(minutes=5)
            
            # Prepare parameters based on what worked before
            if self.api_params["method"] == "POST":
                params = self.api_params["data"].copy()
                # Add time parameters if they're expected
                if "dt1" in params or "start_date" in params:
                    if "dt1" in params:
                        params["dt1"] = dt1.strftime("%Y-%m-%d %H:%M:%S")
                        params["dt2"] = dt2.strftime("%Y-%m-%d %H:%M:%S")
                    elif "start_date" in params:
                        params["start_date"] = dt1.strftime("%Y-%m-%d %H:%M:%S")
                        params["end_date"] = dt2.strftime("%Y-%m-%d %H:%M:%S")
                
                response = self.session.post(CONFIG["api_url"], data=params, timeout=10)
            else:  # GET
                params = self.api_params.get("params", self.api_params["data"]).copy()
                response = self.session.get(CONFIG["api_url"], params=params, timeout=10)
            
            self.log(f"📡 API request to: {CONFIG['api_url']}")
            self.log(f"📊 Method: {self.api_params['method']}")
            
            if response.status_code == 200:
                self.log(f"✅ HTTP 200 OK")
                
                try:
                    data = json.loads(response.text)
                    self.last_api_success = datetime.now().strftime("%H:%M:%S")
                    self.api_error_count = 0
                    
                    # Parse different response formats
                    records = []
                    
                    if isinstance(data, dict):
                        # Format 1: status = "success", data = [...]
                        if data.get("status") == "success" and isinstance(data.get("data"), list):
                            records = data["data"]
                            self.log(f"📊 Found {len(records)} records (status:success)")
                        
                        # Format 2: direct "data" key
                        elif "data" in data and isinstance(data["data"], list):
                            records = data["data"]
                            self.log(f"📊 Found {len(records)} records (has data key)")
                        
                        # Format 3: other possible keys
                        else:
                            for key, value in data.items():
                                if isinstance(value, list):
                                    # Check if this looks like OTP data
                                    if len(value) > 0 and isinstance(value[0], dict):
                                        if any(k in value[0] for k in ["num", "phone", "message"]):
                                            records = value
                                            self.log(f"📊 Found {len(records)} records in key '{key}'")
                                            break
                    
                    elif isinstance(data, list):
                        records = data
                        self.log(f"📊 Found {len(records)} records (direct list)")
                    
                    if records:
                        return self.filter_new_records(records)
                    else:
                        self.log("⚠️ No records found in response")
                        return []
                        
                except json.JSONDecodeError as e:
                    self.log(f"❌ JSON parse error: {e}")
                    self.log(f"📄 Response text: {response.text[:200]}...")
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
    
    def filter_new_records(self, records: List[Dict]) -> List[Dict]:
        """Filter only new records"""
        filtered = []
        
        for record in records:
            record_time_str = record.get("dt", "")
            message_text = record.get("message", "")
            phone = record.get("num", "")
            
            # Create unique ID
            if message_text and phone:
                unique_id = f"{phone}_{hash(message_text[:100])}"
            elif message_text:
                unique_id = f"{hash(message_text[:100])}"
            elif phone:
                unique_id = f"{phone}_{record_time_str}"
            else:
                continue
            
            if unique_id not in self.processed_messages:
                filtered.append(record)
        
        self.log(f"📊 After filtering: {len(filtered)} new records")
        return filtered
    
    def detect_country_from_number(self, phone_number: str) -> str:
        """Detect country from phone number"""
        if not phone_number or phone_number == "Unknown":
            return "Unknown"
            
        num_str = str(phone_number).strip()
        
        # Clean the number
        if num_str.startswith('+'):
            num_str = num_str[1:]
        
        digits = ''.join(filter(str.isdigit, num_str))
        
        if not digits:
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
            '20': 'Egypt',
            '27': 'South Africa',
            '33': 'France',
            '34': 'Spain',
            '39': 'Italy',
            '44': 'UK',
            '49': 'Germany',
            '81': 'Japan',
            '82': 'South Korea',
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
            '238': 'Cape Verde',
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
        
        # Check prefixes from longest to shortest
        sorted_prefixes = sorted(prefixes.items(), key=lambda x: len(x[0]), reverse=True)
        
        for prefix, country in sorted_prefixes:
            if digits.startswith(prefix):
                return country
        
        return "Unknown"
    
    def extract_otp_code(self, message: str) -> str:
        """Extract OTP code from message"""
        if not message:
            return "N/A"
        
        # Clean message
        message = ' '.join(message.split())
        
        # Common OTP patterns
        patterns = [
            r'(\d{3}[-.\s]?\d{3})',  # 123-456, 123.456, 123 456
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
            r'code[\s]*is[\s]*(\d{4,8})',
            r'(\d{4,8})[\s]*for[\s]*verification',
            r'verification[\s]*code[\s]*(\d{4,8})'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            if matches:
                code = matches[0]
                # Clean the code
                code = ''.join(filter(str.isdigit, str(code)))
                if 4 <= len(code) <= 8:
                    return code
        
        # Try to find any 4-8 digit number
        all_numbers = re.findall(r'\d+', message)
        for num in all_numbers:
            if 4 <= len(num) <= 8:
                # Check if it's not a year or common number
                if not (num.startswith('19') or num.startswith('20') or len(num) > 8):
                    return num
        
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
        
        platform_indicators = {
            "WhatsApp": ["whatsapp", "wa ", "wa."],
            "Facebook": ["facebook", "fb ", "fb.", "meta"],
            "Telegram": ["telegram", "tg ", "tg."],
            "Google": ["google", "gmail", "youtube"],
            "Instagram": ["instagram", "insta"],
            "Twitter": ["twitter", "x.com", "tweet"],
            "Amazon": ["amazon"],
            "PayPal": ["paypal"],
            "TikTok": ["tiktok", "抖音"],
            "Snapchat": ["snapchat"],
            "LinkedIn": ["linkedin"],
            "Apple": ["apple", "icloud"],
            "Microsoft": ["microsoft", "outlook", "hotmail"],
            "Yahoo": ["yahoo"],
            "Netflix": ["netflix"],
            "Uber": ["uber"],
            "Grab": ["grab"],
            "Gojek": ["gojek"],
            "Bank": ["bank", "atm", "credit", "debit", "visa", "mastercard"],
            "Government": ["gov", "government", "irs", "tax"]
        }
        
        for platform, keywords in platform_indicators.items():
            for keyword in keywords:
                if keyword in message_lower or keyword in cli_lower:
                    return platform
        
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
                "Twitter": "🐦",
                "Amazon": "🛒",
                "PayPal": "💳",
                "TikTok": "🎵",
                "Snapchat": "👻",
                "LinkedIn": "💼",
                "Apple": "🍎",
                "Microsoft": "🪟",
                "Yahoo": "📧",
                "Netflix": "🎬",
                "Uber": "🚗",
                "Grab": "🚖",
                "Gojek": "🏍️",
                "Bank": "🏦",
                "Government": "🏛️",
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
                f"📝 *Message:*\n"
                f"`{message_text[:150]}{'...' if len(message_text) > 150 else ''}`"
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
                self.log(f"❌ Telegram error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Telegram send error: {e}")
            return False
    
    def process_otps(self):
        """Process OTPs"""
        if not self.bot_active:
            return 0
        
        self.log(f"🔄 Checking for new OTPs...")
        otp_list = self.get_otps_from_api()
        
        if not otp_list:
            if self.api_error_count > 0:
                self.log(f"⚠️ API error count: {self.api_error_count}")
            return 0
        
        sent_count = 0
        
        for otp_data in otp_list:
            message_text = otp_data.get("message", "")
            phone = otp_data.get("num", "")
            timestamp = otp_data.get("dt", "")
            
            # Create unique ID
            unique_id = f"{phone}_{timestamp}_{hash(message_text[:100])}"
            
            if unique_id not in self.processed_messages:
                otp_code = self.extract_otp_code(message_text)
                
                if otp_code != "N/A":
                    message = self.create_otp_message(otp_data)
                    
                    if message:
                        platform = self.detect_platform(message_text, otp_data.get("cli", ""))
                        country = self.detect_country_from_number(phone)
                        
                        self.log(f"🚀 SENDING: {platform} | {phone[:15]}... | {country} | OTP: {otp_code}")
                        
                        if self.send_otp_to_telegram(message):
                            self.processed_messages.add(unique_id)
                            sent_count += 1
                            self.log(f"✅ DELIVERED")
                        
                        time.sleep(0.5)
        
        if sent_count > 0:
            self.log(f"📊 Sent {sent_count} new OTPs")
        
        return sent_count
    
    def send_welcome_message(self):
        """Send welcome message"""
        try:
            message = (
                "🤖 *OTP BOT STARTED*\n\n"
                "✅ Bot is now **ACTIVE**\n"
                f"⚡ Checking every *{CONFIG['check_interval']} seconds*\n"
                f"🌍 *{len(COUNTRIES)-1} Countries* supported\n"
                "🔧 Advanced API detection\n\n"
                "🚨 **Only NEW OTPs will be sent**\n"
                "⚡ **Real-time delivery**\n\n"
                "📡 Testing API connection..."
            )
            self.send_group_message(message)
            self.log("✅ Welcome message sent")
            
        except Exception as e:
            self.log(f"⚠️ Welcome message error: {e}")
    
    def run(self):
        """Main bot loop"""
        print("=" * 60)
        print("🤖 JS OTP BOT - FIXED API VERSION")
        print("=" * 60)
        print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⚡ Check interval: {CONFIG['check_interval']}s")
        print(f"🌍 Countries supported: {len(COUNTRIES)-1}")
        print("=" * 60)
        
        # Test API connection first
        self.log("🔍 Initial API connection test...")
        success, params = self.test_api_connection(True)
        if success:
            self.log("✅ API connection successful")
            self.send_group_message("✅ API connection successful!")
        else:
            self.log("⚠️ API connection test failed")
            self.send_group_message("⚠️ API connection test failed - Bot will still try to connect")
        
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
                    
                    if sent_now == 0 and check_count % 10 == 0:
                        self.log(f"⏳ No new OTPs in last {check_count * CONFIG['check_interval']}s")
                    
                    # Re-test API if too many errors
                    if self.api_error_count >= 5:
                        self.log("⚠️ Too many API errors, re-testing connection...")
                        success, params = self.test_api_connection()
                        if success:
                            self.log("✅ API reconnected successfully")
                            self.api_error_count = 0
                        else:
                            self.log("❌ API reconnection failed")
                    
                    self.log(f"⏳ Next check in {CONFIG['check_interval']}s")
                else:
                    self.log(f"⏸️ Check #{check_count} - Bot inactive")
                
                print("-" * 40)
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
    print("JS OTP BOT - FIXED API CONNECTION")
    print("="*60)
    print("🎯 Features:")
    print(f"• Check interval: {CONFIG['check_interval']}s")
    print(f"• {len(COUNTRIES)-1} Countries supported")
    print("• Advanced API connection testing")
    print("• Better error handling")
    print("• Multiple API parameter attempts")
    print("="*60 + "\n")
    
    print("🚀 Starting bot in 3 seconds...")
    time.sleep(3)
    
    bot = OTPBot()
    bot.run()

if __name__ == "__main__":
    main()
