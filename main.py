import discord
from discord.ext import commands, tasks
from flask import Flask
from threading import Thread
import os
import json
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta
import asyncio

CHEF_ID = int(os.environ.get("CHEF_ID", "1273760276466106539"))
ADMIN_ROLE_ID = int(os.environ.get("ADMIN_ROLE_ID", "1407802972414541935"))
XP_MANAGER_ROLE_ID = int(os.environ.get("XP_MANAGER_ROLE_ID", "1432378602346905780"))
EMOJI_DON = os.environ.get("EMOJI_DON", "<:XP:1432103672761815252>")
DATA_FILE = "xp_data.json"
MESSAGE_TRACKER_FILE = "message_tracker.json"
INVENTORY_FILE = "inventory_data.json"
BOOSTERS_FILE = "boosters_data.json"
INVITER_TRACKER_FILE = "inviter_tracker.json"
COMMAND_SETTINGS_FILE = "command_settings.json"
DAILY_COOLDOWNS_FILE = "daily_cooldowns.json"
XP_REACTIONS_FILE = "xp_reactions.json"
XP_CONFIG_FILE = "xp_config.json"
XP_CHANNELS_FILE = "xp_channels.json"
XP_REACTION_ENABLED_FILE = "xp_reaction_enabled.json"
SHOP_ITEMS_FILE = "shop_items.json"
EVENTS_STATE_FILE = "events_state.json"
XP_REACTION_TIMER_FILE = "xp_reaction_timer.json"

XP_CHANNELS = [1409156083859193949, 1407817830279151766, 1407820173657903113]
XP_NOTIFICATION_CHANNEL = 1432175287948542063
BOOST_NOTIFICATION_CHANNEL = 1407815433100202025
BACKUP_CHANNEL_ID = 1432482977497088030
BACKUP_INTERVAL_MINUTES = 15

def load_xp():
    if Path(DATA_FILE).exists():
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                return {int(k): v for k, v in data.items()}
        except json.JSONDecodeError:
            return {}
    return {}

def save_xp(xp_dict):
    with open(DATA_FILE, 'w') as f:
        json.dump(xp_dict, f, indent=2)

def load_message_tracker():
    if Path(MESSAGE_TRACKER_FILE).exists():
        try:
            with open(MESSAGE_TRACKER_FILE, 'r') as f:
                data = json.load(f)
                return {int(k): v for k, v in data.items()}
        except json.JSONDecodeError:
            return {}
    return {}

def save_message_tracker(tracker_dict):
    with open(MESSAGE_TRACKER_FILE, 'w') as f:
        json.dump(tracker_dict, f, indent=2)

def load_inventory():
    if Path(INVENTORY_FILE).exists():
        try:
            with open(INVENTORY_FILE, 'r') as f:
                data = json.load(f)
                return {int(k): v for k, v in data.items()}
        except json.JSONDecodeError:
            return {}
    return {}

def save_inventory(inventory_dict):
    with open(INVENTORY_FILE, 'w') as f:
        json.dump(inventory_dict, f, indent=2)

def load_boosters():
    if Path(BOOSTERS_FILE).exists():
        try:
            with open(BOOSTERS_FILE, 'r') as f:
                data = json.load(f)
                return {int(k): v for k, v in data.items()}
        except json.JSONDecodeError:
            return {}
    return {}

def save_boosters(boosters_dict):
    with open(BOOSTERS_FILE, 'w') as f:
        json.dump(boosters_dict, f, indent=2)

def load_inviter_tracker():
    if Path(INVITER_TRACKER_FILE).exists():
        try:
            with open(INVITER_TRACKER_FILE, 'r') as f:
                data = json.load(f)
                return {int(k): int(v) for k, v in data.items()}
        except json.JSONDecodeError:
            return {}
    return {}

def save_inviter_tracker(tracker_dict):
    with open(INVITER_TRACKER_FILE, 'w') as f:
        json.dump(tracker_dict, f, indent=2)

def load_command_settings():
    if Path(COMMAND_SETTINGS_FILE).exists():
        try:
            with open(COMMAND_SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_command_settings(settings_dict):
    with open(COMMAND_SETTINGS_FILE, 'w') as f:
        json.dump(settings_dict, f, indent=2)

def load_daily_cooldowns():
    if Path(DAILY_COOLDOWNS_FILE).exists():
        try:
            with open(DAILY_COOLDOWNS_FILE, 'r') as f:
                data = json.load(f)
                return {int(k): v for k, v in data.items()}
        except json.JSONDecodeError:
            return {}
    return {}

def save_daily_cooldowns(cooldowns_dict):
    with open(DAILY_COOLDOWNS_FILE, 'w') as f:
        json.dump(cooldowns_dict, f, indent=2)

def load_xp_reactions():
    if Path(XP_REACTIONS_FILE).exists():
        try:
            with open(XP_REACTIONS_FILE, 'r') as f:
                data = json.load(f)
                return {int(k): v for k, v in data.items()}
        except json.JSONDecodeError:
            return {}
    return {}

def save_xp_reactions(reactions_dict):
    with open(XP_REACTIONS_FILE, 'w') as f:
        json.dump(reactions_dict, f, indent=2)

def load_xp_config():
    if Path(XP_CONFIG_FILE).exists():
        try:
            with open(XP_CONFIG_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {
        "xp_per_message": 1,
        "max_xp_per_hour": 5,
        "daily_xp_reward": 20,
        "emoji_xp_amount": 50,
        "xp_invitation": 25,
        "xp_boost": 500,
        "emoji_xp_cooldown_hours": 1
    }

def save_xp_config(config_dict):
    with open(XP_CONFIG_FILE, 'w') as f:
        json.dump(config_dict, f, indent=2)

def load_xp_channels():
    if Path(XP_CHANNELS_FILE).exists():
        try:
            with open(XP_CHANNELS_FILE, 'r') as f:
                data = json.load(f)
                return [int(ch) for ch in data]
        except (json.JSONDecodeError, ValueError):
            return []
    return []

def save_xp_channels(channels_list):
    with open(XP_CHANNELS_FILE, 'w') as f:
        json.dump(channels_list, f, indent=2)

def load_xp_reaction_enabled():
    if Path(XP_REACTION_ENABLED_FILE).exists():
        try:
            with open(XP_REACTION_ENABLED_FILE, 'r') as f:
                data = json.load(f)
                return data.get("enabled", True)
        except (json.JSONDecodeError, KeyError):
            return True
    return True

def save_xp_reaction_enabled(enabled):
    with open(XP_REACTION_ENABLED_FILE, 'w') as f:
        json.dump({"enabled": enabled}, f, indent=2)

def load_shop_items():
    if Path(SHOP_ITEMS_FILE).exists():
        try:
            with open(SHOP_ITEMS_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {
        "1": {"name": "💬 Discord add", "price": 500},
        "2": {"name": "🎮 Brawl Stars add", "price": 1000}
    }

def save_shop_items(items_dict):
    with open(SHOP_ITEMS_FILE, 'w') as f:
        json.dump(items_dict, f, indent=2)

def load_events_state():
    if Path(EVENTS_STATE_FILE).exists():
        try:
            with open(EVENTS_STATE_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {
        "event": {"enabled": False, "expires_at": None, "xp_reward": 100, "cooldown_hours": 24},
        "gift": {"enabled": False, "expires_at": None, "xp_reward": 50, "cooldown_hours": 12}
    }

def save_events_state(state_dict):
    with open(EVENTS_STATE_FILE, 'w') as f:
        json.dump(state_dict, f, indent=2)

def load_xp_reaction_timer():
    if Path(XP_REACTION_TIMER_FILE).exists():
        try:
            with open(XP_REACTION_TIMER_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {"enabled": True, "expires_at": None}

def save_xp_reaction_timer(timer_dict):
    with open(XP_REACTION_TIMER_FILE, 'w') as f:
        json.dump(timer_dict, f, indent=2)

ALL_JSON_FILES = [
    DATA_FILE,
    MESSAGE_TRACKER_FILE,
    INVENTORY_FILE,
    BOOSTERS_FILE,
    INVITER_TRACKER_FILE,
    COMMAND_SETTINGS_FILE,
    DAILY_COOLDOWNS_FILE,
    XP_REACTIONS_FILE,
    XP_CONFIG_FILE,
    XP_CHANNELS_FILE,
    XP_REACTION_ENABLED_FILE,
    SHOP_ITEMS_FILE,
    EVENTS_STATE_FILE,
    XP_REACTION_TIMER_FILE
]

async def backup_to_discord():
    try:
        channel = bot.get_channel(BACKUP_CHANNEL_ID)
        if not channel:
            print(f"❌ Backup channel not found (ID: {BACKUP_CHANNEL_ID})")
            return
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        files_to_send = []
        
        for json_file in ALL_JSON_FILES:
            if Path(json_file).exists():
                files_to_send.append(json_file)
        
        if files_to_send:
            total_files = len(files_to_send)
            batch_size = 10
            
            for i in range(0, total_files, batch_size):
                batch = files_to_send[i:i + batch_size]
                discord_files = [discord.File(f) for f in batch]
                
                if i == 0:
                    await channel.send(
                        f"🔄 **Automatic Backup** - {timestamp}\n"
                        f"📦 {total_files} files saved (batch {i//batch_size + 1}/{(total_files + batch_size - 1)//batch_size})",
                        files=discord_files
                    )
                else:
                    await channel.send(
                        f"📦 Batch {i//batch_size + 1}/{(total_files + batch_size - 1)//batch_size}",
                        files=discord_files
                    )
            
            print(f"✅ Backup completed: {total_files} files sent to Discord in {(total_files + batch_size - 1)//batch_size} batch(es)")
        else:
            print("⚠️ No JSON files to backup")
    except Exception as e:
        print(f"❌ Backup error: {e}")

async def restore_from_discord():
    try:
        channel = bot.get_channel(BACKUP_CHANNEL_ID)
        if not channel:
            print(f"❌ Backup channel not found (ID: {BACKUP_CHANNEL_ID})")
            return
        
        print("🔍 Looking for backups in Discord...")
        
        async for message in channel.history(limit=50):
            if message.author == bot.user and message.attachments:
                print(f"📥 Found backup from {message.created_at}")
                
                for attachment in message.attachments:
                    if attachment.filename.endswith('.json'):
                        file_path = Path(attachment.filename)
                        await attachment.save(file_path)
                        print(f"  ✅ Restored: {attachment.filename}")
                
                print("🎉 Backup restoration completed!")
                return
        
        print("ℹ️ No backup found in Discord, using existing files")
    except Exception as e:
        print(f"❌ Restore error: {e}")

async def disable_xp_reaction_timer():
    global xp_reaction_enabled, xp_reaction_timer
    xp_reaction_enabled = False
    xp_reaction_timer["enabled"] = False
    xp_reaction_timer["expires_at"] = None
    save_xp_reaction_enabled(False)
    save_xp_reaction_timer(xp_reaction_timer)
    print("⏰ XP Reaction timer expired - disabled")

async def disable_event_timer(event_name):
    global events_state
    events_state[event_name]["enabled"] = False
    events_state[event_name]["expires_at"] = None
    save_events_state(events_state)
    print(f"⏰ {event_name.capitalize()} timer expired - disabled")

async def schedule_xp_reaction_disable(minutes):
    global xp_reaction_timer_task
    if xp_reaction_timer_task and not xp_reaction_timer_task.done():
        xp_reaction_timer_task.cancel()
    await asyncio.sleep(minutes * 60)
    await disable_xp_reaction_timer()

async def schedule_event_disable(event_name, minutes):
    global event_timer_task, gift_timer_task
    await asyncio.sleep(minutes * 60)
    await disable_event_timer(event_name)

async def restore_timers():
    global xp_reaction_timer_task, xp_reaction_enabled, xp_reaction_timer
    global event_timer_task, gift_timer_task, events_state
    
    if xp_reaction_timer.get("expires_at"):
        expires = datetime.fromisoformat(xp_reaction_timer["expires_at"])
        now = datetime.now()
        if now < expires:
            remaining = (expires - now).total_seconds() / 60
            xp_reaction_enabled = True
            xp_reaction_timer_task = asyncio.create_task(schedule_xp_reaction_disable(remaining))
            print(f"🔄 Restored XP Reaction timer: {remaining:.1f} minutes remaining")
        else:
            await disable_xp_reaction_timer()
    
    for event_name in ["event", "gift"]:
        if events_state[event_name].get("expires_at"):
            expires = datetime.fromisoformat(events_state[event_name]["expires_at"])
            now = datetime.now()
            if now < expires:
                remaining = (expires - now).total_seconds() / 60
                events_state[event_name]["enabled"] = True
                task = asyncio.create_task(schedule_event_disable(event_name, remaining))
                if event_name == "event":
                    event_timer_task = task
                else:
                    gift_timer_task = task
                print(f"🔄 Restored {event_name} timer: {remaining:.1f} minutes remaining")
            else:
                await disable_event_timer(event_name)

def is_command_enabled(command_name):
    return command_settings.get(command_name, True)

def is_chef_or_admin(user, member=None):
    if user.id == CHEF_ID:
        return True
    if member and hasattr(member, 'roles'):
        for role in member.roles:
            if role.id == ADMIN_ROLE_ID:
                return True
    return False

def is_chef_or_xp_manager(user, member=None):
    if user.id == CHEF_ID:
        return True
    if member and hasattr(member, 'roles'):
        for role in member.roles:
            if role.id == XP_MANAGER_ROLE_ID:
                return True
    return False

xp_data = load_xp()
invites_cache = {}
message_tracker = load_message_tracker()
inventory_data = load_inventory()
boosters_data = load_boosters()
inviter_tracker = load_inviter_tracker()
command_settings = load_command_settings()
daily_cooldowns = load_daily_cooldowns()
xp_reactions = load_xp_reactions()
xp_config = load_xp_config()
xp_reaction_channels = load_xp_channels()
xp_reaction_enabled = load_xp_reaction_enabled()
shop_items = load_shop_items()
events_state = load_events_state()
xp_reaction_timer = load_xp_reaction_timer()
emoji_xp_cooldowns = {}
event_cooldowns = {}
gift_cooldowns = {}
xp_reaction_timer_task = None
event_timer_task = None
gift_timer_task = None
bot_start_time = None

intents = discord.Intents.default()
intents.reactions = True
intents.message_content = True
intents.guilds = True
intents.members = True
intents.invites = True

bot = commands.Bot(command_prefix="!", intents=intents)

@tasks.loop(minutes=BACKUP_INTERVAL_MINUTES)
async def auto_backup():
    await backup_to_discord()

@auto_backup.before_loop
async def before_auto_backup():
    await bot.wait_until_ready()

async def load_invites(guild):
    try:
        invites = await guild.invites()
        invites_cache[guild.id] = {invite.code: invite.uses for invite in invites}
    except:
        invites_cache[guild.id] = {}

async def check_missing_members():
    all_member_ids = set()
    for guild in bot.guilds:
        all_member_ids.update(member.id for member in guild.members)
    
    members_to_remove = []
    for member_id, inviter_id in inviter_tracker.items():
        if member_id not in all_member_ids:
            members_to_remove.append(member_id)
            
            if inviter_id in xp_data:
                xp_data[inviter_id] = max(0, xp_data.get(inviter_id, 0) - xp_config["xp_invitation"])
                print(f"🔻 Detected offline leave: Member ID {member_id} left. Removed {xp_config['xp_invitation']} XP from inviter (ID: {inviter_id}). New XP: {xp_data[inviter_id]}")
    
    for member_id in members_to_remove:
        del inviter_tracker[member_id]
    
    if members_to_remove:
        save_xp(xp_data)
        save_inviter_tracker(inviter_tracker)
        print(f"✅ Processed {len(members_to_remove)} offline departures")

@bot.event
async def on_ready():
    global bot_start_time, xp_data, message_tracker, inventory_data, boosters_data
    global inviter_tracker, command_settings, daily_cooldowns, xp_reactions
    global xp_config, xp_reaction_channels, xp_reaction_enabled
    global shop_items, events_state, xp_reaction_timer
    
    bot_start_time = datetime.now()
    print(f"✅ Logged in as {bot.user}")
    
    await restore_from_discord()
    
    xp_data = load_xp()
    message_tracker = load_message_tracker()
    inventory_data = load_inventory()
    boosters_data = load_boosters()
    inviter_tracker = load_inviter_tracker()
    command_settings = load_command_settings()
    daily_cooldowns = load_daily_cooldowns()
    xp_reactions = load_xp_reactions()
    xp_config = load_xp_config()
    xp_reaction_channels = load_xp_channels()
    xp_reaction_enabled = load_xp_reaction_enabled()
    shop_items = load_shop_items()
    events_state = load_events_state()
    xp_reaction_timer = load_xp_reaction_timer()
    print("📂 All data reloaded from backup")
    
    await restore_timers()
    
    for guild in bot.guilds:
        await load_invites(guild)
    print(f"📊 Invites loaded for {len(bot.guilds)} server(s)")
    
    await check_missing_members()
    print(f"✅ Checked for members who left while bot was offline")
    
    if not auto_backup.is_running():
        auto_backup.start()
        print(f"🔄 Automatic backup started (every {BACKUP_INTERVAL_MINUTES} minutes)")

@bot.event
async def on_member_join(member):
    if member.bot:
        return
    guild = member.guild
    try:
        new_invites = await guild.invites()
        old_invites = invites_cache.get(guild.id, {})
        for invite in new_invites:
            old_uses = old_invites.get(invite.code, 0)
            if invite.uses > old_uses:
                inviter = invite.inviter
                if inviter and not inviter.bot:
                    xp_data[inviter.id] = xp_data.get(inviter.id, 0) + xp_config["xp_invitation"]
                    save_xp(xp_data)
                    
                    inviter_tracker[member.id] = inviter.id
                    save_inviter_tracker(inviter_tracker)
                    
                    try:
                        notification_channel = bot.get_channel(XP_NOTIFICATION_CHANNEL)
                        if notification_channel and hasattr(notification_channel, 'send'):
                            await notification_channel.send(
                                f"🎉 Welcome {member.mention}! {inviter.mention} received {xp_config['xp_invitation']} XP for inviting!"
                            )
                    except Exception as e:
                        print(f"Error sending invite notification: {e}")
                break
        await load_invites(guild)
    except Exception as e:
        print(f"Invite tracking error: {e}")

@bot.event
async def on_member_remove(member):
    if member.bot:
        return
    
    if member.id in inviter_tracker:
        inviter_id = inviter_tracker[member.id]
        
        if inviter_id in xp_data:
            xp_data[inviter_id] = max(0, xp_data.get(inviter_id, 0) - xp_config["xp_invitation"])
            save_xp(xp_data)
            print(f"🔻 Member {member.name} left. Removed {xp_config['xp_invitation']} XP from inviter (ID: {inviter_id}). New XP: {xp_data[inviter_id]}")
        
        del inviter_tracker[member.id]
        save_inviter_tracker(inviter_tracker)

@bot.event
async def on_member_update(before, after):
    if after.bot:
        return
    
    if before.premium_since is None and after.premium_since is not None:
        user_id = after.id
        
        if user_id in boosters_data:
            print(f"⚠️ {after.name} already received boost XP (skipping)")
            return
        
        boost_xp = xp_config.get("xp_boost", 500)
        xp_data[user_id] = xp_data.get(user_id, 0) + boost_xp
        save_xp(xp_data)
        
        boosters_data[user_id] = after.premium_since.isoformat()
        save_boosters(boosters_data)
        
        print(f"🚀 {after.name} boosted the server! Received {boost_xp} XP. Total: {xp_data[user_id]}")
        
        try:
            boost_channel = bot.get_channel(BOOST_NOTIFICATION_CHANNEL)
            if boost_channel and hasattr(boost_channel, 'send'):
                await boost_channel.send(
                    f"🚀 **{after.mention} just boosted the server!** 🎉\n"
                    f"💎 Received **{boost_xp} XP** as a thank you! Total XP: **{xp_data[user_id]}**"
                )
        except Exception as e:
            print(f"❌ Error sending boost notification: {e}")

@bot.event
async def on_message(message):
    if message.author.bot:
        await bot.process_commands(message)
        return
    
    if message.channel.id in XP_CHANNELS:
        user_id = message.author.id
        current_time = datetime.now()
        
        if user_id not in message_tracker:
            message_tracker[user_id] = {"messages": [], "xp_earned": 0}
        
        user_data = message_tracker[user_id]
        one_hour_ago = current_time - timedelta(hours=1)
        
        user_data["messages"] = [
            msg_time for msg_time in user_data["messages"]
            if datetime.fromisoformat(msg_time) > one_hour_ago
        ]
        
        current_hour_xp = len(user_data["messages"])
        
        if current_hour_xp < xp_config["max_xp_per_hour"]:
            user_data["messages"].append(current_time.isoformat())
            xp_data[user_id] = xp_data.get(user_id, 0) + xp_config["xp_per_message"]
            save_xp(xp_data)
            save_message_tracker(message_tracker)
            
            if current_hour_xp + 1 == xp_config["max_xp_per_hour"]:
                try:
                    notification_channel = bot.get_channel(XP_NOTIFICATION_CHANNEL)
                    if notification_channel and hasattr(notification_channel, 'send'):
                        await notification_channel.send(
                            f"🎉 {message.author.mention} has successfully collected {xp_config['max_xp_per_hour']} XP this hour! Total XP: {xp_data[user_id]}"
                        )
                except Exception as e:
                    print(f"Error sending XP notification: {e}")
    
    await bot.process_commands(message)

@bot.event
async def on_raw_reaction_add(payload):
    if bot.user and payload.user_id == bot.user.id:
        return
    
    guild = bot.get_guild(payload.guild_id)
    if not guild:
        return
    
    member = guild.get_member(payload.user_id)
    if not member:
        return
    
    user = member
    
    emoji_match = False
    if payload.emoji.id:
        emoji_str = f"<:{payload.emoji.name}:{payload.emoji.id}>"
        emoji_match = emoji_str == EMOJI_DON
        print(f"🔍 Custom emoji detected: {emoji_str} | Match: {emoji_match}")
    else:
        emoji_str = str(payload.emoji.name)
        emoji_match = emoji_str == EMOJI_DON
        print(f"🔍 Standard emoji detected: {emoji_str} | Match: {emoji_match}")
    
    print(f"👤 User: {user.name} (ID: {user.id}) | Is chef/XP manager: {is_chef_or_xp_manager(user, member)}")
    
    if is_chef_or_xp_manager(user, member) and emoji_match:
        try:
            channel = bot.get_channel(payload.channel_id)
            if not channel:
                print("❌ Channel not found")
                return
            
            if not xp_reaction_enabled:
                print("❌ XP reactions are currently disabled")
                await channel.send(f"⚠️ XP reactions are currently disabled!")
                return
            
            if xp_reaction_channels and payload.channel_id not in xp_reaction_channels:
                print(f"❌ Channel {payload.channel_id} is not in the XP reaction whitelist")
                await channel.send(f"⚠️ XP reactions are not allowed in this channel!")
                return
            
            message = await channel.fetch_message(payload.message_id)
            target = message.author
            message_id = message.id
            
            print(f"🎯 Target: {target.name} (ID: {target.id}) | Is bot: {target.bot}")
            if target.bot:
                print("❌ Target is a bot, skipping XP reward")
                return
            
            if message_id in xp_reactions:
                print(f"⚠️ Message {message_id} already received XP reward, skipping")
                return
            
            current_time = datetime.now()
            cooldown_hours = xp_config.get("emoji_xp_cooldown_hours", 1)
            
            if target.id in emoji_xp_cooldowns:
                last_reward_time = datetime.fromisoformat(emoji_xp_cooldowns[target.id])
                time_since_last = current_time - last_reward_time
                
                if time_since_last < timedelta(hours=cooldown_hours):
                    remaining_time = timedelta(hours=cooldown_hours) - time_since_last
                    minutes = int(remaining_time.total_seconds() // 60)
                    print(f"⏰ {target.name} is on cooldown. {minutes} minutes remaining")
                    await channel.send(
                        f"⏰ {target.mention} must wait {minutes} more minutes before receiving XP via reaction!"
                    )
                    return
            
            xp_data[target.id] = xp_data.get(target.id, 0) + xp_config["emoji_xp_amount"]
            xp_reactions[message_id] = {
                "target_id": target.id,
                "awarded_by": user.id,
                "timestamp": current_time.isoformat(),
                "amount": xp_config["emoji_xp_amount"]
            }
            emoji_xp_cooldowns[target.id] = current_time.isoformat()
            save_xp(xp_data)
            save_xp_reactions(xp_reactions)
            total_xp = xp_data[target.id]
            print(f"✅ Gave {xp_config['emoji_xp_amount']} XP to {target.name}. New total: {total_xp}")
            
            await message.add_reaction("✅")
            
            await channel.send(
                f"💸 {target.mention} received {xp_config['emoji_xp_amount']} XP from **404ERROR**! Total XP: {total_xp}"
            )
        except Exception as e:
            print(f"❌ Error in on_raw_reaction_add: {e}")

@bot.event
async def on_raw_reaction_remove(payload):
    if bot.user and payload.user_id == bot.user.id:
        return
    
    guild = bot.get_guild(payload.guild_id)
    if not guild:
        return
    
    member = guild.get_member(payload.user_id)
    if not member:
        return
    
    user = member
    
    emoji_match = False
    if payload.emoji.id:
        emoji_str = f"<:{payload.emoji.name}:{payload.emoji.id}>"
        emoji_match = emoji_str == EMOJI_DON
    else:
        emoji_str = str(payload.emoji.name)
        emoji_match = emoji_str == EMOJI_DON
    
    if is_chef_or_xp_manager(user, member) and emoji_match:
        try:
            message_id = payload.message_id
            
            if message_id not in xp_reactions:
                print(f"⚠️ Message {message_id} has no XP reward to remove")
                return
            
            reaction_data = xp_reactions[message_id]
            target_id = reaction_data["target_id"]
            amount = reaction_data["amount"]
            
            xp_data[target_id] = max(0, xp_data.get(target_id, 0) - amount)
            del xp_reactions[message_id]
            save_xp(xp_data)
            save_xp_reactions(xp_reactions)
            
            target = await bot.fetch_user(target_id)
            total_xp = xp_data[target_id]
            print(f"🔻 Removed {amount} XP from {target.name}. New total: {total_xp}")
            
            if target_id in emoji_xp_cooldowns:
                del emoji_xp_cooldowns[target_id]
            
            channel = bot.get_channel(payload.channel_id)
            if channel:
                try:
                    message = await channel.fetch_message(payload.message_id)
                    await message.remove_reaction("✅", bot.user)
                except:
                    pass
                
                await channel.send(
                    f"⚠️ {target.mention} lost {amount} XP (reaction removed by **404ERROR**). Total XP: {total_xp}"
                )
        except Exception as e:
            print(f"❌ Error in on_raw_reaction_remove: {e}")

@bot.command()
async def xp(ctx, member: Optional[discord.Member] = None):
    if not is_command_enabled('xp'):
        await ctx.send("❌ This command is currently disabled!")
        return
    
    author_member = ctx.guild.get_member(ctx.author.id) if ctx.guild else None
    if member:
        if not is_chef_or_xp_manager(ctx.author, author_member):
            await ctx.send("❌ Only chef and XP managers can check others' XP!")
            return
        amount = xp_data.get(member.id, 0)
        await ctx.send(f"💰 {member.mention} has {amount} XP!")
    else:
        amount = xp_data.get(ctx.author.id, 0)
        await ctx.send(f"💰 You have {amount} XP!")

@bot.command()
async def addxp(ctx, member: discord.Member, amount: int):
    if not is_command_enabled('addxp'):
        await ctx.send("❌ This command is currently disabled!")
        return
    
    if ctx.author.id != CHEF_ID:
        await ctx.send("❌ Only the chef can modify XP!")
        return
    if amount == 0:
        await ctx.send("❌ Amount cannot be 0!")
        return
    xp_data[member.id] = xp_data.get(member.id, 0) + amount
    save_xp(xp_data)
    if amount > 0:
        await ctx.send(f"✅ {member.mention} received {amount} XP from 404ERROR!")
    else:
        await ctx.send(f"✅ {member.mention} lost {abs(amount)} XP (removed by 404ERROR)!")

@bot.command()
async def resetxp(ctx):
    if ctx.author.id != CHEF_ID:
        await ctx.send("❌ Only the chef can reset all XP!")
        return
    confirm_msg = await ctx.send(
        "⚠️ **WARNING!** You are about to **RESET ALL XP** for everyone!\n"
        "This action is **IRREVERSIBLE**!\n"
        "React with ✅ to confirm or ❌ to cancel. You have 30 seconds."
    )
    await confirm_msg.add_reaction("✅")
    await confirm_msg.add_reaction("❌")
    def check(reaction, user):
        return user.id == CHEF_ID and str(reaction.emoji) in ["✅", "❌"] and reaction.message.id == confirm_msg.id
    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
        if str(reaction.emoji) == "✅":
            xp_data.clear()
            save_xp(xp_data)
            await ctx.send("🔄 All XP have been reset! Everyone starts from 0.")
        else:
            await ctx.send("❌ Reset cancelled. XP preserved.")
    except Exception:
        await ctx.send("⏱️ Time expired. Reset cancelled.")

@bot.command(aliases=['savebackup', 'save'])
async def backup(ctx):
    if ctx.author.id != CHEF_ID:
        await ctx.send("❌ Only the chef can trigger manual backups!")
        return
    
    await ctx.send("💾 Starting manual backup to Discord...")
    
    try:
        await backup_to_discord()
        await ctx.send("✅ **Manual backup completed!** All data has been saved to Discord.\n🔄 You can safely restart the bot now.")
    except Exception as e:
        await ctx.send(f"❌ Backup failed: {e}\nPlease check the console logs.")
        print(f"❌ Manual backup error: {e}")

@bot.command()
async def shop(ctx):
    if not is_command_enabled('shop'):
        await ctx.send("❌ This command is currently disabled!")
        return
    
    if not shop_items:
        await ctx.send("🛒 **404ERROR's Shop**\n\n⚠️ The shop is empty! The chef can add items with `!addshopitem`")
        return
    
    shop_text = "🛒 **404ERROR's Shop**\n\n"
    for item_id in sorted(shop_items.keys(), key=lambda x: int(x)):
        item = shop_items[item_id]
        shop_text += f"{item_id}️⃣ **{item['name']}** - {item['price']} XP (use !buy {item_id})\n"
    
    await ctx.send(shop_text)

@bot.command()
async def buy(ctx, item: str):
    if not is_command_enabled('buy'):
        await ctx.send("❌ This command is currently disabled!")
        return
    
    user_id = ctx.author.id
    user_xp = xp_data.get(user_id, 0)
    
    if item not in shop_items:
        await ctx.send("❌ Invalid item number! Use `!shop` to see items.")
        return
    
    cost = shop_items[item]["price"]
    name = shop_items[item]["name"]
    
    if user_xp < cost:
        await ctx.send(f"❌ You don't have enough XP to buy **{name}**!")
        return
    
    xp_data[user_id] -= cost
    save_xp(xp_data)
    
    if user_id not in inventory_data:
        inventory_data[user_id] = []
    inventory_data[user_id].append(name)
    save_inventory(inventory_data)
    
    await ctx.send(f"✅ {ctx.author.mention} successfully bought **{name}** for {cost} XP! Remaining XP: {xp_data[user_id]}")

@bot.command()
async def addshopitem(ctx, item_id: str, price: int, *name_parts):
    if ctx.author.id != CHEF_ID:
        await ctx.send("❌ Only the chef can add shop items!")
        return
    
    if price <= 0:
        await ctx.send("❌ Price must be a positive number!")
        return
    
    if not name_parts:
        await ctx.send("❌ Please provide an item name!\n**Usage:** `!addshopitem <item_number> <price> <emoji+name>`\n**Example:** `!addshopitem 3 2000 💀 Death Item`")
        return
    
    item_name = " ".join(name_parts)
    
    global shop_items
    if item_id in shop_items:
        await ctx.send(f"⚠️ Item #{item_id} already exists: **{shop_items[item_id]['name']}** ({shop_items[item_id]['price']} XP)\nThis will overwrite it. React with ✅ to confirm or ❌ to cancel.")
        
        confirm_msg = await ctx.send("Waiting for confirmation...")
        await confirm_msg.add_reaction("✅")
        await confirm_msg.add_reaction("❌")
        
        def check(reaction, user):
            return user.id == CHEF_ID and str(reaction.emoji) in ["✅", "❌"] and reaction.message.id == confirm_msg.id
        
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
            if str(reaction.emoji) != "✅":
                await ctx.send("❌ Cancelled. Item not modified.")
                return
        except:
            await ctx.send("⏱️ Time expired. Cancelled.")
            return
    
    shop_items[item_id] = {"name": item_name, "price": price}
    save_shop_items(shop_items)
    await ctx.send(f"✅ Successfully added item #{item_id}: **{item_name}** for {price} XP!\nUsers can buy it with `!buy {item_id}`")

@bot.command()
async def removeshopitem(ctx, item_id: str):
    if ctx.author.id != CHEF_ID:
        await ctx.send("❌ Only the chef can remove shop items!")
        return
    
    global shop_items
    if item_id not in shop_items:
        await ctx.send(f"❌ Item #{item_id} doesn't exist in the shop! Use `!shop` to see available items.")
        return
    
    item_name = shop_items[item_id]['name']
    item_price = shop_items[item_id]['price']
    
    confirm_msg = await ctx.send(
        f"⚠️ You are about to **REMOVE** item #{item_id}: **{item_name}** ({item_price} XP)\n"
        f"React with ✅ to confirm or ❌ to cancel. You have 30 seconds."
    )
    await confirm_msg.add_reaction("✅")
    await confirm_msg.add_reaction("❌")
    
    def check(reaction, user):
        return user.id == CHEF_ID and str(reaction.emoji) in ["✅", "❌"] and reaction.message.id == confirm_msg.id
    
    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
        if str(reaction.emoji) == "✅":
            del shop_items[item_id]
            save_shop_items(shop_items)
            await ctx.send(f"🗑️ Successfully removed item #{item_id}: **{item_name}** from the shop!")
        else:
            await ctx.send("❌ Cancelled. Item not removed.")
    except:
        await ctx.send("⏱️ Time expired. Cancelled.")

@bot.command()
async def event(ctx, action: str = None):
    global events_state, event_timer_task, event_cooldowns
    
    if action and ctx.author.id != CHEF_ID:
        await ctx.send("❌ Only the chef can activate/deactivate events!")
        return
    
    if action is None:
        if not events_state["event"]["enabled"]:
            await ctx.send("❌ The event is not currently active!")
            return
        
        user_id = ctx.author.id
        if user_id in event_cooldowns:
            last_claim = datetime.fromisoformat(event_cooldowns[user_id])
            cooldown_hours = events_state["event"]["cooldown_hours"]
            time_since = datetime.now() - last_claim
            if time_since < timedelta(hours=cooldown_hours):
                remaining = timedelta(hours=cooldown_hours) - time_since
                hours = int(remaining.total_seconds() // 3600)
                minutes = int((remaining.total_seconds() % 3600) // 60)
                await ctx.send(f"⏰ You already claimed the event! Wait {hours}h {minutes}m before claiming again.")
                return
        
        xp_reward = events_state["event"]["xp_reward"]
        xp_data[user_id] = xp_data.get(user_id, 0) + xp_reward
        save_xp(xp_data)
        event_cooldowns[user_id] = datetime.now().isoformat()
        
        await ctx.send(f"🎉 {ctx.author.mention} claimed the event and received {xp_reward} XP! Total XP: {xp_data[user_id]}")
        return
    
    if action.lower() == 'enable':
        events_state["event"]["enabled"] = True
        events_state["event"]["expires_at"] = None
        if event_timer_task and not event_timer_task.done():
            event_timer_task.cancel()
        save_events_state(events_state)
        await ctx.send(f"✅ Event **enabled** permanently! Users can claim {events_state['event']['xp_reward']} XP with `!event`")
    elif action.lower() == 'disable':
        events_state["event"]["enabled"] = False
        events_state["event"]["expires_at"] = None
        if event_timer_task and not event_timer_task.done():
            event_timer_task.cancel()
        save_events_state(events_state)
        await ctx.send("❌ Event **disabled**!")
    else:
        try:
            minutes = int(action)
            if minutes <= 0:
                await ctx.send("❌ Minutes must be a positive number!")
                return
            events_state["event"]["enabled"] = True
            expires_at = datetime.now() + timedelta(minutes=minutes)
            events_state["event"]["expires_at"] = expires_at.isoformat()
            save_events_state(events_state)
            event_timer_task = asyncio.create_task(schedule_event_disable("event", minutes))
            await ctx.send(f"✅ Event **enabled for {minutes} minutes**! Users can claim {events_state['event']['xp_reward']} XP with `!event`. Auto-disables at {expires_at.strftime('%H:%M:%S')}.")
        except ValueError:
            await ctx.send("❌ Invalid action! Use `enable`, `disable`, or a number of minutes (e.g., `!event 5`).")

@bot.command()
async def gift(ctx, action: str = None):
    global events_state, gift_timer_task, gift_cooldowns
    
    if action and ctx.author.id != CHEF_ID:
        await ctx.send("❌ Only the chef can activate/deactivate gifts!")
        return
    
    if action is None:
        if not events_state["gift"]["enabled"]:
            await ctx.send("❌ Gifts are not currently available!")
            return
        
        user_id = ctx.author.id
        if user_id in gift_cooldowns:
            last_claim = datetime.fromisoformat(gift_cooldowns[user_id])
            cooldown_hours = events_state["gift"]["cooldown_hours"]
            time_since = datetime.now() - last_claim
            if time_since < timedelta(hours=cooldown_hours):
                remaining = timedelta(hours=cooldown_hours) - time_since
                hours = int(remaining.total_seconds() // 3600)
                minutes = int((remaining.total_seconds() % 3600) // 60)
                await ctx.send(f"⏰ You already claimed a gift! Wait {hours}h {minutes}m before claiming again.")
                return
        
        xp_reward = events_state["gift"]["xp_reward"]
        xp_data[user_id] = xp_data.get(user_id, 0) + xp_reward
        save_xp(xp_data)
        gift_cooldowns[user_id] = datetime.now().isoformat()
        
        await ctx.send(f"🎁 {ctx.author.mention} claimed a gift and received {xp_reward} XP! Total XP: {xp_data[user_id]}")
        return
    
    if action.lower() == 'enable':
        events_state["gift"]["enabled"] = True
        events_state["gift"]["expires_at"] = None
        if gift_timer_task and not gift_timer_task.done():
            gift_timer_task.cancel()
        save_events_state(events_state)
        await ctx.send(f"✅ Gifts **enabled** permanently! Users can claim {events_state['gift']['xp_reward']} XP with `!gift`")
    elif action.lower() == 'disable':
        events_state["gift"]["enabled"] = False
        events_state["gift"]["expires_at"] = None
        if gift_timer_task and not gift_timer_task.done():
            gift_timer_task.cancel()
        save_events_state(events_state)
        await ctx.send("❌ Gifts **disabled**!")
    else:
        try:
            minutes = int(action)
            if minutes <= 0:
                await ctx.send("❌ Minutes must be a positive number!")
                return
            events_state["gift"]["enabled"] = True
            expires_at = datetime.now() + timedelta(minutes=minutes)
            events_state["gift"]["expires_at"] = expires_at.isoformat()
            save_events_state(events_state)
            gift_timer_task = asyncio.create_task(schedule_event_disable("gift", minutes))
            await ctx.send(f"✅ Gifts **enabled for {minutes} minutes**! Users can claim {events_state['gift']['xp_reward']} XP with `!gift`. Auto-disables at {expires_at.strftime('%H:%M:%S')}.")
        except ValueError:
            await ctx.send("❌ Invalid action! Use `enable`, `disable`, or a number of minutes (e.g., `!gift 5`).")

@bot.command()
async def topxp(ctx):
    if not is_command_enabled('topxp'):
        await ctx.send("❌ This command is currently disabled!")
        return
    
    if not xp_data:
        await ctx.send("❌ No one has XP yet!")
        return
    sorted_users = sorted(xp_data.items(), key=lambda x: x[1], reverse=True)[:10]
    message = "🏆 **XP Leaderboard** 🏆\n\n"
    for i, (user_id, xp) in enumerate(sorted_users, 1):
        try:
            user = await bot.fetch_user(user_id)
            message += f"{i}. {user.name}: {xp} XP\n"
        except:
            message += f"{i}. Unknown User: {xp} XP\n"
    await ctx.send(message)

@bot.command()
async def top(ctx, limit: int = 10):
    if ctx.author.id != CHEF_ID:
        await ctx.send("❌ Only the chef can use custom top rankings!")
        return
    
    if not is_command_enabled('topxp'):
        await ctx.send("❌ This command is currently disabled!")
        return
    
    if not xp_data:
        await ctx.send("❌ No one has XP yet!")
        return
    
    if limit <= 0:
        await ctx.send("❌ Limit must be a positive number!")
        return
    
    if limit > 100:
        await ctx.send("❌ Maximum limit is 100 users!")
        return
    
    sorted_users = sorted(xp_data.items(), key=lambda x: x[1], reverse=True)[:limit]
    message = f"🏆 **Top {limit} XP Leaderboard** 🏆\n\n"
    
    for i, (user_id, xp) in enumerate(sorted_users, 1):
        try:
            user = await bot.fetch_user(user_id)
            message += f"{i}. {user.name}: {xp} XP\n"
        except:
            message += f"{i}. Unknown User: {xp} XP\n"
    
    await ctx.send(message)

@bot.command()
async def inventory(ctx, member: Optional[discord.Member] = None):
    if not is_command_enabled('inventory'):
        await ctx.send("❌ This command is currently disabled!")
        return
    
    target = member if member else ctx.author
    user_id = target.id
    
    if member:
        author_member = ctx.guild.get_member(ctx.author.id) if ctx.guild else None
        if not is_chef_or_admin(ctx.author, author_member):
            await ctx.send("❌ Only chef and admins can check others' inventory!")
            return
    
    items = inventory_data.get(user_id, [])
    if not items:
        await ctx.send(f"🎒 {target.mention}'s inventory is empty!")
        return
    
    from collections import Counter
    item_counts = Counter(items)
    
    message = f"🎒 **{target.display_name}'s Inventory:**\n\n"
    for item, count in item_counts.items():
        message += f"• {item} x{count}\n"
    
    await ctx.send(message)

@bot.command(aliases=['inventoryreset'])
async def resetinventory(ctx, member: discord.Member):
    if ctx.author.id != CHEF_ID:
        await ctx.send("❌ Only the chef can reset inventories!")
        return
    
    user_id = member.id
    if user_id in inventory_data:
        inventory_data[user_id] = []
        save_inventory(inventory_data)
        await ctx.send(f"✅ {member.mention}'s inventory has been reset!")
    else:
        await ctx.send(f"❌ {member.mention} has no inventory to reset!")

@bot.command()
async def additem(ctx, member: discord.Member, *, item_name: str):
    if not is_command_enabled('additem'):
        await ctx.send("❌ This command is currently disabled!")
        return
    
    if ctx.author.id != CHEF_ID:
        await ctx.send("❌ Only the chef can add items!")
        return
    
    user_id = member.id
    if user_id not in inventory_data:
        inventory_data[user_id] = []
    
    inventory_data[user_id].append(item_name)
    save_inventory(inventory_data)
    await ctx.send(f"✅ Added **{item_name}** to {member.mention}'s inventory!")

@bot.command()
async def removeitem(ctx, member: discord.Member, *, item_name: str):
    if not is_command_enabled('removeitem'):
        await ctx.send("❌ This command is currently disabled!")
        return
    
    if ctx.author.id != CHEF_ID:
        await ctx.send("❌ Only the chef can remove items!")
        return
    
    user_id = member.id
    if user_id not in inventory_data or not inventory_data[user_id]:
        await ctx.send(f"❌ {member.mention} has no items in inventory!")
        return
    
    if item_name in inventory_data[user_id]:
        inventory_data[user_id].remove(item_name)
        save_inventory(inventory_data)
        await ctx.send(f"✅ Removed **{item_name}** from {member.mention}'s inventory!")
    else:
        await ctx.send(f"❌ {member.mention} doesn't have **{item_name}** in their inventory!")

@bot.command()
async def daily(ctx):
    if not is_command_enabled('daily'):
        await ctx.send("❌ This command is currently disabled!")
        return
    
    user_id = ctx.author.id
    current_time = datetime.now()
    
    if user_id in daily_cooldowns:
        last_claim = datetime.fromisoformat(daily_cooldowns[user_id])
        time_diff = current_time - last_claim
        
        if time_diff < timedelta(hours=24):
            remaining_time = timedelta(hours=24) - time_diff
            hours = int(remaining_time.total_seconds() // 3600)
            minutes = int((remaining_time.total_seconds() % 3600) // 60)
            await ctx.send(f"⏰ You already claimed your daily XP! Come back in {hours}h {minutes}m")
            return
    
    xp_data[user_id] = xp_data.get(user_id, 0) + xp_config["daily_xp_reward"]
    daily_cooldowns[user_id] = current_time.isoformat()
    save_xp(xp_data)
    save_daily_cooldowns(daily_cooldowns)
    
    await ctx.send(f"🎁 {ctx.author.mention} claimed their daily reward! +{xp_config['daily_xp_reward']} XP! Total XP: {xp_data[user_id]}")

@bot.command(aliases=['configxp'])
async def setxp(ctx, setting: str = None, value: int = None):
    global events_state
    if ctx.author.id != CHEF_ID:
        await ctx.send("❌ Only the chef can modify XP settings!")
        return
    
    if setting is None or value is None:
        settings_info = (
            "⚙️ **XP Configuration Settings:**\n\n"
            f"📝 `xp_per_message`: {xp_config['xp_per_message']} XP per message\n"
            f"⏰ `max_xp_per_hour`: {xp_config['max_xp_per_hour']} XP max per hour\n"
            f"🎁 `daily_xp_reward`: {xp_config['daily_xp_reward']} XP for daily reward\n"
            f"💎 `emoji_xp_amount`: {xp_config['emoji_xp_amount']} XP per emoji reaction\n"
            f"⏱️ `emoji_xp_cooldown_hours`: {xp_config.get('emoji_xp_cooldown_hours', 1)} hours cooldown for emoji XP\n"
            f"🎉 `xp_invitation`: {xp_config['xp_invitation']} XP per invitation\n"
            f"🚀 `xp_boost`: {xp_config['xp_boost']} XP boost value\n"
            f"🎊 `event_xp_reward`: {events_state['event']['xp_reward']} XP for !event command\n"
            f"🎁 `gift_xp_reward`: {events_state['gift']['xp_reward']} XP for !gift command\n\n"
            "📌 **Usage:** `!setxp <setting> <value>`\n"
            "📌 **Example:** `!setxp emoji_xp_amount 100`\n"
            "📌 **Example:** `!setxp gift_xp_reward 75`"
        )
        await ctx.send(settings_info)
        return
    
    valid_settings = ['xp_per_message', 'max_xp_per_hour', 'daily_xp_reward', 'emoji_xp_amount', 'xp_invitation', 'xp_boost', 'emoji_xp_cooldown_hours', 'event_xp_reward', 'gift_xp_reward']
    
    if setting not in valid_settings:
        await ctx.send(f"❌ Invalid setting! Valid settings: {', '.join(valid_settings)}")
        return
    
    if value < 0:
        await ctx.send("❌ Value cannot be negative!")
        return
    
    if setting == 'event_xp_reward':
        old_value = events_state['event']['xp_reward']
        events_state['event']['xp_reward'] = value
        save_events_state(events_state)
        await ctx.send(f"✅ Updated `{setting}` from {old_value} to {value}! Users will now receive {value} XP with !event")
    elif setting == 'gift_xp_reward':
        old_value = events_state['gift']['xp_reward']
        events_state['gift']['xp_reward'] = value
        save_events_state(events_state)
        await ctx.send(f"✅ Updated `{setting}` from {old_value} to {value}! Users will now receive {value} XP with !gift")
    else:
        old_value = xp_config[setting]
        xp_config[setting] = value
        save_xp_config(xp_config)
        await ctx.send(f"✅ Updated `{setting}` from {old_value} to {value}!")

@bot.command(aliases=['setxpch'])
async def setxpchannels(ctx, *channels: discord.TextChannel):
    if ctx.author.id != CHEF_ID:
        await ctx.send("❌ Only the chef can configure XP reaction channels!")
        return
    
    if not channels:
        await ctx.send("❌ Please mention at least one channel!\n**Usage:** `!setxpchannels #channel1 #channel2 #channel3`")
        return
    
    global xp_reaction_channels
    xp_reaction_channels = [ch.id for ch in channels]
    save_xp_channels(xp_reaction_channels)
    
    channels_list = ", ".join([ch.mention for ch in channels])
    await ctx.send(f"✅ XP reaction channels configured! Reactions will only work in:\n{channels_list}")

@bot.command(aliases=['xpch'])
async def xpchannels(ctx):
    if not xp_reaction_channels:
        await ctx.send("⚠️ No XP reaction channels configured. XP reactions work in all channels!\n**Configure with:** `!setxpchannels #channel1 #channel2`")
        return
    
    channels_text = ""
    for ch_id in xp_reaction_channels:
        channel = bot.get_channel(ch_id)
        if channel:
            channels_text += f"• {channel.mention}\n"
        else:
            channels_text += f"• Unknown Channel (ID: {ch_id})\n"
    
    await ctx.send(f"📋 **XP Reaction Channels:**\n\n{channels_text}\n💡 Only Chef and XP Managers can give XP by reacting in these channels.")

@bot.command(aliases=['xpreact'])
async def xpreaction(ctx, action: str = None):
    global xp_reaction_enabled, xp_reaction_timer, xp_reaction_timer_task
    
    if ctx.author.id != CHEF_ID:
        await ctx.send("❌ Only the chef can configure XP reaction settings!")
        return
    
    if action is None:
        status = "✅ Enabled" if xp_reaction_enabled else "❌ Disabled"
        timer_info = ""
        if xp_reaction_timer.get("expires_at"):
            expires = datetime.fromisoformat(xp_reaction_timer["expires_at"])
            now = datetime.now()
            if now < expires:
                remaining = (expires - now).total_seconds() / 60
                timer_info = f"\n⏰ Auto-disable in: {remaining:.1f} minutes"
        await ctx.send(f"⚙️ **XP Reaction Status:** {status}{timer_info}\n\n💡 **Usage:**\n• `!xpreaction enable` - Enable XP reactions permanently\n• `!xpreaction disable` - Disable XP reactions\n• `!xpreaction <minutes>` - Enable for X minutes (e.g., `!xpreaction 15`)")
        return
    
    if action.lower() == 'enable':
        xp_reaction_enabled = True
        xp_reaction_timer["enabled"] = True
        xp_reaction_timer["expires_at"] = None
        if xp_reaction_timer_task and not xp_reaction_timer_task.done():
            xp_reaction_timer_task.cancel()
        save_xp_reaction_enabled(xp_reaction_enabled)
        save_xp_reaction_timer(xp_reaction_timer)
        await ctx.send("✅ XP reactions have been **enabled** permanently! Chef and XP Managers can now give XP via reactions.")
    elif action.lower() == 'disable':
        xp_reaction_enabled = False
        xp_reaction_timer["enabled"] = False
        xp_reaction_timer["expires_at"] = None
        if xp_reaction_timer_task and not xp_reaction_timer_task.done():
            xp_reaction_timer_task.cancel()
        save_xp_reaction_enabled(xp_reaction_enabled)
        save_xp_reaction_timer(xp_reaction_timer)
        await ctx.send("❌ XP reactions have been **disabled**! No one can give XP via reactions until re-enabled.")
    else:
        try:
            minutes = int(action)
            if minutes <= 0:
                await ctx.send("❌ Minutes must be a positive number!")
                return
            xp_reaction_enabled = True
            expires_at = datetime.now() + timedelta(minutes=minutes)
            xp_reaction_timer["enabled"] = True
            xp_reaction_timer["expires_at"] = expires_at.isoformat()
            save_xp_reaction_enabled(True)
            save_xp_reaction_timer(xp_reaction_timer)
            xp_reaction_timer_task = asyncio.create_task(schedule_xp_reaction_disable(minutes))
            await ctx.send(f"✅ XP reactions have been **enabled for {minutes} minutes**! They will auto-disable at {expires_at.strftime('%H:%M:%S')}.")
        except ValueError:
            await ctx.send("❌ Invalid action! Use `enable`, `disable`, or a number of minutes (e.g., `!xpreaction 15`).")

@bot.command()
async def enable(ctx, command_name: str):
    if ctx.author.id != CHEF_ID:
        await ctx.send("❌ Only the chef can enable/disable commands!")
        return
    
    toggleable_commands = ['xp', 'addxp', 'shop', 'buy', 'inventory', 'topxp', 'daily', 'additem', 'removeitem']
    
    if command_name not in toggleable_commands:
        await ctx.send(f"❌ Cannot toggle command `{command_name}`. Available commands: {', '.join(toggleable_commands)}")
        return
    
    command_settings[command_name] = True
    save_command_settings(command_settings)
    await ctx.send(f"✅ Command `!{command_name}` has been enabled!")

@bot.command()
async def disable(ctx, command_name: str):
    if ctx.author.id != CHEF_ID:
        await ctx.send("❌ Only the chef can enable/disable commands!")
        return
    
    toggleable_commands = ['xp', 'addxp', 'shop', 'buy', 'inventory', 'topxp', 'daily', 'additem', 'removeitem']
    
    if command_name == 'enable' or command_name == 'disable':
        await ctx.send("❌ Cannot disable the enable/disable commands!")
        return
    
    if command_name not in toggleable_commands:
        await ctx.send(f"❌ Cannot toggle command `{command_name}`. Available commands: {', '.join(toggleable_commands)}")
        return
    
    command_settings[command_name] = False
    save_command_settings(command_settings)
    await ctx.send(f"✅ Command `!{command_name}` has been disabled!")

@bot.command(name='commands', aliases=['commandlist'])
async def commands_list(ctx):
    toggleable_commands = ['xp', 'addxp', 'shop', 'buy', 'inventory', 'topxp', 'daily', 'additem', 'removeitem']
    
    message = "📋 **Command Status:**\n\n"
    for cmd in toggleable_commands:
        status = "✅ Enabled" if is_command_enabled(cmd) else "❌ Disabled"
        message += f"`!{cmd}` - {status}\n"
    
    message += "\n💡 **Always Available:**\n"
    message += "`!enable` - Enable a command (chef only)\n"
    message += "`!disable` - Disable a command (chef only)\n"
    message += "`!commands` - Show this list\n"
    message += "`!commandsinfos` - Complete command guide\n"
    message += "`!setxp` - Configure XP values (chef only)\n"
    message += "`!setxpchannels` - Configure XP reaction channels (chef only)\n"
    message += "`!xpchannels` - View XP reaction channels\n"
    message += "`!xpreaction` - Enable/disable XP reactions (chef only)\n"
    message += "`!event` - Claim/manage events (chef for management)\n"
    message += "`!gift` - Claim/manage gifts (chef for management)\n"
    message += "`!top` - Custom leaderboard (chef only)\n"
    message += "`!backup` - Manual backup to Discord (chef only)\n"
    message += "`!resetxp` - Reset all XP (chef only)\n"
    message += "`!resetinventory` - Reset inventory (chef only)\n"
    message += "`!addshopitem` - Add shop item (chef only)\n"
    message += "`!removeshopitem` - Remove shop item (chef only)\n"
    message += "`!alivexp` - Show bot uptime\n"
    
    await ctx.send(message)

@bot.command(aliases=['commandsinfo', 'cmdinfo'])
async def commandsinfos(ctx):
    msg1 = """📚 **COMPLETE COMMAND GUIDE** 📚

**🎯 XP COMMANDS:**
• `!xp` - Check your XP balance (Everyone)
  Example: `!xp` or `!xp @user` (chef/XP managers only)

• `!addxp @user <amount>` - Add/remove XP (Chef only)
  Example: `!addxp @John 50` → Gives 50 XP

• `!topxp` - View XP leaderboard (Everyone)
  Example: `!topxp` → Top 10 users by XP

• `!top <number>` - Custom leaderboard size (Chef only)
  Example: `!top 25` → Top 25 users by XP

• `!daily` - Claim daily XP reward (Everyone, 24h cooldown)
  Example: `!daily` → Get your daily XP"""

    msg2 = """**🛒 SHOP & INVENTORY:**
• `!shop` - Browse 404ERROR's Shop (Everyone)
  Example: `!shop` → View available items

• `!buy <number>` - Purchase item (Everyone)
  Example: `!buy 1` → Buy Discord add (500 XP)

• `!addshopitem <id> <price> <name>` - Add item to shop (Chef only)
  Example: `!addshopitem 3 2000 💀 Death Item`

• `!inventory` - View inventory (Everyone)
  Example: `!inventory` or `!inventory @user` (chef/admin)

• `!additem @user <item>` - Give item (Chef only)
  Example: `!additem @John Discord add`

• `!removeitem @user <item>` - Remove item (Chef only)
  Example: `!removeitem @John Brawl Stars add`"""

    msg3 = """**⚙️ CONFIGURATION (Chef Only):**
• `!setxp <setting> <value>` - Configure XP values
  Settings: xp_per_message, max_xp_per_hour, daily_xp_reward, emoji_xp_amount, emoji_xp_cooldown_hours, xp_invitation, xp_boost, event_xp_reward, gift_xp_reward
  Example: `!setxp emoji_xp_amount 100`
  Example: `!setxp gift_xp_reward 75`

• `!setxpchannels #ch1 #ch2` - Set XP reaction channels
  Example: `!setxpchannels #general`

• `!xpchannels` - View XP reaction channels (Everyone)

• `!xpreaction <action>` or `!xpreact` - Manage XP reactions (Chef only)
  `!xpreaction enable` → Enable permanently
  `!xpreaction disable` → Disable
  `!xpreaction 15` → Enable for 15 minutes

• `!enable <cmd>` - Enable command
  Example: `!enable shop`

• `!disable <cmd>` - Disable command
  Example: `!disable daily`"""

    msg4 = """**🎉 EVENTS & GIFTS:**
• `!event` - Claim event reward (Everyone when active)
  Example: `!event` → Get XP (24h cooldown, configurable with !setxp event_xp_reward)

• `!event <action>` - Manage events (Chef only)
  `!event enable` → Enable permanently
  `!event disable` → Disable
  `!event 5` → Enable for 5 minutes

• `!gift` - Claim gift reward (Everyone when active)
  Example: `!gift` → Get XP (12h cooldown, configurable with !setxp gift_xp_reward)

• `!gift <action>` - Manage gifts (Chef only)
  `!gift enable` → Enable permanently
  `!gift disable` → Disable
  `!gift 10` → Enable for 10 minutes"""

    msg5 = """**🔄 RESET & BACKUP (Chef Only):**
• `!resetxp` - Reset ALL XP (requires ✅ confirmation)
• `!resetinventory @user` - Clear inventory
  Example: `!resetinventory @John`
• `!backup` - Manual backup to Discord
  Example: `!backup` → Saves all data files

**📊 INFO COMMANDS:**
• `!commands` - View command status (Everyone)
• `!commandsinfos` - This help guide (Everyone)
• `!alivexp` - Check bot uptime (Everyone)

**💎 SPECIAL FEATURES:**
✨ Earn XP by sending messages in configured channels
✨ Get XP when someone joins via your invite
✨ Chef/XP Managers give XP by reacting with XP emoji
✨ **Get XP when you boost the Discord server** (configurable with !setxp xp_boost)
✨ Dynamic shop system with custom items
✨ Temporary activation system for XP reactions & events
✨ Automatic Discord backup every 15 minutes"""

    await ctx.send(msg1)
    await ctx.send(msg2)
    await ctx.send(msg3)
    await ctx.send(msg4)
    await ctx.send(msg5)

@bot.command()
async def alivexp(ctx):
    if bot_start_time is None:
        await ctx.send("⏰ Bot uptime information is not available yet.")
        return
    
    uptime = datetime.now() - bot_start_time
    days = uptime.days
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    uptime_message = f"🤖 **Bot Uptime:**\n"
    if days > 0:
        uptime_message += f"📅 {days} day{'s' if days > 1 else ''}, "
    uptime_message += f"⏰ {hours}h {minutes}m {seconds}s\n"
    uptime_message += f"🚀 Started at: {bot_start_time.strftime('%Y-%m-%d %H:%M:%S')}"
    
    await ctx.send(uptime_message)

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

@app.route('/health')
def health():
    return {"status": "ok", "bot": str(bot.user) if bot.user else "Not connected"}

def run():
    app.run(host='0.0.0.0', port=5000)

def keep_alive():
    t = Thread(target=run)
    t.start()

if __name__ == "__main__":
    keep_alive()
    token = os.environ.get("TOKEN")
    if not token:
        print("❌ Error: Missing TOKEN environment variable!")
        exit(1)
    bot.run(token)
