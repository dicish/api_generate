import time
import requests
import streamlit as st

GENERATE_TTS_URL = "https://video.a2e.ai/api/v1/video/send_tts"
API_URL = "https://video.a2e.ai/api/v1/video/generate"
STATUS_URL = "https://video.a2e.ai/api/v1/video/awsResult"
TOKEN = "Bearer YOUR_TOKEN"


def generate_tts_ru_female(token, text, speech_rate=1.0):
    headers = {"Authorization": token, "Content-Type": "application/json"}
    body = {"msg": text, "tts_id": "63a549c1ad2a27fe43d9669a", "speechRate": speech_rate}
    resp = requests.post(GENERATE_TTS_URL, json=body, headers=headers)
    resp.raise_for_status()
    return resp.json()


def create_avatar_video(anchor_id, anchor_type, audio_url):
    headers = {"Authorization": TOKEN, "Content-Type": "application/json"}
    payload = {"title": "Project Avatar", "anchor_id": anchor_id,
               "anchor_type": anchor_type, "audioSrc": audio_url}
    resp = requests.post(API_URL, json=payload, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    task = data.get("data")
    if data.get("code") == 0 and task and "_id" in task:
        return task["_id"]
    else:
        raise Exception(f"Ошибка создания видео: {data}")


def wait_for_video(task_id, interval=3, timeout=600):
    headers = {"Authorization": TOKEN, "Content-Type": "application/json"}
    start = time.time()
    while True:
        resp = requests.post(STATUS_URL, json={"_id": task_id}, headers=headers)
        resp.raise_for_status()
        info = resp.json()["data"][0]
        status = info["status"]
        print(f"Статус задачи {task_id}: {status}")
        if status == "success":
            return info["result"]
        elif status == "fail":
            raise Exception(f"Генерация не удалась: {info.get('msg')}")
        if time.time() - start > timeout:
            raise TimeoutError("Превышено время ожидания")
        time.sleep(interval)


if __name__ == "__main__":
    text = st.text_input("Ведите текст: ")
    if text:
        label = st.info("Идет генерация...")
        tts = generate_tts_ru_female(TOKEN, text)
        if tts.get("code") == 0:
            audio_url = tts["data"]
            print("Аудио создано:", audio_url)
        else:
            raise Exception("TTS ошибка")

        anchor_id = "687faf2f8d3ca5003c804693"
        anchor_type = 1
        task_id = create_avatar_video(anchor_id, anchor_type, audio_url)
        print("ID задачи:", task_id)

        print("Ожидание завершения генерации видео…")
        video_url = wait_for_video(task_id)
        print("🎉 Видео готово! Ссылка:", video_url)
        label.success("Готово")
        st.video(video_url)
