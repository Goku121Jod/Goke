import discord
from discord.ext import commands
import json

with open('config.json') as f:
    config = json.load(f)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="$", intents=intents)

balances = {}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="👋 Introduction",
        description=config["help_message"],
        color=discord.Color.blue()
    )
    view = discord.ui.View()
    for button_cfg in config["help_buttons"]:
        view.add_item(
            discord.ui.Button(
                label=button_cfg["label"],
                style=getattr(discord.ButtonStyle, button_cfg["style"]),
                custom_id=button_cfg["custom_id"]
            )
        )
    await ctx.send(embed=embed, view=view)

@bot.command()
async def bal(ctx):
    user_id = str(ctx.author.id)
    balance = balances.get(user_id, 0.0)
    usd = round(balance * config["ltc_to_usd"], 2)
    embed = discord.Embed(
        title=f"{ctx.author.display_name}'s Litecoin wallet",
        description=f"**Balance**\n\n🪙 {balance:.4f} LTC (≈ ${usd:.2f})\n\nTry $balances command to see all of your balances.",
        color=discord.Color.dark_grey()
    )
    await ctx.send(embed=embed)

@bot.command()
async def setbal(ctx, user: discord.Member, amount: float):
    if str(ctx.author.id) not in config["owner_ids"]:
        return
    balances[str(user.id)] = round(amount / config["ltc_to_usd"], 8)
    await ctx.send(f"Set {user.display_name}'s balance to ${amount:.2f}.")

@bot.command()
async def tip(ctx, user: discord.Member, usd_amount: str):
    try:
        amount = float(usd_amount.strip("$"))
    except ValueError:
        await ctx.send("Invalid amount.")
        return
    ltc = round(amount / config["ltc_to_usd"], 4)
    balances[str(user.id)] = balances.get(str(user.id), 0.0) + ltc
    msg = config["tip_message"].replace("{sender}", ctx.author.mention)\
                               .replace("{receiver}", user.mention)\
                               .replace("{ltc}", f"{ltc:.4f}")\
                               .replace("{usd}", f"{amount:.2f}")
    await ctx.send(msg)

bot.run(config["token"])
  
