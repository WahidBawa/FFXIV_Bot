import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv
import random
import requests
import shutil

from uwu import *

from floppish import *

import time

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

client = commands.Bot(command_prefix='!')

client.remove_command("help")

commands_dict = {
    "ping": "`!ping`\n\tReturns latency in milliseconds",
    "8ball": "`!8ball <question>`\nReturns an answer to your question",
    "clear": "`!clear <num>`\nDeletes the amount of messages specified (**ADMIN ONLY**)",
    "uwu": "`!uwu <sentence>`\nConverts given sentence into UwU",
    "silence": "`!silence @user <num of minutes>m`\nPrevents user from talking in channels for a certain period of time (**ADMIN ONLY**)",
    "coinflip": "`!coinflip`\nFlip a coin",
    "help": "`!help <command>`\nprints details of specified command and if none are specified, displays all commands",
    "remindme": "`!remindme <num>(m || h) <reminder>`\nreminds the user to do the specified task after a certain amount of hours or minutes as specified by user",
    "mock": "`!mock <sentence>`\niT wIlL makE tHe MesSaGE lIkE tHIs",
    "toggle": "`!toggle <on || off>`\nToggles the random message converter (**ADMIN ONLY**)\n`!toggle status`\nreturns the toggle position (**ADMIN ONLY**)",
    "flopify": "`!flopify <text>`\nGenerates text out of flop faces",
    "emojify": "`!emojify <custom_emoji> <text>`\nGenerates text out of provided custom emoji",
    "searchify": "`!searchify <search term>`"
}

silenced_dict = dict()
reminder_dict = dict()

randomCoverter = False
reminder_counter = 0

def mockConverter(message):
    newString = ""
    for i in message:
        newString += i.upper() if rand(0, 1) == 1 else i.lower()
    return newString


def getChannelKey(channel_name):
    return int(os.getenv(channel_name))


def getCurrTime():
    return time.clock_gettime(time.CLOCK_REALTIME)


@client.event
async def on_ready():
    print("Bot is connected")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if rand(1, 5) == 3 and randomCoverter:
        await message.channel.send(mockConverter(str(message.content)) if rand(0, 1) == 1 else receive(message.content))

    if "silenced" in [y.name.lower() for y in message.author.roles]:
        if (getCurrTime() - silenced_dict[message.author.id][1]) / 60 >= silenced_dict[message.author.id][0]:
            role = discord.utils.get(message.author.guild.roles, name="Silenced")
            await (message.author).remove_roles(role)
        else:
            msg = await (message.channel).fetch_message(message.id)
            await msg.delete()

    if"silenced" not in [y.name.lower() for y in message.author.roles]:
        await client.process_commands(message)


@client.command()
async def ping(ctx):
    await ctx.send(f"Latency: {round(client.latency * 1000)}ms")

@client.command(aliases=['8ball'])
async def _8ball(ctx, *, question):
    responses = ["It is certain.", "It is decidedly so.", "Without a doubt.", "Yes - definitely.", "You may rely on it.",
                 "As I see it, yes.", "Most likely.", "Outlook good.", "Yes.", "Signs point to yes.", "Reply hazy, try again.",
                 "Ask again later.", "Better not tell you now.", "Cannot predict now.", "Concentrate and ask again.", "Don't count on it.",
                 "My reply is no.", "My sources say no.", "Outlook not so good.", "Very doubtful."]

    await ctx.send(f'Question: {question}\nAnswer: {random.choice(responses)}')


@client.command(aliases=['snap'])
@commands.has_role("ADMIN")
async def clear(ctx, amount=1):
    await ctx.channel.purge(limit=amount + 1)


@client.event
async def on_member_join(member):
    print(f'{member} has joined the server.')

@client.event
async def on_member_remove(member):
    print(f'{member} has left the server.')


@client.command()
async def uwu(ctx, *, message):
    uwu = receive(message)
    await ctx.send(uwu)


@client.command()
async def mock(ctx, *, message):
    newString = mockConverter(message)

    msg = await (ctx.message.channel).fetch_message(ctx.message.id)
    await msg.delete()

    await ctx.send(newString)


@client.command()
@commands.has_role("ADMIN")
async def toggle(ctx, input):
    global randomCoverter
    input = input.lower()
    if input == 'on':
        randomCoverter = True
        await ctx.send("The Random Converter has been turned on! Good luck :wink:")
    elif input == 'off':
        randomCoverter = False
        await ctx.send("The Random Converter has been turned off! :sob:")
    elif input == 'status':
        await ctx.send(f'Toggled to {randomCoverter}')
    else:
        await ctx.send("Incorrect Parameter!!")


@client.command()
@commands.has_role("ADMIN")
async def silence(ctx, user: discord.Member, waitTime='5m'):
    role = discord.utils.get(user.guild.roles, name="Silenced")
    await user.add_roles(role)
    currTime = time.clock_gettime(time.CLOCK_REALTIME)
    print(user.id)
    silenced_dict[user.id] = (int(waitTime.split("m")[0]), currTime)
    await ctx.send("<@" + str(user.id) + "> has been silenced for " + waitTime[:len(waitTime) - 1] + " minute(s)")


@client.command()
@commands.has_role("ADMIN")
async def do(ctx):
    await ctx.send(reminder_dict)


@client.command()
async def help(ctx, *, command=None):
    embed = discord.Embed(title="HELP", colour=0xff1333)
    if command is None:
        for i in commands_dict:
            embed.add_field(name=i, value=commands_dict[i], inline=False)
    elif command in commands_dict:
        embed.add_field(name=command, value=commands_dict[command], inline=False)
    else:
        await ctx.send("This is not an existing command")
        return
    await ctx.send(embed=embed)


@client.command()
async def remindme(ctx, waitTime, *, reminder):
    global reminder_counter
    if "m" not in waitTime and "h" not in waitTime:
        await ctx.send("Incorrect unit of time!! Please use either 'm' or 'h'")
        return
    convertedWaitTime = int(waitTime.split("m")[0]) if "m" in waitTime else int(waitTime.split("h")[0]) * 60
    reminder_dict[reminder_counter] = (
        reminder, int(convertedWaitTime), int(getCurrTime()), ctx.message.author.id, ctx.message.channel.id)
    reminder_counter += 1
    await ctx.send("Okay, <@" + str(ctx.message.author.id) + ">. I will remind you in " + str(
        convertedWaitTime if "m" in waitTime else convertedWaitTime / 60) + " " + (
                       "minute(s)" if "m" in waitTime else "hour(s)"))


@client.command()
async def flopify(ctx, *, content):
    convertFlop(content, "flop.png")
    await ctx.send(file=discord.File('dat/out.png'))


@client.command(aliases=['flip'])
async def coinflip(ctx):
    await ctx.send("https://gph.is/g/4Dk8dAp" if rand(1, 100) <= 50 else "https://gph.is/g/ZrK0wBl")


@client.command()
async def emojify(ctx, emoji: discord.Emoji, *, content):
    r = requests.get(emoji.url, stream=True)
    if r.status_code == 200:
        r.raw.decode_content = True
        with open("dat/" + emoji.name + ".png", 'wb') as f:
            shutil.copyfileobj(r.raw, f)

    print(content, emoji.name)
    convertFlop(content, emoji.name + ".png")
    await ctx.send(file=discord.File('dat/out.png'))


@client.command()
async def searchify(ctx, *, searchTerm):
    link = "https://lmgtfy.com/?q="
    link += searchTerm.replace(" ", "+")
    await ctx.send(link)


@client.command()
async def profile(ctx, world, first, last):
    await ctx.send(f'https://na.finalfantasyxiv.com/lodestone/character/?q={first}+{last}&worldname={world}&classjob=&race_tribe=&blog_lang=ja&blog_lang=en&blog_lang=de&blog_lang=fr&order=')


async def checkReminders():
    while not client.is_closed():
        await asyncio.sleep(1)
        delList = list()
        for i in reminder_dict.keys():
            if (int(getCurrTime()) - reminder_dict[i][2]) / 60 >= reminder_dict[i][1]:
                channel = client.get_channel(reminder_dict[i][4])
                await channel.send('<@' + str(reminder_dict[i][3]) + '>\n' + reminder_dict[i][0])
                delList.append(i)
        for i in delList:
            reminder_dict.pop(i)


client.loop.create_task(checkReminders())
client.run(token)