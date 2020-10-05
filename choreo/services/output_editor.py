#vid2.mp4는 같은 폴더에 저장된 영상 파일, audio.wav는 음성파일이다. 결과는 같은 폴더에 output.mp4

def output_editor():
  os.system("ffmpeg -i vid2.mp4 -i audio.wav -c:v copy -c:a aac output.mp4")
