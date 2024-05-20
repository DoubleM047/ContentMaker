from openai import OpenAI
import requests
client = OpenAI(api_key = "API_KEY_HERE")
import urllib.request 
from PIL import Image
from pathlib import Path
from moviepy.editor import *

response = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "user", "content": "Can you pretend that you are a youtuber and make a script for a 40 second video that will provide a fun fact for the people watching and only type the spoken text please not the whole script"},
  ]
)

tekst1 = response.choices[0].message.content

response2 = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "user", "content": "now could you pick 3 key phrases that would represent this fact well as pictures and out pass them to me in this format:[fact, fact, fact] do it from this text:" + tekst1},
  ]
)

tekst2 = response2.choices[0].message.content
sez = tekst2.split(", ")

image1 = client.images.generate(
  model="dall-e-2",
  prompt=sez[0],
  size="512x512",
  quality="standard",
  n=1,
)
image_url1 = image1.data[0].url
urllib.request.urlretrieve(image_url1, "1.png") 
# Opening the image and displaying it (to confirm its presence) 
img1 = Image.open(r"1.png") 
img1.show()

image2 = client.images.generate(
  model="dall-e-2",
  prompt=sez[1],
  size="512x512",
  quality="standard",
  n=1,
)
image_url2 = image2.data[0].url
urllib.request.urlretrieve(image_url2, "2.png") 
# Opening the image and displaying it (to confirm its presence) 
img2 = Image.open(r"2.png") 
img2.show()

image3 = client.images.generate(
  model="dall-e-2",
  prompt=sez[2],
  size="512x512",
  quality="standard",
  n=1,
)
image_url3 = image3.data[0].url
urllib.request.urlretrieve(image_url3, "3.png") 
# Opening the image and displaying it (to confirm its presence) 
img3 = Image.open(r"3.png") 
img3.show()


speech_file_path = Path(__file__).parent / "speech.mp3"
response = client.audio.speech.create(
  model="tts-1",
  voice="alloy",
  input=tekst1
)
  
# loading video dsa gfg intro video 
clip = VideoFileClip("background.mp4") 
clip = clip.subclip(0, 60)

audioclip = AudioFileClip("speech.mp3")

new_audioclip = CompositeAudioClip([audioclip])
clip.audio = new_audioclip
clip.write_videofile("output.mp4")
