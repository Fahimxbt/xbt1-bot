from telethon import TelegramClient, events
from telethon.sessions import StringSession
import asyncio

# ========== CONFIG ==========
STRING_SESSION = '1BVtsOHkBu4fLwjsEq8x5VN0k2ab4gdzhRFBZoma4jssW1jW7R2N9-HnQdA51l5kpOoizhtsNM9f3jRhOa8VHUsR872ClCCSsUgh4Udt2AeEaqkmLWhvcmRDN9HhzTVVhwWlHBkfTpOMBavUVQ2rrT5He0nP11-B0dfBkULZxsVOVlCJHS-MNGwJUXBfsdZUMa2ARzWvq5UePsrU3rv5lC9ZQGk_9QU6OpdWnOjySPZ0f8mTYVoIrawgzVclzpzPHUKzsA5oDqRhftKvdHxpOvbz4CsmjHV3_6f66IG8I4Nz9b83wPjn-98CvrW9sY6zqcyEGbFCwTaqRoV3EJrlLAyzG_HiSBKU='
API_ID = 21142963
API_HASH = '157441cb92fd4c237664fc09d33963b9'
# ============================

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

bot_entity = None
sticker_msg_id = None
hi_msg_id = None
f_msg_id = None
match_active = False
promo_sent = False
sending_lock = False  # Prevents double-sending


async def find_sticker():
    global sticker_msg_id, hi_msg_id, f_msg_id
    try:
        msgs = await client.get_messages('me', limit=50)
        for m in msgs:
            if m.sticker:
                sticker_msg_id = m.id
                print("[+] Sticker found!")
            if m.text and m.text.lower() == 'hi':
                hi_msg_id = m.id
                print("[+] 'hi' message found!")
            if m.text and m.text.upper() == 'F':
                f_msg_id = m.id
                print("[+] 'F' message found!")
        
        if sticker_msg_id and hi_msg_id and f_msg_id:
            return True
            
    except Exception as e:
        print(f"[!] Find error: {e}")
    
    print("[!] Send 'hi', 'F', and sticker to Saved Messages first!")
    return False


async def click_next():
    global match_active, promo_sent
    try:
        msgs = await client.get_messages(bot_entity, limit=5)
        for m in msgs:
            if m.reply_markup:
                for row in m.reply_markup.rows:
                    for btn in row.buttons:
                        if 'Next' in btn.text:
                            try:
                                await m.click(text=btn.text)
                                print("[→] Next clicked")
                                match_active = False
                                promo_sent = False
                                return True
                            except:
                                continue
    except Exception as e:
        print(f"[!] get_messages error: {e}")
    
    try:
        await client.send_message(bot_entity, '/next')
        print("[→] /next sent (fallback)")
    except Exception as e:
        print(f"[!] Fallback error: {e}")
    
    match_active = False
    promo_sent = False
    return True


async def send_promo():
    global promo_sent, sending_lock
    
    # Lock to prevent double-sending
    if sending_lock or promo_sent:
        print("[*] Already sending or already sent, skipping...")
        return
    
    sending_lock = True
    print("[*] Starting forward sequence...")
    
    try:
        # Step 1: Forward "hi"
        if hi_msg_id:
            await client.forward_messages(bot_entity, hi_msg_id, 'me')
            print("[+] Forwarded: hi")
        else:
            await client.send_message(bot_entity, "hi")
            print("[+] Sent: hi")
        
        # Wait 4 seconds
        await asyncio.sleep(4)
        
        # Step 2: Forward "F"
        if f_msg_id:
            await client.forward_messages(bot_entity, f_msg_id, 'me')
            print("[+] Forwarded: F")
        else:
            await client.send_message(bot_entity, "F")
            print("[+] Sent: F")
        
        # Wait 4 seconds
        await asyncio.sleep(4)
        
        # Step 3: Forward sticker
        if sticker_msg_id:
            await client.forward_messages(bot_entity, sticker_msg_id, 'me')
            print("[+] Sticker forwarded!")
        else:
            await client.send_message(bot_entity, "💜 @chatxbt_bot\nhttps://t.me/chatxbt_bot")
            print("[+] Text promo sent!")
        
        promo_sent = True
        
        # Wait 4 seconds before next
        await asyncio.sleep(4)
        
    except Exception as e:
        print(f"[!] Send error: {e}")
    
    finally:
        sending_lock = False  # Release lock


@client.on(events.NewMessage(chats='@tikible_bot'))
async def handler(event):
    global match_active, promo_sent, sending_lock
    text = event.text or ''
    
    # Ignore messages while we're sending
    if sending_lock:
        print("[*] Currently sending, ignoring new message...")
        return
    
    if 'Match successful' in text:
        print("[+] Match started!")
        match_active = True
        promo_sent = False
        await asyncio.sleep(1)  # Small delay before starting
        await send_promo()
        await click_next()
        return
    
    if 'Finding a random partner' in text:
        print("[...] Searching...")
        match_active = False
        promo_sent = False
        return
    
    # Only respond to partner message if we haven't sent yet
    if match_active and not event.out and not promo_sent and not sending_lock:
        print("[+] Partner messaged first!")
        await send_promo()
        await click_next()


async def main():
    global bot_entity
    await client.start()
    print("[*] xbt1-bot started!")
    
    bot_entity = await client.get_entity('@tikible_bot')
    await find_sticker()
    await client.send_message(bot_entity, '/next')
    
    await client.run_until_disconnected()


with client:
    client.loop.run_until_complete(main())
