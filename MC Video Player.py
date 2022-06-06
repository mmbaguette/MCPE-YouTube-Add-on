import cv2
import os
import requests as rq
import json
from distutils.dir_util import copy_tree
import youtube_dl
import numpy as np
import shutil
import ffmpeg
import sys

max_frames = 200
max_height = 70
max_FPS = 5
height_ratio = 0.5 # width = max_height / height_ratio
tick = 0.05

def generate_uuid():
    url_b = "https://www.uuidgenerator.net/version1/bulk.json?amount=1"
    b = rq.get(url_b)

    if b.status_code == 200:
        return json.loads(b.text)[0]
    else:
        return None

def create_frames(fileOrUrl, videoName, blocksPath):
    cap = cv2.VideoCapture(fileOrUrl)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frames = str(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    video_frames_left = []
    video_frames_right = []
    print(f"Generating {frames} frames...")

    while(cap.isOpened()): # Read until video is completed
        ret, frame = cap.read() # Capture frame-by-frame

        if ret:
            frame_resized = cv2.resize(frame, (round(max_height / height_ratio), max_height))
            height, width = frame_resized.shape[:2]

            lx1,lx2,ly1,ly2 = 0, int(width / 2), 0, height # left
            rx1,rx2,ry1,ry2 = lx2, width, 0, height

            leftBlock = frame_resized[ly1:ly2,lx1:lx2]
            rightBlock = frame_resized[ry1:ry2,rx1:rx2]

            video_frames_left.append(leftBlock)
            video_frames_right.append(rightBlock)
        else:
            break
    cap.release()
    os.remove(fileOrUrl)

    print("Stacking frames...")
    left_block_video = cv2.vconcat(video_frames_left)
    right_block_video = cv2.vconcat(video_frames_right)

    leftImgPath = f"{blocksPath}left_{videoName}_atlas.png"
    rightImgPath = f"{blocksPath}right_{videoName}_atlas.png"
    print("Writing images to blocks folder...")

    try:
        if cv2.imwrite(leftImgPath, left_block_video) and cv2.imwrite(rightImgPath, right_block_video):
            print("Successfully saved flipbook images!")
        else:
            print("Something went wrong. The flipbook images could not be saved...")
            print(left_block_video.shape)
            print(right_block_video.shape)
            print(leftImgPath)
            print(rightImgPath)
            print(f"Left path exists: {os.path.exists(leftImgPath)}")
            print(f"Right path exists: {os.path.exists(leftImgPath)}")
            cv2.imshow("Left image", left_block_video)
            cv2.imshow("Right image", right_block_video)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            sys.exit(-1)
    except:
        print("Something's wrong with the video you shared. Perhaps try a different format?")
        sys.exit(-1)

    return fps

def trim_audio(input_path, output_path, start=0, end=60):
    input_stream = ffmpeg.input(input_path)

    aud = (
        input_stream.audio
        .filter_('atrim', start=start, end=end)
        .filter_('asetpts', 'PTS-STARTPTS')
    )

    output = ffmpeg.output(aud, output_path)
    output.run()

def download_audio(soundsPath):
    audio_output_path = soundsPath + "sound.ogg"
    ffmpeg.input("youtube_video.mp4").filter('fps', fps=max_FPS, round='up').output('fps_change.mp4').run()

    cap = cv2.VideoCapture("fps_change.mp4")
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()

    if frames > max_frames:
        frames = max_frames

    ffmpeg.input("fps_change.mp4").trim(start_frame=0, end_frame=frames).output('output.mp4').run()

    end_duration = round(frames / max_FPS, 2)

    trim_audio("youtube_video.mp4", audio_output_path, start=0, end=end_duration)

    os.remove("youtube_video.mp4")
    os.remove("fps_change.mp4")

def youtube_video(url):
    ydl_opts = {
        'format': 'worstvideo[fps=30]+worstaudio', # CHANGE FOR VIDEO
        'outtmpl': "youtube_video.%(ext)s",
        "postprocessors": [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat' : 'mp4'
        }]
    }

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_description = info_dict.get("description", None)
            video_url = info_dict['requested_formats'][0]['url'] 
            audio_url = info_dict['requested_formats'][1]['url']
            video_fps = info_dict.get("fps", None)
            video_id = info_dict.get("id", None)
            video_title = info_dict.get("title", None)
    except: # if no 30 FPS frames
        print("No 30 FPS videos found")
        ydl_opts["format"] = 'bestvideo+bestaudio'
        
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            try:
                info_dict = ydl.extract_info(url, download=True)
                video_description = info_dict.get("description", None)
                video_url = info_dict['requested_formats'][0]['url'] 
                audio_url = info_dict['requested_formats'][1]['url']
                video_fps = info_dict.get("fps", None)
                video_id = info_dict.get("id", None)
                video_title = info_dict.get("title", None)
            except:
                print("The YouTube video does not exist or not cannot be accessed.")
                sys.exit(-1)

    print(f"Downloading {video_title} from YouTube...")

    video_data = {
        "video": video_url,
        "audio": audio_url,
        "fps": video_fps,
        "description": video_description,
        "id": video_id,
        "title": video_title,
    }

    return video_data

def main():
    youtube_url = input("\nEnter a Youtube URL: ")
    video_data = youtube_video(youtube_url)
    packName = input("\nWhat would you like to call your video? ").replace(" ","_")
    packDescription = "Made by MmBaguette's Minecraft Video Player from YouTube!\n\n" + video_data["description"]

    packPath = os.getcwd() + "\\" + packName + "\\"
    resourcePackPath = packPath + packName + " R\\"
    behaviourPackPath = packPath + packName + " B\\"

    texturesPath = resourcePackPath + "textures\\"
    textsPath = resourcePackPath + "texts\\"
    soundsPath = resourcePackPath + "sounds\\"
    blocksBPath = behaviourPackPath + "blocks\\"
    blocksRPath = resourcePackPath + "textures\\blocks\\"
    functionsPath = behaviourPackPath + "functions\\"

    thumbnailFilePathLeft = blocksRPath + f"left_{packName}_single.jpg"
    thumbnailFilePathRight = blocksRPath + f"right_{packName}_single.jpg"
    pack_iconRPath = resourcePackPath + "pack_icon.png"
    pack_iconBPath = behaviourPackPath + "pack_icon.png"

    texturesFilePath = texturesPath + "terrain_texture.json"
    flipbookFilePath = texturesPath + "flipbook_textures.json"
    blocksFilePath = resourcePackPath + "blocks.json"
    manifestRFilePath = resourcePackPath + "manifest.json"
    manifestBFilePath = behaviourPackPath + "manifest.json"

    get_vidFilePath = functionsPath + "get_vid.mcfunction"
    play_vidFilePath = functionsPath + "play_vid.mcfunction"
    languagesFilePath = textsPath + "languages.json"
    en_USFilePath = textsPath + "en_US.lang"
    leftBlockPath = blocksBPath + f"left_{packName}.json"
    rightBlockPath = blocksBPath + f"right_{packName}.json"
    soundsFilePath = resourcePackPath + "sounds\\sound_definitions.json"
    
    print("\nCopying addon template...")
    if os.path.exists(packPath):
        shutil.rmtree(packPath)

    if os.path.exists(packPath[:-1] + ".mcaddon"):
        os.remove(packPath[:-1] + ".mcaddon")

    if os.path.exists("output.mp4"):
        os.remove("output.mp4")

    if os.path.exists("fps_change.mp4"):
        os.remove("fps_change.mp4")

    os.makedirs(packPath)
    copy_tree("Video Addon R", resourcePackPath)
    copy_tree("Video Addon B", behaviourPackPath)
    
    print("Retrieving video thumbnail and setting pack icon...")
    thumbnail_url = f"http://img.youtube.com/vi/{video_data['id']}/0.jpg"
    t = rq.get(thumbnail_url, stream=True)

    if t.status_code == 200:
        image = np.asarray(bytearray(t.raw.read()), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        image = cv2.resize(image, (128,128))
        
        cv2.imwrite(thumbnailFilePathLeft, image)
        cv2.imwrite(thumbnailFilePathRight, image)
        cv2.imwrite(pack_iconRPath, image)
        cv2.imwrite(pack_iconBPath, image)
    else:
        print("Could not retrive video thumbnail!")
        sys.exit(-1)

    print("Extracting audio...")
    download_audio(soundsPath)
    fps = create_frames("output.mp4", packName, blocksRPath)
    frameDelay = 1 / fps # time between frames
    ticksPerFrame = frameDelay / tick

    flipbookData = [
        {
            "flipbook_texture": f"textures/blocks/left_{packName}_atlas",
            "atlas_tile": f"left_{packName}",
            "ticks_per_frame": ticksPerFrame
        },
        {
            "flipbook_texture": f"textures/blocks/right_{packName}_atlas",
            "atlas_tile": f"right_{packName}",
            "ticks_per_frame": ticksPerFrame
        }
    ]

    leftBlockData = {
        "format_version": "1.16.0",
        "minecraft:block": {
            "description": {
            "identifier": f"vid:left_{packName}",
            "is_experimental": False
            },
            "components": {
            "minecraft:destroy_time": 0.2,
            "minecraft:explosion_resistance": 1.0,
            "minecraft:map_color": "#ffffff"
            }
        }
    }

    rightBlockData = {
        "format_version": "1.16.0",
        "minecraft:block": {
            "description": {
            "identifier": f"vid:right_{packName}",
            "is_experimental": False
            },
            "components": {
            "minecraft:destroy_time": 0.2,
            "minecraft:explosion_resistance": 1.0,
            "minecraft:map_color": "#ffffff"
            }
        }
    }
    
    manifestRData = {
        "format_version": 2,
        "header": {
            "name": packName + "_R",
            "description": packDescription,
            "uuid": generate_uuid(),
            "version": [
                1,
                0,
                0
            ],
            "min_engine_version": [
                1,
                13,
                0
            ]
        },
        "modules": [
            {
                "type": "resources",
                "uuid": generate_uuid(),
                "version": [
                    1,
                    0,
                    0
                ]
            }
        ]
    }

    manifestBData = {
        "format_version": 2,
        "header": {
            "name": packName + "_B",
            "description": packDescription,
            "uuid": generate_uuid(),
            "version": [
                1,
                0,
                0
            ],
            "min_engine_version": [
                1,
                13,
                0
            ]
        },
        "modules": [
            {
                "type": "data",
                "uuid": generate_uuid(),
                "version": [
                    1,
                    0,
                    0
                ]
            }
        ],
        "dependencies": [
            {
                "version": [
                    1,
                    0,
                    0
                ],
                "uuid": manifestRData["header"]["uuid"]
            }
        ]
    }

    textureData = {
        "resource_pack_name": packName,
        "texture_name": "atlas.terrain",
        "padding": 8,
        "num_mip_levels": 4,
        "texture_data": {
            f"left_{packName}": {
                "textures": f"textures/blocks/left_{packName}_single" # block thumbnail
            },
            f"right_{packName}": {
                "textures": f"textures/blocks/right_{packName}_single" # block thumbnail
            }
        }
    }
    
    blocksData = {
        "format_version": [
            1,
            1,
            0
        ],
        f"vid:left_{packName}": {
            "textures": f"left_{packName}",
            "sound": "glass",
        },
        f"vid:right_{packName}": {
            "textures": f"right_{packName}",
            "sound": "glass",
        }
    }

    sound_data = {
        "format_version": "1.14.0",
        "sound_definitions": {
            f"{packName}.sound": {
                "category": "ui",
                "sounds": [
                    "sounds/sound"
                ]
            }
        }
    }

    languagesData = ["en_US"]
    en_USData = f"tile.vid:{packName.lower()}.name={packName} Video Player Add-on"
    
    get_vidFunctionData = f"give @p vid:left_{packName} 1\n"
    get_vidFunctionData += f"give @p vid:right_{packName} 1"

    # setup
    play_vidData = f"playsound {packName}.sound @a"

    # write the files for terrain texture, flipbook textures, manifest e.t.c.
    texturesW = open(texturesFilePath, "w")
    texturesW.write(json.dumps(textureData, indent=4))
    texturesW.close()

    flipbookW = open(flipbookFilePath, "w")
    flipbookW.write(json.dumps(flipbookData, indent=4))
    flipbookW.close()

    blockW = open(blocksFilePath, "w")
    blockW.write(json.dumps(blocksData, indent=4))
    blockW.close()

    manifestRW = open(manifestRFilePath, "w")
    manifestRW.write(json.dumps(manifestRData, indent=4))
    manifestRW.close()

    manifestBW = open(manifestBFilePath, "w")
    manifestBW.write(json.dumps(manifestBData, indent=4))
    manifestBW.close()

    languagesW = open(languagesFilePath, "w")
    languagesW.write(json.dumps(languagesData, indent=4))
    languagesW.close()
    
    en_USW = open(en_USFilePath, "w")
    en_USW.write(en_USData)
    en_USW.close()

    get_vidW = open(get_vidFilePath, "w")
    get_vidW.write(get_vidFunctionData)
    get_vidW.close()

    play_vidW = open(play_vidFilePath, "w")
    play_vidW.write(play_vidData)
    play_vidW.close()

    leftBlockW = open(leftBlockPath, "w")
    leftBlockW.write(json.dumps(leftBlockData, indent=4))
    leftBlockW.close()

    rightBlockW = open(rightBlockPath, "w")
    rightBlockW.write(json.dumps(rightBlockData, indent=4))
    rightBlockW.close()

    soundskW = open(soundsFilePath, "w")
    soundskW.write(json.dumps(sound_data, indent=4))
    soundskW.close()

    shutil.make_archive(resourcePackPath, 'zip', resourcePackPath)
    shutil.rmtree(resourcePackPath)
    os.rename(resourcePackPath[:-1] + ".zip", resourcePackPath[:-1] + ".mcpack")
    shutil.make_archive(behaviourPackPath, 'zip', behaviourPackPath)
    shutil.rmtree(behaviourPackPath)
    os.rename(behaviourPackPath[:-1] + ".zip", behaviourPackPath[:-1] + ".mcpack")
    shutil.make_archive(packPath, 'zip', packPath)
    shutil.rmtree(packPath)
    os.rename(packPath[:-1] + ".zip", packPath[:-1] + ".mcaddon")
    os.startfile(os.getcwd())

if __name__ == "__main__":
    main()