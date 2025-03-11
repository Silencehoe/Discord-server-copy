import discord
from discord.ext import commands

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def clone(ctx):
    """Clone the server structure into a new server with topics and slow mode"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You need to be an admin to use this command!")
        return

    original_guild = ctx.guild
    new_guild = await bot.create_guild(f"Copy of {original_guild.name}")
    
    await ctx.send(f"New server created: {new_guild.name}. Now copying roles and channels...")

    # Copy roles (excluding @everyone)
    role_mapping = {}
    for role in original_guild.roles[::-1]:  # Reverse to maintain hierarchy
        if role.name != "@everyone":
            new_role = await new_guild.create_role(
                name=role.name,
                permissions=role.permissions,
                colour=role.colour,
                hoist=role.hoist,
                mentionable=role.mentionable
            )
            role_mapping[role] = new_role
    
    # Copy categories and channels
    for category in original_guild.categories:
        new_category = await new_guild.create_category(category.name)
        for channel in category.channels:
            overwrites = {
                role_mapping.get(target, target): overwrite
                for target, overwrite in channel.overwrites.items()
            }
            if isinstance(channel, discord.TextChannel):
                await new_guild.create_text_channel(
                    name=channel.name, 
                    category=new_category, 
                    overwrites=overwrites, 
                    topic=channel.topic, 
                    slowmode_delay=channel.slowmode_delay
                )
            elif isinstance(channel, discord.VoiceChannel):
                await new_guild.create_voice_channel(
                    name=channel.name, 
                    category=new_category, 
                    overwrites=overwrites, 
                    bitrate=channel.bitrate, 
                    user_limit=channel.user_limit
                )

    await ctx.send("Server clone complete with topics and slow mode!")

bot.run("YOUR_BOT_TOKEN")
