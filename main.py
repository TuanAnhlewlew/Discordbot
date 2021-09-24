import discord
import os
# load our local env so we dont have the token in public
from dotenv import load_dotenv
from discord.ext import commands
from discord.ext import tasks
from discord.utils import get
from youtube_dl import YoutubeDL
import gtts
from keep_alive import keep_alive
import itertools
import time
import random

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client = commands.Bot(command_prefix='?')  # prefix our commands 
status = itertools.cycle(['Counter Strike : Global Offensive','League of Legend'])

queues={}
playing={}

@client.event  # check if bot is ready
async def on_ready():
    change_status.start()
    print('Bot online!')


@tasks.loop(seconds=1800)
async def change_status():
  await client.change_presence(activity=discord.Game(next(status)))
  t = time.localtime()
  current_time = time.strftime("%H:%M:%S", t)
  print(current_time)


@client.command(name='join', help='join user voice')
async def join(ctx):
    try:
        channel = ctx.message.author.voice.channel
    except:
        await ctx.send('Vào voice đi đã rồi hẵng gọi tao!')
        return
    voice = get(client.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()

def check_queue(ctx,id):
    global queues
    global playing
    try:
        if queues[id]!=[]:
            voice=ctx.guild.voice_client
            source = queues[id].pop(0)
            playing.update({ctx.message.guild.id:source[1]})
            voice.play(source[0],after=lambda x=None: check_queue(ctx,ctx.message.guild.id))
            print("*** Playing : "+source[1])
        else:
            guild_id = ctx.message.guild.id
            if guild_id in playing:
                del playing[guild_id]
            if guild_id in queues:
                del queues[guild_id]
            print('END QUEUE')
    except:
        guild_id = ctx.message.guild.id
        if guild_id in playing:
            del playing[guild_id]
        if guild_id in queues:
            del queues[guild_id]
        print('END QUEUE')

@client.command(name='queue',help='+link/search thêm vào hàng chờ')
async def queue(ctx,*url):
    global queues

    YDL_OPTIONS = {
    'format': 'bestaudio',
    'noplaylist': 'True',
    '--default-search': "ytsearch"
    }
    FFMPEG_OPTIONS = {
        'before_options':
        '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn'
    }
    with YoutubeDL(YDL_OPTIONS) as ydl:
        if 'https://' in str(url[0]):
            info = ydl.extract_info(url[0], download=False)
        else:
            info = ydl.extract_info(f"ytsearch:{url}",download=False)['entries'][0]
    source= [discord.FFmpegOpusAudio(info['url'], **FFMPEG_OPTIONS),info['title']]
    guild_id = ctx.message.guild.id
    if guild_id in queues:
        queues[guild_id].append(source)
    else:
        queues[guild_id]=[source]
    embed=discord.Embed(color=0x8dcef7)
    embed.add_field(name='Add to Queue !\n',value=':musical_note: ' + info['title'], inline=True)
    embed.set_footer(text='\nadd by '+ctx.author.display_name)
    await ctx.send(embed=embed)
    print('***QUEUE*** '+info['title'])

@client.command(name='pnext', help='+link/search để phát ngay sau bài đang phát')
async def play_next(ctx, *url):
    global queues
    YDL_OPTIONS = {
    'format': 'bestaudio',
    'noplaylist': 'True',
    '--default-search': "ytsearch"
    }
    FFMPEG_OPTIONS = {
        'before_options':
        '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn'
    }
    with YoutubeDL(YDL_OPTIONS) as ydl:
        if 'https://' in str(url[0]):
            info = ydl.extract_info(url[0], download=False)
        else:
            info = ydl.extract_info(f"ytsearch:{url}",download=False)['entries'][0]
    source= [discord.FFmpegOpusAudio(info['url'], **FFMPEG_OPTIONS),info['title']]
    guild_id = ctx.message.guild.id
    if guild_id in queues:
        queues[guild_id].insert(0,source)
    else:
        queues[guild_id]=[source]
    embed=discord.Embed(color=0x8dcef7)
    embed.add_field(name='Add to Play Next !\n',value=':musical_note: ' + info['title'], inline=True)
    embed.set_footer(text='\nadd by '+ctx.author.display_name)
    await ctx.send(embed=embed)
    print('***PLAY NEXT*** '+info['title'])



@client.command(name='p', help='+link/search để phát hoặc cho vào hàng chờ')
async def play(ctx, *url):
    global queues
    global playing
    #join
    try:
        channel = ctx.message.author.voice.channel
    except:
        await ctx.send('Vào voice đi đã rồi hẵng gọi tao!')
        return
    voice = get(client.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
    YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
        }],
    'noplaylist': True,
    '--default-search': "ytsearch"
    }
    FFMPEG_OPTIONS = {
        'before_options':
        '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn'
    }
    with YoutubeDL(YDL_OPTIONS) as ydl:
        if 'https://' in str(url[0]):
            info = ydl.extract_info(url[0], download=False)
        else:
            info = ydl.extract_info(f"ytsearch:{url}",download=False)['entries'][0]
    guild_id = ctx.message.guild.id
    if voice.is_playing():
        source= [discord.FFmpegOpusAudio(info['url'], **FFMPEG_OPTIONS),info['title']]
        if guild_id in queues:
            queues[guild_id].append(source)
        else:
            queues[guild_id]=[source]
        embed=discord.Embed(color=0x8dcef7)
        embed.add_field(name='Add to Queue !\n',value=':musical_note: ' + info['title'], inline=True)
        embed.set_footer(text='\nadd by '+ctx.author.display_name)
        await ctx.send(embed=embed)
        print('***QUEUE*** '+info['title'])
    else:
        source = [discord.FFmpegOpusAudio(info['url'], **FFMPEG_OPTIONS),info['title']]
        embed=discord.Embed(color=0x8dcef7)
        embed.add_field(name='Playing music !\n',value=':musical_note: ' + str(info['title']), inline=True)
        embed.set_footer(text='\nadd by '+ctx.author.display_name)
        await ctx.send(embed=embed)
        
        print('*** PLAYING : '+info['title'])
        
        playing.update({guild_id:info['title']})
        voice.play(source[0],after=lambda x=None: check_queue(ctx,ctx.message.guild.id))

#play list from URL
@client.command(name='pl', help='+URL playlist để phát hoặc cho vào hàng chờ')
async def play_list(ctx, *url):
    global queues
    global playing
    #join
    try:
        channel = ctx.message.author.voice.channel
    except:
        await ctx.send('Vào voice đi đã rồi hẵng gọi tao!')
        return
    voice = get(client.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
    YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
        }],
    'noplaylist': False,
    'quiet': True,
    'playlistend': 10
    }
    FFMPEG_OPTIONS = {
        'before_options':
        '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn'
    }
    with YoutubeDL(YDL_OPTIONS) as ydl:
        if 'https://' in str(url[0]):
            await ctx.send('Extracting list, Please wait...')
            infos = ydl.extract_info(url[0], download=False)['entries']
            guild_id = ctx.message.guild.id
            if voice.is_playing():
                list_queue=['']
                for info in infos:
                    source= [discord.FFmpegOpusAudio(info['url'], **FFMPEG_OPTIONS),info['title']]
                    list_queue.append(info['title'])
                    print('***QUEUE*** '+info['title'])
                    if guild_id in queues:
                        queues[guild_id].append(source)
                    else:
                        queues[guild_id]=[source]

                embed=discord.Embed(color=0x8dcef7)
                embed.add_field(name='Add to Queue !',value='\n:musical_note: '.join(list_queue), inline=False)
                embed.set_footer(text='add by '+ctx.author.display_name)
                await ctx.send(embed=embed)
            else:
                first_info=infos.pop(0)
                source = [discord.FFmpegOpusAudio(first_info['url'], **FFMPEG_OPTIONS),first_info['title']]
                embed=discord.Embed(color=0x8dcef7)
                embed.add_field(name='Playing music !\n',value=':musical_note:  ' + str(first_info['title']), inline=True)
                embed.set_footer(text='\nadd by '+ctx.author.display_name)
                await ctx.send(embed=embed)
                print('***PLAYING : '+first_info['title'])
                playing.update({guild_id:first_info['title']})
                voice.play(source[0],after=lambda x=None: check_queue(ctx,ctx.message.guild.id))

                list_queue=['']
                for info in infos:
                    source= [discord.FFmpegOpusAudio(info['url'], **FFMPEG_OPTIONS),info['title']]
                    list_queue.append(info['title'])
                    print('***QUEUE*** '+info['title']) 
                    if guild_id in queues:
                        queues[guild_id].append(source)
                    else:
                        queues[guild_id]=[source]

                embed=discord.Embed(color=0x8dcef7)
                embed.add_field(name='Add to Queue !',value='\n:musical_note: '.join(list_queue), inline=False)
                embed.set_footer(text='add by '+ctx.author.display_name)
                await ctx.send(embed=embed)
        else:
            await ctx.send('Wrong link play list! Try Again...')

          
@client.command(name='playing', help='bài đang hát')
async def show_playing(ctx):
    global playing
    guild_id = ctx.message.guild.id
    if guild_id in playing:
        embed=discord.Embed(color=0x8dcef7)
        embed.add_field(name='Playing !\n',value=':musical_note: ' + playing[guild_id], inline=True)
        embed.set_footer(text='\nrequest show by '+ctx.author.display_name)
        await ctx.send(embed=embed)
    else:
        await ctx.send('Nothing is playing now !')


# command to speech from text
@client.command(name='t', help='+ message để bot nói')
async def talk(ctx, *txt):
    #join
    try:
        channel = ctx.message.author.voice.channel
        print("JOIN " + str(channel.name))
        voice = get(client.voice_clients, guild=ctx.guild)
        if voice and voice.is_connected():
            await voice.move_to(channel)
        else:
            voice = await channel.connect()
            #convert text to speech
        FFMPEG_OPTIONS = {'options': '-vn'}
        tts = gtts.gTTS(str(txt), lang="vi",slow=False)
        path = './temp/temp_sound.mp3'
        tts.save(path)
        voice.play(discord.FFmpegOpusAudio(path, **FFMPEG_OPTIONS))
        voice.is_playing()
    except:
        await ctx.send('Vào voice đi đã rồi hẵng gọi tao!')



# command to resume voice if it is paused
@client.command(name='resume', help='tiếp tục')
async def resume(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    if not voice.is_playing():
        voice.resume()
        await ctx.send('Bot is resuming!')
    print('RESUME')


# command to pause voice if it is playing
@client.command(name='pause', help='dừng')
async def pause(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice.is_playing():
        voice.pause()
        await ctx.send('Bot has been paused!')
    print('PAUSE')


# command to stop voice
@client.command(name='leave', help='cút')
async def leave(ctx):
    global playing
    global queues
    voice = get(client.voice_clients, guild=ctx.guild)
    guild_id = ctx.message.guild.id
    if voice.is_playing():
        await ctx.send('Stopping...',delete_after=2)
        voice.stop()
    if guild_id in playing:
        del playing[guild_id]
    if guild_id in queues:
        del queues[guild_id]
    await voice.disconnect()
    print('DISCONECT')


# command to clear channel messages
@client.command(name='clear', help='+ n ,xóa n tin nhắn gần nhất(default 5)')
async def clear(ctx, amount=5):
    await ctx.channel.purge(limit=amount+1)
    await ctx.send("Messages have been cleared",delete_after=5.0)
    print('CLEAR')

@client.command(name='chui')
async def chui(ctx,*ten):
    choice=random.randint(1,5)
    if choice ==1:
        await ctx.send('ĐỊT MẸ {}!'.format(' '.join(ten).upper()))
    elif choice ==2:
        await ctx.send('THẰNG {} BỐC CỨT!'.format(' '.join(ten).upper()))
    elif choice ==3:
        await ctx.send('THẰNG {} ĐẦU BUỒI QUẤN GIẺ!'.format(' '.join(ten).upper()))
    elif choice ==4:
        await ctx.send('THẰNG {} ÓC CẶC!'.format(' '.join(ten).upper()))
    elif choice ==5:
        await ctx.send('THẰNG LỒN {} BÚ BUỒI!'.format(' '.join(ten).upper()))

@client.command(name='skip', help='next')
async def skip(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice.is_playing():
        voice.stop()
        await ctx.send('SKIP!')
    print('SKIP')

keep_alive()
client.run(TOKEN)
