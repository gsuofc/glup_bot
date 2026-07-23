import random

import discord
from discord.ext import commands
from discord import app_commands
import logging
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

def log_to_server(message, channel_name='glup-logs'):
    guild = discord.utils.get(bot.guilds, name='globalpositioningsystem\'s server')
    if guild:
        channel = discord.utils.get(guild.text_channels, name=channel_name)
        if channel:
            bot.loop.create_task(channel.send(message))

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')
    try:
        # Syncing registers your slash commands with Discord globally
        synced = await bot.tree.sync()
        print(f"Successfully synced {len(synced)} application command(s).")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name='general')
    if channel:
        await channel.send(f'Welcome to the server, {member.mention}!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('hello'):
        #await message.delete()
        await message.channel.send(f'Hello, {message.author.mention}!')

    # if this is a DM to the bot, send message to a specific channel in the server
    if isinstance(message.channel, discord.DMChannel):
        log_to_server(f'DM from {message.author}: {message.content}', channel_name='glup-responses')

    rng_roll = random.randint(1, 100)
    #log_to_server(f'Random roll: {rng_roll}', channel_name='glup-logs')
    if rng_roll > 95:
        await message.channel.send(f'because bread tastes better than key!!!!!!!!!!')

    await bot.process_commands(message)

@bot.tree.command(name="ping", description="Check the bot's response time")
async def ping(interaction: discord.Interaction):
    # Always use interaction.response.send_message for slash commands
    await interaction.response.send_message(f"Pong! {round(bot.latency * 1000)}ms")

@bot.tree.command(name="glup", description="Glup command")
async def glup(interaction: discord.Interaction):
    # Always use interaction.response.send_message for slash commands
    await interaction.response.send_message(f"Hello I am Glup bot!")

@bot.tree.command(name="neofetch", description="Get system information")
async def neofetch(interaction: discord.Interaction):
    # Run the neofetch command and capture its output
    import subprocess
    result = subprocess.run(['neofetch', '--stdout'], capture_output=True, text=True)
    output = result.stdout
    # Send as embed to avoid message length issues
    embed = discord.Embed(title="System Information", description=f"```\n{output}\n```", color=0x00ff00)
    await interaction.response.send_message(embed=embed)

@bot.command()
async def assign(ctx):
    # Check if the role exists in the guild
    role = discord.utils.get(ctx.guild.roles, name='test')
    if role:
        member = ctx.author
        await member.add_roles(role)
        await ctx.send(f'Assigned {role.name} to {member.mention}')


@bot.command()
async def remove(ctx):
    # Check if the role exists in the guild
    role = discord.utils.get(ctx.guild.roles, name='test')
    if role:
        member = ctx.author
        await member.remove_roles(role)
        await ctx.send(f'Removed {role.name} from {member.mention}')

@bot.command()
async def dm(ctx, member: discord.Member, *, message):
    # check to see if dm disabled role is assigned
    dm_disabled_role = discord.utils.get(ctx.guild.roles, name='DM Disabled')
    if dm_disabled_role in member.roles:
        await ctx.send(f'User has DMs disabled.')
        return
    await member.send(message)
    await ctx.send(f'Sent a DM to {member.name}')

@bot.command()
async def poll(ctx, *, question):
    embed = discord.Embed(title="Poll", description=question, color=0x00ff00)
    poll_message = await ctx.send(embed=embed)
    await poll_message.add_reaction('👍')
    await poll_message.add_reaction('👎')



bot.run(token, log_handler=handler, log_level=logging.DEBUG)