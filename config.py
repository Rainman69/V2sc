# Telegram API Configuration
# Get these from https://my.telegram.org
API_ID = 12345678  # Your API ID
API_HASH = "your_api_hash_here"  # Your API Hash
PHONE_NUMBER = "+1234567890"  # Your phone number

# Session settings
SESSION_NAME = "vpn_scanner"

# Default scanner settings
DEFAULT_SETTINGS = {
    "SCAN_INTERVAL": 60,  # Seconds between channel scans
    "DELAY_BETWEEN_CHANNELS": 5,  # Seconds between scanning each channel
    "DELAY_BETWEEN_MESSAGES": 1,  # Seconds between checking each message
    "MAX_MESSAGES_PER_SCAN": 50,  # Messages to check per channel per scan
    "ENABLED_SERVER_TYPES": ["vmess", "vless", "ss", "trojan", "wireguard", "outline"],
    "ENABLED_FILE_EXTENSIONS": [".bak", ".txt", ".npvt", ".ovpn", ".ehi", ".apk", ".conf"],
    "FILE_FORWARDING_ENABLED": True
}

# VPN server patterns
VPN_PATTERNS = {
    "vmess": [
        r"vmess://[A-Za-z0-9+/=]+",
        r"vmess://[^\s]+",
    ],
    "vless": [
        r"vless://[A-Za-z0-9+/=\-_.~]+@[^\s]+",
        r"vless://[^\s]+",
    ],
    "shadowsocks": [
        r"ss://[A-Za-z0-9+/=]+@[^\s]+",
        r"shadowsocks://[^\s]+",
    ],
    "trojan": [
        r"trojan://[A-Za-z0-9+/=\-_.~]+@[^\s]+",
        r"trojan://[^\s]+",
    ],
    "wireguard": [
        r"\[Interface\][\s\S]*?\[Peer\][\s\S]*?",
        r"wg://[^\s]+",
    ],
    "outline": [
        r"ss://[A-Za-z0-9+/=]+#[^\s]+",
        r"outline://[^\s]+",
    ],
    "proxy_links": [
        r"https://t\.me/proxy\?server=[^\s]+",
        r"tg://proxy\?server=[^\s]+",
    ]
}

# Command settings
COMMAND_PREFIX = "vpn:"
COMMANDS = {
    "start": "vpn:start",
    "stop": "vpn:stop",
    "status": "vpn:status",
    "settings": "vpn:settings",
    "groups": "vpn:groups",
    "set_target": "vpn:set_target",
    "logs": "vpn:logs",
    "toggle_files": "vpn:toggle_files",
    "enable_server": "vpn:enable_server",
    "disable_server": "vpn:disable_server",
    "restart": "vpn:restart"
}

# Storage keys
LOG_CHANNEL_KEY = "📋 VPN_SCANNER_LOGS"
SETTINGS_KEY = "⚙️ VPN_SCANNER_SETTINGS"
TARGET_GROUP_KEY = "🎯 VPN_TARGET_GROUP"
