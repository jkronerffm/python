import ffmpeg

in1 = ffmpeg.input("./Katebush.mp4")
audio = in1.audio
out = ffmpeg.output(audio,"WutheringHeights.mp3")
ffmpeg.run(out)

