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

    await bot.process_commands(message)

@bot.tree.command(name="ping", description="Check the bot's response time")
async def ping(interaction: discord.Interaction):
    # Always use interaction.response.send_message for slash commands
    await interaction.response.send_message(f"Pong! {round(bot.latency * 1000)}ms")

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
    await member.send(message)
    await ctx.send(f'Sent a DM to {member.mention}')

@bot.command()
async def poll(ctx, *, question):
    embed = discord.Embed(title="Poll", description=question, color=0x00ff00)
    poll_message = await ctx.send(embed=embed)
    await poll_message.add_reaction('👍')
    await poll_message.add_reaction('👎')


bot.run(token, log_handler=handler, log_level=logging.DEBUG)