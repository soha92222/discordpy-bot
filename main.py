import discord
from discord.ext import commands
from discord.ui import View, Button
import os
from dotenv import load_dotenv

# Load token from .env file
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Bot settings
intents = discord.Intents.default()
intents.members = True  # To receive new member info
bot = commands.Bot(command_prefix="!", intents=intents)

role_data = {
    "DPS": {"id": 1318928663538044981, "color": discord.ButtonStyle.danger},
    "Healer": {"id": 1318929499076689991, "color": discord.ButtonStyle.success},
    "Tank": {"id": 1318929973817511987, "color": discord.ButtonStyle.primary}
}

user_languages = {}

class LanguageSelectionView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(LanguageButton(label="Persian", custom_id="persian"))
        self.add_item(LanguageButton(label="English", custom_id="english"))

class LanguageButton(Button):
    def __init__(self, label, custom_id):
        super().__init__(label=label, style=discord.ButtonStyle.secondary, custom_id=custom_id)

    async def callback(self, interaction: discord.Interaction):
        user_languages[interaction.user.id] = self.custom_id
        if self.custom_id == "persian":
            await interaction.response.send_message("✅ زبان شما به فارسی تنظیم شد!", ephemeral=True)
        else:
            await interaction.response.send_message("✅ Your language has been set to English!", ephemeral=True)
        
        await send_role_selection(interaction.user)

async def send_role_selection(member):
    channel = member.guild.get_channel(1344302250020966520)
    if channel:
        view = RoleSelectionView()
        lang = user_languages.get(member.id, "english")
        
        if lang == "persian":
            await channel.send(f'🎉 خوش آمدی {member.mention}!
 لطفاً نقشی که بازی می‌کنید را انتخاب کنید:', view=view)
        else:
            await channel.send(f'🎉 Welcome {member.mention}!
 Please select the role you play:', view=view)

class RoleSelectionView(View):
    def __init__(self):
        super().__init__(timeout=None)
        
        for role_name, data in role_data.items():
            self.add_item(RoleButton(label=role_name, custom_id=str(data["id"]), style=data["color"]))

class RoleButton(Button):
    def __init__(self, label, custom_id, style):
        super().__init__(label=label, style=style, custom_id=custom_id)

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        role = discord.utils.get(guild.roles, id=int(self.custom_id))
        if role:
            await interaction.user.add_roles(role)
            lang = user_languages.get(interaction.user.id, "english")
            message = f"✅ شما نقش {role.name} را دریافت کردید!" if lang == "persian" else f"✅ You have received the {role.name} role!"
            await interaction.response.send_message(message, ephemeral=True)
        else:
            await interaction.response.send_message("❌ Role not found!", ephemeral=True)

@bot.event
async def on_ready():
    print(f'✅ {bot.user} is online!')

@bot.event
async def on_member_join(member):
    channel = member.guild.get_channel(1344302250020966520)
    if channel:
        view = LanguageSelectionView()
        await channel.send(f'🎉 Welcome {member.mention}!
 Please select your language:', view=view)

bot.run(TOKEN)
