import speech_recognition as sr
from pytube import YouTube
import vlc
from youtubesearchpython import SearchVideos
import json
import time
import threading

current_player = None  # Глобальная переменная для текущего player

def get_youtube_audio_url(query):
    search = SearchVideos(query, offset=1, mode="json", max_results=1)
    video_info = json.loads(search.result())
    video_url = video_info['search_result'][0]['link']
    yt = YouTube(video_url)
    video = yt.streams.filter(only_audio=True).first()
    return video.url

def play_audio_online(url):
    global current_player
    if current_player:  # Если текущий player существует, останавливаем его
        current_player.stop()
    player = vlc.MediaPlayer(url)
    current_player = player  # Обновляем текущий player
    player.play()
    # Даем время для начала воспроизведения и воспроизводим до конца
    while player.is_playing():
        time.sleep(1)

def stop_current_audio():
    global current_player
    if current_player:
        current_player.stop()

def listen_for_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        while True:
            print("Скажите название песни или 'стоп' для остановки...")
            audio = recognizer.listen(source)
            try:
                text = recognizer.recognize_google(audio, language="ru-RU")
                print(f"Вы сказали: {text}")
                if text.lower() == "стоп":
                    stop_current_audio()
                else:
                    if "включи пожалуйста" in text.lower():
                        text = text.lower().replace("включи пожалуйста", "")
                        print(f"Вы сказали: {text}")
                        audio_url = get_youtube_audio_url(text)
                        threading.Thread(target=play_audio_online, args=(audio_url,)).start()
            except sr.UnknownValueError:
                print("Не удалось распознать команду")
            except sr.RequestError:
                print("Ошибка сервиса распознавания")

if __name__ == "__main__":
    listen_for_command()