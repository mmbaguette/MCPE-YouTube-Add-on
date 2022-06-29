# MCPE YouTube Add-on

Play YouTube videos with sound on Minecraft Bedrock Edition, using only add-ons!

Try out the Obi-wan Kenobi series video add-on in Minecraft: https://github.com/mmbaguette/MCPE-YouTube-Add-on/blob/main/obiwan_kenobi.mcaddon

![image](https://user-images.githubusercontent.com/76597978/172966574-0303623b-393f-4a9f-8e8a-f26462e9997d.png)

## Features
- 🎥 Animates blocks to display a short video in a continuous loop
- 📺 Left and right block for a 1 by 2 size display
- 🔊 Audio downloaded from YouTube video
- 🎫 "The End" screen to indicate when the next video loop starts to play audio in sync with the video
- 🍿 Watch TV with your buddies!

## How to Use
Read the setup below before using.
- Enter the URL of the YouTube video you want to download or the name of the video file (grabs as many frames as possible from the beginning of the video until it reaches `max_frames`)
- Name your addon (only letters, numbers and underscores!)
- Import the addon by double clicking on the new `.mcaddon` file (same location as script)
- Activate the behaviour and resource pack inside your world settings
- When in game, run `/function get_vid` to get the left and right blocks for your video
- Use `/playsound movie.sound` for audio (preferably in a command block with a button so you can play the audio exactly when the video starts)
- Place down the left and right blocks next to each other and enjoy the show!

## Download and Setup

This is a Python script, meaning you'll have to download Python 3.7+ from www.python.org before getting started: https://www.pythontutorial.net/getting-started/install-python/
- Once the Python programming language is installed, download the source code from this repository (click on the green **Code** button), download as a `.zip` file and **extract** it.
- Open `MC Video Player.py` in a text editor like Notepad (right click, *Open with*)
- Change the variables at the top of the program, below the list of `import`'s:
  -  `max_frames` (integer): Maximum number of frames to be displayed in the video (more frames = longer video—may crash your game)
  -  `max_height` (integer): Maximum height of pixel resolution in the video
  -  `max_FPS` (integer): Frames per second of video (less FPS = longer but choppier video)
  -  `use_ending` (True/False case sensitive): Whether you want a 1 second **The End** to be displayed at the end of the video so you know when to start the audio. Change the `ending.png` image if you want to see a different ending.
  -  Make sure to **SAVE** your changes and **DO NOT** change anything else unless you know exactly what you're doing
  -  Run the script by double clicking on the file to open it with Python, or right-click, *Open with* and select *Python* on Windows
  -  Press `Ctrl-C` in the console when you want to stop the program

**NOTE:** Raising the `max_height` or `max_frames` might **CRASH** Minecraft! Make sure to play around with these values to get the best resolution and length, while still being able to join your world!
