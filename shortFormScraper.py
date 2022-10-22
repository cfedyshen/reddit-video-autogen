import math
import random
import textwrap
import gtts
import praw
import sys
from moviepy.config import change_settings
from moviepy.editor import *
from mutagen.mp3 import MP3
from playsound import playsound

change_settings({"IMAGEMAGICK_BINARY": "/usr/local/Cellar/imagemagick/7.1.0-45/bin/convert"})
reddit = praw.Reddit(client_id='VvZmirE6QeTEHc3dJZesEg', client_secret='V0JU73dWYxET7UveT7KjjEs7n_MbNw', user_agent='test')

subName = sys.argv[1]
postNo = int(sys.argv[2])

#finds the postNo post in the subreddit and returns the setup and punchline
def getJoke(subreddit, postNumber):
    hot_posts = reddit.subreddit(subName).hot(limit=postNumber)
    iterator = 0
    for post in hot_posts:
        if iterator == postNumber-1:
            return post.title, post.selftext
        iterator = iterator + 1

setup, punchline = getJoke(subName, postNo)


#generates speech from text and saves it as mp3
def speak(filename, words):
    # make request to google to get synthesis
    tts = gtts.gTTS(words,lang="en-au")
    # save the audio file
    tts.save(filename +".mp3")

speak("setup", setup)
speak("punchline", punchline)

mutagen = MP3("setup.mp3")
setupLen = mutagen.info.length
mutagen = MP3("punchline.mp3")
punchLen = mutagen.info.length
totalLen = setupLen + punchLen

noOfClips = math.ceil(totalLen) / 10
fullClips = math.floor(noOfClips)
finalClipLen = math.ceil((noOfClips - fullClips) *10)
print("NO of Clips: " + str(noOfClips) + " full: " +str(fullClips) + " final Clip Len: " + str(finalClipLen) )
# generates a list of video names from file names startig with vid
vidNames = []
for file in os.listdir("."):
    if file.startswith("vid"):
        vidNames.append(file)
random.shuffle(vidNames)

def makeClip(length, name):
    clip = VideoFileClip(vidNames[name])
    clip = clip.rotate(90)
    # getting video for only starting 10 seconds
    clip = clip.subclip(0, length)
    return clip

def videogen():
    # loading video
    clipArray = []
    rand = random.randint(0, len(vidNames) - 1)
    for segment in range(fullClips):
        clipArray.append(makeClip(10, rand))
        rand = rand + 1
        if rand == len(vidNames):
            rand = 0
    clipArray.append(makeClip(finalClipLen, rand))
    finalClip = concatenate_videoclips(clipArray)
    # loading audio file
    setupClip = AudioFileClip("setup.mp3")
    punchClip = AudioFileClip("punchline.mp3")
    finalAudioClip = concatenate_audioclips([setupClip, punchClip])
    # add audio to clip
    finalClip = finalClip.set_audio(finalAudioClip)
    # Generate a text clip

    # wrap text of setup
    line1 = textwrap.fill(setup, width=34)
    line2 = textwrap.fill(punchline, width=34)
    txt_clip = TextClip(line1, fontsize=52, color='white')
    txt_clip2 = TextClip(line2, fontsize=52, color='white')

    # setting position of text in the center and duration will be the length of the first audio clip
    txt_clip = txt_clip.set_pos('center').set_duration(setupLen)
    txt_clip2 = txt_clip2.set_pos('center').set_duration(punchLen)
    finaltxtClip = concatenate_videoclips([txt_clip, txt_clip2])
    finaltxtClip = finaltxtClip.set_pos('center')

    # Overlay the text clip on the first video clip
    video = CompositeVideoClip([finalClip, finaltxtClip])

    # exporting video
    FinalVideoName = subName+str(postNo)+".mp4"
    print(FinalVideoName)
    video.write_videofile(FinalVideoName, temp_audiofile="temp-audio.m4a", remove_temp=True, codec="libx264", audio_codec="aac")

videogen()

