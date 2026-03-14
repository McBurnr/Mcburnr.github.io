import discord
import re
from langdetect import detect_langs, LangDetectException

#I'll go step, by step, so you understand how this script works!

#FIRST: Make sure you have Python 3.9
#When installing it, make sure you check off "Install to PATH"
#And make sure it's the 64 bit version installer, which is here:
#https://www.python.org/downloads/release/python-390/
#The 64 bit version is x64 and not x86
#Once installed, check to make sure you're installed to path by, well, installing our plugins!

#Type the following into the console window (cmd window):
#pip install discord
#pip install langdetect

#You'll have to wait for each one to install, but you should be ready to start on the bot, after!

#SECOND: Well, You'll need a bot!
#You can make one right over here:
#https://discord.com/developers/applications

#SETTING UP A DISCORD BOT:
# 1) Login to your discord account, and make a developer account if need be.
# 2) Under "APPLICATIONS", click on "New Application"
# 3) Give it a name, a Team isn't necessary, but is for getting it "Verified"
# 4) Click on the checkmark and then "Create", and then you'll have a few tabs on the left. For now, take note of the Discord Provided Link and save it for later.
# 5) Click on "installation" on the left, then make sure user install has "application.commnands" and guild install has that and "bot" and save your changes.
# 6) Click on "Bot" and check off every option [EXCEPT FOR OAUTH2], the intent permissions are a requirement for a lot of the functions we need!
# 7) After saving your changes, click on "Reset Token" to get a bot token (or a new one if you have to), this will be used at the very bottom of the script.
# 8) To get the bot in your server, use the link discord conveniently provides to you in the "Installation" tab, which we mentioned earlier.
# 9) If the bot wasn't given a role already, give it one with manage message permissions, and manage message permissions if you wish for it to delete messages.

"""Our imports at the top do the following:
discord or the dispy plugin is required for every discord python bot, so we can actually get our bot working
langdetect, detect, and langdetectexception are all google plugins, which they graciously provide for free, which just tells you what language a text is in
"""
#We're getting Discord Intent Permissions, which just means read message permissions.
#It also needs manage message permissions if you want it to delete the message after, too!

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
#Here, we're just logging into the bot with the script, and logging in the console that it's all ready.
@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
#And here we're just using a whitelist regex so that URL's and stuff aren't blocked and false flagged as non-english
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    text_to_check = re.sub(r'http[s]?://\S+', '', message.content)
    text_to_check = re.sub(r'<@!?\d+>|<#\d+>|<@&\d+>', '', text_to_check)
    text_to_check = re.sub(r'<a?:\w+:\d+>', '', text_to_check)
    text_to_check = text_to_check.strip()
    
    if not text_to_check:
        return
#Right here, we're detecting any foreign characters, such as chinese, japanese, latin, russian cyrllic, and so forth
#If it conttains any, then we'll delete the message (if we have permission to) and reply to the user that it's an english speaking server
    print(f"Processing message from {message.author}: '{text_to_check}'")
    
    has_cyrillic = bool(re.search(r'[\u0400-\u04FF]', text_to_check))
    has_cjk = bool(re.search(r'[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]', text_to_check))
    has_arabic_hebrew = bool(re.search(r'[\u0590-\u06FF]', text_to_check))
    has_extended_latin = bool(re.search(r'[áéíóúñü¿¡äöüßàèìòùâêîôûëïÿç]', text_to_check, re.IGNORECASE))
    
    has_foreign_chars = has_cyrillic or has_cjk or has_arabic_hebrew or has_extended_latin
    flag_message = False
#here, we're just taking our message, stripping it down to just what they sent as a message
#we're going to send our text to google, and it will return with a country language code
    if has_foreign_chars:
        flag_message = True
        print("Detected explicit foreign characters (Kanji/Cyrillic/Spanish/etc.).")
    elif len(text_to_check) >= 3:
        try:
            langs = detect_langs(text_to_check)
            print(f"Detection results: {langs}")
            
            top_lang = langs[0]
            en_prob = next((l.prob for l in langs if l.lang == 'en'), 0.0)
            word_count = len(text_to_check.split())
#If it's not english, then we'll send our reply...as long as we have permission, of course!
#That being read permissions for the messages, and if we have manage message permissions, we'll delete it too, after making our reply
#You may change the message to send to the user under "message.author.mention"
#I've included a lot of console logs so you understand exactly what happens, why it happens, etc.            
            if top_lang.lang != 'en' and top_lang.prob > 0.85 and en_prob < 0.1:
                if word_count > 2:
                    flag_message = True
        except LangDetectException:
            print("Could not detect language (likely just numbers/symbols).")
        except Exception as e:
            print(f"Language detection error: {e}")
            
    if flag_message:
        print("Flagged as non-English. Taking action...")
        try:
            await message.delete()
            print("Message deleted successfully.")
        except discord.Forbidden:
            print(f"Error: Missing 'Manage Messages' permission to delete message from {message.author}.")
        except discord.HTTPException as e:
            print(f"HTTP Error deleting message: {e}")
        
        try:
            await message.channel.send(
                f"{message.author.mention} This is an english only server. You may use a MTL or translation service of your choice if need be.\n"
                "You may read the rules here: https://discord.com/channels/833766773462794260/1271133297367584768/1438102157743095868"
            )
            print("Warning message sent.")
        except Exception as e:
            print(f"Error sending warning: {e}")
    else:
        print("Passed English check.")
#And right here is just running our bot with the token.
#IMPORTANT: DO NOT EVER SHARE YOUR BOT TOKEN!
#THEY CAN CONTROL YOUR BOT IF IT EVER GETS OUT!
#I did not include anything here, so you'll have to set it up yourself, or I can run it on my end!
if __name__ == "__main__":
    try:
        client.run("YOUR_BOT_TOKEN_HERE")
    except Exception as e:
        print(f"Bot login error: {e}")