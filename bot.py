import os
import discord
from discord import client
from discord.guild import Guild
from discord.member import Member

TOKEN = os.getenv('DISCORD_TOKEN')


class CustomClient(discord.Client):
    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')

    async def on_message(self,message):
        if message.author == self.user:
            return
        if str(message.author) in ["HUNG NGUYEN#1703","_Tũn_#7554","Swordemon#0748","HandsomeGuy#7944","Dat-Tiger#8553","meesaa#3384"]:
            print("bot said")
            await message.channel.send('Dit Me '+str(message.author.display_name) +'!')
            # await message.channel.send('Tuấn Anh đẹp trai!')


a=CustomClient()
a.run(TOKEN)