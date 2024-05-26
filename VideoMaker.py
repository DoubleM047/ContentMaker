# Libraries

from openai import OpenAI
import requests
import urllib.request 
from PIL import Image
from pathlib import Path
from moviepy.editor import *
from openai import OpenAI
import requests
import urllib.request 
from PIL import Image
from pathlib import Path
from moviepy.editor import *
import random
import ffmpeg
from faster_whisper import WhisperModel
import assemblyai as aai
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.editor import TextClip, CompositeVideoClip, VideoFileClip
import moviepy.audio.fx.all as afx
from moviepy.audio.fx import *
from moviepy.audio.fx.all import volumex

# API keys

client = OpenAI(api_key = str(open("OPENAI_KEY.txt", "r").read().strip()))
aai.settings.api_key = str(open("AAI_KEY.txt", "r").read().strip())

# Get the video script

response = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "user", "content": "Can you pretend that you are a youtuber and make a script for a 40 second video that will provide a fun fact for the people watching and only type the spoken text please not the whole script. The fact should be about " + str(input("Fact about:"))},
  ]
)

tekst1 = response.choices[0].message.content # Save script into tekst1

# Pick 3 key phrases from the script to make into images

response2 = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "user", "content": "now could you pick 3 key phrases that would represent this fact well as pictures and enhance them for better image generation and pass them to me in this format:[fact - fact - fact]. Make sure there are 3 and that they are seperated with - do it from this text:" + tekst1},
  ]
)

tekst2 = response2.choices[0].message.content #save the 3 key phrases into tekst2
sez = tekst2.split("-") #split the 3 phrases into a list with 3 elements (seperated by -)

# Image generation

image1 = client.images.generate(
  model="dall-e-2",
  prompt=sez[0],
  size="512x512",
  quality="standard",
  n=1)
image_url1 = image1.data[0].url
urllib.request.urlretrieve(image_url1, "1.png") # Save image 1 as 1.png
img1 = Image.open(r"1.png") # Opening the image and displaying it (to confirm its presence) 


image2 = client.images.generate(
  model="dall-e-2",
  prompt=sez[1],
  size="512x512",
  quality="standard",
  n=1)
image_url2 = image2.data[0].url
urllib.request.urlretrieve(image_url2, "2.png")
img2 = Image.open(r"2.png") 


image3 = client.images.generate(
  model="dall-e-2",
  prompt=sez[2],
  size="512x512",
  quality="standard",
  n=1)
image_url3 = image3.data[0].url
urllib.request.urlretrieve(image_url3, "3.png")
img3 = Image.open(r"3.png")


# Generate a voiceover with text to speech

response = client.audio.speech.create(
    model="tts-1",
    voice="shimmer",
    input=tekst1, 
)

response.stream_to_file("speech.mp3") # Save voiceover to speech.mp3

# Set clips

audioclip = AudioFileClip("speech.mp3")
music = AudioFileClip("music.mp3")
clip = VideoFileClip("background.mp4") # The backgroud used as the main clip which we paste everything else over

#Create subtitles from voiceover

transcript = aai.Transcriber().transcribe("speech.mp3")
subtitles = transcript.export_subtitles_srt(chars_per_caption=15)

# Save subtitles to subtitles.srt

f = open("subtitles.srt", "w")
f.write(subtitles.lower().replace(".", ""))
f.flush()
f.close

# Set some random points to determine where to start the random clip from the video and background music

dur = int(audioclip.duration)  #duration of voiceover
point = random.randint(0, 1852-dur-10)
musicPoint = random.randint(0, 3400)
 
# Cut down the clips to the right length

clip = clip.subclip(point, point+dur+0.5)
music = music.subclip(musicPoint, musicPoint+dur)

# Adjust the volume of voiceover and background music 

music = afx.volumex(music, .1)
audioclip = afx.volumex(audioclip, 2.5)

# Compose the background music and the voiceover together then set them as the audio of the video

new_audioclip = CompositeAudioClip([audioclip, music])
clip.audio = new_audioclip

# Resize clip to fit portrait mode 

clip = clip.resize(height=1920)
clip = clip.crop(x1=1166.6,y1=0,x2=2246.6,y2=1920)

# Make 3 videos of the pictures made beforehand, then set starting point and duration so that they follow eachother nicely 

title1 = ImageClip("1.png").set_start(0).set_duration((dur)//3).set_pos(("center", "top")).margin(top=150, opacity=0).resize(height=800) # .margin moves them down to their designated position, .resize makes them bigger 
title2 = ImageClip("2.png").set_start((dur+3)//3+0.5).set_duration((dur)//3).set_pos(("center", "top")).margin(top=150, opacity=0).resize(height=800)
title3 = ImageClip("3.png").set_start(((dur+3)//3)*2+1).set_duration((dur)//3).set_pos(("center", "top")).margin(top=150, opacity=0).resize(height=800)

# Making subtitles

generator = lambda txt: TextClip(txt, font="Gill-Sans-Ultra-Bold", fontsize=150, color="pink", method='caption', size=clip.size, stroke_width=5, stroke_color="black") # Stroke == border
sub_clip = SubtitlesClip('subtitles.srt', generator)

# Composition of final video, stick all videos together

final = CompositeVideoClip([clip, sub_clip.margin(top=400, opacity=0), title1, title2, title3])

# Render video and save as output.mp4

final.write_videofile("output.mp4")




 
