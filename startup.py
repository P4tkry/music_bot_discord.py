import discord
import os
import sqlite3
from datetime import datetime
from pytube import YouTube
import os
import io
import requests
import datetime
import random
from youtubesearchpython import *

def startmessage(message, word):
    commands=str(message.content).split(' ')
    if commands[0]==str(startchar)+str(word):
        return True
    return False

def checkuserperm(message,perm):
    if perm==[]:
        return True
    for permision in message.author.roles:
        if permision.id in perm:
            return True
    return False

def split_command(message):
    return str(message.content).partition(' ')[2]

async def add_to_queue(message):
    command = split_command(message)
    voice = discord.utils.get(client.voice_clients, guild=message.guild)
    if voice:
        if not voice.channel==message.author.voice.channel:
            await message.channel.send(":x: Aby wykonać tą komendę musisz być na tym samym kanale co bot", delete_after=30)
            return
    if "https://www.youtube.com/watch?" in command:
        url = command
    else:
        video_found = VideosSearch(command, limit=1)
        if video_found.result()['result']==[]:
            await musicchannel.send(":x: Nie odnaleziono takiego utworu: "+str(command), delete_after=30)
            return
        url=video_found.result()['result'][0]['link']
        title=video_found.result()['result'][0]['title']

    if len(playqueue) == 0:
        playqueue[0]=[str(url),str(title)]
        musicinfo = discord.Embed(title=":musical_note:",
                                  description="Uruchamianie muzyki na kanale " + str(message.author.voice.channel),
                                  color=0xcc8400)
        musicinfo.add_field(name="Nazwa utworu", value="["+str(title)+"]("+str(url)+")", inline=True)
        musicinfo.set_thumbnail(url=YouTube(url).thumbnail_url)
        musicinfo.set_footer(text='Komenda wywołana przez: ' + message.author.name + '\n@Na licencji P4tkry',
                             icon_url=str(author.avatar_url))
        await musicchannel.send(embed=musicinfo)
        await gotochannel(message)

    else:
        playqueue[list(playqueue.keys())[-1]+1] = [str(url), str(title)]
        musicinfo = discord.Embed(title=":arrow_heading_up: ",description="Dodano utwór do kolejki",color=0x0073cf)
        musicinfo.add_field(name="Nazwa utworu", value="["+str(title) + "]("+str(url)+")",
                            inline=False)
        musicinfo.add_field(name="Numer w kolejce", value=str(len(playqueue)),
                            inline=False)
        musicinfo.set_thumbnail(url=YouTube(url).thumbnail_url)
        musicinfo.set_footer(text='Komenda wywołana przez: ' + message.author.name + '\n@Na licencji P4tkry',
                             icon_url=str(author.avatar_url))
        await musicchannel.send(embed=musicinfo)

async def gotochannel(message):
    voice = discord.utils.get(client.voice_clients, guild=message.guild)
    user_voice_channel = message.author.voice.channel
    if not voice:
        await user_voice_channel.connect()
    play(message)

def play(message):
    if not len(playqueue)==0:
        print("play")
        ytmusic = YouTube(playqueue[list(playqueue.keys())[0]][0]).streams.filter(only_audio=True).first()
        if not os.path.isfile("music/" + str(ytmusic.default_filename)):
            ytmusic.download(filedir+"/music")
        voice = discord.utils.get(client.voice_clients, guild=message.guild)
        voice.play(discord.FFmpegPCMAudio("music/" + str(ytmusic.default_filename)), after=lambda x: next(message))

def next(message):
    if not len(playqueue)==0:
        del playqueue[list(playqueue.keys())[0]]
        play(message)

async def skip(message):
    voice = discord.utils.get(client.voice_clients, guild=message.guild)
    if len(playqueue)==0:
        await musicchannel.send(":x: Nie ma żadnych utworów na liście !", delete_after=30)
        return
    if len(playqueue)==1:
        skip_embed = discord.Embed(title=":fast_forward: ",
                                  description="Utwór pominięty",
                                  color=0xFf1919)
        skip_embed.add_field(name="Kolejny utwór", value="Brak kolejnych utworów",inline=True)
        skip_embed.set_footer(text='Komenda wywołana przez: ' + message.author.name + '\n@Na licencji P4tkry',
                             icon_url=str(author.avatar_url))
        await musicchannel.send(embed=skip_embed)
    else:
        ytmusic = YouTube(playqueue[1]).streams.filter(only_audio=True).first()
        skip_embed = discord.Embed(title=":fast_forward: ",
                                  description="Utwór pominięty",
                                  color=0xFf1919)
        skip_embed.add_field(name="Kolejny utwór", value="[" + str(ytmusic.title) + "](" + str(playqueue[1]) + ")", inline=True)
        skip_embed.set_thumbnail(url=YouTube(playqueue[1]).thumbnail_url)
        skip_embed.set_footer(text='Komenda wywołana przez: ' + message.author.name + '\n@Na licencji P4tkry',
                             icon_url=str(author.avatar_url))
        await musicchannel.send(embed=skip_embed)

    voice.stop()

async def leave(message):
    voice = discord.utils.get(client.voice_clients, guild=message.guild)
    await voice.disconnect()

async def stop(message):
    global playqueue
    voice = discord.utils.get(client.voice_clients, guild=message.guild)
    voice.stop()
    playqueue=[]
    stopmusic = discord.Embed(title=":stop_button:", description="Zatrzymano odtwarzanie", color=0xff0000)
    stopmusic.add_field(name="Zatrzymano", value="Odtwarzanie muzyki zostało zatrzymane", inline=False)
    stopmusic.set_footer(text='Komenda wywołana przez: ' + message.author.name + '\n@Na licencji P4tkry',
                         icon_url=str(author.avatar_url))
    await musicchannel.send(embed=stopmusic)

async def reporterror(message):
    dte=datetime.datetime.now()
    errorfile=open("error.log", "a")
    numer_zgoszenia=str(message.author.id)+"_"+dte.strftime("%Y:%m:%d:%H:%M:%S")
    errorfile.write(str(numer_zgoszenia)+";"+str(message.author).replace(";"," ")+";"+str(split_command(message)).replace(";"," "))
    errorfile.close()
    zgloszeniembed = discord.Embed(title=":warning:", description="Zgłoszenie błędu lub poprawki", color=0xffd700)
    zgloszeniembed.add_field(name="Numer zgłoszenia:", value=str(numer_zgoszenia), inline=False)
    zgloszeniembed.add_field(name="Zgłoszenie", value=str(split_command(message)).replace(";"," "), inline=False)
    zgloszeniembed.set_footer(text='@Na licencji P4tkry',
                             icon_url=str(author.avatar_url))
    await message.author.send(embed=zgloszeniembed)

async def playlistprint(message):
    playlist_embed=discord.Embed(title=":twisted_rightwards_arrows:", description="Informacje o kolejce odtwarzania", color=0xfff314)
    playlist_embed.set_footer(text='@Na licencji P4tkry',
                              icon_url=str(author.avatar_url))

    for muzyka in playqueue:
        playlist_embed.add_field(name=str(list(playqueue.keys()).index(muzyka)+1), value="[" + str(playqueue[muzyka][1]) + "](" + str(playqueue[muzyka][0]) + ")", inline=False)

    await musicchannel.send(embed=playlist_embed)

async def deleteelement(message):
    if not len(playqueue)==0:
        try:
            number=int(str(message.content).split(" ")[1])-1
        except:
            await message.channel.send(":exclamation: Błędny argument!!!", delete_after=30)
            return
        usunietezplaylisty_embed = discord.Embed(title=":arrow_heading_down:", description="Usunięto z kolejki odtwarzania",
                                                 color=0x8140f)
        usunietezplaylisty_embed.add_field(name=str(number+1),
                                           value="[" + str(playqueue[number][1]) + "](" + str(playqueue[number][0]) + ")",
                                           inline=False)
        usunietezplaylisty_embed.set_footer(text='Komenda wywołana przez: ' + message.author.name + '\n@Na licencji P4tkry',
                                            icon_url=str(author.avatar_url))
        try:
            del playqueue[list(playqueue.keys())[number]]
        except:
            await message.channel.send(":exclamation: Błędny argument!!!", delete_after=30)
            return

        await musicchannel.send(embed=usunietezplaylisty_embed)
    else:
        await message.channel.send(":exclamation: Lista jest pusta!!!", delete_after=30)

async def getmeme(message):
    lista_memów=os.listdir("meme")
    if len(lista_memów)==0:
        await message.channel.send(":loudspeaker: Nie ma żadnych memów bądź pierwszy i wrzuć swojego mema:grey_exclamation:", delete_after=30)
        return
    else:
        await message.channel.send(file=discord.File("meme/"+str(random.choice(lista_memów))))


async def addmeme(message):
    image_filmend = ["jpg", "png", "gif", "mp4", "mp3"]
    for attachment in message.attachments:
        if any(attachment.filename.lower().endswith(image) for image in image_filmend):
            await attachment.save("meme/"+attachment.filename)
            await message.channel.send(":star_struck: Dodano twojego mema " + str(message.author.name))
        else:
            print(message.author, "Niedozwolony format pliku", attachment.filename)
            await message.channel.send(":bangbang: Niedozwolone rozszerzenie pliku " + str(message.author), delete_after=30.0)

async def commands(message):
    if startmessage(message, "version"):
        await deletemsg(message)
        await versioninfo(message)

    if startmessage(message, "help"):
        await deletemsg(message)
        await help(message)

    if startmessage(message, "error"):
        await message.delete()
        await reporterror(message)

    if startmessage(message, "covid"):
        await deletemsg(message)
        await covidinfo(message)

    if not message.channel.type is discord.ChannelType.private:
        #
        # if startmessage(message, "meme"):
        #     await deletemsg(message)
        #     await getmeme(message)
        #
        # if startmessage(message, "addmeme"):
        #     await deletemsg(message)
        #     await addmeme(message)

        if startmessage(message,"connect"):
            await deletemsg(message)
            if not karna_ranga_muzyczna in message.author.roles:
                if message.author.voice and message.author.voice.channel:
                    try:
                        await gotochannel(message)
                    except:
                        pass
                    await message.channel.send(":arrow_upper_right:Pomyślnie dołączono do kanału głosowego", delete_after=30)
                else:
                    await message.channel.send(":x: Nie jesteś na żadnym kanale głosowym", delete_after=30)
            else:
                await message.channel.send(
                    ":x:Nie masz " + str(message.author.name) + " uprawnień do wysyłania tego typu komend",
                    delete_after=30)

        if startmessage(message,"play") or startmessage(message,"p"):
            await deletemsg(message)
            if not karna_ranga_muzyczna in message.author.roles:
                if message.author.voice and message.author.voice.channel:
                    await add_to_queue(message)
                else:
                    await message.channel.send(":x: Nie jesteś na żadnym kanale głosowym", delete_after=30)
            else:
                await message.channel.send(":x:Nie masz " + str(message.author.name) + " uprawnień do wysyłania tego typu komend",delete_after=30.0)

        if startmessage(message,"delete") or startmessage(message,"del"):
            await deletemsg(message)
            if not karna_ranga_muzyczna in message.author.roles:
                if message.author.voice and message.author.voice.channel:
                    await deleteelement(message)
                else:
                    await message.channel.send(":x: Nie jesteś na żadnym kanale głosowym", delete_after=30)
            else:
                await message.channel.send(":x:Nie masz " + str(message.author.name) + " uprawnień do wysyłania tego typu komend",delete_after=30.0)


        if startmessage(message,"skip") or startmessage(message,"fs"):
            await deletemsg(message)
            if not karna_ranga_muzyczna in message.author.roles:
                if message.author.voice and message.author.voice.channel:
                    await skip(message)
                else:
                    await message.channel.send(":x: Nie jesteś na żadnym kanale głosowym", delete_after=30)
            else:
                await message.channel.send(
                    ":x:Nie masz " + str(message.author.name) + " uprawnień do wysyłania tego typu komend",
                    delete_after=30.0)


        if startmessage(message,"leave") or startmessage(message,"dc"):
            await deletemsg(message)
            if not karna_ranga_muzyczna in message.author.roles:
                await leave(message)
            else:
                await message.channel.send(
                    ":x:Nie masz " + str(message.author.name) + " uprawnień do wysyłania tego typu komend",
                    delete_after=30.0)


        if startmessage(message,"stop") or startmessage(message,"s"):
            await deletemsg(message)
            if not karna_ranga_muzyczna in message.author.roles:
                voice = discord.utils.get(client.voice_clients, guild=message.guild)
                if voice:
                    await stop(message)
                else:
                    await message.channel.send(":exclamation: Żadna muzyka nie jest obecnie odtwarzana")
            else:
                await message.channel.send(
                    ":x:Nie masz " + str(message.author.name) + " uprawnień do wysyłania tego typu komend",
                    delete_after=30.0)

        if startmessage(message,"playlist") or startmessage(message,"ps"):
            await deletemsg(message)
            if not karna_ranga_muzyczna in message.author.roles:
                await playlistprint(message)
            else:
                await message.channel.send(
                    ":x:Nie masz " + str(message.author.name) + " uprawnień do wysyłania tego typu komend",
                    delete_after=30.0)

        if message.channel.id==music_channel:
            try:
                await message.delete()
            except:
                pass

def check_files():
    global configs
    if not os.path.isdir("music"):
        os.mkdir("music")
    if not os.path.isdir("meme"):
        os.mkdir("meme")

    if not os.path.isfile("key.wb"):
        print("brak pliku configuracyjnego")
        exit()
    configfile = open("key.wb", "r")
    configs = configfile.readlines()
    configfile.close()
    if not len(configs) == 4:
        print("Błędny plik konfiguracyjny")
        exit()
    print("checked")

def get_data(data, klucze):
    numer = 0
    date = {}
    for key in klucze:
        date[key] = data[numer]
        numer = numer + 1
    return date

async def covidinfo(message):
    command=split_command(message).lower()
    if command in ["polska", 'dolnośląskie', 'kujawsko-pomorskie', 'lubelskie', 'lubuskie', 'łódzkie', 'małopolskie', 'mazowieckie', 'opolskie', 'podkarpackie', 'podlaskie', 'pomorskie', 'śląskie', 'świętokrzyskie', 'warmińsko-mazurskie', 'wielkopolskie', 'zachodniopomorskie']:
        if command=="polska":
            command="Cały kraj"
        req = requests.get("https://www.arcgis.com/sharing/rest/content/items/153a138859bb4c418156642b5b74925b/data")
        url_content = req.content
        dane = url_content.decode("cp1250")
        linie_danych = dane.split("\r\n")
        linie_danych = linie_danych[:-1]
        tabela = {}
        klucze = linie_danych[0].split(";")
        linie_danych.pop(0)
        for woj in linie_danych:
            tmp = woj.split(";")
            tabela[tmp[0]] = get_data(tmp, klucze)
        covidembed=discord.Embed(title=":biohazard:", description="Informacje dotyczące covid-19", color=0x4B8DCA)
        covidembed.set_thumbnail(url="https://reliefweb.int/sites/reliefweb.int/files/styles/s/public/topic-icons/covid19-icon_0_0_0.png?itok=024FFUqJ")
        covidembed.add_field(name="Województwo",value=str(tabela[command]['wojewodztwo']), inline=False)
        covidembed.add_field(name="Dane na dzień", value=str(tabela[command]['stan_rekordu_na']), inline=False)
        covidembed.add_field(name="Liczba nowych zachorowań", value=str(tabela[command]['liczba_testow_z_wynikiem_pozytywnym']), inline=False)
        covidembed.add_field(name="Liczba nowych zgonów",value=str(tabela[command]['zgony']), inline=False)
        covidembed.set_footer(text='@Na licencji P4tkry', icon_url=str(author.avatar_url))
        await message.channel.send(embed=covidembed)

async def versioninfo(message):
    aboutversion = discord.Embed(title=":screwdriver:",
                                 description="1.2", color=0xfff314)
    aboutversion.add_field(name="Nazwa update",
                           value="Function update :bulb:",
                           inline=False)
    aboutversion.set_footer(text='@Na licencji P4tkry',
                            icon_url=str(author.avatar_url))
    await message.channel.send(embed=aboutversion)

async def help(message):
    helpembed = discord.Embed(title=":grey_question: ",
                                 description="Menu pomocy wersji 1.2", color=0x4245f5)
    helpembed.add_field(name="!help",
                           value="wyświetla tą informację",
                           inline=False)
    helpembed.add_field(name="!play(!p) [nazwa muzyki:url]",
                           value="puszcza muzykę na kanale głosowym",
                           inline=False)
    helpembed.add_field(name="!stop(!s)",
                           value="zatrzymuje całkowicie wszystkie muzyki",
                           inline=False)
    helpembed.add_field(name="!error [informacja]",
                           value="wysyła informację do moderacji bota w celu późniejszego zaimplementowania poprawki",
                           inline=False)
    helpembed.add_field(name="!delete(!del) [numer utworu z kolejki odtwarzania]",
                           value="usuwa konkretną muzykę z kolejki odtwarzania",
                           inline=False)
    helpembed.add_field(name="!skip(!fs)",
                           value="pomija obecnie odtwarzaną muzykę",
                           inline=False)
    helpembed.add_field(name="!leave(!dc)",
                        value="opuszcza kanał głosowy",
                        inline=False)
    helpembed.add_field(name="!playlist(!ps)",
                        value="wyświetla kolejkę odtwarzania",
                        inline=False)
    helpembed.add_field(name="!covid [nazwa województwa lub polska]",
                        value="wyświetla aktualne dane dotyczące covid-19",
                        inline=False)
    # helpembed.add_field(name="!meme",
    #                     value="wyświetla losowego mema(beta)",
    #                     inline=False)
    # helpembed.add_field(name="!addmeme [złącznik z memem]",
    #                     value="dodaje mema do bazy danych memów(beta)",
    #                     inline=False)
    helpembed.add_field(name="!version",
                        value="wyświetla informację na temat obecnej wersji bota",
                        inline=False)
    helpembed.set_footer(text='@Na licencji P4tkry',
                            icon_url=str(author.avatar_url))
    await message.author.send(embed=helpembed)

async def deletemsg(message):
    try:
        await message.delete()
    except:
        pass
check_files()
#set variables for code

filedir=os.getcwd()
client = discord.Client()
musicplaying=""
karna_ranga_muzyczna=str(configs[3].replace("\n",""))
playqueue={}
startchar=str(configs[2].replace("\n",""))
music_channel=int(configs[1].replace("\n",""))

#author id
patkryid=444547466180689920


@client.event
async def on_ready():
    global author, musicchannel
    await client.change_presence(activity=discord.Game(name="!help"))
    author = await client.fetch_user(patkryid)
    musicchannel = client.get_channel(music_channel)
@client.event
async def on_message(message):
    if message.author!=client.user:
        await commands(message)






client.run(configs[0].replace("\n",""))