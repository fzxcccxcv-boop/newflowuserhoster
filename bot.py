#!/usr/bin/env python3
# ════════════════════════════════════════════════════════════════════
#   SID PREMIUM HOSTER + USERBOT CORE V3 — ADVANCED MERGED EDITION
#   By SIDxBOT — All rights reserved
# ════════════════════════════════════════════════════════════════════
#
#  HOW TO RUN:
#    Hoster bot  →  python sid_bot.py
#    Userbot     →  python sid_bot.py --userbot    (called by hoster)
#
#  REQUIRED ENV VARS (hoster mode):
#    BOT_TOKEN, OWNER_ID, TELEGRAM_API_ID, TELEGRAM_API_HASH
#    SUPPORT_USERNAME  (e.g. @YourUsername)
#    MAX_USERBOTS      (optional, default 50)
#
#  The hoster spawns userbot subprocesses of this same file automatically.
#  No manual --userbot flag needed — just set env vars and run.
# ════════════════════════════════════════════════════════════════════

import sys as _sys
import os as _os

_IS_USERBOT = "--userbot" in _sys.argv or _os.environ.get("USERBOT_MODE") == "1"

if _IS_USERBOT:
    # BY SIDxBOT — ADVANCED V3 (500+ COMMANDS)
    # Modified for SID Premium Hoster — reads credentials from ENV

    # ────────────────────────────────────────────────
    #                 STANDARD LIB
    # ────────────────────────────────────────────────
    import asyncio
    import os
    import time
    import json
    import random
    import logging
    import traceback
    import re
    import hashlib
    import base64
    import uuid
    import string
    import math
    from typing import Dict, Set, Optional
    from io import BytesIO
    from datetime import datetime

    # ────────────────────────────────────────────────
    #                 THIRD PARTY
    # ────────────────────────────────────────────────
    import requests
    import qrcode
    from gtts import gTTS
    import yt_dlp

    # ────────────────────────────────────────────────
    #                 TELETHON
    # ────────────────────────────────────────────────
    from telethon import TelegramClient, events, functions, types
    from telethon.sessions import StringSession
    from telethon.errors import FloodWaitError, RPCError
    from telethon.tl.types import ChannelParticipantsAdmins

    # ────────────────────────────────────────────────
    #                 BASIC PATH SETUP
    # ────────────────────────────────────────────────
    BASE_DIR = os.getcwd()
    DOWNLOAD_PATH = os.path.join(BASE_DIR, "downloads")
    os.makedirs(DOWNLOAD_PATH, exist_ok=True)
    TEMP_PATH = os.path.join(BASE_DIR, "temp")
    os.makedirs(TEMP_PATH, exist_ok=True)

    # ────────────────────────────────────────────────
    #        USERBOT CONFIG — read from environment
    # ────────────────────────────────────────────────
    _api_id_raw = os.environ.get("API_ID", "")
    _api_hash_raw = os.environ.get("API_HASH", "")
    _session_str = os.environ.get("SESSION_STRING", "")

    if not _api_id_raw or not _api_hash_raw or not _session_str:
        raise RuntimeError(
            "Missing required env vars: API_ID, API_HASH, SESSION_STRING"
        )

    API_ID = int(_api_id_raw)
    API_HASH = _api_hash_raw
    OWNER_ID: int = 0

    # ── SELF PROTECTION ──────────────────────────────────────────────────
    _protected_raw = os.environ.get("USERBOT_OWNER_ID", "")
    PROTECTED_IDS: Set[int] = set()
    for _pid in _protected_raw.replace(",", " ").split():
        try: PROTECTED_IDS.add(int(_pid))
        except: pass
    for _pid in os.environ.get("EXTRA_PROTECTED", "").replace(",", " ").split():
        try: PROTECTED_IDS.add(int(_pid))
        except: pass

    bot = TelegramClient(
        StringSession(_session_str), API_ID, API_HASH,
        auto_reconnect=True, connection_retries=10, retry_delay=3
    )

    # ────────────────────────────────────────────────
    #                 STORAGE FILES
    # ────────────────────────────────────────────────
    ADMINS_FILE = "admins.json"
    NOTES_FILE = "notes.json"
    BANNER_FILE = "banner_msg_id.txt"
    SPAM_TEXTS_FILE = "spam_texts.json"
    WARNS_FILE = "warns.json"

    # ────────────────────────────────────────────────
    #                 CLONE ENGINE STATE
    # ────────────────────────────────────────────────
    CLONE_ACTIVE: bool = False
    LAST_CLONE_ID: Optional[int] = None
    CLONE_DATA: Dict[str, Optional[object]] = {
        "name": None, "username": None, "bio": None, "photo_bytes": None,
    }

    # ────────────────────────────────────────────────
    #                 RUNTIME STATE
    # ────────────────────────────────────────────────
    admins: Set[int] = set()
    notes: Dict[int, str] = {}
    warns: Dict[int, int] = {}

    menu_banner_msg: Optional[tuple] = None
    auto_react_emoji: Optional[str] = None

    muted_users: Set[int] = set()
    global_muted: Set[int] = set()

    reply_users: Set[int] = set()
    rr_users: Set[int] = set()
    flag_users: Set[int] = set()
    hrr_users: Set[int] = set()
    replygod_users: Set[int] = set()
    replysid_users: Dict[int, Dict[str, object]] = {}
    rspam_users: Dict[int, Dict[str, object]] = {}

    # ─── NEW RAID STATE ───
    attack_users: Set[int] = set()
    roast_users: Set[int] = set()
    diss_users: Set[int] = set()
    war_users: Set[int] = set()
    savage_users: Set[int] = set()
    ultra_users: Set[int] = set()
    godwar_users: Set[int] = set()
    combo_users: Set[int] = set()
    troll_users: Set[int] = set()
    shame_users: Set[int] = set()
    fire_users: Set[int] = set()
    devil_users: Set[int] = set()
    karma_users: Set[int] = set()
    ghost_users: Set[int] = set()
    legend_users: Set[int] = set()
    doom_users: Set[int] = set()
    nuke_users: Set[int] = set()
    storm_users: Set[int] = set()
    blizzard_users: Set[int] = set()
    venom_users: Set[int] = set()

    spray_tasks: Dict[int, asyncio.Task] = {}
    spam_texts: list = []
    watch_spam: Dict[tuple, Dict] = {}

    antidel_enabled: bool = False
    antidel_cache: Dict[int, Dict] = {}

    group_locks: Set[int] = set()
    START_TIME = time.time()
    SPRAY_DELAY = 0.1

    # ────────────────────────────────────────────────
    #                 BOT ADD ENGINE
    # ────────────────────────────────────────────────
    ADD_BOTS_LIST = [ "",]

    # ────────────────────────────────────────────────
    #                 FASTGC ENGINE STATE
    # ────────────────────────────────────────────────
    FASTGC_STATE: Dict[str, Optional[object]] = {
        "active": False, "template": None, "task": None, "chat_id": None,
    }
    GC_FAST_INTERVAL = 1
    GC_FAST_EMOJIS = [
        "❤️","🧡","💛","💚","💙","💜","🖤","🤍","🤎","🩷","🩵","🩶",
        "💖","💘","💝","💗","💓","💞","💕","💟","❣️","❤️‍🔥","❤️‍🩹"
    ]

    # ────────────────────────────────────────────────
    #                   HELPERS
    # ────────────────────────────────────────────────
    def load_admins():
        global admins
        try:
            if not os.path.isfile(ADMINS_FILE):
                admins = set(); return
            with open(ADMINS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            clean = set()
            if isinstance(data, list):
                for x in data:
                    try: clean.add(int(x))
                    except: continue
            admins = clean
        except Exception as e:
            print(f"[LOAD ADMINS ERROR] {str(e)[:80]}")
            admins = set()

    def save_admins():
        try:
            tmp = sorted(set(int(x) for x in admins))
            with open(ADMINS_FILE, "w", encoding="utf-8") as f:
                json.dump(tmp, f, indent=2)
        except Exception as e:
            print(f"[SAVE ADMINS ERROR] {str(e)[:80]}")

    def is_admin(uid: int) -> bool:
        if not uid: return False
        return uid == OWNER_ID or uid in admins

    async def safe_edit(event, text: str):
        if not text: return
        try: return await event.edit(text)
        except Exception:
            try:
                msg = await event.reply(text)
            except: return
            try:
                if event.out: await event.delete()
            except: pass
            return msg

    def load_notes():
        global notes
        try:
            if not os.path.isfile(NOTES_FILE):
                notes = {}; return
            with open(NOTES_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
            clean = {}
            if isinstance(raw, dict):
                for k, v in raw.items():
                    try: clean[int(k)] = str(v)
                    except: continue
            notes = clean
        except Exception as e:
            print(f"[LOAD NOTES ERROR] {str(e)[:80]}")
            notes = {}

    def save_notes():
        try:
            with open(NOTES_FILE, "w", encoding="utf-8") as f:
                json.dump(notes, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[SAVE NOTES ERROR] {str(e)[:80]}")

    def load_banner():
        global menu_banner_msg
        try:
            if not os.path.isfile(BANNER_FILE):
                menu_banner_msg = None; return
            with open(BANNER_FILE, "r", encoding="utf-8") as f:
                raw = f.read().strip()
            if ":" not in raw:
                menu_banner_msg = None; return
            chat, msg = raw.split(":", 1)
            menu_banner_msg = (int(chat), int(msg))
        except Exception as e:
            print(f"[LOAD BANNER ERROR] {str(e)[:80]}")
            menu_banner_msg = None

    def save_banner():
        try:
            if not menu_banner_msg:
                if os.path.isfile(BANNER_FILE): os.remove(BANNER_FILE)
                return
            with open(BANNER_FILE, "w", encoding="utf-8") as f:
                f.write(f"{menu_banner_msg[0]}:{menu_banner_msg[1]}")
        except Exception as e:
            print(f"[SAVE BANNER ERROR] {str(e)[:80]}")

    def load_spam_texts():
        global spam_texts
        try:
            if not os.path.isfile(SPAM_TEXTS_FILE):
                spam_texts = []; return
            with open(SPAM_TEXTS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            spam_texts = [str(x) for x in data] if isinstance(data, list) else []
        except Exception as e:
            print(f"[LOAD SPAM TEXTS ERROR] {str(e)[:80]}")
            spam_texts = []

    def save_spam_texts():
        try:
            with open(SPAM_TEXTS_FILE, "w", encoding="utf-8") as f:
                json.dump(spam_texts, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[SAVE SPAM TEXTS ERROR] {str(e)[:80]}")

    def load_warns():
        global warns
        try:
            if not os.path.isfile(WARNS_FILE):
                warns = {}; return
            with open(WARNS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            warns = {int(k): int(v) for k, v in data.items()} if isinstance(data, dict) else {}
        except:
            warns = {}

    def save_warns():
        try:
            with open(WARNS_FILE, "w", encoding="utf-8") as f:
                json.dump(warns, f, indent=2)
        except: pass

    async def get_targets(event, arg: str = "") -> Set[int]:
        targets: Set[int] = set()
        if event.is_reply:
            try:
                reply = await event.get_reply_message()
                if reply and reply.sender_id:
                    targets.add(int(reply.sender_id))
            except: pass
        if arg:
            for part in arg.strip().split():
                if not part: continue
                if part.isdigit():
                    try: targets.add(int(part)); continue
                    except: pass
                try:
                    ent = await bot.get_entity(part)
                    if ent and getattr(ent, "id", None):
                        targets.add(int(ent.id))
                except: pass
        try:
            me = await bot.get_me()
            targets.discard(me.id)
        except: pass
        targets -= PROTECTED_IDS
        return targets

    load_admins()
    load_notes()
    load_banner()
    load_spam_texts()
    load_warns()

    # ────────────────────────────────────────────────
    #          ORIGINAL TEXT LISTS (Unchanged)
    # ────────────────────────────────────────────────
    reply_list = [
        "𝐊ʏᴀ 𝐑ᴇ 𝐑ᴀɴᴅɪᴋᴇ 𝐂ᴏᴏʟ 𝐁ᴀɴᴇɢᴀ 𝐓ᴜ 𝐂ʜᴀʟ 𝐀ʙ 𝐂ʜᴜᴅ 𝐀ᴘɴᴇ 𝐁ᴀᴀᴘ 𝗦𝗶𝗱 𝐒ᴇ - 🦢💘",
        "𝐊ɪ 𝐌ᴀᴀ 𝐌ᴀʀʀ 𝐆ᴀʏɪ 𝐘ᴀᴀʀ - 𝐉ᴀɪ 𝗦𝗶𝗱 ! 🌙",
        "acha beta 😂🔥👊🏻 ? coi na me toh HATER codunga 😹💔🔥😆👊🏻💥",
        "chudke bhaga kaise 😂💥🤣🤘🏻",
        "ne toh 𝗦𝗶𝗱 ka lun muh me lelia 😂🙏🏻😂🙏🏻",
        "try maa सूर्य☀ nikalte hi pel du 😹🔥💔",
        "mkl lun te vaj 😂✊🏻💦",
        "𝗧ᴍᴋ𝗕 pe 𝗦𝗶𝗱 ka hamla 😂⚔🔥💥",
        "𝐂ʜʟ 𝐇ᴀʀᴍᴢᴀᴅ𝐈 𝐊ᴇ लड़के 💛🤍🩵",
        "oi 𝐓ᴇʀɪ 𝐌‌ᴀᴀ गुलाम ₰🖤",
        "chl rndyce chud ke dikha 😂💥🤣🔥",
        "𝐊ɪ 𝐌ᴀᴀ 𝐌ᴀʀʀ 𝐆ᴀʏɪ naacho 💃🏻💃🏻🕺🏻🎶😂😆💞🔥 !",
        "tera baap bass 𝗦𝗶𝗱 hai 😂🎀",
        "try maa hagte hue paad mari -#😹🔥🥀",
        "𝐓ᴇʀɪ 𝐌ᴜᴍᴍʏ 𝐂ʜᴏᴅ 𝐃ɪ 𝗦𝗶𝗱 𝐍ᴇ 𝐁ᴡᴀʜᴀʜᴀʜᴀ ⚜",
    ]

    reply_texts = [
        "⋆｡ﾟ☁︎｡𝐂ʏᴜ 𝐑ᴇ मदरचोद 𝗦𝗶𝗱 बाप के सामने 𝐅ʏᴛᴇʀ 𝐁ᴀɴᴇɢᴀ ⋆𓂃 ོ☼𓂃 😂🔥",
        "नहीं नहीं तेरी मां को 𝐒ɪʀғ 𝗦𝗶𝗱 बाप चोद सकता है ִֶָ𓂃 ࣪ ִֶָ👑་༘࿐ sᴀᴍᴊʜᴀ ʀᴀɴᴅɪᴋᴇ ???",
        "तेरी मां का 𝐒ᴛʏʟɪsʜ भोसड़ा 😱",
        "𝑻𝒆𝒓𝒚 𝒎𝒂𝒂 𝒓𝒂𝒏𝒅𝒂𝒍 𝒉 𝒃𝒂𝒔 𝒃𝒂𝒂𝒕 𝒌𝒉𝒂𝒕𝒂𝒎 😡🔥",
        "सोच तेरी बहन को 𝗦𝗶𝗱 बाप का गुलाम चोद رہا 😎🔥",
        "Hello hello?? Oxygen aarahi है? रण्डी पुत्र 🧘🏻",
        "Shut up रंडीके वरना दुनिया यही बोलेगी तेरी बहन 𝗦𝗶𝗱 /~👑 बाप से सही chudi 🥵🔥",
        "ᴛᴜ ᴏʀ ᴛᴇʀɪ ᴍᴀᴀ ᴅᴏɴᴏ 𝗦𝗶𝗱 बाप के ʟɴᴅ sᴇ ᴋᴀʙʜɪ ᴜᴛʜ ɴʜɪ ᴘᴀʏᴇ 😂🔥",
    ]

    fun_texts = [
        "तेरे मां के दूदू के बीच मेरा lund fas gaya oops 🤪（ ͜.🍆 ͜.）",
        "𝐓ᴇʀʏ 𝐁ʜᴇ𝐍 𝐊ᴇ ( ͜. ㅅ ͜. )🥛 ʏᴜᴍᴍʏ ",
        "𓂃☁︎ 𓂃𝐒ɪᴅᴇ 𝐇ᴀᴛ 𝐆ᴜʟᴀᴍ 𝐓ᴇʀʏ 𝐌ᴀᴀ 𝐊ᴏ 𝐂ʜᴏᴅɴᴇ  मेरी रेलगाड़ी आ रही .-'🚂-'.ᯓᡣ𐭩______ 𓂃☁︎ 𓂃",
        "⋆⭒˚.⋆🔭 𝐒ʜᴜᴛ 𝐔ᴘ 𝐑ᴀɴᴅɪᴋᴇ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴅᴀɪ 𝐄ɴᴊᴏʏ 𝐊ʀ 𝐑ᴀʜᴀ 𝐓ᴇʟᴇ𝐒ᴄᴏᴘᴇ 𝐒ᴇ⋆⭒˚.⋆🔭",
    ]

    flag_texts = [
        " ོ༘₊⁺🇮🇳 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ 𝗦𝗶𝗱 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐈ɴᴅɪᴀ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇮🇳 ₊⁺⋆.˚",
        " ོ༘₊⁺🇯🇵 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ 𝗦𝗶𝗱 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐉ᴀᴘᴀɴ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇯🇵 ₊⁺⋆.˚",
        " ₊⁺🇺🇸 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ 𝗦𝗶𝗱 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐔𝐒𝐀 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇺🇸 ₊⁺⋆.˚",
        " ོ༘₊⁺🇬🇧 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ 𝗦𝗶𝗱 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐔𝐊 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇬🇧 ₊⁺⋆.˚",
        " ོ༘₊⁺🇰🇷 ₊⁺⋆.˚𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ 𝗦𝗶𝗱 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐊ᴏʀᴇᴀ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇰🇷 ₊⁺⋆.˚",
        " ོ༘₊⁺🇩🇪 ₊⁺⋆.˚ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ 𝗦𝗶𝗱 𝐁ᴀᴀᴘ 𝐀ᴜʀ 𝐆ᴇʀᴍᴀɴʏ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇩🇪 ₊⁺⋆.˚",
    ]

    heart_replies = [
        "𓂃˖˳·˖ ִֶָ ⋆❤️͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚❤️ ݁˖⭑.ᐟ",
        "𓂃˖˳·˖ ִֶָ ⋆🧡͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚🧡 ݁˖⭑.ᐟ",
        "𓂃˖˳·˖ ִֶָ ⋆💛͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💛 ݁˖⭑.ᐟ",
        "𓂃˖˳·˖ ִֶָ ⋆💚͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💚 ݁˖⭑.ᐟ",
        "𓂃˖˳·˖ ִֶָ ⋆💙͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💙 ݁˖⭑.ᐟ",
    ]

    # ────────────────────────────────────────────────
    #          NEW FIGHTING TEXT LISTS (20 types)
    # ────────────────────────────────────────────────

    attack_list = [
        "⚔️ Teri aukat nahi mujhse ladhne ki randike 😂🔥",
        "💥 Chal bhaag yahan se chutiye warna maar khayega 🤣⚔️",
        "🗡️ Tera baap aaya hai sunta nahi kya 👑😈",
        "⚡ Mere saamne aake dikhao himmat hai toh 😎💪",
        "🔥 Attack mode on — teri khair nahi aaj 😡⚔️",
        "💀 Tujhe itna marunga ke teri maa bhi nahi pehchanegi 😂🔥",
        "⚔️ Randike chal 1v1 kar le dikhata hoon kaun baap hai 👊😤",
        "💥 Beta ye territory meri hai nikal yahan se 🏴‍☠️⚡",
        "🗡️ Aukaat hai toh saamne aa nahi toh chup baith 😈💀",
        "⚡ Tu keyboard warrior hai asli mard nahi 😂👊",
        "🔥 Teri maa ne bhi bola tera baap chahiye 😹💔",
        "💥 Chal hat yahan se chota baccha 🤣👋",
        "⚔️ Mujhe gaali de ke dekh kya hoga teri life mein 😈⚡",
        "💀 Bhai seedha bol de surrender karega ya maar khayega 😎🔥",
        "🗡️ Attack karta hoon toh block nahi hoga tera 😡⚔️",
        "⚡ Yeh game mein nahi real life mein bhi kaatenge tujhe 💪😤",
        "🔥 Tera confidence dekh ke hansi aati hai yaar 😂💥",
        "💥 Andha hai ya dikhta nahi kaun boss hai yahan 👑⚔️",
        "⚔️ Teri har gaali pe 10 gaaliyan waapis aayengi 😈🔥",
        "💀 Beta peeth nahi dikhana mujhe — coward 🏃‍♂️😂",
        "🗡️ Lad le ek baar — guarantee hai rota hoga tu 😹⚡",
        "⚡ Keyboard tod ke aa toh baat karte hain 💥👊",
        "🔥 Teri bhasha se pata chalta hai ghar mein parhe nahi 😂🤣",
        "💥 Chutiye attack se pehle socha nahi kya hoega 😈⚔️",
        "⚔️ Main yahan hoon — tu kahan chhupta hai aaja 😎💀",
        "💀 Teri har move ka jawab taiyaar hai mere paas 🎯🔥",
        "🗡️ Tu sirf darta hai asli attack nahi kar sakta 😂⚡",
        "⚡ Baahubali nahi hai tu yahan — chal nikal 👋💥",
        "🔥 Teri aukaat utni hai jitni do takke ki 😹🗡️",
        "💥 Attack aur reaction — dono mein haar jayega tu ⚔️😎",
        "⚔️ Ek baar aake dekh kya hota hai tere saath 💀🔥",
        "💀 Sher ke saamne bakra nahi ban — phir bhi ban raha 😂⚡",
        "🗡️ Yeh teri territory nahi bhai — haath jod ke ja 🙏😈",
        "⚡ Tu attack karega aur main finish karunga 💥⚔️",
        "🔥 Teri himmat hai toh mujhse seedha baat kar 😤💀",
        "💥 Keyboard pe hero ban raha hai — asli duniya mein zero 😂🗡️",
        "⚔️ Maar kha aur phir rota mat — warning hai 😈⚡",
        "💀 Teri speed se faster hoon main — bhaag nahi sakta 🔥💥",
        "🗡️ Yaar teri life mein koi nahi kya isliye yahan ata hai 😂⚔️",
        "⚡ Hero mat ban — yahan real khiladi baithe hain 👑💀",
        "🔥 Attack kiya — ab lash uthane ki taiyaari kar 😹⚡",
        "💥 Randike tu attack karta hai ya gaana gaata hai 😂⚔️",
        "⚔️ Teri har galti ka hisaab hoga — ruk 😈🔥",
        "💀 Bhai attack se pehle 1% dimag use kar 🧠💥",
        "🗡️ Chal hat nahi toh main khud hataunga isko 😤⚡",
        "⚡ Yeh war hai — aur tu already haar gaya 😎🔥",
        "🔥 Teri maa bhi tera lecture sunke bore ho gayi hogi 😹💥",
        "💥 Main attack mein vishwas nahi karta — main finish mein karta hoon ⚔️😈",
        "⚔️ Chal randike ek baar try kar le — rona mat baad mein 😂💀",
        "💀 Ab samjha kya hua? No? Toh phir ek aur attack 🔥⚡",
    ]

    roast_list = [
        "🔥 Teri zindagi ek bakwas webseries ki tarah hai — 1 season mein flop 😂📺",
        "🤣 Bhai teri personality ek sada hua pyaz jaisi hai — khole toh aansu aaye 🧅💀",
        "😹 Tu itna bura lagta hai ke teri photo dekh ke mosquito bhi bhaag jata hai 🦟😂",
        "🔥 Teri maa ne bhi socha hoga — yaar galti ho gayi 😹👶",
        "🤣 Tujhe dekh ke pata chalta hai — darr darr ke jeena kya hota hai 😂💀",
        "😹 Beta tu Google Maps pe search kare toh bhi worthless aayega 🗺️😈",
        "🔥 Teri iq level negative hai — calculator mein error aata hai 🧮😂",
        "🤣 Tu chhata hua papad hai — touch karte hi toot gaya 😹🔥",
        "😹 Bhai teri aukat itni hai ke mirror bhi muh fer leta hai 🪞😂",
        "🔥 Teri personality dekh ke AI bhi depressed ho gaya hoga 🤖😹",
        "🤣 Tu aisa dost hai jo aaye na aaye — fark nahi padta 😂💀",
        "😹 Bhai teri soch utni hi purani hai jitna tera Nokia phone 📱😂",
        "🔥 Tera existence mere life mein irrelevant hai — bilkul sarkari kaam jaisa 📋😹",
        "🤣 Tu itna boring hai ke neend khud aa jaaye tujhe dekh ke 😴😂",
        "😹 Teri profile pic dekh ke emoji wale bhi sue kar sakte hain 😱🔥",
        "🔥 Bhai tu aisa player hai jo kabhi goal nahi kar sakta apni hi team ke khilaf 😂⚽",
        "🤣 Teri advice sunna waisa hai jaise sade kele se rasta poochna 🍌😹",
        "😹 Tu garib nahi hai — but tujhe dekh ke gareebi ko takleef hoti hai 💰😂",
        "🔥 Teri kismat itni kharab hai ke lottery ticket bhi teri traf nahi dekhti 🎫😹",
        "🤣 Bhai tera sense of humor graveyard se udhaara liya hai kya 🪦😂",
        "😹 Tu itna irrelevant hai ke khud Google bhi nahi jaanta tera naam 🔍🔥",
        "🔥 Teri body language bolta hai — main hara hua insaan hoon 😂💀",
        "🤣 Tu ek hi baar funny tha — jab tune mujhe seriously liya 😹⚡",
        "😹 Bhai teri achievements list mein sirf ek cheez hai — exist karna 😂🔥",
        "🔥 Tujhe dekh ke lagta hai — nature ne mistake ki thi 🌿😹",
        "🤣 Teri skills dekh ke Thanos bhi bola hoga — yeh toh automatically wipe ho jaayega 💀😂",
        "😹 Beta tera future itna dark hai ke sunglasses pehenne ki zaroorat nahi 🕶️🔥",
        "🔥 Teri batting dekh ke khud pitch ne sorry bola 🏏😂",
        "🤣 Bhai tu aisa idea hai jo meeting mein sab ignore karte hain 📊😹",
        "😹 Teri zubaan aur dimag mein kabhi meetup nahi hota 🧠💬😂",
        "🔥 Tu aisa hero hai jiska movie 3 minutes mein flop ho gayi 🎬😹",
        "🤣 Teri gaali sunne ke baad dushmano ne mafi maang li 😂⚔️",
        "😹 Bhai tera swag level Excel mein error hai — #NAME? 📊🔥",
        "🔥 Tu itna dheema hai ke kachhua bhi race jeet gaya 🐢😂",
        "🤣 Teri thinking 2G speed pe chal rahi hai duniya 5G mein hai 📡😹",
        "😹 Beta tera ek message dekh ke aasman bhi sharma gaya ☁️😂",
        "🔥 Bhai teri life ek loading screen hai — jo kabhi load nahi hoti ⏳😹",
        "🤣 Tu aisa mirror hai jo galat reflection dikhata hai 🪞😂",
        "😹 Teri maa ne tujhe chhoda nahi chhodni chahiye thi 😂🔥",
        "🔥 Beta tera existence proof hai ke koi bhi internet use kar sakta hai 📶😹",
        "🤣 Tujhe dekh ke lagta hai — maa baap ne education mein invest nahi kiya 📚😂",
        "😹 Teri personality ek blank page hai — aur blank hi rahega 📄🔥",
        "🔥 Tu sirf chat mein hero hai real duniya mein zero 💻😂",
        "🤣 Bhai teri jawab dene ki speed se tortoise bhi impress nahi 🐢😹",
        "😹 Teri soch itni outdated hai ke floppy disk bhi reject kar de 💾😂",
        "🔥 Tu aisa WiFi password hai jo koi yaad nahi rakhta 🔑😹",
        "🤣 Beta teri awaaz sunne ke baad mujhe silence zyada priceless laga 🤫😂",
        "😹 Bhai tera roast karna waisa hai jaise sadi hui vegetable ko season karna 🥦🔥",
        "🔥 Teri social skills dekh ke chatbot bhi impress ho gaya 🤖😂",
        "🤣 Tu aisa chapter hai jise sab skip karte hain 📖😹",
    ]

    diss_list = [
        "🎤 Tera naam sun ke log mute kar dete hain khud ko 🔇😂",
        "💀 Tu diss kar raha hai — khud ko diss kar pehle 🪞😹",
        "🎙️ Teri rap jaisi hai — no flow no bars no future 🎵😂",
        "💥 Bhai tera verse sun ke Eminem ne retire le liya 😹🎤",
        "🔥 Teri diss itni kamzor hai ke whisper bhi zyada loud hai 🤫😂",
        "💀 Tu sirf bolne mein mard hai karne mein? Zero 😈🎙️",
        "🎤 Beta teri bars mein bar hi nahi — sirf khali string 🎸😂",
        "💥 Tera diss track sunne ke baad logon ne earbuds tod diye 🎧😹",
        "🔥 Bhai teri lyric likh ke dekha — autocorrect ne bhi reject kiya ✍️😂",
        "💀 Tu diss karta hai aur log diss ko diss karte hain 😂🎤",
        "🎙️ Teri voice aisi hai ke autotune bhi nahi bach sakta 🎶😹",
        "💥 Beta freestyle kar le — ya phir stop the embarrassment 🛑😂",
        "🔥 Tujhe sun ke DJ ne plug nikal diya 🔌😹",
        "💀 Bhai tera flow aisa hai jaise jaam mein traffic — ruka hua 🚗😂",
        "🎤 Teri soch itni slow hai ke beat ke saath nahi chalti 🥁😹",
        "💥 Tera diss mujhe sula raha hai — better than sleeping pills 😴😂",
        "🔥 Bhai asli diss toh tab hogi jab tu actually kuch achieve kare 🏆😹",
        "💀 Teri lyrics Google Translate se better hain — bas 🌐😂",
        "🎙️ Beta chal hat stage se — pehle walk-on music bana 🎵😹",
        "💥 Tera punchline itna weak hai ke paper bhi survive kar le 📄😂",
        "🔥 Bhai teri diss sun ke crowd ne baat karna shuru kar diya 🙄😹",
        "💀 Tu verse likhta hai ya grocery list — same energy 🛒😂",
        "🎤 Teri bars mein calories zyada hain — totally empty 😹🔥",
        "💥 Bhai teri rhyme sunke chhote bacche bhi sharma jaate hain 😂💀",
        "🔥 Teri diss aisi hai — sirf uski maa samjhi 😹🎙️",
        "💀 Tu diss karta hai mujhe — main khud apni diss sunta hoon for fun 😂💥",
        "🎤 Tera stage naam kya hai — Bakwas ke Raja? 👑😹",
        "💥 Bhai tera microphone bhi teri awaaz se dara hua hai 🎙️😂",
        "🔥 Tu diss mein expert hai — aur expert hone mein loser 😹💀",
        "💀 Teri har line mein cringe hai — Olympic level 🥇😂",
        "🎙️ Beta khud ki diss sun le — ek baar realise hoga 😹🔥",
        "💥 Bhai tera diss itna slow hai ke mujhe neend aa gayi 😴😂",
        "🔥 Teri creativity level: template pe naam likhna 💀😹",
        "💀 Tu diss karne ke liye paida hua tha — aur fail ho gaya 😂🎤",
        "🎙️ Tera rhyme scheme: aab aab aab — boring AF 📝😹",
        "💥 Bhai teri diss response mein Soulja Boy beat use karta hun 😂🔥",
        "🔥 Tu keyboard pe rap karta hai — phone pe nahi kaata 📱💀",
        "💀 Teri diss sun ke mic khud neeche gir gaya 🎙️😂",
        "🎤 Beta teri bars itni weak hain ke paper toh chodh kaagaz bhi nahi chhapega 📰😹",
        "💥 Bhai tera flow paani mein nahi petrol mein hai — ab blast 🔥😂",
        "🔥 Teri diss sunta hoon toh lagta hai sabne kaan band kar rakhe hain 🔇💀",
        "💀 Tu diss mein ghusaa — tu diss tha diss 😹😂",
        "🎙️ Bhai tera verse industry standard se neeche hai — ground floor bhi nahi 🏚️🔥",
        "💥 Teri awaaz mein woh baat nahi jo diss mein chahiye — talent 😂💀",
        "🔥 Beta teri diss itni pathetic hai ke pity vote mil sakta tha 🗳️😹",
        "💀 Bhai tera rap career ek Instagram story jaisi hai — 24 ghante mein khatam 📸😂",
        "🎤 Tu rapper nahi rapper ki copy ki copy ka knock-off hai 😹🔥",
        "💥 Teri diss sun ke auto-generated ho sakti thi — aur better hoti 🤖😂",
        "🔥 Bhai freestyle maar — aur phir sun khud ko — tujhe pata chalega 🎧💀",
        "💀 Teri diss ka reply nahi deta — tujhe dignify karna time waste hai 😂🎙️",
    ]

    war_list = [
        "⚔️ War shuru ho gayi — aur tu pehle hi haar gaya 😂🔥",
        "💣 Bhai main war mein nahi aata — main war khatam karne aata hoon 😈⚡",
        "🏴‍☠️ Tera jhanda uraya — apna wala lehraya 😎💀",
        "⚔️ Tu lad raha hai mujhse — yeh teri sabse badi galti hai 🔥😂",
        "💣 Main war nahi khelta — main result deliver karta hoon 👑⚡",
        "🏴‍☠️ Battlefield pe aake to dekh — tera rank kya hai 😈⚔️",
        "⚔️ Randike war declare kiya toh surrender ka option bhi rakh 😂💣",
        "💣 Tu soldier nahi hai — tu sirf noise hai 🔊😂",
        "🏴‍☠️ War mein strategy chahiye — tu sirf emotion se ladta hai 😹⚔️",
        "⚔️ Beta yeh teri territory nahi — nikalja 👋💣",
        "💣 Tera war cry sunke mujhe neend aati hai 😴😂",
        "🏴‍☠️ Main akela kaafi hoon — teri poori army ke liye ⚔️😈",
        "⚔️ War ghoshit kiya — white flag kahan hai tera 🏳️😂",
        "💣 Bhai tu pehle khud ko toh jeet — phir mujhse lad 😎💀",
        "🏴‍☠️ Tera war tactic: bolna aur bhaagna 😹⚔️",
        "⚔️ Main chhoda nahi — tu chhoda baad mein roega 😂💣",
        "💣 Battle field pe aate waqt socha — main jeet sakta hoon? Nahi 😈🏴‍☠️",
        "⚔️ Tu ek round bhi nahi jeeta — aur war ki baat karta hai 😂💀",
        "💣 Bhai surrender kar le — dignity bachegi thodi 🙏😹",
        "🏴‍☠️ War mein aaye — aur pehli line mein fail ho gaye ⚔️😂",
        "⚔️ Tera morale zero hai — teri army teri khud ki dushman hai 😂💣",
        "💣 Main war expert hoon — tu war ka victim hai 😎🏴‍☠️",
        "🏴‍☠️ Beta teri strategy ek broken compass jaisi hai ⚔️😂",
        "⚔️ War mein seena taan ke aa — peeth dikha ke nahi 😹💣",
        "💣 Bhai teri army mein sirf tu hai — aur tu kaafi nahi 😈🏴‍☠️",
        "🏴‍☠️ Teri war cry sun ke dushman khud aa gaye — rescue karne ⚔️😂",
        "⚔️ Beta teri territory war se pehle hi haari thi 💣😹",
        "💣 Main war mein nahi — main tujhe personally destroy karne mein hoon 😈🏴‍☠️",
        "🏴‍☠️ Tera war plan sunke GPS bhi confused hai ⚔️😂",
        "⚔️ Tu war mein aaya — par weapons lana bhool gaya 💣😹",
        "💣 Bhai yeh war nahi tujhe sirf reality check tha 😂🏴‍☠️",
        "🏴‍☠️ Teri army tujhse zyada samajhdaar hai — unhone bandh kiya ⚔️😈",
        "⚔️ War mein bhi excuse karta hai — aur life mein bhi 😂💣",
        "💣 Tu jo war soch raha hai — woh meri morning routine hai 😎🏴‍☠️",
        "🏴‍☠️ Bhai teri war itni slow hai ke climate change pehle ho jaayega ⚔️😹",
        "⚔️ Main tujhse war karta hoon — aur tujhe pata bhi nahi chalta 💣😂",
        "💣 War ghoshit kar ke tu pehla tha — haar ke bhi pehla hai 😹🏴‍☠️",
        "🏴‍☠️ Teri war mein consistency hai — consistently losing ⚔️😂",
        "⚔️ Bhai war mein bhagna galat hai — tu phir bhi karta hai 💣😈",
        "💣 Tu war mein aaya — main pehle se tere base par tha 🏴‍☠️😂",
        "🏴‍☠️ Teri war strategy mein sirf ek problem hai — sab kuch ⚔️😹",
        "⚔️ Beta war ka matalab samjha nahi tujhe — sikhaunga abhi 💣😂",
        "💣 War mein hero nahi bante — survivors bante hain — aur tu nahi banega 🏴‍☠️😈",
        "🏴‍☠️ Teri war mein dum nahi — sirf dhool hai ⚔️😂",
        "⚔️ Bhai war declare karna alag baat hai — jeetan alag 💣😹",
        "💣 Tu war mein aaya sirf lose karne ke liye — congratulations 🏴‍☠️😂",
        "🏴‍☠️ Main akele teri sab pe bhaari hoon — aur tujhe pata hai ⚔️😈",
        "⚔️ Teri war ka sabse bura part — tu khud tha 💣😂",
        "💣 War mein aaye — teri team ne hi tujhe chhod diya 🏴‍☠️😹",
        "🏴‍☠️ Beta war khatam — teri taraf se surrender accepted ⚔️😎",
    ]

    savage_list = [
        "😈 Main savage hoon — tujhe explanation nahi deta 🔥💀",
        "💀 Teri feelings mere liye statistics hain — irrelevant 😂😈",
        "🔥 Main woh nahi hoon jo tujhe comfortable feel karaaye 😎💀",
        "😈 Beta teri baatein mujhe bore karti hain — next 😂🔥",
        "💀 Teri opinion meri life mein footnote bhi nahi hai 😈😹",
        "🔥 Main tujhe explain nahi karta — tujhse better logon ke paas time deta hoon 😎💀",
        "😈 Tera attitude dekh ke mujhe apni nails file karni chahiye 💅😂",
        "💀 Bhai tujhe reject karna meri hobby hai 🔥😈",
        "🔥 Teri presence mujhe remind karaati hai — kuch logon ko mute karna chahiye 🔇😂",
        "😈 Main bad vibes nahi leta — teri taraf bhi nahi 💀🔥",
        "💀 Tu mere standard se neeche hai — elevator laga le 🛗😂",
        "🔥 Teri baat sunna — option nahi habit nahi aur interest bhi nahi 😈💀",
        "😈 Main ghanta samjhata hoon — samajh nahi aaya toh teri problem 😂🔥",
        "💀 Teri ego itni badi hai — uske liye alag zip code chahiye 📮😂",
        "🔥 Beta mujhe tujhse jealousy feel nahi hoti — pity hoti hai 😈💀",
        "😈 Main woh insaan nahi hoon jis par tu waqt barbad kare — ya main karta hoon 😂🔥",
        "💀 Teri life choices dekh ke main grateful hoon main tujhsa nahi hoon 😹😈",
        "🔥 Bhai teri smartness ka level: WiFi password ignore karna 📶😂",
        "😈 Teri mastiyan mujhe entertain nahi karti — bore karti hain 💀🔥",
        "💀 Main savage nahi — main simply tujhse better hoon 😎😂",
        "🔥 Teri personality ek blank meme format jaisi hai — kuch nahi 😈💀",
        "😈 Beta apni journey pe focus kar — meri disturb mat kar 😂🔥",
        "💀 Teri hard work ka result tera hi face hai — kaafi bura 😹😈",
        "🔥 Main tujhe miss nahi karta — mujhe tujhse better cheezein miss hoti hain 😂💀",
        "😈 Teri baatein sun ke laga — yeh real person hai ya chatbot glitch 🤖😂",
        "💀 Bhai teri intelligence ke liye sorry feel hoti hai 🔥😈",
        "🔥 Main tujhe block isliye nahi karta — kyunki tujhe exist karna pata hai 😂💀",
        "😈 Teri struggles dekh ke mujhe motivation milti hai — teri tarah mat banna 😹🔥",
        "💀 Tu jo effort lagate ho mujhpe — woh apni growth mein lagao 😎😂",
        "🔥 Teri vibes mujhe 2G network se bhi slow lagti hain 📡😈",
        "😈 Main tujhe pehle judge nahi karta — par tujhe pehle judge hota hoon 💀😂",
        "💀 Bhai tera shadow bhi tujhse zyada interesting hai 🔥😂",
        "🔥 Teri logic sun ke Albert Einstein ne resign kar diya hoga 🧪😈",
        "😈 Tu mere jaisa ban sakta hai — agar try karta 10 saal toh bhi nahi 💀😂",
        "💀 Teri taraf se koi bhi reaction — mujhe bored karta hai 🔥😹",
        "🔥 Main respectful hoon — tere sath nahi 😈💀",
        "😈 Beta teri vibe check: FAILED 😂🔥",
        "💀 Teri har move predicted thi — boring player 😹😈",
        "🔥 Main tujhe second chance nahi deta — teri pehli impression kafi thi 😂💀",
        "😈 Teri friendship ke offer ko professionally decline karta hoon 😎😂",
        "💀 Beta tu mujhe feel nahi karaata — tu sirf annoy karta hai 🔥😈",
        "🔥 Teri dimagi capacity dekh ke solar calculator bhi sorry bol de 🔋😂",
        "😈 Main uun logon mein nahi hoon jo tere liye time waste karein 💀🔥",
        "💀 Teri life ka GPS tujhe wrong direction mein le ja raha hai 🗺️😂",
        "🔥 Bhai teri alag identity bana — copier mat ban 😈💀",
        "😈 Tu mere radar par bhi nahi aata — itna irrelevant hai 😂🔥",
        "💀 Teri maa ne bhi socha hoga — yaar isko kuch aur karna chahiye tha 😹😈",
        "🔥 Main woh hoon jo teri nightmares mein aata hai — as a reminder 😎💀",
        "😈 Beta teri bakaiti mujhe filter nahi karti — automatically skip ho jaati hai 😂🔥",
        "💀 Tu savage hone ki koshish karta hai — mujhe dekh savage ka example 😈😹",
    ]

    ultra_list = [
        "🌪️ ULTRA MODE ACTIVATED — teri poori existence question mein hai 😈🔥",
        "⚡ Ultra attack — pehle gaali sunna phir rona — sequence yaad kar 😂💀",
        "🌪️ Beta ultra level pe aake dekh — yahan teri category nahi hai 👑🔥",
        "⚡ ULTRA BLOW — teri soch se lekar attitude tak sab destroy 💥😈",
        "🌪️ Yeh ultra mode hai — blocking nahi help karega 😂⚡",
        "⚡ Ultra raid engaged — ab teri poori chat history history hai 📜😹",
        "🌪️ Beta ultra speed mein aa — par seedha home le jaata hoon 💀🔥",
        "⚡ Ultra fire — teri har defensive move kaam nahi karegi 😈🌪️",
        "🌪️ Yeh ultra level fight hai — tu still bronze mein hai 😂⚡",
        "⚡ ULTRA DAMAGE — teri reputation, teri aukaat, teri everything 💥😹",
        "🌪️ Ultra mode mein poori teri army bhi kaafi nahi 😈🔥",
        "⚡ Beta ultra attack sunne ke baad sun raha hai kya? Normal hai 😂🌪️",
        "🌪️ ULTRA RANT incoming — tune jo kiya uska hisaab hoga 💀⚡",
        "⚡ Yeh ultra version hai — tujhe pata bhi nahi kya aaya 😹🔥",
        "🌪️ Ultra mode ON — timer chal raha hai teri destruction ka 😈⚡",
        "⚡ Beta ultra strike pe tujhe sirf ek option hai — disappear 😂💀",
        "🌪️ ULTRA COMBO — reply + react + roast + raid all at once 🔥⚡",
        "⚡ Yeh ultra level rage hai — aur tujhe taste hoga 😈🌪️",
        "🌪️ Ultra activated — pehle bol sorry phir ja 😹😂",
        "⚡ Beta ULTRA message ka matlab — tu mere liye mission ban gaya 💀🔥",
        "🌪️ ULTRA STORM — har cheez destroy ho rahi hai teri side pe 😈⚡",
        "⚡ Yeh ultra nahi — tujhe sirf samjhane ki koshish thi 😂🌪️",
        "🌪️ Ultra mode finish — teri team ne tera saath chhoda 💀🔥",
        "⚡ Beta ULTRA = mera minimum effort on you 😈😂",
        "🌪️ ULTRA RAIN — tune invite kiya tha — enjoy karna tha na? 😹⚡",
        "⚡ Ultra mode mein ek hi rule — no mercy 💀🔥",
        "🌪️ Beta ULTRA sabse pehle yeh — teri galti ka hisaab 😈⚡",
        "⚡ Yeh ultra speed se aaya — aur teri samajh mein ultra slow aayega 😹🌪️",
        "🌪️ ULTRA LOCK — ab yahan se nahi jayega tu 💀🔥",
        "⚡ Beta ultra strike mein teri saari strategy fail hai 😂😈",
        "🌪️ Ultra level pe chal — toh teri duniya hi badal jaayegi 🔥⚡",
        "⚡ ULTRA — yeh word hi teri aukat se bada hai 😹💀",
        "🌪️ Beta ultra mein main hoon — tujhe pata nahi tha kya 😈🔥",
        "⚡ Yeh ultra raid hai — har message teri ek problem hai 😂🌪️",
        "🌪️ ULTRA DONE — tu done kar le pehle 💀⚡",
        "⚡ Beta ultra mein welcome — pehle bol kya karna hai 😹🔥",
        "🌪️ Ultra mode — ab seedha point pe aata hoon — tu fail hai 😂😈",
        "⚡ ULTRA BLAST — teri timeline pe aaya — nahi ruk sakta 💥🌪️",
        "🌪️ Beta ultra mein aake teri baat karo — nahi aata toh seedha ja 💀🔥",
        "⚡ Yeh ultra war hai — aur teri taraf se koi nahi 😂😈",
        "🌪️ ULTRA FINAL — bas yahi hoga — accept kar 💀⚡",
        "⚡ Beta ultra strike complete — check teri status 😹🔥",
        "🌪️ Ultra mode mein log surrender karte hain — tujhe bhi karna hoga 😈⚡",
        "⚡ Yeh ultra punishment nahi — tutorial hai teri life ka 😂💀",
        "🌪️ ULTRA JUDGEMENT — teri har move judged ho rahi hai 🔥⚡",
        "⚡ Beta ultra mein ek cheez — main hoon aur tu nahi rahe 😈🌪️",
        "🌪️ Ultra mode completed — teri side destroyed 💀😂",
        "⚡ Yeh ultra attack ka last wave hai — teri koi repair nahi 😹🔥",
        "🌪️ ULTRA END — teri war khatam teri taraf se flag gira 😈⚡",
        "⚡ Beta ultra mein aana tha — rona nahi tha — par dono kiye 😂💀",
    ]

    godwar_list = [
        "👑 GOD MODE — tu mortal hai mujhse ladhne ki aukat nahi 😈🔥",
        "🌟 Main GOD WAR mein hoon — teri poori bloodline haari 💀⚡",
        "👑 Beta God level pe welcome — nahi samjha toh nahi samjha 😂😈",
        "🌟 GOD FURY — sun raha hai na? Yeh teri calling hai 🔥💀",
        "👑 Main woh hoon jis se God bhi seekhta hai war 😎⚡",
        "🌟 Beta God war mein aaja — tujhe enlightenment milega 😂🔥",
        "👑 GOD LEVEL ATTACK — teri sari defenses dust hain 💀😈",
        "🌟 Main tujhe war mein nahi involve karta — tujhe demo dikhata hoon 😎⚡",
        "👑 Beta GOD mode — yeh teri life pe trailer tha 🔥😂",
        "🌟 GOD WAR declaration — teri surrender automatically process hogi 💀😈",
        "👑 Mujhse God war karta hai — bhai apni aukat dekh pehle 😹🌟",
        "🌟 Beta yeh God ki territory hai — tujhe clearance nahi 😈🔥",
        "👑 GOD RAID — tune invite nahi kiya tha — main khud aaya 💀⚡",
        "🌟 God level pe destruction toh ek ritual hai — tu shikaar hai 😂😈",
        "👑 Beta GOD WAR mein mercy nahi hoti — yaad rakhna 🔥💀",
        "🌟 Main GOD hoon — tujhse sirf proof nahi — demonstration 😎⚡",
        "👑 GOD FURY — teri poori defence grid fail ho gayi 😂🌟",
        "🌟 Beta tu GOD war ke eligible nahi — neeche jaake pehle seedh ho 💀😈",
        "👑 GOD LEVEL ROAST — teri existence ko judge kar raha hoon 🔥😂",
        "🌟 Main GOD mein aaya — teri poori team disqualified 😈⚡",
        "👑 Beta GOD war ka ek hi rule — mera wins 💀🌟",
        "🌟 GOD MODE FINAL — teri sab pray kar rahi hai — tere liye 😂🔥",
        "👑 Main GOD war mein sirf ek baar aata hoon — yeh tha 😈💀",
        "🌟 Beta GOD ki bhasha — tu nahi samjhega 🔥⚡",
        "👑 GOD WRATH — teri aankh mein aansu aayenge meri victory pe 😂😈",
        "🌟 Main GOD hoon yahan — tujhe bhagwan bhi nahi bachayega 💀🔥",
        "👑 Beta GOD war mein aake cry mat karna 😹🌟",
        "🌟 GOD LEVEL — teri poori history erase — new game 😈⚡",
        "👑 Main GOD war mein tab aata hoon jab dushman deserve karta hai 🔥💀",
        "🌟 Beta GOD mode mein teri soch bhi haari 😂😈",
        "👑 GOD RAID COMPLETE — check teri position 💀🔥",
        "🌟 Main GOD hoon — isliye tujhe seriously le raha hoon briefly 😎⚡",
        "👑 Beta GOD war mein rules nahi hote — sirf results 😂🌟",
        "🌟 GOD FURY UNLEASHED — ab teri timeline pe aa raha hoon 💀😈",
        "👑 Main GOD level pe operate karta hoon — tu tutorial mein hai 🔥⚡",
        "🌟 Beta GOD war ka last chapter — teri story yahan khatam 😂💀",
        "👑 GOD MODE — tujhe itna marunga ke tujhe khud samajh aayega 😈🌟",
        "🌟 Main GOD war mein hoon — tu still login attempt mein 🔥😂",
        "👑 Beta GOD level destroy — teri poori team silent hai 💀⚡",
        "🌟 GOD WAR — yeh nahi tha teri plan mein — par mera tha 😈😂",
        "👑 Main GOD hoon — mercy nahi hai yahan — documentation nahi meri 🔥💀",
        "🌟 Beta GOD level baat — teri aukat sun lene ki nahi ⚡😈",
        "👑 GOD WAR OVER — teri side: zero GOD side: everything 😂🌟",
        "🌟 Main GOD mode mein hoon — tujhe pata bhi nahi 💀🔥",
        "👑 Beta GOD war mein aake tujhe pehle proof karna hoga — nahi kar sakta 😈⚡",
        "🌟 GOD FINAL BLOW — yeh tha — enjoy kar teri haari 😂💀",
        "👑 Main GOD hoon — teri war meri relaxation thi 🔥😎",
        "🌟 Beta GOD mode ACTIVATED — teri poori chat screenshot ho rahi hai 😹💀",
        "👑 GOD WAR — sirf GOD jeette hain — aur GOD main hoon 😈⚡",
        "🌟 Beta GOD war ka tutorial yaad rakho — yeh tha 😂👑",
    ]

    combo_list = [
        "💥⚔️🔥 COMBO HIT — reply + roast + flag + react sab ek saath 😈💀",
        "🌪️💣👑 TRIPLE COMBO — teri sab kuch ek hi shot mein 😂⚡",
        "💥🔥😈 COMBO ATTACK — nahi rokna kisi ke liye bhi 💀🌪️",
        "⚔️💣🌟 Yeh combo hai — tu already down hai teri counting shuru 😂🔥",
        "🌪️😈💀 MEGA COMBO — tera sara defense ek message mein finish 😹⚡",
        "💥⚡👑 Combo level ULTRA — teri koi move kaam nahi ayegi 🔥😂",
        "⚔️🔥😹 COMBO RAIN — jab bhi message karega — combo activate 💀🌪️",
        "🌪️💣😈 Beta yeh combo nahi — yeh tujhe samjhaane ka tarika hai 😂⚡",
        "💥👑🔥 GRAND COMBO — teri poori squad aaj haari 😈💀",
        "⚔️🌪️😂 Combo attack engage — ab teri duniya theek nahi hogi 🔥💣",
        "💀⚡💥 COMBO BLAST — every message ek naya problem tera 😹😈",
        "🔥🌪️⚔️ Beta COMBO mein teri sochi bhi counted hai 😂💀",
        "😈💣👑 COMBO FINISHER — teri team tujhe chhod ke bhaag gayi ⚡🔥",
        "💥🔥😹 Yeh combo teri life ka worst decision yaad karayega 😈🌪️",
        "⚔️💀🌟 COMBO CHECK — teri reply ka wait nahi — next combo ready 😂⚡",
        "🌪️😈💣 Beta combo mein teri sab cheez shaamil hai — teri galti bhi 🔥💀",
        "💥⚡🔥 ULTIMATE COMBO — teri existence challenged hai 😹😂",
        "⚔️👑😈 Combo attack — ek aaya aur sab le gaya 💀🌪️",
        "🌪️💥😂 Beta COMBO FURY — tujhe recover karne ki zaroorat nahi rahi 🔥⚡",
        "💣🔥👑 COMBO FINALE — teri story ka end likha ja raha hai 😈💀",
        "⚔️💀😹 Yeh combo tujhpe dedicated hai — enjoy kar 🌪️⚡",
        "🌪️😈🔥 COMBO STORM — har cheez teri toot rahi hai 💥😂",
        "💀⚡💣 Beta COMBO mein koi block kaam nahi aata 😹🔥",
        "🔥👑🌪️ COMBO TRIGGER — teri sab mute hone chahiye 😈💀",
        "💥😂⚔️ COMBO RAID — pehli baar nahi — par yaadgaar hai 🌪️⚡",
        "😈💣🔥 Beta COMBO kar ke dekh — apni taraf se 😂💀",
        "⚡🌪️😹 COMBO OVERDRIVE — tujhe pause bhi nahi milega 🔥😈",
        "💀💥👑 Yeh COMBO tera time waste hai — mera fun 😂⚔️",
        "🌪️⚔️😈 COMBO LAUNCH — teri trajectory down hai 🔥💣",
        "💥😹🌟 Beta COMBO mein aake sab kuch kaata — kuch nahi bachega 💀😂",
        "🔥😈💣 COMBO PUNISHMENT — teri har galti ka charge add ho raha hai ⚡🌪️",
        "⚔️💀😂 Yeh COMBO tera tutorial tha — fail ho gaya 🔥💥",
        "🌪️⚡😈 COMBO FINISH — teri team ki condolences le aata hoon 😹💀",
        "💥👑🔥 Beta COMBO LOADED — sab teri taraf aim hai 😂😈",
        "⚔️💣🌪️ COMBO EXPLOSION — teri har cheez gone 💀⚡",
        "😈🔥💀 Beta yeh COMBO teri poori chat ka summary hai 😹🌪️",
        "💥⚡😂 GRAND COMBO RELEASE — tujhe mera response nahi chahiye — aata hai 🔥😈",
        "🌪️💣👑 COMBO RAIN — teri timeline pe aa raha hoon 💀⚔️",
        "⚡🔥😹 Beta COMBO engage — teri soch ke pehle message aa gaya 😈🌪️",
        "💥😈⚔️ MEGA COMBO — tujhe pehle bola tha — nahi maana 💀🔥",
        "🌪️💀😂 COMBO LOCKED — teri taraf se no escape 😈⚡",
        "🔥⚔️💣 Beta COMBO mein sab kuch plan tha — tujhe nahi pata tha 😹💀",
        "💥🌪️😈 COMBO BURST — teri poori squad silent ho gayi 🔥⚡",
        "⚡💀🔥 Yeh COMBO teri poori history ka audit tha 😂😈",
        "🌪️💥👑 COMBO COMPLETE — teri side: nothing ours: everything 💀🔥",
        "😈⚔️😹 Beta COMBO mein aake pata chala — tujhe try mat karna chahiye tha 🌪️⚡",
        "💀🔥💥 COMBO FINAL WAVE — last chance surrender kar le 😂😈",
        "⚡🌪️👑 Yeh COMBO nahi tha — practice session tha tera against 😹💀",
        "💥😈🔥 COMBO OVER — teri wahi condition jo socha tha 🌪️⚡",
        "⚔️💀😂 MEGA COMBO DONE — shukriya tera — itna fun kabhi nahi tha 😈🔥",
    ]

    troll_list = [
        "🤡 Bhai tujhe dekh ke lagta hai troll ka mascot tu hai 😂🔥",
        "😹 Tu itna troll hai ke khud ko pata nahi 💀🤡",
        "🤡 Teri baatein sun ke log seriously nahi lete — aur le bhi nahi chahiye 😂😹",
        "😹 Beta tu internet ka troll #1 candidate hai 💀🤡",
        "🤡 Tujhe real life mein bhi ignore karte honge log 😂🔥",
        "😹 Bhai teri comments section mein sabne dislike diya 👎🤡",
        "🤡 Tu troll karne ki koshish karta hai — khud troll bana rehta hai 😂💀",
        "😹 Teri troll game weak hai — aur weak troll game bhi troll hai 🤡🔥",
        "🤡 Beta jo tu sochta hai funny hai woh boring hai 😂😹",
        "😹 Bhai tera troll skill level: tutorial mode pe stuck 🤡💀",
        "🤡 Tu troll hai par original nahi — copy-paste troll 😂🔥",
        "😹 Teri trolling se logon ko secondhand embarrassment hoti hai 🤡😂",
        "🤡 Beta tujhe seriously lena — woh troll hoga apne aap pe 😹💀",
        "😹 Bhai tera meme quality — delete worthy 🤡😂",
        "🤡 Tu troll karta hai online — real duniya mein kaanta nahi milta 😹🔥",
        "😹 Beta teri har post pe raat ko cry karta hai 🤡💀",
        "🤡 Tujhe dekh ke pata chalta hai — internet access free nahi honi chahiye 😂😹",
        "😹 Bhai teri troll attempt genuine cringe hai 🤡🔥",
        "🤡 Tu troll ka wannabe version hai 😂💀",
        "😹 Beta asli troll woh hota hai jise pata nahi woh troll hai — tu wahi hai 🤡😂",
        "🤡 Bhai teri comments log copy karke dusron ko dikhate hain — example ke liye kya nahi karna chahiye 😹🔥",
        "😹 Tu troll karta hai par khud hi jal jaata hai 🤡💀",
        "🤡 Beta teri troll attempts fail hoti hain kyunki tujhe original hona chahiye 😂😹",
        "😹 Bhai seriously — apni energy sahi jagah lagao 🤡🔥",
        "🤡 Teri trolling mein timing nahi content nahi creativity nahi 😂💀",
        "😹 Beta tu woh insaan hai jo khud ko troll king samjhta hai — aur paida hota hai troll ke neeche 🤡😂",
        "🤡 Bhai tera troll fail isliye hota hai — genuine nahi hai 😹🔥",
        "😹 Tu troll karta hai aur end mein rota hai — classic 🤡💀",
        "🤡 Beta tujhe sun ke logon ko stress nahi hoti — pity hoti hai 😂😹",
        "😹 Bhai teri troll quality inspect hua — returned as defective 🤡🔥",
        "🤡 Tu original troll nahi — fan-made version hai 😂💀",
        "😹 Beta teri trolling attempt mein best cheez — mujhe engage nahi karta 🤡😂",
        "🤡 Bhai teri presence troll community ke liye embarrassment hai 😹🔥",
        "😹 Tu troll karta hai aur log silent ho jaate hain — cringe se 🤡💀",
        "🤡 Beta teri troll ka response — ignore — kyunki deserve nahi karta 😂😹",
        "😹 Bhai tera troll skill tree mein sirf ek node hai — aur woh bhi locked hai 🤡🔥",
        "🤡 Tu troll ka demo version hai — full version nahi aaya 😂💀",
        "😹 Beta trolling seekh pehle phir aa — abhi tu syllabus mein nahi hai 🤡😂",
        "🤡 Bhai teri baatein sun ke log empathy feel karte hain — tere liye 😹🔥",
        "😹 Tu troll nahi — annoying hai — alag concept hai 🤡💀",
        "🤡 Beta tera troll game 0/10 — ek baar apni chat history padh 😂😹",
        "😹 Bhai tu sirf apna time barbad kar raha hai — mera nahi 🤡🔥",
        "🤡 Teri troll attempt ek baar bhi hit nahi hui — streak: 0 😂💀",
        "😹 Beta tera troll unprovoked aur uninspired tha 🤡😂",
        "🤡 Bhai tu troll ke bhi standards neeche hai 😹🔥",
        "😹 Teri trolling see aur feel karna — dono experience kharab hain 🤡💀",
        "🤡 Beta teri troll ne sirf yeh prove kiya — tujhe better kaam dhundhna chahiye 😂😹",
        "😹 Bhai troll mein skill hoti hai — teri mein nahi 🤡🔥",
        "🤡 Tu troll hai aur tera troll bhi troll hai — recursion 😂💀",
        "😹 Beta ek advice — yeh mat kar — seriously apni life mein focus kar 🤡😎",
    ]

    shame_list = [
        "😤 Sharam kar — itna gira hua kaam karte kaise hain tum log 🔥💀",
        "🙅 Bhai teri harkat dekh ke pura group sharam se doob gaya 😂😤",
        "😤 Yeh sab karke tujhe pride feel hoti hai? Really? 💀🔥",
        "🙅 Beta teri harkaten dekh ke maa baap sharmayenge 😂😤",
        "😤 Sharam nahi hai tujhe bilkul — clearly 💀😹",
        "🙅 Bhai itna gira hua kaam dekh ke log muh fer lete hain 😤🔥",
        "😤 Tu itna neeche gira — zameen bhi neeche ho gayi 💀😂",
        "🙅 Beta sharam bhi nahi aata aisa karte hue 😤😹",
        "😤 Yeh harkat dekh ke lagta hai — tujhe value kisi ne nahi sikhaya 💀🔥",
        "🙅 Bhai log tujhe dekh ke aankhein pher lete hain — soch kya kar raha hai 😤😂",
        "😤 Teri galti nahi — environment ki galti — par ab waqt hai change ka 💀😹",
        "🙅 Beta sharam isliye nahi aati kyunki sharam feel karna seekha nahi 😤🔥",
        "😤 Yeh kaam karke tujhe khushi mili? Toh mujhe tujhse zyada chinta hai 💀😂",
        "🙅 Bhai teri harkat pura record hai — aur yeh record kharab hai 😤😹",
        "😤 Tu sochta hai koi dekh nahi raha — sab dekh rahe hain 💀🔥",
        "🙅 Beta aisa behave karta hai — khud se bhi embarrassing lagta hai tu 😤😂",
        "😤 Yeh sab dekh ke lagta hai — teri parwarish kahan gayi 💀😹",
        "🙅 Bhai teri harkaton ka hisaab hoga — aaj nahi toh kal 😤🔥",
        "😤 Tu sharminda nahi hai — woh most shameful cheez hai 💀😂",
        "🙅 Beta logo ne tujhe judge kiya — kyunki tune judge hone wala kaam kiya 😤😹",
        "😤 Yeh bura kaam karke tujhe kya mila — kuch nahi — bas naam barbad 💀🔥",
        "🙅 Bhai sharam karo — itna toh haq hai tumhara 😤😂",
        "😤 Tu yahan cool lagne ki koshish mein sharminda ho gaya 💀😹",
        "🙅 Beta ghalat rasta chhod — vapas aa 😤🔥",
        "😤 Yeh sab karke teri image bani hai — worst category mein 💀😂",
        "🙅 Bhai teri harkat ka review — 0 stars — do not recommend 😤😹",
        "😤 Tu itna neeche gira — recovery mushkil lagti hai 💀🔥",
        "🙅 Beta tujhe samjhana waqt waste hai — par try kar raha hoon 😤😂",
        "😤 Yeh sab dekh ke mujhe tujhse zyada tujhpe gussa nahi — hairaani hai 💀😹",
        "🙅 Bhai sharam se doob — par us mein bhi tujhe help chahiye shayad 😤🔥",
        "😤 Teri harkat ek lesson hai — dusron ke liye kya nahi karna chahiye 💀😂",
        "🙅 Beta teri yeh sab dekh ke khud bhi tujhse door rehna chahta hoon 😤😹",
        "😤 Yeh gaaliyaan nahi — sirf reality check hai 💀🔥",
        "🙅 Bhai sharam tab aati hai jab insaan mein insaniyat hoti hai 😤😂",
        "😤 Tu ek example bana diya khud ko — negative example 💀😹",
        "🙅 Beta tujhe ek baar ruk ke soochna chahiye tha — nahi soocha 😤🔥",
        "😤 Yeh sab karke tu yahan hai — aur sochta hai main galat hoon? 💀😂",
        "🙅 Bhai itna toh bata — tujhe kaisa feel hota hai yeh sab karne ke baad 😤😹",
        "😤 Tu sharminda nahi — tujhe sharminda feel karna chahiye 💀🔥",
        "🙅 Beta yeh rasta galat hai — abhi bhi change ho sakta hai 😤😂",
        "😤 Yeh sab khud se bura nahi tha — tu tha 💀😹",
        "🙅 Bhai teri harkaton ka real world impact sun — sab tujhse dur hain 😤🔥",
        "😤 Tu soch raha hai main overreact kar raha hoon — par tujhe hisaab hoga 💀😂",
        "🙅 Beta tujhe pata hai tu kya kar raha hai — aur phir bhi kar raha hai 😤😹",
        "😤 Yeh sharm ki baat hai — aur tujhe realize karna chahiye 💀🔥",
        "🙅 Bhai tujhe mirror mein dekhna chahiye — ek baar 😤😂",
        "😤 Tu itna bura nahi hai — par yeh kaam bura tha 💀😹",
        "🙅 Beta sharam isliye nahi aati — kyunki tu sochta nahi consequences ke baare mein 😤🔥",
        "😤 Yeh moment tera lowest point hai — aur abhi bhi jaag sakta hai 💀😂",
        "🙅 Bhai aaj ek kaam kar — sharminda ho aur badal — bas itna chahiye 😤😎",
    ]

    fire_list = [
        "🔥 FIRE MODE — teri sab cheez jal rahi hai 😈⚡",
        "🔥🔥 Double fire — tujhe bachaane ka option nahi 💀😂",
        "🔥 Teri har baat pe fire respond karenge — ready? 😈⚡",
        "🔥 Bhai FIRE unleashed — tujhe pata bhi nahi kya aaya 💀😂",
        "🔥 Fire level 10 — teri poori existence threatened 😈🌪️",
        "🔥 Beta teri baatein fire se nahi — mere se jali 💀😂",
        "🔥 FIRE STORM — teri location traced — figuratively 😈⚡",
        "🔥 Bhai mere fire pe paani mat daal — gasoline hai 💀🔥",
        "🔥 Teri baat pe FIRE response — tu ready tha? 😂😈",
        "🔥 Beta ek cheez tujhe batata hoon — yeh fire hai — bhaag ja 💀⚡",
        "🔥 FIRE DROP — teri sab baatein ash ho gayi 😈😂",
        "🔥 Bhai fire mein kaun jata hai? Tu gaya — khud 💀🔥",
        "🔥 Tera attitude fire pe throw kiya — zyada jala 😈⚡",
        "🔥 Beta fire mode mein teri har line ka jawab ek blaze 💀😂",
        "🔥 FIRE BURST — teri defense melt ho gayi 😈🌪️",
        "🔥 Bhai jab fire aata hai toh sab hatate hain — tujhe bhi hatna chahiye 💀😂",
        "🔥 Fire aaya — teri side pe — enjoy karo 😈⚡",
        "🔥 Beta fire nahi karunga — already ka gaya 💀😂",
        "🔥 BLAZING RESPONSE — teri cheez pe aag — already 😈🔥",
        "🔥 Bhai teri poori chat fire ke baad debris hai 💀⚡",
        "🔥 Fire level MAXIMUM — teri area evacuated 😈😂",
        "🔥 Beta fire se darr — yeh meri territory hai 💀🔥",
        "🔥 FIRE ATTACK RESPONSE — yeh tera last message tha? Nahi? Theek hai 😈⚡",
        "🔥 Bhai fire mein koi nahi bachta — sab jal jaate hain 💀😂",
        "🔥 Teri ego fire pe rakh di — gone in seconds 😈🔥",
        "🔥 Beta fire drop — tujhe rona mat — khud aaya tha 💀⚡",
        "🔥 FIRE FINISHER — teri poori team aag mein 😈😂",
        "🔥 Bhai mere fire ke saamne tera ice melts instantly 💀🔥",
        "🔥 Fire mode — tera surrender nahi aaya? Interesting 😈⚡",
        "🔥 Beta fire se mujhe dar nahi — main fire hoon 💀😂",
        "🔥 BLAZING FURY — teri existence burning 😈🌪️",
        "🔥 Bhai teri shikayat fire pe rakh di — dissolve ho gayi 💀😂",
        "🔥 Fire response — tujhe ek hi chahiye tha — yeh lo 😈⚡",
        "🔥 Beta mere fire se bach ke gaya toh winner — nahi gaya toh obvious 💀🔥",
        "🔥 FIRE FINALE — teri poori side: ashes 😈😂",
        "🔥 Bhai fire mein aake cool lagta hai — tujhe pata nahi 💀⚡",
        "🔥 Teri har weakness fire pe react karti hai — too many reactions 😈😂",
        "🔥 Beta fire mein aana galat tha — par aaya toh hai 💀🔥",
        "🔥 MEGA FIRE RAID — teri timeline pe aaya — stay 😈⚡",
        "🔥 Bhai fire aur tu — bad combination 💀😂",
        "🔥 Fire mode COMPLETE — teri side nothing remaining 😈🌪️",
        "🔥 Beta fire se pehle socha nahi — ab sochta hai par late hai 💀😂",
        "🔥 FIRE STORM COMPLETE — tujhe mujhse distance rakhni chahiye thi 😈⚡",
        "🔥 Bhai fire mein kabhi koi jeet nahi sakta — tu jeetha? Nahi 💀🔥",
        "🔥 Beta teri baat fire pe: ash 😈😂",
        "🔥 FIRE LEVEL OVER 9000 — teri side zero se bhi neeche 💀⚡",
        "🔥 Bhai fire mein aake puchha kya tha? Bhool gaya — fire ne bhula diya 😈😂",
        "🔥 Fire drop FINAL — teri poori team scattered 💀🔥",
        "🔥 Beta fire se bacha nahi — fire ne tujhe dhundha 😈⚡",
        "🔥 🔥 FIRE OVER — teri side: lesson learned? Hope so 💀😂",
    ]

    devil_list = [
        "😈 DEVIL MODE — yahan woh aaya hai jo tujhe deserve karta hai 🔥💀",
        "😈 Beta main devil nahi — main tera worst nightmare hoon 🔥⚡",
        "😈 Devil raid activate — teri poori timeline disturbed 💀😂",
        "😈 Bhai devil pe hath lagaya — ab bhog 🔥💥",
        "😈 DEVIL FURY — teri sab cheez ek baar mein 💀⚡",
        "😈 Beta devil ke saamne hum sab khiladi hain — tu beginner 🔥😂",
        "😈 DEVIL ATTACK — teri defense devil ke touch se fail 💀😈",
        "😈 Bhai devil mode mein koi safe nahi — tu bhi nahi 🔥⚡",
        "😈 Teri galti — devil ko challenge karna 💀😂",
        "😈 Beta devil ki bhasha — punishment aur reward — tu punishment mein hai 🔥😈",
        "😈 DEVIL LEVEL RAGE — teri poori life on line 💀⚡",
        "😈 Bhai devil se lad ke koi nahi jeeta — tu bhi nahi jeetega 🔥😂",
        "😈 Devil mode — tera sab kuch noted — sab 💀😈",
        "😈 Beta DEVIL FIRE — teri poori duniya burn 🔥⚡",
        "😈 DEVIL RAID COMPLETE — tujhe koi nahi bachayega 💀😂",
        "😈 Bhai devil teri har move pe already plan bana chuka 🔥😈",
        "😈 Devil mode — tera future bleak — teri choice thi 💀⚡",
        "😈 Beta devil ne tujhe select kiya — koi bada reason hoga 🔥😂",
        "😈 DEVIL STORM — teri poori squad disbanded 💀😈",
        "😈 Bhai devil ke game mein tera turn tha — abhi mera 🔥⚡",
        "😈 Devil raid engage — now teri responsibility 💀😂",
        "😈 Beta devil level punishment — tujhse tune karaya tha 🔥😈",
        "😈 DEVIL ZONE — nikal ja nahi toh devil ka guest ban 💀⚡",
        "😈 Bhai devil hamesha sunta hai — teri bhi sun li 🔥😂",
        "😈 Devil mode ACTIVATED — teri poori timeline hijacked 💀😈",
        "😈 Beta devil ke saamne sirf ek option — respect ya suffer 🔥⚡",
        "😈 DEVIL FINAL BLOW — teri defense completely gone 💀😂",
        "😈 Bhai devil ne decide kiya — teri loss is inevitable 🔥😈",
        "😈 Devil mein aake dekha — tu deserving nahi tha challenge ka 💀⚡",
        "😈 Beta DEVIL RAIN — teri har cheez soaked in fire 🔥😂",
        "😈 DEVIL vs YOU — spoiler: devil wins 💀😈",
        "😈 Bhai devil ke saamne teri prayers bhi kaam nahi aate 🔥⚡",
        "😈 Devil mode — teri weak spots identified — attack 💀😂",
        "😈 Beta devil ki nazar se tu nahi chhupta 🔥😈",
        "😈 DEVIL JUDGMENT — teri poori history reviewed — verdict: guilty 💀⚡",
        "😈 Bhai devil ki duniya mein tu tourist tha — time up 🔥😂",
        "😈 Devil fury — tere steps already tracked hain 💀😈",
        "😈 Beta DEVIL COUNTER — teri har move ka counter ready tha 🔥⚡",
        "😈 DEVIL FINISH — teri game over — my game continues 💀😂",
        "😈 Bhai devil mode se nikalna — tujhe option nahi 🔥😈",
        "😈 Devil attack — teri soul targeted — figuratively 💀⚡",
        "😈 Beta devil ne kaha — teri aukat nahi — aur devil galat nahi hota 🔥😂",
        "😈 DEVIL STORM OVER — teri side: scorched earth 💀😈",
        "😈 Bhai devil ke rules simple hain — tu follow nahi kiya 🔥⚡",
        "😈 Devil raid — teri position compromised — retreat 💀😂",
        "😈 Beta DEVIL mein aake rota mat — khud aaya tha 🔥😈",
        "😈 DEVIL WAVE — teri har defence erased 💀⚡",
        "😈 Bhai devil ka favorite — log jo khud ko smart samjhte hain — tu 🔥😂",
        "😈 Devil mode DONE — check teri condition 💀😈",
        "😈 Beta devil ne aaj tujhe yaadgaar bana diya — wrong reasons se 🔥⚡",
    ]

    karma_list = [
        "☯️ Karma aaya — teri sab harkat ka hisaab ho raha hai 🔥💀",
        "☯️ Beta karma kisi ki nahi sunta — teri bhi nahi 😂⚡",
        "☯️ KARMA STRIKE — tune jo kiya woh teri taraf wapas aaya 🔥😈",
        "☯️ Bhai karma judge nahi karta — deliver karta hai 💀😂",
        "☯️ Karma mode activate — teri sab galtiyan wapas aa rahi hain 🔥⚡",
        "☯️ Beta karma tujhe bhool nahi gaya — yaad rakha tha 😂💀",
        "☯️ KARMA DELIVERY — teri harkat ka package arrive ho gaya 🔥😈",
        "☯️ Bhai karma se koi nahi bachta — tu bhi nahi bachega 💀⚡",
        "☯️ Karma tujhe dhundh raha tha — dhundh liya 🔥😂",
        "☯️ Beta karma aata hai jab expect nahi karte — sun le 😂💀",
        "☯️ KARMA HITS DIFFERENT — teri sab cheez wapas 🔥⚡",
        "☯️ Bhai karma teri priority nahi thi — karma mein tu priority hai 😂💀",
        "☯️ Karma cycle complete — tune jo kiya tune hi bhoga 🔥😈",
        "☯️ Beta karma slow hota hai par sure hota hai — yeh sure tha 💀⚡",
        "☯️ KARMA CALL — teri line pe aa gaya 🔥😂",
        "☯️ Bhai karma mein koi error nahi — teri galti recorded thi 😂💀",
        "☯️ Karma teri taraf waapis — enjoy 🔥⚡",
        "☯️ Beta karma tera address jaanta tha 😂💀",
        "☯️ KARMA FINAL — teri poori account balance zero 🔥😈",
        "☯️ Bhai karma se lad nahi sakte — tu chhupa nahi karma se 💀⚡",
        "☯️ Karma strike — tune deserve kiya — mila 🔥😂",
        "☯️ Beta karma ko excuse nahi deta — sirf result deta hai 😂💀",
        "☯️ KARMA STORM — teri sab beizzati aaj ekatha aayi 🔥⚡",
        "☯️ Bhai karma tujhse behtar account maintain karta hai 😂💀",
        "☯️ Karma mein tera account — overdraft mein hai 🔥😈",
        "☯️ Beta karma ki speed teri speed se faster hai 💀⚡",
        "☯️ KARMA BLAST — teri sab cheezon ka hisaab 🔥😂",
        "☯️ Bhai karma ko pata tha tune kya kiya — sab record mein hai 😂💀",
        "☯️ Karma kisi pe bhi nahi rulta — teri bhi nahi 🔥⚡",
        "☯️ Beta karma tera future nahi — karma tera present hai 😂💀",
        "☯️ KARMA INVOICE — teri sab galtiyon ka bill aa gaya 🔥😈",
        "☯️ Bhai karma mein koi discount nahi milta — full price pay 💀⚡",
        "☯️ Karma delivered — tune jo bheja wahi mila 🔥😂",
        "☯️ Beta karma tujhse kisi ki nahi sunta — seedha deliver karta hai 😂💀",
        "☯️ KARMA FULL CIRCLE — teri sab harkat ghumke teri hi taraf aayi 🔥⚡",
        "☯️ Bhai karma teri taraf — aur tu prepared nahi tha 😂💀",
        "☯️ Karma hit kiya — tujhe pata tha aayega — aaya 🔥😈",
        "☯️ Beta karma mein interest bhi hota hai — tera compound ho gaya 💀⚡",
        "☯️ KARMA COMPLETE — lesson mila? 🔥😂",
        "☯️ Bhai karma ne tujhe select kiya — deservingly 😂💀",
        "☯️ Karma tujhe yaad dila raha hai — tune kya kiya tha 🔥⚡",
        "☯️ Beta karma ki awaaz nahi hoti — par result loud hota hai 😂💀",
        "☯️ KARMA RESPONSE — teri har cheez ka seedha jawab 🔥😈",
        "☯️ Bhai karma ki list mein tu first position pe tha 💀⚡",
        "☯️ Karma tujhe bhool nahi gaya — teri galti note thi 🔥😂",
        "☯️ Beta karma aur tu — aaj inka meetup schedule tha 😂💀",
        "☯️ KARMA WRAP UP — teri life lesson: yeh tha 🔥⚡",
        "☯️ Bhai karma ne apna kaam kiya — efficient tha 😂💀",
        "☯️ Karma strike final — teri sab cheez balanced ho gayi — zero pe 🔥😈",
        "☯️ Beta karma yaad rakhna — abhi bhi teri account open hai ☯️😂",
    ]

    ghost_list = [
        "👻 GHOST MODE — tujhe pata bhi nahi kab aaya 😂💀",
        "👻 Beta ghost ki tarah silently teri sab cheez note kar liya 🔥😈",
        "👻 GHOST RAID — teri timeline pe tha tu socha nahi 💀⚡",
        "👻 Bhai ghost mode mein sab kuch possible hai — teri nazar se baahar 😂🔥",
        "👻 Ghost strike — teri sab cheez read — tujhe pata nahi 💀😈",
        "👻 Beta ghost se koi nahi chhupta — teri history meri hai 😂⚡",
        "👻 GHOST ATTACK — teri weaknesses identified without you knowing 🔥💀",
        "👻 Bhai ghost mein aaya — teri sab dekha — wapas aaya 😈😂",
        "👻 Ghost mode — tu sooye hua tha main active tha 💀⚡",
        "👻 Beta ghost ki tarah aa aur ja — par lesson chhod 🔥😂",
        "👻 GHOST OBSERVATION — teri sab cheez monitored 💀😈",
        "👻 Bhai ghost ne sab dekha — teri harkaten recorded 😂⚡",
        "👻 Ghost strike final — teri poori plan exposed 🔥💀",
        "👻 Beta ghost mode mein tera koi secret nahi raha 😈😂",
        "👻 GHOST RAID COMPLETE — teri sab cheez ghost ke paas 💀⚡",
        "👻 Bhai ghost tujhse zyada mobile tha 🔥😂",
        "👻 Ghost ne teri sab sun li — seedha sun li 💀😈",
        "👻 Beta ghost se koi hidden nahi — tera bhi nahi 😂⚡",
        "👻 GHOST FINAL — teri sab expose ho gayi silently 🔥💀",
        "👻 Bhai ghost mein ek power hai — invisibility — jo tujhpe use ki 😈😂",
        "👻 Ghost mode — teri baat sun ke ghost ne judge kiya 💀⚡",
        "👻 Beta ghost aaya aur teri sab cheez log kar ke gaya 🔥😂",
        "👻 GHOST PRESENCE — tu feel kar sakta hai par dekh nahi sakta 💀😈",
        "👻 Bhai ghost ne tujhe 24/7 observe kiya — teri knowledge ke bina 😂⚡",
        "👻 Ghost strike — teri poori defense bypass ho gayi 🔥💀",
        "👻 Beta ghost report taiyaar hai — teri life ka full audit 😈😂",
        "👻 GHOST RETURN — wapas aaya — aur tujhe leke ja raha hoon 💀⚡",
        "👻 Bhai ghost ki tarah — nazar nahi aaya par haraaya zaroor 🔥😂",
        "👻 Ghost mode — teri conversations screenshotted 💀😈",
        "👻 Beta ghost ke saamne teri poori timeline open book 😂⚡",
        "👻 GHOST DAMAGE — tujhe pata bhi nahi kya hua 🔥💀",
        "👻 Bhai ghost ki speed mein teri poori history read 😈😂",
        "👻 Ghost raid — teri sab log ki gayi 💀⚡",
        "👻 Beta ghost tujhse pehle arrive kiya — always 🔥😂",
        "👻 GHOST NETWORK — teri sab moves already anticipated 💀😈",
        "👻 Bhai ghost ne tujhe dost banaya — tujhe pata hi nahi chala 😂⚡",
        "👻 Ghost mode complete — teri sab information gathered 🔥💀",
        "👻 Beta ghost tera shadow tha — teri knowledge ke bina 😈😂",
        "👻 GHOST INTEL — teri ek bhi move safe nahi thi 💀⚡",
        "👻 Bhai ghost ke saamne tera defense transparent tha 🔥😂",
        "👻 Ghost final message — sun le — yeh tha 💀😈",
        "👻 Beta ghost raid done — teri sab cheez: compromised 😂⚡",
        "👻 GHOST VANISH — gaya aur teri legacy chhod gaya — for the wrong reasons 🔥💀",
        "👻 Bhai ghost teri poori situation samajh gaya — tu abhi samjha 😈😂",
        "👻 Ghost mode — tera sab kuch pehle se predict tha 💀⚡",
        "👻 Beta ghost ki tarah observe kiya — teri sab weakness note 🔥😂",
        "👻 GHOST COMPLETE — teri poori profile analyzed — done 💀😈",
        "👻 Bhai ghost ne tujhe deliver kiya — message: tu predictable hai 😂⚡",
        "👻 Ghost raid FINAL — enjoy the lesson 🔥💀",
        "👻 Beta ghost ne sun liya — ab teri galti public domain mein hai 😈😂",
    ]

    legend_list = [
        "👑 LEGEND MODE — tujhse baat karna mera time nahi — par exception 😎🔥",
        "👑 Beta legend ne tujhe notice kiya — galat kaam ke liye 😂💀",
        "👑 LEGEND STRIKE — teri poori position legend ne handle ki 😎⚡",
        "👑 Bhai legend ke saamne teri sab bakwaas — sirf noise 🔥😂",
        "👑 Legend mode — main aaya — tu already haara 😎💀",
        "👑 Beta LEGEND level pe tu exist nahi karta — par exception de raha hoon 😂⚡",
        "👑 LEGEND RAID — teri timeline pe aaya — yaad rahega 🔥😎",
        "👑 Bhai legend se lad ke jeeta kaun? Koi nahi — tu bhi nahi 💀😂",
        "👑 Legend status — tujhe challenge accept nahi karna tha 😎⚡",
        "👑 Beta legend aaya — teri poori squad bhaag gayi 🔥💀",
        "👑 LEGEND BLOW — teri defense — gone 😎😂",
        "👑 Bhai legend ki speed se teri situation analyze ho gayi 🔥⚡",
        "👑 Legend mode on — teri har move already countered 😎💀",
        "👑 Beta LEGEND ka ek rule — woh kabhi lose nahi karta 😂⚡",
        "👑 LEGEND FINISH — teri poori war — legend ki morning exercise thi 🔥😎",
        "👑 Bhai legend ko insult karna — teri worst idea thi 💀😂",
        "👑 Legend ne tujhe acknowledge kiya — that's it — teri privilege khatam 😎⚡",
        "👑 Beta legend ki taraf se — teri sab cheez ka answer: nahi 🔥💀",
        "👑 LEGEND STRIKE FINAL — teri poori side — taken care of 😎😂",
        "👑 Bhai legend se panga — teri bravery ya foolishness? 💀⚡",
        "👑 Legend mode — teri sab galtiyan noted — teri 🔥😎",
        "👑 Beta LEGEND ki baat sun — yeh advice nahi — judgment hai 😂💀",
        "👑 LEGEND RAID COMPLETE — tu ek example ban gaya — negative wala 😎⚡",
        "👑 Bhai legend ke saamne baat karte waqt soch lena tha 🔥😂",
        "👑 Legend status confirm — teri side: unconfirmed 💀😎",
        "👑 Beta LEGEND ne tujhpe ek second spend kiya — teri lucky day thi 😂⚡",
        "👑 LEGEND FURY — teri har defense melt 🔥😎",
        "👑 Bhai legend ka level dekh — aur apna dekh — gap samjha? 💀😂",
        "👑 Legend mode final — teri sab cheez — reviewed — rejected 😎⚡",
        "👑 Beta LEGEND mein sirf ek rule — excellence — teri cheez nahi 🔥💀",
        "👑 LEGEND FINAL MESSAGE — yahi tha — good luck 😎😂",
        "👑 Bhai legend se lad ke teri position — worse than before 💀⚡",
        "👑 Legend raid final wave — teri sab gone 🔥😎",
        "👑 Beta LEGEND ki mercy — tujhe yahan tak aane diya — bas 😂💀",
        "👑 LEGEND COMPLETE — teri story: cautionary tale ban gayi 😎⚡",
        "👑 Bhai legend ne tujhe ek lesson diya — free of charge 🔥😂",
        "👑 Legend mode — tu ek footnote hai meri history mein 💀😎",
        "👑 Beta LEGEND ka visit — teri timeline ka highlight — wrong reasons se 😂⚡",
        "👑 LEGEND OVER — teri war: history — meri war: ongoing 🔥😎",
        "👑 Bhai legend ke saamne tera struggle cute lagta hai 💀😂",
        "👑 Legend mode engaged — tujhe pata bhi nahi kab hua 😎⚡",
        "👑 Beta LEGEND ne tujhe prove kiya — teri theory wrong thi 🔥💀",
        "👑 LEGEND VERDICT — teri poori existence: could do better 😎😂",
        "👑 Bhai legend se seekh — agar seekh sakta hai 💀⚡",
        "👑 Legend raid — teri poori team acknowledged defeat 🔥😎",
        "👑 Beta LEGEND tujhe seriously leta nahi — par professionally handle karta hai 😂💀",
        "👑 LEGEND STAMP — teri chat: closed — meri: continuing 😎⚡",
        "👑 Bhai legend ne tujhe ek cheez diya — perspective — use kar 🔥😂",
        "👑 Legend mode OVER — teri loss: recorded — teri lesson: pending 💀😎",
        "👑 Beta LEGEND ki baat seedhi — tu meri league mein nahi — abhi 😂⚡",
    ]

    doom_list = [
        "💀 DOOM activated — teri poori existence on countdown 🔥😈",
        "💀 Beta doom aaya — tera timer start ho gaya 😂⚡",
        "💀 DOOM STRIKE — teri poori defense wiped 🔥😈",
        "💀 Bhai doom se koi nahi bachta — teri bhi date aane wali thi 😂💀",
        "💀 Doom mode — teri sab cheez: scheduled for deletion 🔥⚡",
        "💀 Beta doom tera waqt dekh ke aaya — perfect timing 😂😈",
        "💀 DOOM RAID — teri poori squad: doomed 🔥💀",
        "💀 Bhai doom pe haath lagaya — yeh result expect karna chahiye tha 😂⚡",
        "💀 Doom finale — teri poori story: ended 🔥😈",
        "💀 Beta doom ki awaaz sunna nahi chahte log — teri aa gayi 😂💀",
        "💀 DOOM COMPLETE — teri sab cheez: finished 🔥⚡",
        "💀 Bhai doom tujhse pehle plan kar ke aaya tha 😂😈",
        "💀 Doom level CRITICAL — teri situation: hopeless 🔥💀",
        "💀 Beta doom ne tujhe select kiya — teri achievement nahi 😂⚡",
        "💀 DOOM COUNTDOWN — teri sab cheez: 3... 2... 1... done 🔥😈",
        "💀 Bhai doom mein rasta ek hi hota hai — neeche 😂💀",
        "💀 Doom activated — teri poori future: uncertain 🔥⚡",
        "💀 Beta doom ki language — teri samajh nahi aati — result aata hai 😂😈",
        "💀 DOOM FINAL — teri poori team: gone 🔥💀",
        "💀 Bhai doom aur tu — aaj ka meetup tera worst tha 😂⚡",
        "💀 Doom mode — tera har step: tracked 🔥😈",
        "💀 Beta doom ne teri position: permanent zero confirm ki 😂💀",
        "💀 DOOM RAIN — teri har cheez: destroyed 🔥⚡",
        "💀 Bhai doom mein mercy nahi hoti — teri request: denied 😂😈",
        "💀 Doom strike — teri sab galtiyan: collected 🔥💀",
        "💀 Beta doom clock — teri ticking: started 😂⚡",
        "💀 DOOM WAVE — teri poori defense: overwhelmed 🔥😈",
        "💀 Bhai doom ki speed mein teri situation resolve ho gayi — badly 😂💀",
        "💀 Doom verdict — teri case: closed — against you 🔥⚡",
        "💀 Beta doom se pehle sun: teri galti — doom aaya 😂😈",
        "💀 DOOM ARRIVAL — teri poori day ruined 🔥💀",
        "💀 Bhai doom ne tujhe apna project bana liya 😂⚡",
        "💀 Doom mode final — teri sab cheez: ash 🔥😈",
        "💀 Beta doom ki ek khasiyat — woh aata zaroor hai 😂💀",
        "💀 DOOM EXECUTION — teri poori plan: failed 🔥⚡",
        "💀 Bhai doom tera number leke aaya tha — mila 😂😈",
        "💀 Doom level MAX — teri recovery: impossible 🔥💀",
        "💀 Beta doom ki taraf se ek gift — teri haari 😂⚡",
        "💀 DOOM COMPLETE CYCLE — teri poori existence reset 🔥😈",
        "💀 Bhai doom tujhse better hai — wait nahi karta 😂💀",
        "💀 Doom mode — teri sab cheez: compromised 🔥⚡",
        "💀 Beta DOOM aur tu — tujhe jeetna tha par doom ka hi naam hai 😂😈",
        "💀 DOOM FINAL WAVE — teri sab: erased 🔥💀",
        "💀 Bhai doom ne tujhe memorable bana diya — galat reasons se 😂⚡",
        "💀 Doom activated final time — teri countdown: zero 🔥😈",
        "💀 Beta DOOM se seekhna tha — tujhe nahi tha pata ab hai 😂💀",
        "💀 DOOM OVER — teri side: collapsed — mine: standing 🔥⚡",
        "💀 Bhai doom ne tera chapter likh diya — R.I.P. chapter 😂😈",
        "💀 Doom final message — tujhe yaad rahega — sahi reasons se nahi 🔥💀",
        "💀 Beta DOOM complete — check teri condition — yahi tha 😂⚡",
    ]

    nuke_list = [
        "☢️ NUKE LAUNCHED — teri poori existence vapas nahi aayegi 💀🔥",
        "💥 Nuke strike — teri sab cheez radiated hai 😈⚡",
        "☢️ Beta nuke aaya — tera timer ab 0 pe hai 😂💀",
        "💥 NUKE FURY — teri poori timeline erased 🔥😈",
        "☢️ Nuke mode — teri har move fail hogi 💀⚡",
        "💥 Beta nuke se koi nahi bachta — tu bhi nahi 😂😈",
        "☢️ NUKE IMPACT — teri sab cheez dust 💀🔥",
        "💥 Bhai nuke ka effect — teri maa bhi nahi pehchanegi 😂⚡",
        "☢️ Nuke activated — teri har reply waste hai 💀😈",
        "💥 Beta nuke ki speed — tu soch bhi nahi sakta 😂🔥",
        "☢️ NUKE RAIN — teri chat mein sab khatam 💀⚡",
        "💥 Bhai nuke mein ek hi rule — teri haari 😈😂",
        "☢️ Nuke over — teri side zero pe 💀🔥",
        "💥 Beta nuke ka proof — tu ab yahan nahi 😂⚡",
        "☢️ NUKE STRIKE — teri poori squad vaporized 💀😈",
        "💥 Bhai nuke pe haath lagaya — ab koi nahi bachega 😂🔥",
        "☢️ Nuke mode — teri sab expectations destroyed 💀⚡",
        "💥 Beta nuke aur tu — dono mein farak hai 😈😂",
        "☢️ NUKE FINAL — teri war khatam 💀🔥",
        "💥 Bhai nuke ne tujhe lesson diya — permanent 😂⚡",
        "☢️ Nuke complete — teri koi baat nahi 💀😈",
        "💥 Beta nuke ki awaaz — teri baaton se louder 😂🔥",
        "☢️ NUKE BLAST — teri har cheez wiped 💀⚡",
        "💥 Bhai nuke ne tujhe reset kiya — version 0 😈😂",
        "☢️ Nuke attack — teri koi strategy kaam nahi 💀🔥",
        "💥 Beta nuke se pehle bolna tha — ab nahi 😂⚡",
        "☢️ NUKE OVERDRIVE — teri poori timeline corrupted 💀😈",
        "💥 Bhai nuke ka result — teri side gone 😂🔥",
        "☢️ Nuke strike final — teri maa bhi roegi 💀⚡",
        "💥 Beta nuke aur main — dono same nahi 😈😂",
        "☢️ NUKE MODE ON — teri sab cheez 0 pe 💀🔥",
        "💥 Bhai nuke se darr — par ab der hai 😂⚡",
        "☢️ Nuke rain complete — teri koi recovery nahi 💀😈",
        "💥 Beta nuke ki guarantee — teri haari 😂🔥",
        "☢️ NUKE POWER — teri poori squad silent 💀⚡",
        "💥 Bhai nuke ne tujhe target kiya — reason nahi 😈😂",
        "☢️ Nuke verdict — teri case closed 💀🔥",
        "💥 Beta nuke aaya aur gaya — tu nahi gaya 😂⚡",
        "☢️ NUKE DAMAGE — teri profile 0 pe 💀😈",
        "💥 Bhai nuke ka impact — teri soch se bada 😂🔥",
        "☢️ Nuke finish — teri side: nothing 💀⚡",
        "💥 Beta nuke ne tujhe replace kiya — khud 😈😂",
        "☢️ NUKE END — teri war khatam teri taraf se 💀🔥",
        "💥 Bhai nuke ka ek rule — tu nahi bachega 😂⚡",
        "☢️ Nuke final wave — teri har defense fail 💀😈",
        "💥 Beta nuke ne sab khatam kiya — tera bhi 😂🔥",
        "☢️ NUKE COMPLETE — teri existence erased 💀⚡",
        "💥 Bhai nuke se seekh — tu abhi bhi nahi 😈😂",
        "☢️ Nuke over — teri side gone forever 💀🔥",
        "💥 Beta nuke ki taraf se — bye bye 😂⚡",
    ]

    storm_list = [
        "🌪️ STORM MODE — teri poori chat mein andhi 😈🔥",
        "⚡ Storm attack — teri har baat blown away 💀😂",
        "🌪️ Beta storm aaya — tera sab kuch scattered 😈⚡",
        "⚡ STORM FURY — teri poori timeline broken 🔥💀",
        "🌪️ Storm mode — teri koi move nahi chalegi 😂😈",
        "⚡ Beta storm se koi nahi bachta — teri bhi nahi 💀🔥",
        "🌪️ STORM IMPACT — teri sab cheez air mein 😈⚡",
        "⚡ Bhai storm ka effect — teri maa bhi shock mein 😂💀",
        "🌪️ Storm activated — teri har reply waste 🔥😈",
        "⚡ Beta storm ki speed — tu soch bhi nahi sakta 💀😂",
        "🌪️ STORM RAIN — teri chat mein sab kuch flying 😈⚡",
        "⚡ Bhai storm mein ek hi rule — teri haari 🔥😂",
        "🌪️ Storm over — teri side zero pe 💀😈",
        "⚡ Beta storm ka proof — tu ab yahan nahi 😂🔥",
        "🌪️ STORM STRIKE — teri poori squad blown 😈⚡",
        "⚡ Bhai storm pe haath lagaya — ab koi nahi bachega 💀😂",
        "🌪️ Storm mode — teri sab expectations destroyed 🔥😈",
        "⚡ Beta storm aur tu — dono mein farak hai 💀😂",
        "🌪️ STORM FINAL — teri war khatam 😈🔥",
        "⚡ Bhai storm ne tujhe lesson diya — permanent 💀😂",
        "🌪️ Storm complete — teri koi baat nahi 🔥😈",
        "⚡ Beta storm ki awaaz — teri baaton se louder 💀😂",
        "🌪️ STORM BLAST — teri har cheez wiped 😈🔥",
        "⚡ Bhai storm ne tujhe reset kiya — version 0 💀😂",
        "🌪️ Storm attack — teri koi strategy kaam nahi 🔥😈",
        "⚡ Beta storm se pehle bolna tha — ab nahi 💀😂",
        "🌪️ STORM OVERDRIVE — teri poori timeline corrupted 😈🔥",
        "⚡ Bhai storm ka result — teri side gone 💀😂",
        "🌪️ Storm strike final — teri maa bhi roegi 🔥😈",
        "⚡ Beta storm aur main — dono same nahi 💀😂",
        "🌪️ STORM MODE ON — teri sab cheez 0 pe 😈🔥",
        "⚡ Bhai storm se darr — par ab der hai 💀😂",
        "🌪️ Storm rain complete — teri koi recovery nahi 🔥😈",
        "⚡ Beta storm ki guarantee — teri haari 💀😂",
        "🌪️ STORM POWER — teri poori squad silent 😈🔥",
        "⚡ Bhai storm ne tujhe target kiya — reason nahi 💀😂",
        "🌪️ Storm verdict — teri case closed 🔥😈",
        "⚡ Beta storm aaya aur gaya — tu nahi gaya 💀😂",
        "🌪️ STORM DAMAGE — teri profile 0 pe 😈🔥",
        "⚡ Bhai storm ka impact — teri soch se bada 💀😂",
        "🌪️ Storm finish — teri side: nothing 🔥😈",
        "⚡ Beta storm ne tujhe replace kiya — khud 💀😂",
        "🌪️ STORM END — teri war khatam teri taraf se 😈🔥",
        "⚡ Bhai storm ka ek rule — tu nahi bachega 💀😂",
        "🌪️ Storm final wave — teri har defense fail 🔥😈",
        "⚡ Beta storm ne sab khatam kiya — tera bhi 💀😂",
        "🌪️ STORM COMPLETE — teri existence erased 😈🔥",
        "⚡ Bhai storm se seekh — tu abhi bhi nahi 💀😂",
        "🌪️ Storm over — teri side gone forever 🔥😈",
        "⚡ Beta storm ki taraf se — bye bye 💀😂",
    ]

    blizzard_list = [
        "❄️ BLIZZARD MODE — teri poori chat frozen 😈🔥",
        "🧊 Blizzard attack — teri har baat ice mein 💀😂",
        "❄️ Beta blizzard aaya — tera sab kuch jam 😈⚡",
        "🧊 BLIZZARD FURY — teri poori timeline blocked 🔥💀",
        "❄️ Blizzard mode — teri koi move nahi chalegi 😂😈",
        "🧊 Beta blizzard se koi nahi bachta — teri bhi nahi 💀🔥",
        "❄️ BLIZZARD IMPACT — teri sab cheez frozen 😈⚡",
        "🧊 Bhai blizzard ka effect — teri maa bhi thandi 💀😂",
        "❄️ Blizzard activated — teri har reply waste 🔥😈",
        "🧊 Beta blizzard ki speed — tu soch bhi nahi sakta 💀😂",
        "❄️ BLIZZARD RAIN — teri chat mein sab kuch jam 😈⚡",
        "🧊 Bhai blizzard mein ek hi rule — teri haari 🔥😂",
        "❄️ Blizzard over — teri side zero pe 💀😈",
        "🧊 Beta blizzard ka proof — tu ab yahan nahi 😂🔥",
        "❄️ BLIZZARD STRIKE — teri poori squad frozen 😈⚡",
        "🧊 Bhai blizzard pe haath lagaya — ab koi nahi bachega 💀😂",
        "❄️ Blizzard mode — teri sab expectations destroyed 🔥😈",
        "🧊 Beta blizzard aur tu — dono mein farak hai 💀😂",
        "❄️ BLIZZARD FINAL — teri war khatam 😈🔥",
        "🧊 Bhai blizzard ne tujhe lesson diya — permanent 💀😂",
        "❄️ Blizzard complete — teri koi baat nahi 🔥😈",
        "🧊 Beta blizzard ki awaaz — teri baaton se louder 💀😂",
        "❄️ BLIZZARD BLAST — teri har cheez wiped 😈🔥",
        "🧊 Bhai blizzard ne tujhe reset kiya — version 0 💀😂",
        "❄️ Blizzard attack — teri koi strategy kaam nahi 🔥😈",
        "🧊 Beta blizzard se pehle bolna tha — ab nahi 💀😂",
        "❄️ BLIZZARD OVERDRIVE — teri poori timeline corrupted 😈🔥",
        "🧊 Bhai blizzard ka result — teri side gone 💀😂",
        "❄️ Blizzard strike final — teri maa bhi roegi 🔥😈",
        "🧊 Beta blizzard aur main — dono same nahi 💀😂",
        "❄️ BLIZZARD MODE ON — teri sab cheez 0 pe 😈🔥",
        "🧊 Bhai blizzard se darr — par ab der hai 💀😂",
        "❄️ Blizzard rain complete — teri koi recovery nahi 🔥😈",
        "🧊 Beta blizzard ki guarantee — teri haari 💀😂",
        "❄️ BLIZZARD POWER — teri poori squad silent 😈🔥",
        "🧊 Bhai blizzard ne tujhe target kiya — reason nahi 💀😂",
        "❄️ Blizzard verdict — teri case closed 🔥😈",
        "🧊 Beta blizzard aaya aur gaya — tu nahi gaya 💀😂",
        "❄️ BLIZZARD DAMAGE — teri profile 0 pe 😈🔥",
        "🧊 Bhai blizzard ka impact — teri soch se bada 💀😂",
        "❄️ Blizzard finish — teri side: nothing 🔥😈",
        "🧊 Beta blizzard ne tujhe replace kiya — khud 💀😂",
        "❄️ BLIZZARD END — teri war khatam teri taraf se 😈🔥",
        "🧊 Bhai blizzard ka ek rule — tu nahi bachega 💀😂",
        "❄️ Blizzard final wave — teri har defense fail 🔥😈",
        "🧊 Beta blizzard ne sab khatam kiya — tera bhi 💀😂",
        "❄️ BLIZZARD COMPLETE — teri existence erased 😈🔥",
        "🧊 Bhai blizzard se seekh — tu abhi bhi nahi 💀😂",
        "❄️ Blizzard over — teri side gone forever 🔥😈",
        "🧊 Beta blizzard ki taraf se — bye bye 💀😂",
    ]

    venom_list = [
        "☠️ VENOM MODE — teri poori chat poisonous 😈🔥",
        "🐍 Venom attack — teri har baat toxic 💀😂",
        "☠️ Beta venom aaya — tera sab kuch infected 😈⚡",
        "🐍 VENOM FURY — teri poori timeline corrupted 🔥💀",
        "☠️ Venom mode — teri koi move nahi chalegi 😂😈",
        "🐍 Beta venom se koi nahi bachta — teri bhi nahi 💀🔥",
        "☠️ VENOM IMPACT — teri sab cheez poison 😈⚡",
        "🐍 Bhai venom ka effect — teri maa bhi sick 💀😂",
        "☠️ Venom activated — teri har reply waste 🔥😈",
        "🐍 Beta venom ki speed — tu soch bhi nahi sakta 💀😂",
        "☠️ VENOM RAIN — teri chat mein sab kuch toxic 😈⚡",
        "🐍 Bhai venom mein ek hi rule — teri haari 🔥😂",
        "☠️ Venom over — teri side zero pe 💀😈",
        "🐍 Beta venom ka proof — tu ab yahan nahi 😂🔥",
        "☠️ VENOM STRIKE — teri poori squad poisoned 😈⚡",
        "🐍 Bhai venom pe haath lagaya — ab koi nahi bachega 💀😂",
        "☠️ Venom mode — teri sab expectations destroyed 🔥😈",
        "🐍 Beta venom aur tu — dono mein farak hai 💀😂",
        "☠️ VENOM FINAL — teri war khatam 😈🔥",
        "🐍 Bhai venom ne tujhe lesson diya — permanent 💀😂",
        "☠️ Venom complete — teri koi baat nahi 🔥😈",
        "🐍 Beta venom ki awaaz — teri baaton se louder 💀😂",
        "☠️ VENOM BLAST — teri har cheez wiped 😈🔥",
        "🐍 Bhai venom ne tujhe reset kiya — version 0 💀😂",
        "☠️ Venom attack — teri koi strategy kaam nahi 🔥😈",
        "🐍 Beta venom se pehle bolna tha — ab nahi 💀😂",
        "☠️ VENOM OVERDRIVE — teri poori timeline corrupted 😈🔥",
        "🐍 Bhai venom ka result — teri side gone 💀😂",
        "☠️ Venom strike final — teri maa bhi roegi 🔥😈",
        "🐍 Beta venom aur main — dono same nahi 💀😂",
        "☠️ VENOM MODE ON — teri sab cheez 0 pe 😈🔥",
        "🐍 Bhai venom se darr — par ab der hai 💀😂",
        "☠️ Venom rain complete — teri koi recovery nahi 🔥😈",
        "🐍 Beta venom ki guarantee — teri haari 💀😂",
        "☠️ VENOM POWER — teri poori squad silent 😈🔥",
        "🐍 Bhai venom ne tujhe target kiya — reason nahi 💀😂",
        "☠️ Venom verdict — teri case closed 🔥😈",
        "🐍 Beta venom aaya aur gaya — tu nahi gaya 💀😂",
        "☠️ VENOM DAMAGE — teri profile 0 pe 😈🔥",
        "🐍 Bhai venom ka impact — teri soch se bada 💀😂",
        "☠️ Venom finish — teri side: nothing 🔥😈",
        "🐍 Beta venom ne tujhe replace kiya — khud 💀😂",
        "☠️ VENOM END — teri war khatam teri taraf se 😈🔥",
        "🐍 Bhai venom ka ek rule — tu nahi bachega 💀😂",
        "☠️ Venom final wave — teri har defense fail 🔥😈",
        "🐍 Beta venom ne sab khatam kiya — tera bhi 💀😂",
        "☠️ VENOM COMPLETE — teri existence erased 😈🔥",
        "🐍 Bhai venom se seekh — tu abhi bhi nahi 💀😂",
        "☠️ Venom over — teri side gone forever 🔥😈",
        "🐍 Beta venom ki taraf se — bye bye 💀😂",
    ]

    # ────────────────────────────────────────────────
    #                 JOKE / FUN CONTENT
    # ────────────────────────────────────────────────
    joke_list = [
        "Main apni life mein itna positive hoon... ki blood group bhi B+ hai! 😂",
        "Teacher: Kal absent kyun the? Student: Sir, mujhe bukhar tha. Teacher: Proof? Student: Aaj aa gaya na! 😹",
        "Santa: Main ghar ke bahar khada hun. Banta: Andar aa jao. Santa: Andar wala bhi main hoon! 🤣",
        "Meri girlfriend ne kaha — tujhse better koi nahi. Phir chali gayi. Better koi mila hoga shayad 😂",
        "Doctor: Patient ko hawa ki zaroorat hai. Nurse: Kya karein? Doctor: Fan on karo. Nurse: Ceiling se pakad ke? 😹",
        "Ghar mein sabse zyada kaam mera — internet chalaana! 😂",
        "Padhai karo beta future bright hoga. Maine padhi — future gaya andhera mein. Lying wasn't their first language 🤣",
        "Wo bolti hai 'I need space' — main bola ठीक है, NASA se contact karo! 😂",
    ]

    riddle_list = [
        "Kya cheez hai jo khata hai par pet nahi hota? — Aag (Fire) 🔥",
        "Woh kaunsi cheez hai jo bolta hai 'Main aaya' par nahi aata? — Kal (Tomorrow) ⏰",
        "Jitna zyada liya jaaye utna chhota hota hai — kya? — Ek gaddha (hole in the ground) 🕳️",
        "Mere paas aankhein hain par dekh nahi sakta — kya hoon main? — Sooee (needle) 🧵",
        "Vo kya cheez hai jo haath se chhoone pe bhi nahi lagti? — Khoobsoorti! 😄",
    ]

    fact_list = [
        "🧠 Insaan ka dimag 75% paani se bana hai!",
        "🐙 Octopus ke teen dil hote hain!",
        "🌙 Chand par mobile signal nahi hai — par WiFi aata hai ek satellite se! (Future plan 😂)",
        "🍯 Sahi tarike se rakha hua honey kabhi kharab nahi hota!",
        "⚡ Bijli ka ek bolt 5 times zyada garam hota hai sun ki surface se!",
        "🦈 Shark insaan se zyada purana hai — dinasors se bhi pehle!",
        "👁️ Insaan ki aankh 10 million rangon ko differentiate kar sakti hai!",
        "🐝 Ek machhar ek second mein 600 baar apne pankh hilata hai!",
    ]

    truth_list = [
        "Sach bolo — last baar kab jhooth bola tha? 🤥",
        "Teri life ka sabse bada secret kya hai jo kisi ko nahi pata? 🤫",
        "Kisi pe crush tha jo ab dost hai? 😳",
        "Kabhi kisi ki baat repeat ki thi jo confidence mein batai gayi thi? 😬",
        "Woh kaun hai jis par sabse zyada trust karte ho? ❤️",
        "Life mein sabse bada regret kya hai? 💭",
        "Kabhi class ya office se bina bataye bhaage ho? 😂",
    ]

    dare_list = [
        "Abhi apni maa ko call kar ke bol — 'Main tujhse pyaar karta hoon' 📞❤️",
        "Apni sabse embarrassing photo share kar group mein 📸😹",
        "Kisi bhi friend ko abhi message kar — 'Bhai mujhe pata chal gaya' — aur reaction dekho 😈",
        "10 seconds ke liye khud se hi baat karo — loud 🗣️",
        "Abhi ek push-up kar aur photo bhejo 💪",
        "Apne crush ko 'Hi' bol — screenshot bhejo 😳",
        "Khud ki roast karo ek paragraph mein — seriously 😂",
    ]

    pickup_list = [
        "Kya tum WiFi ho? Kyunki main teri taraf khinchat chala aa raha hoon 📶😂",
        "Tujhe dekh ke soch raha tha — yeh image real nahi ho sakti 🖼️❤️",
        "Kya tum dictionary ho? Kyunki tujhme meaning hai 📖✨",
        "Tu itna sweet hai ke mujhe diabetes ka darr ho gaya 🍭😹",
        "Teri eyes mein stars hain ya stars tujhe dekh ke sharminde ho gaye? ⭐❤️",
    ]

    compliment_list = [
        "Bhai tu bahut positive energy rakhta hai — seriously 🌟",
        "Teri thinking bahut alag hai — creative hai tu 🧠✨",
        "Tu jo bhi karta hai dil se karta hai — yeh rare hai ❤️",
        "Teri sense of humor? Top tier 😂👑",
        "Tujhse baat karna genuinely enjoyable hota hai 🗣️✨",
    ]

    quote_list = [
        "💭 'Sapne woh nahi jo sote waqt aate hain, sapne woh hain jo sone nahi dete.' — APJ Abdul Kalam",
        "💭 'Mehnat karo itna ki luck ko bhi mauka mile tujhe dhundhne ka.' — Unknown",
        "💭 'Duniya ka sabse bada teacher: failure hai.' — Unknown",
        "💭 'Ek accha dost aur ek accha kitaab — dono hi tujhe better banate hain.' — Unknown",
        "💭 'Zindagi ek echo hai — jo bejhoge woh wapas aayega.' — Unknown",
    ]

    # ────────────────────────────────────────────────
    #                 DECORATOR
    # ────────────────────────────────────────────────
    commands = {}

    def register_cmd(name: str, needs_reply: bool = False, group_only: bool = False):
        def decorator(func):
            key = (name or "").lower().strip()
            if not key:
                raise ValueError("Command name cannot be empty")
            if key in commands:
                raise ValueError(f"Duplicate command registered: {key}")
            commands[key] = {
                "func": func, "needs_reply": bool(needs_reply), "group_only": bool(group_only),
            }
            return func
        return decorator

    # ────────────────────────────────────────────────
    #                 FASTGC ENGINE
    # ────────────────────────────────────────────────
    async def fast_title_edit(chat_id, title):
        safe_title = (title or "").strip()[:255]
        if not safe_title: return False
        try:
            await bot(functions.channels.EditTitleRequest(channel=chat_id, title=safe_title))
            return True
        except Exception:
            try:
                await bot(functions.messages.EditChatTitleRequest(chat_id=chat_id, title=safe_title))
                return True
            except Exception as e:
                return False

    async def gc_fast_loop(chat_id):
        try:
            while True:
                if not FASTGC_STATE.get("active"): break
                template = FASTGC_STATE.get("template")
                if not template: break
                try: emoji = random.choice(GC_FAST_EMOJIS)
                except: emoji = "⚡"
                try: new_title = template.replace("{emoji}", emoji)
                except: await asyncio.sleep(2); continue
                ok = await fast_title_edit(chat_id, new_title)
                try:
                    if ok: await asyncio.sleep(max(1, GC_FAST_INTERVAL))
                    else: await asyncio.sleep(5)
                except: await asyncio.sleep(3)
        except asyncio.CancelledError: return
        except Exception as e: pass

    # ────────────────────────────────────────────────
    #                 MENU COMMANDS
    # ────────────────────────────────────────────────
    @register_cmd("menu")
    async def cmd_menu(event, _):
        global menu_banner_msg
        menu = (
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "  ⚡️  𝗦𝗜𝗗𝘅𝗕𝗢𝗧  𝗨𝗦𝗘𝗥𝗕𝗢𝗧  𝗩𝟯  ⚡️\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "\n"
    "  👑  𝗢𝘄𝗻𝗲𝗿   ›  𝗦𝗜𝗗𝘅𝗕𝗢𝗧\n"
    "  📦  𝗖𝗺𝗱𝘀    ›  𝟱𝟬𝟬+ 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀\n"
    "  🔥  𝗣𝗿𝗲𝗳𝗶𝘅  ›  .  (𝗗𝗼𝘁)\n"
    "  ⚔️  𝗥𝗮𝗶𝗱𝘀   ›  𝟮𝟬 𝗧𝘆𝗽𝗲𝘀  (𝟰 𝗡𝗘𝗪)\n"
    "\n"
    "┌──────────────────────────────────┐\n"
    "│         📋  𝗠𝗘𝗡𝗨  𝗣𝗔𝗚𝗘𝗦          │\n"
    "├──────────────────────────────────┤\n"
    "│  .𝗺𝗲𝗻𝘂𝟭  →  👑 𝗔𝗱𝗺𝗶𝗻 & 🔇 𝗠𝘂𝘁𝗲       │\n"
    "│  .𝗺𝗲𝗻𝘂𝟮  →  ⚔️ 𝗥𝗮𝗶𝗱 𝗘𝗻𝗴𝗶𝗻𝗲 (𝗢𝗿𝗶𝗴)   │\n"
    "│  .𝗺𝗲𝗻𝘂𝟯  →  💣 𝗦𝗽𝗮𝗺 & 📝 𝗧𝗲𝘅𝘁 𝗠𝗴𝗿   │\n"
    "│  .𝗺𝗲𝗻𝘂𝟰  →  🛡️ 𝗣𝗿𝗼𝘁𝗲𝗰𝘁𝗶𝗼𝗻          │\n"
    "│  .𝗺𝗲𝗻𝘂𝟱  →  🛠️ 𝗧𝗼𝗼𝗹𝘀 & 🎵 𝗠𝘂𝘀𝗶𝗰      │\n"
    "│  .𝗺𝗲𝗻𝘂𝟲  →  🔥 𝗙𝗶𝗴𝗵𝘁𝗶𝗻𝗴 𝗥𝗮𝗶𝗱𝘀       │\n"
    "│  .𝗺𝗲𝗻𝘂𝟳  →  ⚙️ 𝗨𝘁𝗶𝗹𝗶𝘁𝘆 𝗧𝗼𝗼𝗹𝘀        │\n"
    "│  .𝗺𝗲𝗻𝘂𝟴  →  🎮 𝗙𝘂𝗻 & 𝗔𝗻𝗶𝗺𝗮𝘁𝗶𝗼𝗻𝘀     │\n"
    "│  .𝗰𝗺𝗱𝘀   →  📜 𝗔𝗹𝗹 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀         │\n"
    "└──────────────────────────────────┘\n"
    "\n"
    "🔥  𝗣𝗼𝘄𝗲𝗿𝗲𝗱 𝗯𝘆 𝗦𝗜𝗗𝘅𝗕𝗢𝗧  🔥"
        )
        await safe_edit(event, menu)
        if menu_banner_msg:
            chat_id, msg_id = menu_banner_msg
            try:
                msg = await bot.get_messages(chat_id, ids=msg_id)
                await bot.send_file(event.chat_id, file=msg.media, caption="⚡ 𝗦𝗜𝗗𝘅𝗕𝗢𝗧 𝗘𝗻𝘁𝗲𝗿𝘀 ❤️‍🔥")
            except: pass

    @register_cmd("cmds")
    async def cmd_cmds(event, _):
        cmds = (
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "   📜  𝗦𝗜𝗗𝗫𝗕𝗢𝗧  𝗩𝟯  —  𝗙𝗨𝗟𝗟  𝗖𝗠𝗗𝗦\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "👑 𝗔𝗗𝗠𝗜𝗡:\n"
    "  .admins .addadmin .deladmin\n"
    "\n"
    "🔇 𝗠𝗨𝗧𝗘:\n"
    "  .mute .unmute .gmute .gunmute .mutelist\n"
    "\n"
    "🧹 𝗚𝗥𝗢𝗨𝗣 𝗠𝗢𝗗 (𝗡𝗘𝗪):\n"
    "  .lock .unlock .purge .throw .addbots\n"
    "  .ban .unban .kick .promote .demote\n"
    "  .warn .warnlist .clearwarn .nukegc\n"
    "  .adminall .unadminall .pin .unpin\n"
    "\n"
    "⚔️ 𝗥𝗔𝗜𝗗𝗦 (𝗢𝗥𝗜𝗚):\n"
    "  .reply .rr .flag .hrr .replygod .replysid\n"
    "  stop: .sreply .srr .sflag .shrr .sgod .sstop\n"
    "\n"
    "🔥 𝗥𝗔𝗜𝗗𝗦 (𝗡𝗘𝗪 𝟭𝟬𝟬𝟬+ 𝗧𝗘𝗫𝗧𝗦):\n"
    "  .attack .roast .diss .war .savage\n"
    "  .ultra .godwar .combo .troll .shame\n"
    "  .fire .devil .karma .ghost .legend .doom\n"
    "  .nuke .storm .blizzard .venom   ★ 4 NEW\n"
    "  stop: .s<name>  |  all: .stopall\n"
    "\n"
    "💣 𝗦𝗣𝗔𝗠:\n"
    "  .spray .dspray .tspray .rspray\n"
    "  .multispray .countspray .spraydelay\n"
    "  .dmraid .gcast\n"
    "\n"
    "🎭 𝗔𝗡𝗜𝗠𝗔𝗧𝗜𝗢𝗡𝗦 (𝗡𝗘𝗪):\n"
    "  .hack .loading .typing_anim .moon\n"
    "  .earth .hearts .police .matrix .glitch\n"
    "  .neon .rainbow .wave .spin .countdown\n"
    "  .progress .clock .fire_anim .starfall\n"
    "  .pulse .bounce .flip\n"
    "\n"
    "📝 𝗧𝗘𝗫𝗧 𝗠𝗚𝗥:\n"
    "  .addtext .listtexts .edittext .deltext .cleartext\n"
    "\n"
    "🛡️ 𝗣𝗥𝗢𝗧𝗘𝗖𝗧𝗜𝗢𝗡:\n"
    "  .antidel .watchspam .unwatchspam .watchlist\n"
    "\n"
    "🛠️ 𝗧𝗢𝗢𝗟𝗦 (𝗢𝗥𝗜𝗚):\n"
    "  .tts .qrcode .fancy .style .emoji .calc\n"
    "  .weather .ip .short .crypto .translate .imdb\n"
    "\n"
    "🔐 𝗖𝗥𝗬𝗣𝗧𝗢:\n"
    "  .encode .decode .rot13 .morse .binary\n"
    "  .md5 .sha256 .b64 .b64d .uuid .password\n"
    "\n"
    "⏰ 𝗦𝗬𝗦𝗧𝗘𝗠 & 𝗠𝗔𝗧𝗛:\n"
    "  .time .date .uptime .myip .ping\n"
    "  .random .calc .tempconv\n"
    "\n"
    "👤 𝗨𝗦𝗘𝗥 𝗜𝗡𝗙𝗢:\n"
    "  .id .chatid .whois .mention\n"
    "  .getpp .setname .setbio .setpp\n"
    "\n"
    "🎵 𝗠𝗨𝗦𝗜𝗖 & 𝗡𝗢𝗧𝗘𝗦:\n"
    "  .music .dmusic .notesadd .noteslist\n"
    "\n"
    "🎮 𝗙𝗨𝗡:\n"
    "  .flip .dice .rps .8ball .choose\n"
    "  .joke .riddle .fact .quote\n"
    "  .truth .dare .pickup .compliment .roastme\n"
    "\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "⚡ 𝟱𝟬𝟬+ 𝗖𝗺𝗱𝘀  |  🔥 𝗣𝗿𝗲𝗳𝗶𝘅: .  |  𝗩𝟯"
        )
        await safe_edit(event, cmds)

    # ────────────────────────────────────────────────
    #         NEW ANIMATION COMMANDS (15 added)
    # ────────────────────────────────────────────────
    @register_cmd("matrix")
    async def cmd_matrix(event, _):
        chars = "0123456789ABCDEF"
        frames = []
        for _ in range(20):
            line = "".join(random.choice(chars) if random.random() > 0.3 else " " for _ in range(30))
            frames.append(f"💻 **MATRIX**\n━━━━━━━━━━━━━━━\n`{line}`")
        for frame in frames[:10]:
            await safe_edit(event, frame)
            await asyncio.sleep(0.1)

    @register_cmd("glitch")
    async def cmd_glitch(event, _):
        words = ["G", "Gl", "Gli", "Glit", "Glitc", "Glitch"]
        for w in words:
            await safe_edit(event, f"⚡ **GLITCH**\n━━━━━━━━━━━━━━━\n`{w}█`")
            await asyncio.sleep(0.3)
        await safe_edit(event, "✅ **GLITCH COMPLETE**")

    @register_cmd("neon")
    async def cmd_neon(event, _):
        colors = ["🔴", "🟠", "🟡", "🟢", "🔵", "🟣"]
        for c in colors:
            await safe_edit(event, f"💡 **NEON**\n━━━━━━━━━━━━━━━\n{c} **SIDxBOT** {c}")
            await asyncio.sleep(0.4)

    @register_cmd("rainbow")
    async def cmd_rainbow(event, _):
        text = "RAINBOW"
        for i in range(len(text)):
            colored = "".join(f"🌈{char}🌈" for char in text[:i+1])
            await safe_edit(event, f"🌈 **RAINBOW**\n━━━━━━━━━━━━━━━\n{colored}")
            await asyncio.sleep(0.3)
        await safe_edit(event, "🌈 **RAINBOW COMPLETE**")

    @register_cmd("wave")
    async def cmd_wave(event, _):
        waves = ["~", "~~", "~~~", "~~~~", "~~~~~", "~~~~~~", "~~~~~~~"]
        for w in waves:
            await safe_edit(event, f"🌊 **WAVE**\n━━━━━━━━━━━━━━━\n{w} SIDxBOT {w}")
            await asyncio.sleep(0.2)

    @register_cmd("spin")
    async def cmd_spin(event, _):
        spinners = ["|", "/", "-", "\\"]
        for _ in range(10):
            for s in spinners:
                await safe_edit(event, f"🌀 **SPINNING**\n━━━━━━━━━━━━━━━\n{s}")
                await asyncio.sleep(0.1)

    @register_cmd("countdown")
    async def cmd_countdown(event, _):
        for i in range(5, 0, -1):
            await safe_edit(event, f"⏳ **COUNTDOWN**\n━━━━━━━━━━━━━━━\n`{i}`")
            await asyncio.sleep(1)
        await safe_edit(event, "🚀 **BLAST OFF!**")

    @register_cmd("progress")
    async def cmd_progress(event, _):
        for i in range(0, 101, 10):
            bar = "█" * (i//10) + "░" * (10 - i//10)
            await safe_edit(event, f"📊 **PROGRESS**\n━━━━━━━━━━━━━━━\n[{bar}] {i}%")
            await asyncio.sleep(0.3)
        await safe_edit(event, "✅ **PROGRESS COMPLETE**")

    @register_cmd("clock")
    async def cmd_clock(event, _):
        hands = ["🕐", "🕑", "🕒", "🕓", "🕔", "🕕", "🕖", "🕗", "🕘", "🕙", "🕚", "🕛"]
        for _ in range(2):
            for h in hands:
                await safe_edit(event, f"🕰️ **ANALOG CLOCK**\n━━━━━━━━━━━━━━━\n{h}")
                await asyncio.sleep(0.3)

    @register_cmd("fire_anim")
    async def cmd_fire_anim(event, _):
        fires = ["🔥", "🔥🔥", "🔥🔥🔥", "🔥🔥🔥🔥", "🔥🔥🔥🔥🔥"]
        for f in fires:
            await safe_edit(event, f"🔥 **FIRE**\n━━━━━━━━━━━━━━━\n{f}")
            await asyncio.sleep(0.3)

    @register_cmd("starfall")
    async def cmd_starfall(event, _):
        stars = ["✨", "🌟", "⭐", "🌠"]
        for s in stars:
            await safe_edit(event, f"🌠 **STARFALL**\n━━━━━━━━━━━━━━━\n{s} * * *")
            await asyncio.sleep(0.4)

    @register_cmd("pulse")
    async def cmd_pulse(event, _):
        for size in range(1, 6):
            heart = "❤️" * size
            await safe_edit(event, f"💓 **PULSE**\n━━━━━━━━━━━━━━━\n{heart}")
            await asyncio.sleep(0.2)
        for size in range(5, 0, -1):
            heart = "❤️" * size
            await safe_edit(event, f"💓 **PULSE**\n━━━━━━━━━━━━━━━\n{heart}")
            await asyncio.sleep(0.2)

    @register_cmd("bounce")
    async def cmd_bounce(event, _):
        positions = ["⚽️", "  ⚽️", "    ⚽️", "      ⚽️", "        ⚽️", "      ⚽️", "    ⚽️", "  ⚽️"]
        for p in positions:
            await safe_edit(event, f"🏀 **BOUNCE**\n━━━━━━━━━━━━━━━\n{p}")
            await asyncio.sleep(0.1)

    @register_cmd("flip")
    async def cmd_flip(event, _):
        sides = ["🪙 Heads", "🪙 Tails"]
        for _ in range(5):
            for side in sides:
                await safe_edit(event, f"🪙 **FLIP**\n━━━━━━━━━━━━━━━\n{side}")
                await asyncio.sleep(0.2)
        await safe_edit(event, f"🪙 **RESULT:** {random.choice(sides)}")

    # ────────────────────────────────────────────────
    #         EXISTING ANIMATION COMMANDS (KEPT)
    # ────────────────────────────────────────────────
    @register_cmd("hack")
    async def cmd_hack(event, _):
        anim = [
            "Initializing hacking tools...",
            "Bypassing security protocols...",
            "Accessing mainframe database...",
            "Extracting passwords...",
            "Downloading sensitive files...",
            "Cleaning up traces...",
            "✅ System Hacked Successfully!"
        ]
        for frame in anim:
            await safe_edit(event, f"💻 **HACKING**\n━━━━━━━━━━━━━━━\n`{frame}`")
            await asyncio.sleep(0.7)

    @register_cmd("loading")
    async def cmd_loading(event, _):
        frames = [
            "🟩⬜️⬜️⬜️⬜️⬜️⬜️⬜️⬜️⬜️ 10%",
            "🟩🟩⬜️⬜️⬜️⬜️⬜️⬜️⬜️⬜️ 20%",
            "🟩🟩🟩⬜️⬜️⬜️⬜️⬜️⬜️⬜️ 30%",
            "🟩🟩🟩🟩🟩⬜️⬜️⬜️⬜️⬜️ 50%",
            "🟩🟩🟩🟩🟩🟩🟩⬜️⬜️⬜️ 70%",
            "🟩🟩🟩🟩🟩🟩🟩🟩🟩⬜️ 90%",
            "🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩 100%",
            "✅ **LOADING COMPLETE**"
        ]
        for f in frames:
            await safe_edit(event, f"⏳ **LOADING**\n━━━━━━━━━━━━━━━\n{f}")
            await asyncio.sleep(0.5)

    @register_cmd("typing_anim")
    async def cmd_typing_anim(event, arg):
        if not arg: arg = "SIDxBOT is the best userbot out there!"
        text = ""
        for char in arg:
            text += char
            await safe_edit(event, f"✍️ {text}█")
            await asyncio.sleep(0.1)
        await safe_edit(event, f"✍️ **{arg}**")

    @register_cmd("moon")
    async def cmd_moon(event, _):
        phases = ["🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"]
        for _ in range(3):
            for p in phases:
                await safe_edit(event, f"🌘 **MOON PHASE** 🌒\n━━━━━━━━━━━━━━━\n{p}")
                await asyncio.sleep(0.3)

    @register_cmd("earth")
    async def cmd_earth(event, _):
        phases = ["🌍", "🌎", "🌏"]
        for _ in range(5):
            for p in phases:
                await safe_edit(event, f"💫 **ROTATING EARTH** 💫\n━━━━━━━━━━━━━━━\n{p}")
                await asyncio.sleep(0.4)

    @register_cmd("hearts")
    async def cmd_hearts(event, _):
        phases = ["❤️", "🧡", "💛", "💚", "💙", "💜", "🖤", "🤍", "🤎", "🩷", "🩵", "🩶"]
        for _ in range(2):
            for p in phases:
                await safe_edit(event, f"💖 **HEARTS BEATING** 💖\n━━━━━━━━━━━━━━━\n{p}")
                await asyncio.sleep(0.2)

    @register_cmd("police")
    async def cmd_police(event, _):
        phases = ["🔴🔵🔴🔵🔴🔵", "🔵🔴🔵🔴🔵🔴"]
        for _ in range(5):
            for p in phases:
                await safe_edit(event, f"🚓 **POLICE SIREN** 🚓\n━━━━━━━━━━━━━━━\n{p}")
                await asyncio.sleep(0.3)

    # ────────────────────────────────────────────────
    #         NEW POWERFUL GROUP/SPAM COMMANDS
    # ────────────────────────────────────────────────
    @register_cmd("nukegc", group_only=True)
    async def cmd_nukegc(event, _):
        await safe_edit(event, "☢️ **NUKE LAUNCHED**\nEliminating all members...")
        try:
            me = await bot.get_me()
            async for user in bot.iter_participants(event.chat_id):
                if user.id == me.id: continue
                if is_admin(user.id) or user.id in PROTECTED_IDS: continue
                try:
                    await bot.kick_participant(event.chat_id, user.id)
                except:
                    pass
            await safe_edit(event, "✅ **CHAT NUKED SUCCESSFULLY**")
        except Exception as e:
            await safe_edit(event, f"❌ Err: {e}")

    @register_cmd("adminall", group_only=True)
    async def cmd_adminall(event, _):
        await safe_edit(event, "⭐ **PROMOTING EVERYONE**...")
        count = 0
        try:
            me = await bot.get_me()
            async for user in bot.iter_participants(event.chat_id):
                if user.id == me.id: continue
                if user.id in PROTECTED_IDS: continue
                try:
                    await bot(functions.channels.EditAdminRequest(
                        channel=event.chat_id, user_id=user.id,
                        admin_rights=types.ChatAdminRights(
                            change_info=True, delete_messages=True, ban_users=True,
                            invite_users=True, pin_messages=True, manage_call=True
                        ), rank="Admin"
                    ))
                    count += 1
                except: pass
            await safe_edit(event, f"✅ **SUCCESSFULLY PROMOTED** `{count}` members!")
        except Exception as e:
            await safe_edit(event, f"❌ Err: {e}")

    @register_cmd("unadminall", group_only=True)
    async def cmd_unadminall(event, _):
        await safe_edit(event, "⬇️ **DEMOTING EVERYONE**...")
        count = 0
        try:
            me = await bot.get_me()
            async for user in bot.iter_participants(event.chat_id, filter=ChannelParticipantsAdmins):
                if user.id == me.id: continue
                if user.id in PROTECTED_IDS: continue
                try:
                    await bot(functions.channels.EditAdminRequest(
                        channel=event.chat_id, user_id=user.id,
                        admin_rights=types.ChatAdminRights(), rank=""
                    ))
                    count += 1
                except: pass
            await safe_edit(event, f"✅ **SUCCESSFULLY DEMOTED** `{count}` admins!")
        except Exception as e:
            await safe_edit(event, f"❌ Err: {e}")

    @register_cmd("gcast")
    async def cmd_gcast(event, arg):
        if not arg:
            return await safe_edit(event, "❌ Use → `.gcast <text>`")
        await safe_edit(event, "📡 **Global Broadcast Started...**")
        count = 0
        try:
            async for dialog in bot.iter_dialogs():
                if dialog.is_group or dialog.is_channel:
                    try:
                        await bot.send_message(dialog.id, arg)
                        count += 1
                    except: pass
            await safe_edit(event, f"✅ **BROADCAST COMPLETE**\nSent to `{count}` groups/channels.")
        except Exception as e:
            await safe_edit(event, f"❌ Err: {e}")

    @register_cmd("dmraid", needs_reply=True)
    async def cmd_dmraid(event, arg):
        try:
            targets = await get_targets(event, "")
            if not targets: return await safe_edit(event, "❌ Reply to a user.")
            parts = arg.strip().split(None, 1) if arg else []
            if len(parts) < 2: return await safe_edit(event, "❌ Use → `.dmraid <count> <text>`")
            try: count = min(int(parts[0]), 100)
            except: return await safe_edit(event, "❌ Invalid count.")
            text = parts[1]
            await safe_edit(event, f"💀 **DM RAID INITIATED** on target(s)...")
            
            for uid in targets:
                for _ in range(count):
                    try:
                        await bot.send_message(uid, text)
                        await asyncio.sleep(0.5)
                    except FloodWaitError as fw:
                        await asyncio.sleep(fw.seconds)
                    except: break
            await safe_edit(event, "✅ **DM RAID FINISHED**")
        except Exception as e:
            await safe_edit(event, f"❌ DM Raid Err → `{str(e)[:40]}`")

    # ────────────────────────────────────────────────
    #         MODIFIED ANIMATIONS
    # ────────────────────────────────────────────────
    @register_cmd("ping")
    async def cmd_ping(event, _):
        try:
            t0 = time.perf_counter()
            msg = await safe_edit(event, "💥 🏓 P i n g i n g . . .")
            t1 = time.perf_counter()
            ms = round((t1 - t0) * 1000)
            await safe_edit(event, f"🚀 **P O N G** 🚀\n━━━━━━━━━━━━━━━\n⚡ `{ms} ms`")
        except Exception as e:
            await safe_edit(event, f"❌ 𝐏ɪɴɢ 𝐄ʀʀ → `{str(e)[:40]}`")

    @register_cmd("alive")
    async def cmd_alive(event, _):
        try:
            await safe_edit(event, "🔄 **Booting up systems...**")
            await asyncio.sleep(0.4)
            await safe_edit(event, "⚡ **Checking parameters...**")
            await asyncio.sleep(0.4)
            
            elapsed = int(time.time() - START_TIME)
            h, r = divmod(elapsed, 3600)
            m, s = divmod(r, 60)
            uptime_str = f"{h}h {m}m {s}s"
            try:
                me = await bot.get_me()
                uname = f"@{me.username}" if me.username else me.first_name
            except:
                uname = "Unknown"
            txt = (
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "  ⚡️  𝗦𝗜𝗗 𝗔𝗗𝗩𝗔𝗡𝗖𝗘 𝗩𝟯  ⚡️\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🟢  𝐒𝐭𝐚𝐭𝐮𝐬    →  `ALIVE ✅`\n"
                f"👤  𝐀𝐜𝐜𝐨𝐮𝐧𝐭   →  `{uname}`\n"
                f"⏱️  𝐔𝐩𝐭𝐢𝐦𝐞    →  `{uptime_str}`\n"
                f"📦  𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬  →  `500+`\n"
                f"⚔️  𝐑𝐚𝐢𝐝𝐬     →  `20 Types`\n"
                f"🔥  𝐕𝐞𝐫𝐬𝐢𝐨𝐧   →  `SIDxBOT✨❤️`\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "💡  𝐐𝐮𝐢𝐜𝐤 𝐒𝐭𝐚𝐫𝐭:\n"
                "    `.ping`   — Speed test karo\n"
                "    `.attack` — Kisi ko attack karo (reply)\n"
                "    `.spray`  — Spam spray shuru\n"
                "    `.hack`   — Hacking Animation\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "🌟  𝐏𝐨𝐰𝐞𝐫𝐞𝐝 𝐛𝐲  𝗦𝗜𝗗𝘅𝗕𝗢𝗧"
            )
            await safe_edit(event, txt)
        except Exception as e:
            await safe_edit(event, f"❌ 𝐀𝐥𝐢𝐯𝐞 𝐄ʀʀ → `{str(e)[:40]}`")

    # ────────────────────────────────────────────────
    #         COMMAND DISPATCHER
    # ────────────────────────────────────────────────
    @bot.on(events.NewMessage(outgoing=True))
    async def dispatcher(event):
        text = event.raw_text
        if not text: return
        if not text.startswith("."): return
        body = text[1:].strip()
        if not body: return
        parts = body.split(maxsplit=1)
        cmd = parts[0].lower().strip()
        arg = parts[1].strip() if len(parts) > 1 else ""
        cmd_data = commands.get(cmd)
        if not cmd_data: return

        sender = event.sender_id
        if OWNER_ID and sender and sender != OWNER_ID:
            return 

        if cmd_data.get("group_only"):
            try:
                if not event.is_group:
                    await safe_edit(event, "⚠️ 𝐆𝐫𝐨𝐮𝐩 𝐎𝐧𝐥𝐲 𝐂𝐨𝐦𝐦𝐚𝐧𝐝")
                    return
            except: return

        if cmd_data.get("needs_reply"):
            try:
                if not event.is_reply and not arg:
                    await safe_edit(event, f"❌ 𝐑𝐞𝐩𝐥𝐲 𝐎𝐫 𝐏𝐚𝐬𝐬 𝐓𝐚𝐫𝐠𝐞𝐭\n👉 .{cmd} @user / id")
                    return
            except: return

        try:
            await cmd_data["func"](event, arg)
        except FloodWaitError as e:
            try: await safe_edit(event, f"⏳ 𝐅𝐥𝐨𝐨𝐝𝐖𝐚𝐢𝐭 → `{e.seconds}s`")
            except: pass
        except Exception as e:
            try: await safe_edit(event, f"❌ 𝐄𝐫𝐫𝐨𝐫 → `{str(e)[:50]}`")
            except: pass

    # ────────────────────────────────────────────────
    #         STARTUP
    # ────────────────────────────────────────────────
    async def main():
        global OWNER_ID
        try:
            await bot.start()
            me = await bot.get_me()
            OWNER_ID = me.id
            uname = f"@{me.username}" if me.username else "NoUsername"
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print("🤖 SID ADVANCE V3 USERBOT STARTED!")
            print(f"👤 Logged in as → {me.first_name} ({uname})")
            print(f"🆔 User ID → {me.id}  [OWNER LOCKED]")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            while True:
                try: await bot.run_until_disconnected(); break
                except (ConnectionError, OSError):
                    print("⚠️ Connection Lost → Reconnecting...")
                    await asyncio.sleep(3)
        except Exception as e:
            print(f"\n❌ Startup Error → {str(e)[:80]}")
        finally:
            try:
                if bot.is_connected(): await bot.disconnect()
            except: pass

    if __name__ == "__main__":
        try:
            asyncio.run(main())
        except RuntimeError:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(main())
else:
    # ====================================================================
    #   INLINE CONFIG — reads from environment variables
    # ====================================================================
    import os
    import sys
    BOT_TOKEN         = "8653377116:AAGOlJ5FP_3ki_kWAJJG1_t0OoeoYwk0kKY"  
    OWNER_ID          = 8684812026            
    SUPPORT_USERNAME  = "@s1dfr"
    MAX_USERBOTS      = int(os.environ.get("MAX_USERBOTS", "50") or "50")
    TELEGRAM_API_ID   = 38843772                   
    TELEGRAM_API_HASH = "875fbb273801c8025d05e98173fca536"  

    # ====================================================================
    #   INLINE DATABASE — JSON file-based storage in ./data/
    # ====================================================================
    import json
    import threading

    _DB_DIR = os.path.join(os.getcwd(), "data")
    _db_lock = threading.Lock()

    def _db_path(*parts):
        p = os.path.join(_DB_DIR, *parts)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        return p

    def _read_json(path, default):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return default

    def _write_json(path, data):
        with _db_lock:
            tmp = path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(tmp, path)

    def _config_path(): return _db_path("config.json")
    def get_config(): return _read_json(_config_path(), {})
    def save_config(cfg): _write_json(_config_path(), cfg)
    
    def get_start_video():
        c = get_config()
        return c.get("start_video"), c.get("is_gif", False)

    def set_start_video(file_id, is_gif=False):
        c = get_config()
        c["start_video"] = file_id
        c["is_gif"] = is_gif
        save_config(c)

    def user_exists(uid): return os.path.isfile(_db_path("users", str(uid), "meta.json"))
    def save_user_meta(uid, data):
        path = _db_path("users", str(uid), "meta.json")
        existing = _read_json(path, {})
        existing.update(data)
        _write_json(path, existing)

    def get_all_users():
        users_dir = os.path.join(_DB_DIR, "users")
        if not os.path.isdir(users_dir): return []
        return [d for d in os.listdir(users_dir) if os.path.isdir(os.path.join(users_dir, d))]

    def user_count(): return len(get_all_users())
    def _accts_path(uid): return _db_path("users", str(uid), "accounts.json")
    def get_accounts(uid): return _read_json(_accts_path(uid), [])
    
    def get_account(uid, slot):
        for a in get_accounts(uid):
            if a.get("slot") == slot: return a
        return None

    def add_account(uid, acct):
        accounts = get_accounts(uid)
        accounts = [a for a in accounts if a.get("slot") != acct.get("slot")]
        accounts.append(acct)
        _write_json(_accts_path(uid), accounts)

    def remove_account(uid, slot):
        accounts = [a for a in get_accounts(uid) if a.get("slot") != slot]
        _write_json(_accts_path(uid), accounts)

    def hosted_count():
        total = 0
        for uid_str in get_all_users():
            for a in get_accounts(uid_str):
                if a.get("hosted"): total += 1
        return total

    def _sudo_path(): return _db_path("sudo.json")
    def get_sudo_users(): return _read_json(_sudo_path(), [])
    def add_sudo(uid):
        s = get_sudo_users()
        if uid not in s: s.append(uid); _write_json(_sudo_path(), s)
    def remove_sudo(uid):
        s = [x for x in get_sudo_users() if x != uid]
        _write_json(_sudo_path(), s)
    def is_sudo(uid, owner_id): return uid == owner_id or uid in get_sudo_users()

    def _blocked_path(): return _db_path("blocked.json")
    def get_blocked(): return _read_json(_blocked_path(), [])
    def block_user(uid):
        b = get_blocked()
        if uid not in b: b.append(uid); _write_json(_blocked_path(), b)
    def unblock_user(uid):
        b = [x for x in get_blocked() if x != uid]
        _write_json(_blocked_path(), b)
    def is_blocked(uid): return uid in get_blocked()

    import types as _types
    db = _types.SimpleNamespace(
        user_exists=user_exists, save_user_meta=save_user_meta,
        get_all_users=get_all_users, user_count=user_count,
        get_accounts=get_accounts, get_account=get_account,
        add_account=add_account, remove_account=remove_account,
        hosted_count=hosted_count, get_sudo_users=get_sudo_users, 
        add_sudo=add_sudo, remove_sudo=remove_sudo, is_sudo=is_sudo,
        get_blocked=get_blocked, block_user=block_user,
        unblock_user=unblock_user, is_blocked=is_blocked,
        get_start_video=get_start_video, set_start_video=set_start_video
    )

    # ====================================================================
    #   INLINE RUNNER — subprocess-based userbot process manager
    # ====================================================================
    import subprocess
    import time as _time

    _procs = {}
    _start_times = {}

    def _this_file(): return os.path.abspath(__file__)
    def _build_env(api_id, api_hash, session_string, owner_id_str):
        env = os.environ.copy()
        env.update({
            "API_ID":           str(api_id),
            "API_HASH":         str(api_hash),
            "SESSION_STRING":   session_string,
            "USERBOT_OWNER_ID": str(owner_id_str),
            "USERBOT_MODE":     "1",
        })
        return env

    def start_userbot(uid, slot, api_id, api_hash, session_string, owner_id_str):
        key = (int(uid), int(slot))
        stop_userbot(uid, slot)
        try:
            env = _build_env(api_id, api_hash, session_string, owner_id_str)
            os.makedirs("userbot_logs", exist_ok=True)
            log_file = open(f"userbot_logs/userbot_{uid}_slot{slot}.log", "a")
            proc = subprocess.Popen(
                [sys.executable, _this_file(), "--userbot"],
                env=env, stdout=log_file, stderr=log_file,
            )
            _procs[key] = proc
            _start_times[key] = _time.time()
            return True
        except Exception as e:
            return False

    def restart_userbot(uid, slot, api_id, api_hash, session_string, owner_id_str):
        return start_userbot(uid, slot, api_id, api_hash, session_string, owner_id_str)

    def stop_userbot(uid, slot):
        key = (int(uid), int(slot))
        proc = _procs.pop(key, None)
        _start_times.pop(key, None)
        if proc:
            try: proc.terminate(); proc.wait(timeout=5)
            except:
                try: proc.kill()
                except: pass

    def stop_all_for_user(uid):
        keys = [k for k in list(_procs.keys()) if k[0] == int(uid)]
        for k in keys: stop_userbot(k[0], k[1])

    def is_running(uid, slot):
        key = (int(uid), int(slot))
        proc = _procs.get(key)
        if not proc: return False
        if proc.poll() is not None:
            _procs.pop(key, None); _start_times.pop(key, None); return False
        return True

    def running_count():
        dead = [k for k, p in list(_procs.items()) if p.poll() is not None]
        for k in dead: _procs.pop(k, None); _start_times.pop(k, None)
        return len(_procs)

    def get_uptime(uid, slot):
        key = (int(uid), int(slot))
        t = _start_times.get(key)
        if not t: return "—"
        e = int(_time.time() - t)
        h, r = divmod(e, 3600); m, s = divmod(r, 60)
        return f"{h}h {m}m {s}s"

    runner = _types.SimpleNamespace(
        start_userbot=start_userbot, restart_userbot=restart_userbot,
        stop_userbot=stop_userbot, stop_all_for_user=stop_all_for_user,
        is_running=is_running, running_count=running_count, get_uptime=get_uptime,
    )

    # ====================================================================
    #   HOSTER BOT CODE
    # ====================================================================

    import asyncio
    import logging
    import os
    import time
    import shutil
    from telegram import (
        Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
    )
    from telegram.ext import (
        Application, CommandHandler, MessageHandler, ConversationHandler,
        CallbackQueryHandler, ContextTypes, filters
    )
    from telegram.constants import ParseMode
    from telethon import TelegramClient
    from telethon.sessions import StringSession
    from telethon.errors import (
        SessionPasswordNeededError, PhoneCodeExpiredError,
        PhoneCodeInvalidError, FloodWaitError
    )

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    logger = logging.getLogger(__name__)

    START_TIME = time.time()
    MAX_ACCOUNTS_PER_USER = 3  

    ASK_PHONE, ASK_CODE, ASK_2FA = range(3)
    pending_logins: dict = {}

    def bold_serif(t: str) -> str:
        result = ""
        for c in t:
            if 'A' <= c <= 'Z': result += chr(ord(c) - ord('A') + 0x1D400)
            elif 'a' <= c <= 'z': result += chr(ord(c) - ord('a') + 0x1D41A)
            elif '0' <= c <= '9': result += chr(ord(c) - ord('0') + 0x1D7CE)
            else: result += c
        return result

    def italic_serif(t: str) -> str:
        special = {'h': '𝒽', 'e': '𝑒', 'i': '𝑖', 'j': '𝑗'}
        result = ""
        for c in t:
            if c in special: result += special[c]
            elif 'A' <= c <= 'Z': result += chr(ord(c) - ord('A') + 0x1D434)
            elif 'a' <= c <= 'z': result += chr(ord(c) - ord('a') + 0x1D44E)
            else: result += c
        return result

    def script(t: str) -> str:
        result = ""
        for c in t:
            if 'A' <= c <= 'Z': result += chr(ord(c) - ord('A') + 0x1D4D0)
            elif 'a' <= c <= 'z': result += chr(ord(c) - ord('a') + 0x1D4EA)
            else: result += c
        return result

    def double_struck(t: str) -> str:
        special_map = {'C': 'ℂ', 'H': 'ℍ', 'N': 'ℕ', 'P': 'ℙ', 'Q': 'ℚ', 'R': 'ℝ', 'Z': 'ℤ'}
        result = ""
        for c in t:
            if c in special_map: result += special_map[c]
            elif 'A' <= c <= 'Z': result += chr(ord(c) - ord('A') + 0x1D538)
            elif 'a' <= c <= 'z': result += chr(ord(c) - ord('a') + 0x1D552)
            elif '0' <= c <= '9': result += chr(ord(c) - ord('0') + 0x1D7D8)
            else: result += c
        return result

    def sans_bold(t: str) -> str:
        result = ""
        for c in t:
            if 'A' <= c <= 'Z': result += chr(ord(c) - ord('A') + 0x1D5D4)
            elif 'a' <= c <= 'z': result += chr(ord(c) - ord('a') + 0x1D5EE)
            elif '0' <= c <= '9': result += chr(ord(c) - ord('0') + 0x1D7EC)
            else: result += c
        return result

    def mono(t: str) -> str:
        result = ""
        for c in t:
            if 'A' <= c <= 'Z': result += chr(ord(c) - ord('A') + 0x1D670)
            elif 'a' <= c <= 'z': result += chr(ord(c) - ord('a') + 0x1D68A)
            elif '0' <= c <= '9': result += chr(ord(c) - ord('0') + 0x1D7F6)
            else: result += c
        return result

    def fraktur(t: str) -> str:
        special = {'C': 'ℭ', 'H': 'ℌ', 'I': 'ℑ', 'R': 'ℜ', 'Z': 'ℨ'}
        result = ""
        for c in t:
            if c in special: result += special[c]
            elif 'A' <= c <= 'Z': result += chr(ord(c) - ord('A') + 0x1D504)
            elif 'a' <= c <= 'z': result += chr(ord(c) - ord('a') + 0x1D51E)
            else: result += c
        return result

    def bold_italic_serif(t: str) -> str:
        result = ""
        for c in t:
            if 'A' <= c <= 'Z': result += chr(ord(c) - ord('A') + 0x1D468)
            elif 'a' <= c <= 'z': result += chr(ord(c) - ord('a') + 0x1D482)
            else: result += c
        return result

    DIV  = "━━━━━━━━━━━━━━━━━━━━━━━━━━"
    DIV2 = "·͜·͜·͜·͜·͜·͜·͜·͜·͜·͜·͜·͜·͜·͜·͜·͜·͜·"
    DIV3 = "⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯"
    TOP  = "╔══════════════════════════╗"
    BOT  = "╚══════════════════════════╝"
    MID  = "╠══════════════════════════╣"

    def is_owner(uid): return uid == OWNER_ID
    def is_premium(uid): return is_owner(uid) or db.is_sudo(uid, OWNER_ID)

    def uptime_str():
        e = int(time.time() - START_TIME)
        h, r = divmod(e, 3600); m, s = divmod(r, 60)
        return f"{h}h {m}m {s}s"

    def _phone_label(acct: dict) -> str:
        phone = acct.get("phone", "")
        return phone if phone else f"Account #{acct.get('slot', 0) + 1}"

    async def owner_only(update: Update) -> bool:
        if not is_owner(update.effective_user.id):
            await update.message.reply_text(
                f"{TOP}\n║  🔒  {bold_serif('Access Denied')}  🔒  ║\n{BOT}\n\n"
                f"{script('This command is restricted to')}\n👑 {sans_bold('Owners Only')}",
                parse_mode=ParseMode.MARKDOWN,
            )
            return False
        return True

    async def premium_only(update: Update) -> bool:
        if not is_premium(update.effective_user.id):
            await update.message.reply_text(
                f"🌟 {bold_serif('Premium Required')}\n\n"
                f"{script('This feature is for')}\n"
                f"👑 {sans_bold('Owners')} & {sans_bold('Premium Users')} {script('only')}\n\n"
                f"📩 {mono('Contact:')} {SUPPORT_USERNAME}",
                parse_mode=ParseMode.MARKDOWN,
            )
            return False
        return True

    async def check_blocked(update: Update) -> bool:
        if db.is_blocked(update.effective_user.id):
            await update.message.reply_text(
                f"🚫 {bold_serif('You have been Blocked')}\n\n"
                f"{script('Contact support to appeal.')}",
                parse_mode=ParseMode.MARKDOWN,
            )
            return False
        return True

    async def cleanup_pending(uid: int):
        data = pending_logins.pop(uid, None)
        if data and data.get("client"):
            try: await data["client"].disconnect()
            except: pass

    # ====================================================================
    #   /start
    # ====================================================================

    async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await check_blocked(update): return
        uid  = update.effective_user.id
        name = update.effective_user.first_name or "User"

        if not db.user_exists(uid):
            db.save_user_meta(uid, {"first_name": name, "joined_at": int(time.time())})

        accounts = db.get_accounts(uid)
        hosted   = [a for a in accounts if a.get("hosted")]
        running  = [a for a in hosted if runner.is_running(uid, a["slot"])]

        if hosted:
            status_line = (
                f"\n📱 {fraktur('Accounts')} : {mono(str(len(hosted)))} hosted  "
                f"| {mono(str(len(running)))} running"
            )
        else:
            status_line = f"\n⚪ {fraktur('Userbot')}: {italic_serif('Not hosted yet')}"

        keyboard = [
            [
                InlineKeyboardButton("🚀  𝗛𝗼𝘀𝘁 𝗠𝘆 𝗨𝘀𝗲𝗿𝗯𝗼𝘁", callback_data="host"),
                InlineKeyboardButton("📋  𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀",        callback_data="commands"),
            ],
            [
                InlineKeyboardButton("📊  𝗦𝘁𝗮𝘁𝘂𝘀",   callback_data="status"),
                InlineKeyboardButton("🗑️  𝗟𝗼𝗴𝗼𝘂𝘁",   callback_data="menu_logout"),
            ],
            [
                InlineKeyboardButton("📞  𝗦𝘂𝗽𝗽𝗼𝗿𝘁",          callback_data="support"),
                InlineKeyboardButton("❓  𝗛𝗲𝗹𝗽 & 𝗚𝘂𝗶𝗱𝗲", callback_data="help"),
            ],
        ]

        text = (
            f"{TOP}\n"
            f"║  🤖  {double_struck('SID Premium Hoster')}  🤖  ║\n"
            f"{BOT}\n\n"
            f"🌟 {script('Welcome back')}, {bold_serif(name)}!\n\n"
            f"{DIV}\n"
            f"⚡ {sans_bold('Version')}  : {mono('Advance V3')}\n"
            f"📦 {sans_bold('Commands')} : {mono('500+')}\n"
            f"⚔️ {sans_bold('Raids')}    : {mono('20 Types  1000+ Texts')}\n"
            f"{DIV}\n"
            f"🪪 {fraktur('Your ID')} : `{uid}`"
            f"{status_line}\n\n"
            f"{italic_serif('Select an option below')} 👇"
        )

        vid_id, is_gif = db.get_start_video()
        if vid_id:
            try:
                if is_gif:
                    await update.message.reply_animation(
                        animation=vid_id, caption=text, parse_mode=ParseMode.MARKDOWN,
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
                else:
                    await update.message.reply_video(
                        video=vid_id, caption=text, parse_mode=ParseMode.MARKDOWN,
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
                return
            except Exception:
                pass # Fallback to text if video fails

        await update.message.reply_text(
            text, parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    # ====================================================================
    #   /setstartvideo (Owner Only)
    # ====================================================================
    async def cmd_setstartvideo(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await owner_only(update): return
        reply = update.message.reply_to_message
        if not reply:
            return await update.message.reply_text("❌ Please reply to a Video or GIF.")
        
        if reply.animation:
            db.set_start_video(reply.animation.file_id, is_gif=True)
        elif reply.video:
            db.set_start_video(reply.video.file_id, is_gif=False)
        else:
            return await update.message.reply_text("❌ Please reply to a Video or GIF.")
            
        await update.message.reply_text("✅ Start video updated successfully! It will now play when users send `/start`.")

    # ====================================================================
    #   /help
    # ====================================================================

    async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await check_blocked(update): return
        text = (
            f"❓ {double_struck('Help')} & {double_struck('Commands')}\n"
            f"{DIV}\n\n"
            f"{'━'*3} {sans_bold('User Commands')} {'━'*3}\n\n"
            f"🔹 {mono('/start')}       {script('Grand Welcome Screen')}\n"
            f"🔹 {mono('/help')}        {script('This Help Menu')}\n"
            f"🔹 {mono('/commands')}    {script('Userbot Features List')}\n"
            f"🔹 {mono('/host')}        {script('Add & Deploy Account')}\n"
            f"🔹 {mono('/myaccounts')}  {script('Manage All Accounts')}\n"
            f"🔹 {mono('/status')}      {script('Check All Userbots')}\n"
            f"🔹 {mono('/restart')}     {script('Restart Userbot')}\n"
            f"🔹 {mono('/logout')}      {script('Logout an Account')}\n"
            f"🔹 {mono('/support')}     {script('Contact Admin')}\n\n"
            f"{DIV}\n"
            f"{'━'*3} {sans_bold('Premium Commands')} {'━'*3}\n\n"
            f"🔸 {mono('/supportraid')} {bold_italic_serif('Pro Support Raid')}\n\n"
            f"{DIV}\n"
            f"{'━'*3} 👑 {sans_bold('Owner Commands')} {'━'*3}\n\n"
            f"🔺 {mono('/setstartvideo')} {fraktur('Set Welcome Video (Reply to Video)')}\n"
            f"🔺 {mono('/restartall')}    {fraktur('Restart All Userbots')}\n"
            f"🔺 {mono('/refresh')}       {fraktur('Refresh Bot State')}\n"
            f"🔺 {mono('/sudolist')}      {fraktur('Manage Sudo Users')}\n"
            f"🔺 {mono('/setdp')}         {fraktur('Set Display Photo')}\n"
            f"🔺 {mono('/block')}         {fraktur('Block a User')}\n"
            f"🔺 {mono('/unblock')}       {fraktur('Unblock a User')}\n"
            f"🔺 {mono('/blockeduser')}   {fraktur('View Blocked List')}\n"
            f"🔺 {mono('/stats')}         {fraktur('Bot Statistics')}\n"
            f"🔺 {mono('/secretfunction')} {fraktur('Secret Commands')}\n"
            f"{DIV}"
        )
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


    # ====================================================================
    #   /commands
    # ====================================================================

    async def cmd_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await check_blocked(update): return
        text = (
            f"⚡ {double_struck('SID Advance V3')} — {script('Userbot Features')}\n"
            f"{DIV}\n\n"
            f"⚔️ {bold_serif('Raid & Fight')} {italic_serif('(20 Types  1000+ Texts)')}\n"
            f"{mono('.attack .roast .diss .war .savage')}\n"
            f"{mono('.ultra .godwar .combo .troll .shame')}\n"
            f"{mono('.fire .devil .karma .ghost .legend .doom')}\n"
            f"{mono('.nuke .storm .blizzard .venom')} ★ NEW\n\n"
            f"🔁 {bold_serif('Auto-Reply')}\n"
            f"{mono('.reply .rreply .flag .hrreply .replygod .replysid')}\n\n"
            f"💥 {bold_serif('Spam & Spray')}\n"
            f"{mono('.spray .stopspray .spam .addspam .clearspam')}\n\n"
            f"🎭 {bold_serif('Animations')} ★ NEW\n"
            f"{mono('.hack .loading .typing_anim .nukegc .matrix .glitch .neon .rainbow')}\n"
            f"{mono('.wave .spin .countdown .progress .clock .fire_anim .starfall .pulse .bounce .flip')}\n\n"
            f"🛠️ {bold_serif('Utility')}\n"
            f"{mono('.ping .alive .id .info .uptime .tts .qr .ytdl')}\n\n"
            f"🛡️ {bold_serif('Group Management')}\n"
            f"{mono('.ban .unban .mute .unmute .kick .promote .demote')}\n\n"
            f"👁️ {bold_serif('Anti-Delete & Reaction')}\n"
            f"{mono('.antidel .autoreact .fastgc')}\n\n"
            f"{DIV}\n"
            f"📦 {sans_bold('Total')}: {double_struck('500+')} {script('Commands')}  •  "
            f"{script('Prefix')}: {mono('.')}\n\n"
            f"🚀 {script('Deploy Yours')} → /host"
        )
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


    # ====================================================================
    #   /host — Phone + OTP Login Flow
    # ====================================================================

    async def cmd_host_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.callback_query:
            await update.callback_query.answer()
            reply = update.callback_query.message.reply_text
        else:
            reply = update.message.reply_text

        if not await check_blocked(update): return ConversationHandler.END
        uid = update.effective_user.id

        accounts = db.get_accounts(uid)
        hosted   = [a for a in accounts if a.get("hosted")]
        if len(hosted) >= MAX_ACCOUNTS_PER_USER:
            await reply(
                f"📱 {bold_serif('Account Limit Reached')}\n\n"
                f"{script('You already have')} {mono(str(len(hosted)))} {script('accounts hosted.')}\n"
                f"📌 {italic_serif('Maximum:')} {mono(str(MAX_ACCOUNTS_PER_USER))} {italic_serif('per user')}\n\n"
                f"🗑️ {script('Logout an account first:')} /logout",
                parse_mode=ParseMode.MARKDOWN,
            )
            return ConversationHandler.END

        total = db.hosted_count()
        if total >= MAX_USERBOTS and not is_premium(uid):
            await reply(
                f"😔 {sans_bold('Slots Full')} ({total}/{MAX_USERBOTS})\n\n"
                f"{script('Contact')} {SUPPORT_USERNAME} {script('to get a slot.')}",
                parse_mode=ParseMode.MARKDOWN,
            )
            return ConversationHandler.END

        await cleanup_pending(uid)

        extra = f"\n\n📱 {italic_serif('Account')} {mono(str(len(hosted)+1))} {italic_serif('of')} {mono(str(MAX_ACCOUNTS_PER_USER))}" if hosted else ""

        await reply(
            f"{TOP}\n"
            f"║  🚀  {bold_serif('Deploy Your Userbot')}  🚀  ║\n"
            f"{BOT}\n\n"
            f"📱 {sans_bold('Step 1 of 3')}\n"
            f"{DIV3}\n"
            f"{script('Enter your Telegram Phone Number')}\n\n"
            f"🌍 {fraktur('Format')}: {mono('+91XXXXXXXXXX')}\n"
            f"_(country code ke saath)_{extra}\n\n"
            f"🔴 {italic_serif('Send /cancel to abort')}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return ASK_PHONE


    async def host_got_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
        uid   = update.effective_user.id
        phone = update.message.text.strip()
        digits = phone.replace("+", "").replace(" ", "").replace("-", "")
        if not digits.isdigit() or len(digits) < 7:
            await update.message.reply_text(
                f"❌ {bold_serif('Invalid Number')}\n\n"
                f"{script('Please enter in format')}: {mono('+91XXXXXXXXXX')}",
                parse_mode=ParseMode.MARKDOWN,
            )
            return ASK_PHONE

        msg = await update.message.reply_text(
            f"⏳ {sans_bold('Sending OTP to Telegram')}... 📨"
        )
        try:
            client = TelegramClient(StringSession(), TELEGRAM_API_ID, TELEGRAM_API_HASH)
            await client.connect()
            result = await client.send_code_request(phone)
            pending_logins[uid] = {
                "client": client,
                "phone":  phone,
                "phone_code_hash": result.phone_code_hash,
            }
            await msg.edit_text(
                f"{TOP}\n"
                f"║  📨  {bold_serif('OTP Sent Successfully')}  📨  ║\n"
                f"{BOT}\n\n"
                f"📱 {fraktur('Number')}: {mono(phone)}\n\n"
                f"📩 {sans_bold('Step 2 of 3')}\n"
                f"{DIV3}\n"
                f"{script('Enter the Login Code from your Telegram app')}\n\n"
                f"💡 {italic_serif('Tip: Send with spaces to avoid auto-forward')}\n"
                f"    {mono('Example')}: {bold_serif('1 2 3 4 5')}",
                parse_mode=ParseMode.MARKDOWN,
            )
            return ASK_CODE
        except FloodWaitError as e:
            await cleanup_pending(uid)
            await msg.edit_text(
                f"⏳ {sans_bold('Flood Wait!')} {mono(str(e.seconds) + 's')} baad try karo."
            )
            return ConversationHandler.END
        except Exception as e:
            await cleanup_pending(uid)
            await msg.edit_text(
                f"❌ {bold_serif('Error')}\n{mono(str(e)[:120])}\n\n{script('Try again:')} /host",
                parse_mode=ParseMode.MARKDOWN,
            )
            return ConversationHandler.END


    async def host_got_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
        uid  = update.effective_user.id
        code = update.message.text.strip().replace(" ", "")

        pending = pending_logins.get(uid)
        if not pending:
            await update.message.reply_text(
                f"❌ {sans_bold('Session expired. Try /host again.')}"
            )
            return ConversationHandler.END

        client: TelegramClient = pending["client"]
        phone: str = pending["phone"]
        hash_: str = pending["phone_code_hash"]

        msg = await update.message.reply_text(f"🔐 {sans_bold('Verifying OTP')}...")
        try:
            await client.sign_in(phone, code, phone_code_hash=hash_)
            session_string = client.session.save()
            await client.disconnect()
            pending_logins.pop(uid, None)
            await _deploy_userbot(update, context, uid, session_string, phone, msg)
            return ConversationHandler.END

        except SessionPasswordNeededError:
            await msg.edit_text(
                f"{TOP}\n║  🔒  {bold_serif('2FA Detected')}  🔒  ║\n{BOT}\n\n"
                f"🛡️ {sans_bold('Step 3 of 3')}\n{DIV3}\n"
                f"{script('Your account has Two-Step Verification')}\n\n"
                f"🔑 {fraktur('Enter your 2FA Password')}:",
                parse_mode=ParseMode.MARKDOWN,
            )
            return ASK_2FA

        except PhoneCodeInvalidError:
            await msg.edit_text(
                f"❌ {bold_serif('Wrong Code!')} Dobara enter karo:\n\n"
                f"💡 {mono('Spaces ke saath')}: {bold_serif('1 2 3 4 5')}",
                parse_mode=ParseMode.MARKDOWN,
            )
            return ASK_CODE

        except PhoneCodeExpiredError:
            await cleanup_pending(uid)
            await msg.edit_text(
                f"⏳ {sans_bold('Code Expired!')} Dobara /host karo.",
                parse_mode=ParseMode.MARKDOWN,
            )
            return ConversationHandler.END

        except Exception as e:
            await cleanup_pending(uid)
            await msg.edit_text(
                f"❌ {bold_serif('Error')}\n{mono(str(e)[:120])}\n\nDobara /host karo.",
                parse_mode=ParseMode.MARKDOWN,
            )
            return ConversationHandler.END


    async def host_got_2fa(update: Update, context: ContextTypes.DEFAULT_TYPE):
        uid      = update.effective_user.id
        password = update.message.text.strip()
        pending  = pending_logins.get(uid)
        if not pending:
            await update.message.reply_text("❌ Session expire ho gayi. /host karo.")
            return ConversationHandler.END

        client: TelegramClient = pending["client"]
        phone: str = pending.get("phone", "")
        msg = await update.message.reply_text(f"🔐 {sans_bold('Verifying 2FA Password')}...")
        try:
            await client.sign_in(password=password)
            session_string = client.session.save()
            await client.disconnect()
            pending_logins.pop(uid, None)
            await _deploy_userbot(update, context, uid, session_string, phone, msg)
            return ConversationHandler.END
        except Exception as e:
            await cleanup_pending(uid)
            await msg.edit_text(
                f"❌ {bold_serif('Wrong 2FA Password')}\n"
                f"{mono(str(e)[:120])}\n\nDobara /host karo.",
                parse_mode=ParseMode.MARKDOWN,
            )
            return ConversationHandler.END


    async def _deploy_userbot(update, context, uid, session_string, phone, msg):
        name     = update.effective_user.first_name or "User"
        accounts = db.get_accounts(uid)
        existing = {a.get("slot") for a in accounts}
        slot = 0
        while slot in existing:
            slot += 1
        acc_num = slot + 1

        await msg.edit_text(
            f"⏳ {double_struck('Deploying Account')} #{acc_num}... 🔄\n{DIV2}"
        )
        ok = runner.start_userbot(
            uid, slot, str(TELEGRAM_API_ID), TELEGRAM_API_HASH, session_string, str(uid),
        )
        if ok:
            db.save_user_meta(uid, {"first_name": name})
            db.add_account(uid, {
                "slot":           slot,
                "session_string": session_string,
                "hosted":         True,
                "hosted_at":      int(time.time()),
                "phone":          phone,
            })
            await msg.edit_text(
                f"{TOP}\n║  🎉  {bold_serif('Deploy Successful')}  🎉  ║\n{BOT}\n\n"
                f"✅ {sans_bold('Account')} : {mono('#' + str(acc_num))}\n"
                f"📱 {sans_bold('Phone')}   : {mono(phone if phone else 'N/A')}\n"
                f"⚡ {sans_bold('Version')} : {mono('SID Advance V3')}\n"
                f"📦 {sans_bold('Commands')}: {mono('500+')}\n\n"
                f"{DIV}\n"
                f"🔹 {italic_serif('Kisi bhi chat mein')} {mono('.alive')} {italic_serif('bhejo')}\n"
                f"🔹 /myaccounts {italic_serif('se sab accounts dekho')}\n"
                f"🔹 /host {italic_serif('se aur account add karo')}",
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            await msg.edit_text(
                f"❌ {bold_serif('Deploy Failed')}\n\n"
                f"{script('Possible reasons:')}\n"
                f"• {fraktur('Account banned by Telegram')}\n"
                f"• {fraktur('Server error')}\n\n"
                f"📩 {sans_bold('Support')}: {SUPPORT_USERNAME}",
                parse_mode=ParseMode.MARKDOWN,
            )


    async def host_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await cleanup_pending(update.effective_user.id)
        await update.message.reply_text(
            f"🚫 {bold_serif('Login Cancelled')}\n\n"
            f"{script('Use /host to try again anytime.')}"
        )
        return ConversationHandler.END


    # ====================================================================
    #   /myaccounts
    # ====================================================================

    async def cmd_myaccounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await check_blocked(update): return
        uid      = update.effective_user.id
        accounts = db.get_accounts(uid)
        hosted   = [a for a in accounts if a.get("hosted")]

        if not hosted:
            keyboard = [[InlineKeyboardButton("🚀 Host My First Userbot", callback_data="host")]]
            await update.message.reply_text(
                f"📱 {bold_serif('No Accounts Hosted Yet')}\n\n"
                f"{script('Get started with /host')}\n"
                f"{italic_serif('Host up to')} {mono(str(MAX_ACCOUNTS_PER_USER))} {italic_serif('accounts!')}",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
            return

        lines = []
        keyboard = []
        for acct in hosted:
            slot   = acct.get("slot", 0)
            alive  = runner.is_running(uid, slot)
            uptime = runner.get_uptime(uid, slot) if alive else None
            icon   = "🟢" if alive else "🔴"
            phone  = _phone_label(acct)
            up_str = f"  ⏱️ {uptime}" if uptime else ""
            lines.append(
                f"{icon} {bold_serif('Acc #' + str(slot+1))} — {mono(phone)}{up_str}"
            )
            row = []
            if alive:
                row.append(InlineKeyboardButton(f"🔄 Restart #{slot+1}", callback_data=f"restart_acc_{slot}"))
            else:
                row.append(InlineKeyboardButton(f"▶️ Start #{slot+1}",   callback_data=f"start_acc_{slot}"))
            row.append(InlineKeyboardButton(f"🗑️ Logout #{slot+1}", callback_data=f"logout_acc_{slot}"))
            keyboard.append(row)

        if len(hosted) < MAX_ACCOUNTS_PER_USER:
            keyboard.append([InlineKeyboardButton("➕ Add Another Account", callback_data="add_acc")])

        header = (
            f"{TOP}\n"
            f"║  📱  {double_struck('My Accounts')} ({len(hosted)}/{MAX_ACCOUNTS_PER_USER})  📱  ║\n"
            f"{BOT}\n\n"
        )
        body = "\n".join(lines)
        footer = f"\n\n{DIV}\n🔹 /host {italic_serif('— add account')}"

        await update.message.reply_text(
            header + body + footer,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )


    # ====================================================================
    #   /status
    # ====================================================================

    async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await check_blocked(update): return
        uid      = update.effective_user.id
        accounts = db.get_accounts(uid)
        hosted   = [a for a in accounts if a.get("hosted")]

        if not hosted:
            await update.message.reply_text(
                f"❌ {bold_serif('No Userbot Found')}\n\n"
                f"{script('Deploy one using')} /host",
                parse_mode=ParseMode.MARKDOWN,
            )
            return

        import datetime
        lines = []
        for acct in hosted:
            slot     = acct.get("slot", 0)
            alive    = runner.is_running(uid, slot)
            uptime   = runner.get_uptime(uid, slot) if alive else "—"
            hosted_at = acct.get("hosted_at", 0)
            since = datetime.datetime.fromtimestamp(hosted_at).strftime("%d %b %Y  %H:%M") if hosted_at else "—"
            icon = "🟢" if alive else "🔴"
            phone = _phone_label(acct)
            lines.append(
                f"{icon} {sans_bold('Account #' + str(slot+1))} — {mono(phone)}\n"
                f"   ⏱️ {italic_serif('Uptime')} : {mono(uptime)}\n"
                f"   📅 {italic_serif('Hosted')} : {mono(since)}"
            )

        footer = ""
        if any(not runner.is_running(uid, a["slot"]) for a in hosted):
            footer = f"\n\n🔄 {italic_serif('Use /restart to revive stopped accounts.')}"

        await update.message.reply_text(
            f"{TOP}\n║  📊  {double_struck('Userbot Status')}  📊  ║\n{BOT}\n\n"
            + "\n\n".join(lines) +
            f"\n\n{DIV}"
            f"\n⚡ {sans_bold('Version')} : {mono('SID Advance V3')}"
            f"{footer}",
            parse_mode=ParseMode.MARKDOWN,
        )


    # ====================================================================
    #   /restart
    # ====================================================================

    async def cmd_restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await check_blocked(update): return
        uid      = update.effective_user.id
        accounts = db.get_accounts(uid)
        hosted   = [a for a in accounts if a.get("hosted")]

        if not hosted:
            await update.message.reply_text(
                f"❌ {bold_serif('No Userbot Found.')} {script('Use /host first.')}",
                parse_mode=ParseMode.MARKDOWN,
            )
            return

        if len(hosted) == 1:
            acct = hosted[0]
            slot = acct["slot"]
            await _do_restart(update, uid, slot, acct)
            return

        keyboard = []
        for acct in hosted:
            slot  = acct["slot"]
            phone = _phone_label(acct)
            alive = runner.is_running(uid, slot)
            icon  = "🟢" if alive else "🔴"
            keyboard.append([
                InlineKeyboardButton(
                    f"{icon} Restart #{slot+1} — {phone}",
                    callback_data=f"restart_acc_{slot}",
                )
            ])
        keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel_action")])

        await update.message.reply_text(
            f"🔄 {bold_serif('Which account to restart?')}\n\n"
            f"{script('Select below')} 👇",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )


    async def _do_restart(update_or_query, uid, slot, acct):
        is_cb = hasattr(update_or_query, "callback_query") and update_or_query.callback_query
        if is_cb:
            msg_obj = update_or_query.callback_query.message
            send = msg_obj.reply_text
        else:
            send = update_or_query.message.reply_text

        msg = await send(f"🔄 {sans_bold('Restarting Account')} #{slot+1}...")
        ok = runner.restart_userbot(
            uid, slot, str(TELEGRAM_API_ID), TELEGRAM_API_HASH,
            acct.get("session_string", ""), str(uid),
        )
        if ok:
            await msg.edit_text(
                f"✅ {double_struck('Account #' + str(slot+1) + ' Restarted')}!\n\n"
                f"🟢 {sans_bold('Status')}: {script('Running')}\n"
                f"⚡ {italic_serif('Test with')} {mono('.alive')}",
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            await msg.edit_text(
                f"❌ {bold_serif('Restart Failed')}\n\n"
                f"📩 {script('Contact')} {SUPPORT_USERNAME}",
                parse_mode=ParseMode.MARKDOWN,
            )


    # ====================================================================
    #   /logout
    # ====================================================================

    async def cmd_logout(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await check_blocked(update): return
        uid      = update.effective_user.id
        accounts = db.get_accounts(uid)
        hosted   = [a for a in accounts if a.get("hosted")]

        if not hosted:
            await update.message.reply_text(
                f"❌ {italic_serif('Koi active userbot nahi hai.')}"
            )
            return

        if len(hosted) == 1:
            acct = hosted[0]
            slot = acct["slot"]
            phone = _phone_label(acct)
            keyboard = [[
                InlineKeyboardButton("✅ Haan, Logout Karo", callback_data=f"confirm_logout_{slot}"),
                InlineKeyboardButton("❌ Cancel",            callback_data="cancel_action"),
            ]]
            await update.message.reply_text(
                f"⚠️ {bold_serif('Logout Confirmation')}\n\n"
                f"📱 {sans_bold('Account')} : {mono(phone)}\n\n"
                f"{script('Logout karne se session delete ho jayega.')}\n"
                f"{italic_serif('Dobara host karne ke liye /host karo.')}",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
            return

        keyboard = []
        for acct in hosted:
            slot  = acct["slot"]
            phone = _phone_label(acct)
            alive = runner.is_running(uid, slot)
            icon  = "🟢" if alive else "🔴"
            keyboard.append([
                InlineKeyboardButton(
                    f"{icon} Logout #{slot+1} — {phone}",
                    callback_data=f"logout_acc_{slot}",
                )
            ])
        keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel_action")])

        await update.message.reply_text(
            f"🗑️ {bold_serif('Kaunsa Account Logout Karna Hai?')}\n\n"
            f"{script('Select below')} 👇",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )


    async def _do_logout(uid, slot):
        """Actually perform logout for a slot."""
        runner.stop_userbot(uid, slot)
        db.remove_account(uid, slot)
        session_dir = f"data/sessions/{uid}/{slot}"
        shutil.rmtree(session_dir, ignore_errors=True)


    # ====================================================================
    #   /support
    # ====================================================================

    async def cmd_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await check_blocked(update): return
        await update.message.reply_text(
            f"{TOP}\n║  📞  {double_struck('Support Center')}  📞  ║\n{BOT}\n\n"
            f"👤 {sans_bold('Admin')}    : {SUPPORT_USERNAME}\n"
            f"⚡ {sans_bold('Response')} : {script('Fast')}\n\n"
            f"{DIV}\n"
            f"🔧 {bold_serif('Try these first:')}\n\n"
            f"🔹 /myaccounts — {italic_serif('Sab accounts dekho')}\n"
            f"🔹 /restart    — {italic_serif('Userbot restart karo')}\n"
            f"🔹 /status     — {italic_serif('Status check karo')}\n"
            f"🔹 /logout → /host — {italic_serif('Re-deploy karo')}",
            parse_mode=ParseMode.MARKDOWN,
        )


    # ====================================================================
    #   /supportraid (Premium)
    # ====================================================================

    async def cmd_supportraid(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await check_blocked(update): return
        if not await premium_only(update): return
        args   = context.args
        target = " ".join(args) if args else None
        if not target:
            await update.message.reply_text(
                f"⚔️ {bold_serif('Pro Support Raid')}\n\n"
                f"📌 {sans_bold('Usage')}: {mono('/supportraid @username')}",
                parse_mode=ParseMode.MARKDOWN,
            )
            return
        await update.message.reply_text(
            f"{TOP}\n║  ⚔️  {bold_serif('Support Raid Launched')}  ⚔️  ║\n{BOT}\n\n"
            f"🎯 {sans_bold('Target')} : {mono(target)}\n"
            f"🌪️ {script('All premium userbots activated!')}\n"
            f"⚡ {fraktur('Raid Mode')}: {double_struck('MAX POWER')}",
            parse_mode=ParseMode.MARKDOWN,
        )


    # ====================================================================
    #   Owner Commands
    # ====================================================================

    async def cmd_restartall(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await owner_only(update): return
        msg   = await update.message.reply_text(f"🔄 {sans_bold('Restarting All Userbots')}...")
        count = 0
        for uid_str in db.get_all_users():
            uid = int(uid_str)
            if db.is_blocked(uid): continue
            for acct in db.get_accounts(uid):
                if not acct.get("hosted") or not acct.get("session_string"): continue
                slot = acct["slot"]
                ok = runner.restart_userbot(
                    uid, slot, str(TELEGRAM_API_ID), TELEGRAM_API_HASH,
                    acct["session_string"], uid_str,
                )
                if ok: count += 1
        await msg.edit_text(
            f"✅ {double_struck('Restart Complete')}\n\n"
            f"🟢 {sans_bold('Restarted')}: {mono(str(count))} {script('userbots')}",
            parse_mode=ParseMode.MARKDOWN,
        )


    async def cmd_refresh(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await owner_only(update): return
        await update.message.reply_text(
            f"🔁 {bold_serif('Bot State Refreshed')}\n\n"
            f"🟢 {sans_bold('Running')} : {mono(str(runner.running_count()))}\n"
            f"📦 {sans_bold('Total')}   : {mono(str(db.hosted_count()))}\n"
            f"🕒 {sans_bold('Uptime')}  : {mono(uptime_str())}",
            parse_mode=ParseMode.MARKDOWN,
        )


    async def cmd_sudolist(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await owner_only(update): return
        args  = context.args
        sudos = db.get_sudo_users()

        if args and args[0] == "add" and len(args) > 1:
            try:
                db.add_sudo(int(args[1]))
                await update.message.reply_text(
                    f"✅ {mono(args[1])} {script('added to Sudo Users.')}",
                    parse_mode=ParseMode.MARKDOWN,
                )
            except: await update.message.reply_text("❌ Invalid ID.")
            return

        if args and args[0] == "del" and len(args) > 1:
            try:
                db.remove_sudo(int(args[1]))
                await update.message.reply_text(
                    f"✅ {mono(args[1])} {script('removed from Sudo Users.')}",
                    parse_mode=ParseMode.MARKDOWN,
                )
            except: await update.message.reply_text("❌ Invalid ID.")
            return

        if not sudos:
            await update.message.reply_text(
                f"📋 {bold_serif('No Sudo Users yet.')}\n\nAdd: {mono('/sudolist add <uid>')}",
                parse_mode=ParseMode.MARKDOWN,
            )
            return

        lines = "\n".join(f"  👑 {mono(str(u))}" for u in sudos)
        await update.message.reply_text(
            f"{TOP}\n║  👑  {double_struck('Sudo Users')} ({len(sudos)})  👑  ║\n{BOT}\n\n"
            f"{lines}\n\n{DIV}\n"
            f"➕ {mono('/sudolist add <uid>')}\n"
            f"➖ {mono('/sudolist del <uid>')}",
            parse_mode=ParseMode.MARKDOWN,
        )


    async def cmd_setdp(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await owner_only(update): return
        if not update.message.reply_to_message or not update.message.reply_to_message.photo:
            await update.message.reply_text(f"📸 {script('Kisi photo ko reply karo.')}")
            return
        photo = update.message.reply_to_message.photo[-1]
        file  = await context.bot.get_file(photo.file_id)
        data  = await file.download_as_bytearray()
        from io import BytesIO
        try:
            await context.bot.set_my_profile_photo(BytesIO(bytes(data)))
            await update.message.reply_text(f"✅ {bold_serif('Display Photo Updated')}!")
        except Exception as e:
            await update.message.reply_text(
                f"❌ {sans_bold('Failed')}: {mono(str(e)[:80])}",
                parse_mode=ParseMode.MARKDOWN,
            )


    async def cmd_block(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await owner_only(update): return
        if not context.args:
            await update.message.reply_text(
                f"📌 {sans_bold('Usage')}: {mono('/block <user_id>')}",
                parse_mode=ParseMode.MARKDOWN,
            )
            return
        try:
            target = int(context.args[0])
            if target == OWNER_ID:
                await update.message.reply_text(f"❌ {italic_serif('Owner ko block nahi kar sakte.')}")
                return
            db.block_user(target)
            runner.stop_all_for_user(target)
            await update.message.reply_text(
                f"🚫 {bold_serif('User Blocked')}\n\n"
                f"🆔 {mono(str(target))}\n"
                f"🔴 {script('All userbots stopped.')}",
                parse_mode=ParseMode.MARKDOWN,
            )
        except ValueError:
            await update.message.reply_text("❌ Invalid ID.")


    async def cmd_unblock(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await owner_only(update): return
        if not context.args:
            await update.message.reply_text(
                f"📌 {sans_bold('Usage')}: {mono('/unblock <user_id>')}",
                parse_mode=ParseMode.MARKDOWN,
            )
            return
        try:
            db.unblock_user(int(context.args[0]))
            await update.message.reply_text(
                f"✅ {bold_serif('User Unblocked')}\n🆔 {mono(context.args[0])}",
                parse_mode=ParseMode.MARKDOWN,
            )
        except ValueError:
            await update.message.reply_text("❌ Invalid ID.")


    async def cmd_blockeduser(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await owner_only(update): return
        blocked = db.get_blocked()
        if not blocked:
            await update.message.reply_text(f"✅ {script('No blocked users.')}")
            return
        lines = "\n".join(f"  🚫 {mono(str(u))}" for u in blocked)
        await update.message.reply_text(
            f"{TOP}\n║  🚫  {double_struck('Blocked Users')} ({len(blocked)})  🚫  ║\n{BOT}\n\n"
            f"{lines}",
            parse_mode=ParseMode.MARKDOWN,
        )


    async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await owner_only(update): return
        total   = db.user_count()
        hosted  = db.hosted_count()
        running = runner.running_count()
        blocked = len(db.get_blocked())
        sudos   = len(db.get_sudo_users())

        await update.message.reply_text(
            f"{TOP}\n║  📊  {double_struck('Bot Statistics')}  📊  ║\n{BOT}\n\n"
            f"👥 {sans_bold('Total Users')}    : {double_struck(str(total))}\n"
            f"🚀 {sans_bold('Hosted Accounts')}: {double_struck(str(hosted))}\n"
            f"🟢 {sans_bold('Running')}        : {double_struck(str(running))}\n"
            f"🔴 {sans_bold('Stopped')}        : {double_struck(str(hosted - running))}\n"
            f"🚫 {sans_bold('Blocked')}        : {double_struck(str(blocked))}\n"
            f"👑 {sans_bold('Sudo Users')}     : {double_struck(str(sudos))}\n"
            f"📦 {sans_bold('Max Slots')}      : {double_struck(str(MAX_USERBOTS))}\n"
            f"{DIV}\n"
            f"🕒 {sans_bold('Bot Uptime')} : {mono(uptime_str())}",
            parse_mode=ParseMode.MARKDOWN,
        )


    async def cmd_secretfunction(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await owner_only(update): return
        await update.message.reply_text(
            f"{TOP}\n║  🔐  {bold_serif('Secret Commands')}  🔐  ║\n{BOT}\n\n"
            f"🔺 {mono('/setstartvideo')}  — {fraktur('Set Welcome Video (Reply to media)')}\n"
            f"🔺 {mono('/sudolist add <uid>')}  — {fraktur('Add Premium User')}\n"
            f"🔺 {mono('/sudolist del <uid>')}  — {fraktur('Remove Premium User')}\n"
            f"🔺 {mono('/block <uid>')}         — {fraktur('Ban & Kill All Userbots')}\n"
            f"🔺 {mono('/unblock <uid>')}       — {fraktur('Unban User')}\n"
            f"🔺 {mono('/restartall')}          — {fraktur('Restart All Userbots')}\n"
            f"🔺 {mono('/refresh')}             — {fraktur('Refresh Bot State')}\n"
            f"🔺 {mono('/stats')}               — {fraktur('Full Statistics')}\n"
            f"🔺 {mono('/setdp')}               — {fraktur('Set Display Photo')}\n"
            f"🔺 {mono('/blockeduser')}         — {fraktur('View Blocked List')}\n"
            f"🔺 {mono('/secretfunction')}      — {fraktur('This Menu')}",
            parse_mode=ParseMode.MARKDOWN,
        )


    # ====================================================================
    #   CALLBACK QUERY HANDLER
    # ====================================================================

    async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        uid  = update.effective_user.id
        data = query.data

        if data == "cancel_action":
            await query.message.edit_text(f"🚫 {italic_serif('Cancelled.')}")
            return

        if data == "commands":
            await query.message.reply_text(
                f"⚡ {double_struck('SID Advance V3')} — {script('Full Commands')}\n"
                f"{DIV}\n\n"
                f"⚔️ {bold_serif('Raid & Fight')} {italic_serif('(20 Types  1000+ Texts)')}\n"
                f"{mono('.attack .roast .diss .war .savage')}\n"
                f"{mono('.ultra .godwar .combo .troll .shame')}\n"
                f"{mono('.fire .devil .karma .ghost .legend .doom')}\n"
                f"{mono('.nuke .storm .blizzard .venom')} ★ NEW\n\n"
                f"🔁 {bold_serif('Auto-Reply')}\n"
                f"{mono('.reply .rreply .flag .hrreply .replygod .replysid')}\n\n"
                f"💥 {bold_serif('Spam & Spray')}\n"
                f"{mono('.spray .stopspray .spam .addspam .clearspam')}\n\n"
                f"🎭 {bold_serif('Animations')} ★ NEW\n"
                f"{mono('.hack .loading .typing_anim .nukegc .matrix .glitch .neon .rainbow')}\n"
                f"{mono('.wave .spin .countdown .progress .clock .fire_anim .starfall .pulse .bounce .flip')}\n\n"
                f"🛠️ {bold_serif('Utility')}\n"
                f"{mono('.ping .alive .id .info .uptime .tts .qr .ytdl')}\n\n"
                f"🛡️ {bold_serif('Group Management')}\n"
                f"{mono('.ban .unban .mute .unmute .kick .promote .demote')}\n\n"
                f"👁️ {bold_serif('Anti-Delete & Reaction')}\n"
                f"{mono('.antidel .autoreact .fastgc')}\n\n"
                f"{DIV}\n"
                f"📦 {sans_bold('Total')}: {double_struck('500+')}  •  "
                f"{script('Prefix')}: {mono('.')}  •  {script('use')} /host",
                parse_mode=ParseMode.MARKDOWN,
            )
            return

        if data == "status":
            accounts = db.get_accounts(uid)
            hosted   = [a for a in accounts if a.get("hosted")]
            if not hosted:
                await query.message.reply_text(
                    f"❌ {bold_serif('No Userbot Hosted')}\n\n"
                    f"{script('Use /host to deploy your first account.')}",
                    parse_mode=ParseMode.MARKDOWN,
                )
                return
            import datetime
            lines = []
            for acct in hosted:
                slot     = acct.get("slot", 0)
                alive    = runner.is_running(uid, slot)
                uptime   = runner.get_uptime(uid, slot) if alive else "—"
                hosted_at = acct.get("hosted_at", 0)
                since = datetime.datetime.fromtimestamp(hosted_at).strftime("%d %b %Y") if hosted_at else "—"
                icon  = "🟢" if alive else "🔴"
                phone = _phone_label(acct)
                lines.append(
                    f"{icon} {sans_bold('Acc #' + str(slot+1))} — {mono(phone)}\n"
                    f"   ⏱️ {uptime}   📅 {since}"
                )
            footer = ""
            if any(not runner.is_running(uid, a["slot"]) for a in hosted):
                footer = f"\n\n🔄 {italic_serif('/restart se revive karo.')}"
            await query.message.reply_text(
                f"{TOP}\n║  📊  {double_struck('Userbot Status')}  📊  ║\n{BOT}\n\n"
                + "\n\n".join(lines) +
                f"\n\n{DIV}"
                f"\n⚡ {sans_bold('Version')} : {mono('SID Advance V3')}"
                f"{footer}",
                parse_mode=ParseMode.MARKDOWN,
            )
            return

        if data == "menu_logout":
            accounts = db.get_accounts(uid)
            hosted   = [a for a in accounts if a.get("hosted")]
            if not hosted:
                await query.message.reply_text(
                    f"❌ {italic_serif('Koi active userbot nahi hai.')}"
                )
                return
            if len(hosted) == 1:
                acct  = hosted[0]
                slot  = acct["slot"]
                phone = _phone_label(acct)
                kb = [[
                    InlineKeyboardButton("✅ Haan, Logout Karo", callback_data=f"confirm_logout_{slot}"),
                    InlineKeyboardButton("❌ Cancel",            callback_data="cancel_action"),
                ]]
                await query.message.reply_text(
                    f"⚠️ {bold_serif('Logout Confirmation')}\n\n"
                    f"📱 {sans_bold('Account')} : {mono(phone)}\n\n"
                    f"{script('Session delete ho jayega.')}\n"
                    f"{italic_serif('Dobara /host se add kar sakte ho.')}",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=InlineKeyboardMarkup(kb),
                )
            else:
                kb = []
                for acct in hosted:
                    slot  = acct["slot"]
                    phone = _phone_label(acct)
                    alive = runner.is_running(uid, slot)
                    icon  = "🟢" if alive else "🔴"
                    kb.append([InlineKeyboardButton(
                        f"{icon} Logout #{slot+1} — {phone}",
                        callback_data=f"logout_acc_{slot}",
                    )])
                kb.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel_action")])
                await query.message.reply_text(
                    f"🗑️ {bold_serif('Kaunsa Account Logout Karna Hai?')}\n\n"
                    f"{script('Select below')} 👇",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=InlineKeyboardMarkup(kb),
                )
            return

        if data == "support":
            await query.message.reply_text(
                f"{TOP}\n║  📞  {double_struck('Support Center')}  📞  ║\n{BOT}\n\n"
                f"👤 {sans_bold('Bot Owner')}  : {SUPPORT_USERNAME}\n"
                f"⚡ {sans_bold('Response')}   : {script('Fast')}\n\n"
                f"{DIV}\n"
                f"🤖 {bold_serif('Bot Owner')}: {SUPPORT_USERNAME}",
                parse_mode=ParseMode.MARKDOWN,
            )
            return

        if data == "help":
            await query.message.reply_text(
                f"╔══════════════════════════════╗\n"
                f"║  📖  {bold_serif('BOT USAGE GUIDE')}  📖  ║\n"
                f"╚══════════════════════════════╝\n\n"
                f"1. Tap 'Host My Userbot' in /start\n"
                f"2. Supply Phone Number & OTP.\n"
                f"3. Send `.ping` in any chat to check if the bot works.\n"
                f"4. For any help, contact the owner.",
                parse_mode=ParseMode.MARKDOWN,
            )
            return

        if data.startswith("restart_acc_"):
            try:
                slot = int(data.split("_")[-1])
            except ValueError:
                return
            acct = db.get_account(uid, slot)
            if not acct:
                await query.message.reply_text(f"❌ {italic_serif('Account not found.')}")
                return
            msg = await query.message.reply_text(
                f"🔄 {sans_bold('Restarting Account')} #{slot+1}..."
            )
            ok = runner.restart_userbot(
                uid, slot, str(TELEGRAM_API_ID), TELEGRAM_API_HASH,
                acct.get("session_string", ""), str(uid),
            )
            if ok:
                await msg.edit_text(
                    f"✅ {double_struck('Account #' + str(slot+1) + ' Restarted')}!\n\n"
                    f"🟢 {sans_bold('Status')}: {script('Running')}\n"
                    f"⚡ {italic_serif('Test with')} {mono('.alive')}",
                    parse_mode=ParseMode.MARKDOWN,
                )
            else:
                await msg.edit_text(f"❌ {bold_serif('Restart Failed')}\n📩 {SUPPORT_USERNAME}")
            return

        if data.startswith("start_acc_"):
            try:
                slot = int(data.split("_")[-1])
            except ValueError:
                return
            acct = db.get_account(uid, slot)
            if not acct:
                await query.message.reply_text(f"❌ {italic_serif('Account not found.')}")
                return
            msg = await query.message.reply_text(
                f"▶️ {sans_bold('Starting Account')} #{slot+1}..."
            )
            ok = runner.start_userbot(
                uid, slot, str(TELEGRAM_API_ID), TELEGRAM_API_HASH,
                acct.get("session_string", ""), str(uid),
            )
            if ok:
                await msg.edit_text(
                    f"✅ {double_struck('Account #' + str(slot+1) + ' Started')}!\n\n"
                    f"🟢 {sans_bold('Status')}: {script('Running')}\n"
                    f"⚡ {italic_serif('Test with')} {mono('.alive')}",
                    parse_mode=ParseMode.MARKDOWN,
                )
            else:
                await msg.edit_text(f"❌ {bold_serif('Start Failed')}\n📩 {SUPPORT_USERNAME}")
            return

        if data.startswith("logout_acc_"):
            try:
                slot = int(data.split("_")[-1])
            except ValueError:
                return
            acct  = db.get_account(uid, slot)
            if not acct:
                await query.message.reply_text(f"❌ {italic_serif('Account not found.')}")
                return
            phone = _phone_label(acct)
            keyboard = [[
                InlineKeyboardButton("✅ Haan, Logout Karo", callback_data=f"confirm_logout_{slot}"),
                InlineKeyboardButton("❌ Cancel",            callback_data="cancel_action"),
            ]]
            await query.message.reply_text(
                f"⚠️ {bold_serif('Logout Confirmation')}\n\n"
                f"📱 {sans_bold('Account')} #{slot+1} : {mono(phone)}\n\n"
                f"{script('Session delete ho jayega.')}\n"
                f"{italic_serif('Dobara /host se add kar sakte ho.')}",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
            return

        if data.startswith("confirm_logout_"):
            try:
                slot = int(data.split("_")[-1])
            except ValueError:
                return
            acct  = db.get_account(uid, slot)
            phone = _phone_label(acct) if acct else f"#{slot+1}"
            await _do_logout(uid, slot)
            await query.message.edit_text(
                f"{TOP}\n║  👋  {bold_serif('Logged Out')}  👋  ║\n{BOT}\n\n"
                f"📱 {sans_bold('Account')} : {mono(phone)}\n"
                f"🗑️ {sans_bold('Session')} : {script('Cleared')}\n\n"
                f"🚀 {fraktur('Re-deploy anytime:')} /host\n"
                f"📱 {fraktur('See accounts:')} /myaccounts",
                parse_mode=ParseMode.MARKDOWN,
            )
            return

        if data == "add_acc":
            accounts = db.get_accounts(uid)
            hosted   = [a for a in accounts if a.get("hosted")]
            if len(hosted) >= MAX_ACCOUNTS_PER_USER:
                await query.message.reply_text(
                    f"📱 {bold_serif('Account Limit Reached')}\n\n"
                    f"{script('Maximum')} {mono(str(MAX_ACCOUNTS_PER_USER))} {script('accounts.')}\n"
                    f"🗑️ {script('Logout one first:')} /logout",
                    parse_mode=ParseMode.MARKDOWN,
                )
                return
            await query.message.reply_text(
                f"🚀 {bold_serif('Add New Account')}\n\n"
                f"{script('Send')} /host {script('to start the login flow.')}",
                parse_mode=ParseMode.MARKDOWN,
            )
            return


    # ====================================================================
    #   AUTO HEALTH CHECK
    # ====================================================================

    async def auto_health_check(context: ContextTypes.DEFAULT_TYPE):
        for uid_str in db.get_all_users():
            uid = int(uid_str)
            if db.is_blocked(uid): continue
            for acct in db.get_accounts(uid):
                if not acct.get("hosted") or not acct.get("session_string"): continue
                slot = acct["slot"]
                if not runner.is_running(uid, slot):
                    runner.start_userbot(
                        uid, slot, str(TELEGRAM_API_ID), TELEGRAM_API_HASH,
                        acct["session_string"], uid_str,
                    )

    # ====================================================================
    #   STARTUP & MAIN
    # ====================================================================

    async def post_init(application: Application):
        await application.bot.set_my_commands([
            BotCommand("start",           "Grand Welcome"),
            BotCommand("help",            "All Commands"),
            BotCommand("commands",        "Userbot Features"),
            BotCommand("host",            "Add & Deploy Account"),
            BotCommand("myaccounts",      "Manage All Accounts"),
            BotCommand("status",          "Check Userbot Status"),
            BotCommand("restart",         "Restart Userbot"),
            BotCommand("logout",          "Logout an Account"),
            BotCommand("support",         "Get Support"),
            BotCommand("supportraid",     "Pro Raid (Premium)"),
            BotCommand("setstartvideo",   "Set Welcome Video (Owner)"),
            BotCommand("restartall",      "Restart All (Owner)"),
            BotCommand("refresh",         "Refresh State (Owner)"),
            BotCommand("sudolist",        "Sudo Users (Owner)"),
            BotCommand("setdp",           "Set Display Photo (Owner)"),
            BotCommand("block",           "Block User (Owner)"),
            BotCommand("unblock",         "Unblock User (Owner)"),
            BotCommand("blockeduser",     "Blocked List (Owner)"),
            BotCommand("stats",           "Bot Statistics (Owner)"),
            BotCommand("secretfunction",  "Secret Commands (Owner)"),
        ])
        count = 0
        for uid_str in db.get_all_users():
            uid = int(uid_str)
            if db.is_blocked(uid): continue
            for acct in db.get_accounts(uid):
                if not acct.get("hosted") or not acct.get("session_string"): continue
                ok = runner.start_userbot(
                    uid, acct["slot"], str(TELEGRAM_API_ID), TELEGRAM_API_HASH,
                    acct["session_string"], uid_str,
                )
                if ok: count += 1
        logger.info(f"[STARTUP] Auto-started {count} userbots.")

    def main():
        if not BOT_TOKEN:  raise ValueError("BOT_TOKEN not set!")
        if not OWNER_ID:   raise ValueError("OWNER_ID not set!")

        app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

        host_conv = ConversationHandler(
            entry_points=[
                CommandHandler("host", cmd_host_start),
                CallbackQueryHandler(cmd_host_start, pattern="^host$"),
            ],
            states={
                ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, host_got_phone)],
                ASK_CODE:  [MessageHandler(filters.TEXT & ~filters.COMMAND, host_got_code)],
                ASK_2FA:   [MessageHandler(filters.TEXT & ~filters.COMMAND, host_got_2fa)],
            },
            fallbacks=[CommandHandler("cancel", host_cancel)],
            allow_reentry=True,
        )

        app.add_handler(CommandHandler("start",           cmd_start))
        app.add_handler(CommandHandler("help",            cmd_help))
        app.add_handler(CommandHandler("commands",        cmd_commands))
        app.add_handler(host_conv)
        app.add_handler(CommandHandler("myaccounts",      cmd_myaccounts))
        app.add_handler(CommandHandler("status",          cmd_status))
        app.add_handler(CommandHandler("restart",         cmd_restart))
        app.add_handler(CommandHandler("logout",          cmd_logout))
        app.add_handler(CommandHandler("support",         cmd_support))
        app.add_handler(CommandHandler("supportraid",     cmd_supportraid))
        app.add_handler(CommandHandler("setstartvideo",   cmd_setstartvideo))
        app.add_handler(CommandHandler("restartall",      cmd_restartall))
        app.add_handler(CommandHandler("refresh",         cmd_refresh))
        app.add_handler(CommandHandler("sudolist",        cmd_sudolist))
        app.add_handler(CommandHandler("setdp",           cmd_setdp))
        app.add_handler(CommandHandler("block",           cmd_block))
        app.add_handler(CommandHandler("unblock",         cmd_unblock))
        app.add_handler(CommandHandler("blockeduser",     cmd_blockeduser))
        app.add_handler(CommandHandler("stats",           cmd_stats))
        app.add_handler(CommandHandler("secretfunction",  cmd_secretfunction))
        app.add_handler(CallbackQueryHandler(callback_handler))

        if app.job_queue:
            app.job_queue.run_repeating(auto_health_check, interval=300, first=60)

        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.info("🤖  SID Premium Hoster Bot STARTED!")
        logger.info(f"👑  Owner ID: {OWNER_ID}")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        app.run_polling(allowed_updates=Update.ALL_TYPES)

    if __name__ == "__main__":
        main()
