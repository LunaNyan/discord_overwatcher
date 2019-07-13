#!/usr/bin/python3
import discord, asyncio, configparser, datetime, re, os

bot_ver = "1.0.1b"

db_path = "config.txt"

db = configparser.ConfigParser()
db.read(db_path)
print('successfully loaded configurarion file. connecting to Discord server. please wait...')

client = discord.Client()

@client.event
async def bgjob_change_playing():
    while True:
        members_sum = 0
        for s in client.servers:
            members_sum += len(s.members)
        await asyncio.sleep(10)
        await client.change_presence(game=discord.Game(name=str(members_sum) + ' users available'))
        await asyncio.sleep(10)
        await client.change_presence(game=discord.Game(name='v' + bot_ver))
        await asyncio.sleep(10)
        await client.change_presence(game=discord.Game(name=str(os.popen('uptime -p').read())))
        await asyncio.sleep(10)
        await client.change_presence(game=discord.Game(name=str(os.popen('cat /proc/loadavg').read())))
        await asyncio.sleep(10)
        await client.change_presence(game=discord.Game(name=str(os.popen('/opt/vc/bin/vcgencmd measure_temp').read())))

@client.event
async def on_ready():
    print('name    : ' + str(client.user.name))
    print('id      : ' + str(client.user.id))
    print('version : ' + bot_ver)
    client.loop.create_task(bgjob_change_playing())

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    elif message.author.bot:
        return
    if message.server.id == db.get('config', 'server_id'):
        hatespeech = re.compile(db.get("string", "hatespeech"))
        hs_match = hatespeech.match(message.content)
        if hs_match:
            await client.send_message(discord.Object(id=db.get('config', 'alert_channel_id')), "possible hate speech found at " + message.channel.name + "\n" + message.author.display_name + " : " + message.content + "\nat : " + str(datetime.datetime.now()))
        if str(message.channel.id) == db.get('config', 'shell_channel_id') and message.author.id == db.get('config', 'owner_id'):
            if message.content.startswith('cputemp'):
                await client.send_message(message.channel, str(os.popen('/opt/vc/bin/vcgencmd measure_temp').read()))
            else:
                shl_str = message.content
                shl_str = shl_str.replace('hauzen execute ','')
                try:
                    await client.send_message(message.channel, str(os.popen(shl_str).read()))
                except:
                    await client.send_message(message.channel, ':facepalm:')
    else:
        await client.leave_server(message.server)
    with open(db_path, 'w') as configfile:
        db.write(configfile)

@client.event
async def on_message_delete(message):
    if message.author == client.user:
        return
    elif message.author.bot:
        return
    await client.send_message(discord.Object(id=db.get('config', 'log_channel_id')), "message removed from " + message.author.display_name + " at " + message.channel.name + "\n" + message.content + "\nat : " + str(datetime.datetime.now()))

@client.event
async def on_message_edit(before, after):
    if before.author == client.user:
        return
    elif before.author.bot:
        return
    await client.send_message(discord.Object(id=db.get('config', 'log_channel_id')), "message edited from " + before.author.display_name + " at " + before.channel.name + "\nbefore : " + before.content + "\nafter : " + after.content + "\nat : " + str(datetime.datetime.now()))

client.run(db.get("config", "bot_token"))
