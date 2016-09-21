from __future__ import unicode_literals
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup
import youtube_dl
import os
import glob
import shutil
import sys
import imaplib
import getpass
import email
import datetime
from pydub import AudioSegment
from pydub.utils import make_chunks
from functools import reduce

songInfoList = ['hello adele', 'spirits strumbrellas', 'aane waala pal', 'chhaiya chhaiya', 'Neolpolitan Dreams Lisa Mitchell',
'Telegraph Ave Childish Gambino', 'Me Myself & I GEazy', 'Be Alone Gambino', 'Heartbeat Gambino', '3005 Gambino', 'Freaks and Geeks Gambino'
'Sweatpants Gambino', 'Nice Guys Nigahiga', 'Do ya like Gambino', 'Break(All of the Lights) Gambino', 'Favorite Song Chance the Rapper',
'Everyday A$AP Rocky', 'Seven Years Lukas Graham', 'Sorry JB', 'Love yourself JB', 'Forever Young Alphaville',
'Forever Young One Direction', 'Fireproof One Direction', 'Night Changes One Direction', 'Kokomo The beach boys',
'you raise me up Josh Groban', 'down under men at work', 'unsteady X Ambassadors', 'Bam Bam Sister Nancy', 'Let your heart hold fast Fort Atlantic', 
'You found me the fray', 'how to save a life the fray', "I still havent found what i'm looking for U2", 'Beautiful Day U2', 
'With or without you U2', "can't help falling in love haley reinhart", 'I Just Died in your Arms cutting crew', 'carry on wayward son kansas',
'its my life bon jovi', 'livin on a prayer bon jovi', 'safe and soung taylor swift', 'stitches shawn mendes', 'something big shawn mendes',
'ill mind of hopsin 5 hopsin', 'Keep Up Gambino', 'Smells like teen spirit nirvana', 'feeling good avicii', 
'apparently j.Cole', 'wet dreamz j.Cole', 'my hero foo fighters', 'chasing cars snow patrol', 'through the fire and the flames dragon force', 
'people keep talking hoodie allen', 'this could be us Rae Sremmurd', 'come get her rae sremmurd', 
'hero family of the year', 'wherever you go sublime', 'sirens sublime', 'right above it Lil Wayne, drake', 'home sweet home motley crue',
'holy diver dio', 'let her go mike stud', 'show me mike stud', "we can't stop timeflies tuesday", 'under the sea timeflies tuesday',
'let it go timeflies tuesday','party in the usa timeflies tuesday','lose yourself eminem', 'mockingbird eminem', 'could have been me the struts',
'my immortal evanescence', 'simple song the shins', 'not your fault Awolnation', 'the funeral band of horses', 'eye of the tiger Rocky', 
'hotel california eagles', 'the rose bette midler', 'the boys of summer the ataris', 'holding out for a hero bonnie tyler', 
'remember you Wiz khalifa', 'firework jennie lena', 'pursuit of happiness kid cudi', 'beautiful lasers lupe fiasco', 
'the show goes on lupe fiasco', "it wasn't me shaggy", 'fooled around and fell in love elvin bishop', 'come and get your love redbone',
'escape ruper holmes', 'hooked on a feeling blue swede', 'no interruption hoodie allen', 'no faith in brooklyn hoodie allen',
'into the nothing breaking benjamin', 'clouds one direction', 'forever papa roach', 'jumper third eye blind', 'my body young the giant',
'where did the angels go papa roach', 'chalk outline three days grace', 'the high road three days grace', 'iridescent linkin park',
'leave out all the rest linkin park', 'shadow of the day linkin park', 'castle of glass linkin park', 'without you breaking benjamin',
'dear agony breaking benjamin', 'i will not bow breaking benjamin', 'hero skillet', 'the diary of jane breaking benjamin', 
'mind of matter young the giant', 'cough syrup young giant', 'someone like you adele', 'i feel good', 'disturbed sound of silence', 'bromance nigahiga', 
'im gonna be duke daniel', 'one day knaan', 'man in the mirror michael jackson','lips of an angel',
'im still loving you the voice', 'to follow a river', 'calling you the voice']
# songInfoList = ['hello adele', 'spirits strumbrellas']



def fixSound(songName):

    def detect_leading_silence(sound, silence_threshold=-50.0, chunk_size=10):
        '''
        sound is a pydub.AudioSegment
        silence_threshold in dB
        chunk_size in ms

        iterate over chunks until you find the first one with sound
        '''
        trim_ms = 0 # ms
        while sound[trim_ms:trim_ms+chunk_size].dBFS < silence_threshold:
            trim_ms += chunk_size

        return trim_ms
    
    def match_target_amplitude(sound, target_dBFS):
        change_in_dBFS = target_dBFS - sound.dBFS
        return sound.apply_gain(change_in_dBFS)

    def sound_slice_normalize(sound, sample_rate, target_dBFS):
        def max_min_volume(min, max):
            for chunk in make_chunks(sound, sample_rate):
                if chunk.dBFS < min:
                    yield match_target_amplitude(chunk, min)
                elif chunk.dBFS > max:
                    yield match_target_amplitude(chunk, max)
                else:
                    yield chunk

        return reduce(lambda x, y: x + y, max_min_volume(target_dBFS[0], target_dBFS[1]))

    sound = AudioSegment.from_file("/Users/kireet/Projects/YoutubeRip/" + songName + ".mp3", format="mp3")

    start_trim = detect_leading_silence(sound)
    end_trim = detect_leading_silence(sound.reverse())

    duration = len(sound)    
    trimmed_sound = sound[start_trim:duration - end_trim]

    # trimmed_sound.export("/Users/kireet/Projects/YoutubeRip/" + songName + ".mp3", format="mp3", bitrate="192k")

    # sound = AudioSegment.from_file("/Users/kireet/Projects/YoutubeRip/Holy Diver Dio.mp3", format="mp3")

    normalized_db = min_normalized_db, max_normalized_db = [-32.0, -18.0]
    sample_rate = 1000
    normalized_sound = sound_slice_normalize(trimmed_sound, sample_rate, normalized_db)

    normalized_sound.export("/Users/kireet/Projects/YoutubeRip/" + songName + ".mp3", format="mp3", bitrate="192k")


def renameRecent(filename):
    newest = max(glob.iglob('*.[Mm][Pp]3'), key=os.path.getctime)
    os.rename(newest, filename + '.mp3')

def fileExists(filename):
    return filename in [f for f in os.listdir('.')]

def findYouTubeURL(info):
    textToSearch =  info
    query = urllib.parse.quote(textToSearch)
    url = "https://www.youtube.com/results?search_query=" + query
    response = urllib.request.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html)
    return ('https://www.youtube.com' + soup.find(attrs={'class':'yt-uix-tile-link'})['href'])

def downloadAudio(info):

    try:
        # hello = "https://www.youtube.com/watch?v=YQHsXMglC9A"
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([findYouTubeURL(info)])
            renameRecent(info)
            fixSound(info)


            shutil.copy("/Users/kireet/Projects/YoutubeRip/" + info + ".mp3", "/Users/kireet/Music/iTunes/iTunes Media/Automatically Add to iTunes.localized")
            # subprocess.getoutput("cp " + info + ".mp3 /Users/kireet/Music/iTunes/iTunes Media/Automatically Add to iTunes")
    except Exception:
        print("There was a problem downloading " + info)

def get_text_part(msg):
    maintype = msg.get_content_maintype()
    if maintype == 'multipart':
        for part in msg.get_payload():
            if part.get_content_maintype() == 'text':
                return part.get_payload()
            else:
                return get_text_part(part)
    elif maintype == 'text':
        return msg.get_payload()

def getEmailSongs(number):
    m = imaplib.IMAP4_SSL('imap.gmail.com')
    try:
        m.login('example@gmail.com', getpass.getpass())
    except imaplib.IMAP4.error:
        print("LOGIN FAILED! ")

    m.select('inbox', readonly=True)
    resp, items = m.search(None, 'ALL')
    items = items[0].split()[::-1]

    for emailid in items[:number]:
        resp, data = m.fetch(emailid, "(RFC822)")
        email_body = data[0][1]
        mail = email.message_from_string(email_body.decode("utf-8") )
        if mail["Subject"].lower() == "music":
            for x in get_text_part(mail).splitlines():
                if x not in open("songs.txt").read():
                    downloadAudio(x)
                    print(x)
                    with open("songs.txt", "a") as text_file:
                        text_file.write(x + '\n')
    m.close()
    m.logout()

getEmailSongs(10)


# downloadAudio('adele someone like you')

for songInfo in songInfoList:
    songInfo = songInfo.title()
    if not fileExists(songInfo + '.mp3'):
        downloadAudio(songInfo)
    else:
        print('Already downloaded: ' + songInfo)









