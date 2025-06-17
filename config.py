# Telegram API Configuration
API_ID = 25255297
API_HASH = "92c68d49f5d47362c8a73ef3cb769bc7"
PHONE_NUMBER = "+989224053123"

# Session settings
SESSION_NAME = "vpn_scanner"

# Default scanner settings
DEFAULT_SETTINGS = {
    "SCAN_INTERVAL": 60,
    "DELAY_BETWEEN_CHANNELS": 10,
    "DELAY_BETWEEN_MESSAGES": 2,
    "MAX_MESSAGES_PER_SCAN": 50,
    "ENABLED_SERVER_TYPES": ["vmess", "vless", "ss", "trojan", "wireguard", "outline"],
    "ENABLED_FILE_EXTENSIONS": [".bak", ".txt", ".npvt", ".ovpn", ".ehi", ".apk", ".conf"],
    "FILE_FORWARDING_ENABLED": True,
    "REAL_TIME_MODE": True  # New setting for real-time processing
}

# VPN server patterns (fixed regex patterns)
VPN_PATTERNS = {
    "vmess": [
        r"vmess://[A-Za-z0-9+/=]+",
        r"vmess://[^\s]+",
    ],
    "vless": [
        r"vless://[A-Za-z0-9+/=\-_.~]+@[^\s]+",
        r"vless://[^\s]+",
    ],
    "ss": [  # Fixed key name
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
    ],
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
    "restart": "vpn:restart",
    "toggle_realtime": "vpn:toggle_realtime"  # New command
}

# Storage keys
LOG_CHANNEL_KEY = "📋 VPN_SCANNER_LOGS"
SETTINGS_KEY = "⚙️ VPN_SCANNER_SETTINGS"
TARGET_GROUP_KEY = "🎯 VPN_TARGET_GROUP"
