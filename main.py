from telethon import TelegramClient, events
from telethon.sessions import StringSession
import asyncio
from flask import Flask
from threading import Thread

# PASTE YOUR STRING SESSION HERE
STRING_SESSION = '1BVtsOHgBu60QAahD6ILkOhmE5sm9LmkBaKt002pQlFD8Yk9GT7CST8Fq-E6W_IVn4fQfd5W-uqWZdMmR1tfWf3JM_rdZkYKhvO0VAIoeY9JsedAtqUu3o9aZ-dLkMdapWM0jY9GrJrU8rh-wBOoXMGkUfIFniHvehNTwp0BgDo_If9fWnK_L49hucHCMRNXPiZOp7SPfTJ5gwUDcxa7PKXrlX8O7VeLkJhvOqv-NOdEc1MQ4mDmJb91QRR65PKtCuQjuzUSLL7gEFvLUXo2bTsqI-x5eYhrDxFGOxdOA8U3oRdMpxg4lD7TOdvJpxX1I_gOW6yL0laOFtC6k6-j6ttrS6KWA82E='

API_ID = 21142963
API_HASH = '157441cb92fd4c237664fc09d33963b9'

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

bot_entity = None
sticker_msg_id = None
match_active = False
promo_sent = False


async def find_sticker():
    global sticker_msg_id
    msgs = await client.get_messages('me', limit=30)
    for m in msgs:
        if m.sticker:
            sticker_msg_id = m.id
            print("[+] Sticker found!")
            return True
    print("[!] No sticker in Saved Messages!")
    return False


async def click_next():
    global match_active, promo_sent
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
                            pass
    await client.send_message(bot_entity, '/next')
    print("[→] /next sent")
    match_active = False
    promo_sent = False
    return True


async def send_promo():
    global promo_sent
    if promo_sent:
        return
    print("[*] Sending promo...")
    try:
        if sticker_msg_id:
            await client.forward_messages(bot_entity, sticker_msg_id, 'me')
        else:
            await client.send_message(bot_entity, "💜 @chatxbt_bot\nhttps://t.me/chatxbt_bot")
        print("[+] Promo sent!")
        promo_sent = True
    except Exception as e:
        print(f"[!] Error: {e}")


@client.on(events.NewMessage(chats='@tikible_bot'))
async def handler(event):
    global match_active, promo_sent
    text = event.text or ''
    
    if 'Match successful' in text:
        print("[+] Match started!")
        match_active = True
        promo_sent = False
        await asyncio.sleep(0.5)
        await send_promo()
        await asyncio.sleep(5)
        await click_next()
        return
    
    if 'Finding a random partner' in text:
        print("[...] Searching...")
        match_active = False
        return
    
    if match_active and not event.out and not promo_sent:
        print("[+] Partner messaged first!")
        await send_promo()
        await asyncio.sleep(5)
        await click_next()


async def main():
    global bot_entity
    await client.start()
    print("[*] xbt1-bot started!")
    
    bot_entity = await client.get_entity('@tikible_bot')
    await find_sticker()
    await client.send_message(bot_entity, '/next')
    
    await client.run_until_disconnected()


# Start keep-alive server
keep_alive()

# Start bot
with client:
    client.loop.run_until_complete(main())
