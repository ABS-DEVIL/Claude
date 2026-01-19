from pyrogram import Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant, ChatAdminRequired
from bot.utils.database import db

async def check_fsub(client: Client, user_id: int):
    """Check if user has joined all force subscribe channels"""
    fsub_channels = await db.get_all_fsub()
    
    if not fsub_channels:
        return True, None
    
    not_joined = []
    buttons = []
    
    for channel in fsub_channels:
        channel_id = channel.get("channel_id")
        channel_name = channel.get("channel_name", "Channel")
        
        try:
            member = await client.get_chat_member(channel_id, user_id)
            if member.status in ["left", "kicked"]:
                not_joined.append(channel_name)
                # Create join button
                try:
                    chat = await client.get_chat(channel_id)
                    invite_link = chat.invite_link
                    if not invite_link:
                        invite_link = f"https://t.me/{chat.username}" if chat.username else None
                    
                    if invite_link:
                        buttons.append([InlineKeyboardButton(f"Join {channel_name}", url=invite_link)])
                except:
                    pass
        except UserNotParticipant:
            not_joined.append(channel_name)
            try:
                chat = await client.get_chat(channel_id)
                invite_link = chat.invite_link
                if not invite_link:
                    invite_link = f"https://t.me/{chat.username}" if chat.username else None
                
                if invite_link:
                    buttons.append([InlineKeyboardButton(f"Join {channel_name}", url=invite_link)])
            except:
                pass
        except ChatAdminRequired:
            continue
        except Exception as e:
            print(f"Error checking fsub: {e}")
            continue
    
    if not_joined:
        buttons.append([InlineKeyboardButton("✅ I Joined, Check Again", callback_data="check_fsub")])
        return False, InlineKeyboardMarkup(buttons)
    
    return True, None

async def send_fsub_message(message: Message, keyboard):
    """Send force subscribe message"""
    fsub_text = """
🚫 <b>Arre bhai, pehle channels join kar!</b> 🚫

Mere kaam karne se pehle tu yeh channels join kar le:

⬇️ <b>Niche ke buttons pe click kar aur join kar</b> ⬇️

Join karne ke baad <b>"I Joined, Check Again"</b> pe click kar 👇

<i>Bina join kiye kuch nahi milega tujhe 😤</i>
"""
    
    await message.reply_text(
        fsub_text,
        quote=True,
        reply_markup=keyboard
    )

@Client.on_callback_query()
async def fsub_check_callback(client: Client, callback_query):
    if callback_query.data == "check_fsub":
        user_id = callback_query.from_user.id
        
        is_joined, keyboard = await check_fsub(client, user_id)
        
        if is_joined:
            await callback_query.message.delete()
            await callback_query.message.reply_text(
                "✅ <b>Sahi hai bhai! Ab tu channels join kar chuka hai</b> 🎉\n\n"
                "Ab file ya link bhej, main kaam karunga 🔥",
                quote=True
            )
        else:
            await callback_query.answer(
                "❌ Abhi bhi kuch channels pending hai bhai!\n"
                "Saare channels join kar pehle 😑",
                show_alert=True
            )
