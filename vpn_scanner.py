import asyncio
import json
import re
import time
import os
from datetime import datetime, timedelta
from telethon import TelegramClient, events, errors
from telethon.tl.functions.channels import CreateChannelRequest
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, DocumentAttributeFilename
import config

class VPNScanner:
    def __init__(self):
        self.client = TelegramClient(
            config.SESSION_NAME,
            config.API_ID,
            config.API_HASH
        )
        self.scanning = False
        self.target_group_id = None
        self.log_channel_id = None
        self.settings = config.DEFAULT_SETTINGS.copy()
        self.scan_stats = {
            'total_scans': 0,
            'servers_found': 0,
            'files_forwarded': 0,
            'last_scan': None,
            'start_time': None
        }
        
    async def start(self):
        """Initialize and start the client"""
        await self.client.start(phone=config.PHONE_NUMBER)
        me = await self.client.get_me()
        
        # Load previous settings
        await self.load_settings()
        await self.load_target_group()
        
        # Create or get log channel
        await self.setup_log_channel()
        
        # Send startup message
        await self.log_message(
            f"🤖 **VPN Scanner Started**\n\n"
            f"👤 Account: @{me.username}\n"
            f"📊 Scan interval: {self.settings['SCAN_INTERVAL']} seconds\n"
            f"🎯 Target group: {'Set' if self.target_group_id else 'Not set'}\n\n"
            f"**Available Commands:**\n"
            f"• `{config.COMMANDS['groups']}` - List available groups\n"
            f"• `{config.COMMANDS['set_target']} GROUP_ID` - Set target group\n"
            f"• `{config.COMMANDS['start']}` - Start scanning\n"
            f"• `{config.COMMANDS['stop']}` - Stop scanning\n"
            f"• `{config.COMMANDS['status']}` - Show status\n"
            f"• `{config.COMMANDS['settings']}` - Configure settings\n"
            f"• `{config.COMMANDS['toggle_files']}` - Toggle file forwarding\n"
            f"• `{config.COMMANDS['restart']}` - Restart scanner"
        )
        
    async def setup_log_channel(self):
        """Create or find log channel"""
        try:
            # Check if log channel already exists
            async for dialog in self.client.iter_dialogs():
                if dialog.title == "VPN Scanner Logs" and dialog.is_channel:
                    self.log_channel_id = dialog.id
                    return
                    
            # Create new log channel
            result = await self.client(CreateChannelRequest(
                title="VPN Scanner Logs",
                about="Automated logs for VPN Scanner Bot",
                broadcast=True
            ))
            
            self.log_channel_id = result.chats[0].id
            await self.log_message("📋 **Log Channel Created Successfully**")
            
        except Exception as e:
            print(f"❌ Error setting up log channel: {e}")
    
    async def log_message(self, message):
        """Send message to log channel and saved messages"""
        try:
            # Send to log channel
            if self.log_channel_id:
                await self.client.send_message(self.log_channel_id, message)
            
            # Also send to saved messages as backup
            await self.client.send_message('me', f"[LOG] {message}")
            
        except Exception as e:
            print(f"❌ Error logging message: {e}")
    
    async def load_settings(self):
        """Load scanner settings from saved messages"""
        try:
            async for message in self.client.iter_messages('me', limit=50):
                if message.text and config.SETTINGS_KEY in message.text:
                    lines = message.text.split('\n')
                    for line in lines:
                        if '=' in line and not line.startswith('**'):
                            try:
                                key, value = line.split('=', 1)
                                key = key.strip()
                                if key in self.settings:
                                    if isinstance(self.settings[key], list):
                                        self.settings[key] = value.strip().split(',')
                                    elif isinstance(self.settings[key], bool):
                                        self.settings[key] = value.strip().lower() == 'true'
                                    elif isinstance(self.settings[key], int):
                                        self.settings[key] = int(value.strip())
                            except:
                                continue
                    break
        except Exception as e:
            await self.log_message(f"❌ Error loading settings: {e}")
    
    async def save_settings(self):
        """Save current settings to saved messages"""
        settings_text = f"{config.SETTINGS_KEY}\n\n"
        settings_text += "**Current VPN Scanner Settings:**\n\n"
        for key, value in self.settings.items():
            if isinstance(value, list):
                settings_text += f"{key} = {','.join(map(str, value))}\n"
            else:
                settings_text += f"{key} = {value}\n"
        
        # Find and update existing settings message
        try:
            async for message in self.client.iter_messages('me', limit=50):
                if message.text and config.SETTINGS_KEY in message.text:
                    await message.edit(settings_text)
                    return
        except:
            pass
        
        # Create new settings message
        await self.client.send_message('me', settings_text)
    
    async def load_target_group(self):
        """Load target group ID from saved messages"""
        try:
            async for message in self.client.iter_messages('me', limit=50):
                if message.text and config.TARGET_GROUP_KEY in message.text:
                    lines = message.text.split('\n')
                    for line in lines:
                        if 'GROUP_ID:' in line:
                            self.target_group_id = int(line.split('GROUP_ID:')[1].strip())
                            break
                    break
        except Exception as e:
            await self.log_message(f"❌ Error loading target group: {e}")
    
    async def save_target_group(self, group_id):
        """Save target group ID to saved messages"""
        target_text = f"{config.TARGET_GROUP_KEY}\n\nGROUP_ID: {group_id}"
        
        # Find and update existing target message
        try:
            async for message in self.client.iter_messages('me', limit=50):
                if message.text and config.TARGET_GROUP_KEY in message.text:
                    await message.edit(target_text)
                    return
        except:
            pass
        
        # Create new target message
        await self.client.send_message('me', target_text)
    
    async def get_channels_list(self):
        """Get list of all channels the account has joined"""
        channels = []
        try:
            async for dialog in self.client.iter_dialogs():
                if dialog.is_channel and not dialog.is_group:
                    channels.append({
                        'id': dialog.id,
                        'title': dialog.title,
                        'username': dialog.entity.username or 'No username'
                    })
            return channels
        except Exception as e:
            await self.log_message(f"❌ Error getting channels: {e}")
            return []
    
    async def get_groups_list(self):
        """Get list of all groups the account has joined"""
        groups = []
        try:
            async for dialog in self.client.iter_dialogs():
                if dialog.is_group:
                    groups.append({
                        'id': dialog.id,
                        'title': dialog.title,
                        'participants': getattr(dialog.entity, 'participants_count', 'Unknown')
                    })
            return groups
        except Exception as e:
            await self.log_message(f"❌ Error getting groups: {e}")
            return []
    
    def extract_vpn_configs(self, text):
        """Extract VPN configurations from text"""
        found_configs = []
        
        for server_type in self.settings['ENABLED_SERVER_TYPES']:
            if server_type not in config.VPN_PATTERNS:
                continue
                
            for pattern in config.VPN_PATTERNS[server_type]:
                matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    found_configs.append({
                        'type': server_type,
                        'config': match.strip()
                    })
        
        return found_configs
    
    async def check_file_extension(self, message):
        """Check if message contains file with target extensions"""
        if not message.document:
            return None
            
        # Get filename
        filename = None
        for attr in message.document.attributes:
            if isinstance(attr, DocumentAttributeFilename):
                filename = attr.file_name
                break
        
        if not filename:
            return None
        
        # Check if extension matches
        for ext in self.settings['ENABLED_FILE_EXTENSIONS']:
            if filename.lower().endswith(ext.lower()):
                return {
                    'filename': filename,
                    'extension': ext,
                    'size': message.document.size
                }
        
        return None
    
    async def forward_content(self, content, source_channel, content_type='server'):
        """Forward VPN config or file to target group"""
        if not self.target_group_id:
            return False
            
        try:
            if content_type == 'server':
                # Forward VPN server config
                caption = (
                    f"🔒 **{content['type'].upper()} Server**\n\n"
                    f"📡 Source: {source_channel}\n"
                    f"⏰ Found: {datetime.now().strftime('%H:%M:%S')}\n\n"
                    f"``````"
                )
                await self.client.send_message(self.target_group_id, caption)
                
            elif content_type == 'file':
                # Forward file with caption
                caption = (
                    f"📁 **VPN Config File**\n\n"
                    f"📄 Filename: `{content['filename']}`\n"
                    f"📊 Size: {content['size']} bytes\n"
                    f"📡 Source: {source_channel}\n"
                    f"⏰ Found: {datetime.now().strftime('%H:%M:%S')}"
                )
                await self.client.forward_messages(
                    self.target_group_id,
                    content['message'],
                    source_channel
                )
                await self.client.send_message(self.target_group_id, caption)
            
            return True
            
        except Exception as e:
            await self.log_message(f"❌ Error forwarding content: {e}")
            return False
    
    async def scan_channel(self, channel):
        """Scan a specific channel for VPN configs"""
        channel_stats = {
            'servers_found': 0,
            'files_forwarded': 0,
            'messages_scanned': 0
        }
        
        try:
            # Get recent messages
            messages = await self.client.get_messages(
                channel['id'],
                limit=self.settings['MAX_MESSAGES_PER_SCAN']
            )
            
            for message in messages:
                if not self.scanning:
                    break
                    
                channel_stats['messages_scanned'] += 1
                
                # Check for VPN configs in text
                if message.text:
                    configs = self.extract_vpn_configs(message.text)
                    for config_data in configs:
                        success = await self.forward_content(
                            config_data,
                            channel['title'],
                            'server'
                        )
                        if success:
                            channel_stats['servers_found'] += 1
                            self.scan_stats['servers_found'] += 1
                
                # Check for files if enabled
                if self.settings['FILE_FORWARDING_ENABLED']:
                    file_info = await self.check_file_extension(message)
                    if file_info:
                        file_info['message'] = message
                        success = await self.forward_content(
                            file_info,
                            channel['title'],
                            'file'
                        )
                        if success:
                            channel_stats['files_forwarded'] += 1
                            self.scan_stats['files_forwarded'] += 1
                
                # Rate limiting
                await asyncio.sleep(self.settings['DELAY_BETWEEN_MESSAGES'])
            
            # Log channel scan results
            if channel_stats['servers_found'] > 0 or channel_stats['files_forwarded'] > 0:
                await self.log_message(
                    f"📡 **Channel Scan Complete**\n\n"
                    f"📺 Channel: {channel['title']}\n"
                    f"📊 Messages scanned: {channel_stats['messages_scanned']}\n"
                    f"🔒 Servers found: {channel_stats['servers_found']}\n"
                    f"📁 Files forwarded: {channel_stats['files_forwarded']}"
                )
                
        except Exception as e:
            await self.log_message(f"❌ Error scanning {channel['title']}: {e}")
        
        return channel_stats
    
    async def start_scanning(self):
        """Start the main scanning loop"""
        if self.scanning:
            await self.log_message("⚠️ **Scanner already running!**")
            return
            
        if not self.target_group_id:
            await self.log_message("❌ **No target group set! Use vpn:set_target command first.**")
            return
        
        self.scanning = True
        self.scan_stats['start_time'] = datetime.now()
        
        await self.log_message(
            f"🚀 **VPN Scanner Started**\n\n"
            f"⏱️ Scan interval: {self.settings['SCAN_INTERVAL']} seconds\n"
            f"🎯 Target group ID: {self.target_group_id}"
        )
        
        # Get channels list
        channels = await self.get_channels_list()
        await self.log_message(f"📡 Found {len(channels)} channels to scan")
        
        # Main scanning loop
        while self.scanning:
            try:
                scan_start = datetime.now()
                scan_results = {
                    'channels_scanned': 0,
                    'total_servers': 0,
                    'total_files': 0
                }
                
                # Scan each channel
                for channel in channels:
                    if not self.scanning:
                        break
                        
                    stats = await self.scan_channel(channel)
                    scan_results['channels_scanned'] += 1
                    scan_results['total_servers'] += stats['servers_found']
                    scan_results['total_files'] += stats['files_forwarded']
                    
                    # Delay between channels
                    await asyncio.sleep(self.settings['DELAY_BETWEEN_CHANNELS'])
                
                # Update scan statistics
                self.scan_stats['total_scans'] += 1
                self.scan_stats['last_scan'] = datetime.now()
                
                # Log scan completion
                scan_duration = datetime.now() - scan_start
                await self.log_message(
                    f"✅ **Scan #{self.scan_stats['total_scans']} Complete**\n\n"
                    f"⏱️ Duration: {scan_duration.seconds} seconds\n"
                    f"📺 Channels: {scan_results['channels_scanned']}\n"
                    f"🔒 Servers found: {scan_results['total_servers']}\n"
                    f"📁 Files forwarded: {scan_results['total_files']}\n\n"
                    f"⏳ Next scan in {self.settings['SCAN_INTERVAL']} seconds"
                )
                
                # Wait for next scan
                if self.scanning:
                    await asyncio.sleep(self.settings['SCAN_INTERVAL'])
                    
            except Exception as e:
                await self.log_message(f"❌ **Critical scan error:** {e}")
                await asyncio.sleep(30)  # Wait before retrying
    
    async def stop_scanning(self):
        """Stop the scanning process"""
        if not self.scanning:
            await self.log_message("ℹ️ **Scanner not running**")
            return
            
        self.scanning = False
        runtime = datetime.now() - self.scan_stats['start_time']
        
        await self.log_message(
            f"⏹️ **Scanner Stopped**\n\n"
            f"⏱️ Total runtime: {str(runtime).split('.')[0]}\n"
            f"📊 Total scans: {self.scan_stats['total_scans']}\n"
            f"🔒 Total servers found: {self.scan_stats['servers_found']}\n"
            f"📁 Total files forwarded: {self.scan_stats['files_forwarded']}"
        )
    
    async def show_status(self):
        """Show current scanner status"""
        if self.scanning:
            runtime = datetime.now() - self.scan_stats['start_time']
            status = (
                f"🔄 **Scanner Running**\n\n"
                f"⏱️ Runtime: {str(runtime).split('.')[0]}\n"
                f"📊 Scans completed: {self.scan_stats['total_scans']}\n"
                f"🔒 Servers found: {self.scan_stats['servers_found']}\n"
                f"📁 Files forwarded: {self.scan_stats['files_forwarded']}\n"
                f"⏰ Last scan: {self.scan_stats['last_scan'].strftime('%H:%M:%S') if self.scan_stats['last_scan'] else 'None'}"
            )
        else:
            status = (
                f"⏹️ **Scanner Idle**\n\n"
                f"📊 Total scans: {self.scan_stats['total_scans']}\n"
                f"🔒 Total servers found: {self.scan_stats['servers_found']}\n"
                f"📁 Total files forwarded: {self.scan_stats['files_forwarded']}\n"
                f"🎯 Target group: {'Set' if self.target_group_id else 'Not set'}"
            )
        
        await self.log_message(status)
    
    @events.register(events.NewMessage(chats='me'))
    async def handle_commands(self, event):
        """Handle commands from saved messages"""
        if not event.text or not event.text.startswith(config.COMMAND_PREFIX):
            return
            
        text = event.text.strip()
        command_parts = text.split()
        command = command_parts[0]
        
        try:
            if command == config.COMMANDS['start']:
                asyncio.create_task(self.start_scanning())
                
            elif command == config.COMMANDS['stop']:
                await self.stop_scanning()
                
            elif command == config.COMMANDS['restart']:
                await self.stop_scanning()
                await asyncio.sleep(5)
                asyncio.create_task(self.start_scanning())
                
            elif command == config.COMMANDS['status']:
                await self.show_status()
                
            elif command == config.COMMANDS['groups']:
                groups = await self.get_groups_list()
                groups_text = "📋 **Available Groups:**\n\n"
                for i, group in enumerate(groups[:20], 1):
                    groups_text += f"{i}. **{group['title']}**\n"
                    groups_text += f"   ID: `{group['id']}`\n"
                    groups_text += f"   Members: {group['participants']}\n\n"
                groups_text += f"\nUse `{config.COMMANDS['set_target']} GROUP_ID` to set target"
                await self.client.send_message('me', groups_text)
                
            elif command == config.COMMANDS['set_target'] and len(command_parts) > 1:
                try:
                    group_id = int(command_parts[1])
                    self.target_group_id = group_id
                    await self.save_target_group(group_id)
                    await self.log_message(f"✅ **Target group set to:** {group_id}")
                except ValueError:
                    await self.client.send_message('me', "❌ Invalid group ID format")
                    
            elif command == config.COMMANDS['toggle_files']:
                self.settings['FILE_FORWARDING_ENABLED'] = not self.settings['FILE_FORWARDING_ENABLED']
                await self.save_settings()
                status = "enabled" if self.settings['FILE_FORWARDING_ENABLED'] else "disabled"
                await self.log_message(f"📁 **File forwarding {status}**")
                
            elif command == config.COMMANDS['settings']:
                await self.show_settings()
                
            # Handle setting changes
            elif '=' in text and not text.startswith(config.COMMAND_PREFIX):
                await self.handle_setting_change(text)
                
            await event.delete()
            
        except Exception as e:
            await self.log_message(f"❌ Command error: {e}")
    
    async def show_settings(self):
        """Show current settings"""
        settings_text = (
            f"⚙️ **Current Settings**\n\n"
            f"⏱️ Scan interval: {self.settings['SCAN_INTERVAL']} seconds\n"
            f"📺 Channel delay: {self.settings['DELAY_BETWEEN_CHANNELS']} seconds\n"
            f"💬 Message delay: {self.settings['DELAY_BETWEEN_MESSAGES']} seconds\n"
            f"📊 Max messages per scan: {self.settings['MAX_MESSAGES_PER_SCAN']}\n"
            f"📁 File forwarding: {'Enabled' if self.settings['FILE_FORWARDING_ENABLED'] else 'Disabled'}\n\n"
            f"**Enabled servers:** {', '.join(self.settings['ENABLED_SERVER_TYPES'])}\n"
            f"**File extensions:** {', '.join(self.settings['ENABLED_FILE_EXTENSIONS'])}\n\n"
            f"**To change settings, send:**\n"
            f"`SCAN_INTERVAL = 120`\n"
            f"`ENABLED_SERVER_TYPES = vmess,vless,ss`"
        )
        await self.client.send_message('me', settings_text)
    
    async def handle_setting_change(self, text):
        """Handle setting changes"""
        try:
            key, value = text.split('=', 1)
            key = key.strip()
            value = value.strip()
            
            if key in self.settings:
                if isinstance(self.settings[key], list):
                    self.settings[key] = [item.strip() for item in value.split(',')]
                elif isinstance(self.settings[key], bool):
                    self.settings[key] = value.lower() in ['true', '1', 'yes', 'on']
                elif isinstance(self.settings[key], int):
                    self.settings[key] = int(value)
                    
                await self.save_settings()
                await self.log_message(f"✅ **Updated {key}:** {self.settings[key]}")
            else:
                await self.client.send_message('me', f"❌ Unknown setting: {key}")
                
        except Exception as e:
            await self.log_message(f"❌ Setting change error: {e}")
    
    async def run(self):
        """Main run function"""
        await self.start()
        
        # Register event handler
        self.client.add_event_handler(self.handle_commands)
        
        await self.log_message("🤖 **VPN Scanner Ready**")
        print("🤖 VPN Scanner is running...")
        print("💬 Send commands to your Saved Messages to control the scanner")
        
        # Keep running
        await self.client.run_until_disconnected()

async def main():
    scanner = VPNScanner()
    
    try:
        await scanner.run()
    except KeyboardInterrupt:
        print("\n⏹️ Scanner stopped by user")
        await scanner.stop_scanning()
    except Exception as e:
        print(f"❌ Critical error: {e}")
        if scanner.log_channel_id:
            await scanner.log_message(f"❌ **Critical system error:** {e}")
    finally:
        if scanner.client.is_connected():
            await scanner.client.disconnect()
        print("👋 Disconnected from Telegram")

if __name__ == "__main__":
    asyncio.run(main())
