import asyncio
import os
import tempfile
from pathlib import Path

import requests
import speech_recognition as sr
import tomli
from gtts import gTTS
from pydub import AudioSegment


class SpeechHandler:
    def __init__(self):
        self.config = self._load_config()
        self.recognizer = sr.Recognizer()
        self._ensure_temp_dir()

    def _load_config(self):
        config_path = Path("config/config.toml")
        with open(config_path, "rb") as f:
            return tomli.load(f)

    def _ensure_temp_dir(self):
        temp_dir = self.config["speech"]["local"]["temp_dir"]
        os.makedirs(temp_dir, exist_ok=True)

    def _convert_to_wav(self, audio_file):
        """将音频文件转换为WAV格式"""
        try:
            # 获取文件扩展名
            ext = os.path.splitext(audio_file)[1].lower()

            # 如果是WAV格式，直接返回
            if ext == ".wav":
                return audio_file

            # 创建临时文件
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_wav_path = temp_file.name

            # 根据文件类型加载音频
            if ext == ".mp3":
                audio = AudioSegment.from_mp3(audio_file)
            elif ext == ".ogg":
                audio = AudioSegment.from_ogg(audio_file)
            elif ext == ".flac":
                audio = AudioSegment.from_flac(audio_file)
            else:
                raise ValueError(f"不支持的音频格式: {ext}")

            # 导出为WAV格式
            audio.export(temp_wav_path, format="wav")
            return temp_wav_path

        except Exception as e:
            print(f"音频转换错误: {str(e)}")
            return None

    async def speech_to_text(self, audio_file):
        """将语音文件转换为文字"""
        try:
            # 转换为WAV格式
            wav_file = self._convert_to_wav(audio_file)
            if not wav_file:
                return None

            # 识别语音
            with sr.AudioFile(wav_file) as source:
                audio = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio, language="zh-CN")

            # 如果是临时文件，删除它
            if wav_file != audio_file:
                os.unlink(wav_file)

            return text
        except Exception as e:
            print(f"语音识别错误: {str(e)}")
            return None

    async def text_to_speech_google(self, text, output_file):
        """使用Google TTS将文字转换为语音"""
        try:
            tts = gTTS(text=text, lang="zh-cn")
            tts.save(output_file)
            return output_file
        except Exception as e:
            print(f"Google语音合成错误: {str(e)}")
            return None

    async def text_to_speech_minimax(self, text, output_file):
        """使用Minimax API将文字转换为语音"""
        try:
            group_id = self.config["speech"]["synthesis"]["minimax"]["group_id"]
            api_key = self.config["speech"]["synthesis"]["minimax"]["api_key"]

            url = f"https://api.minimax.chat/v1/t2a_v2?GroupId={group_id}"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": "speech-02-hd",
                "text": text,
                "timber_weights": [
                    {"voice_id": "Chinese (Mandarin)_Kind-hearted_Elder", "weight": 1}
                ],
                "voice_setting": {
                    "voice_id": "",
                    "speed": 1,
                    "pitch": 0,
                    "vol": 1,
                    "latex_read": False,
                },
                "audio_setting": {
                    "sample_rate": 32000,
                    "bitrate": 128000,
                    "format": "mp3",
                },
                "language_boost": "auto",
            }

            response = requests.post(url, headers=headers, json=payload)

            if response.status_code == 200:
                # 保存音频数据到文件
                with open(output_file, "wb") as f:
                    f.write(response.content)
                return output_file
            else:
                print(f"Minimax API错误: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            print(f"Minimax语音合成错误: {str(e)}")
            return None

    async def text_to_speech(self, text):
        """将文字转换为语音并播放"""
        try:
            output_file = os.path.join(
                self.config["speech"]["local"]["temp_dir"], "output.mp3"
            )

            # 根据配置选择语音合成服务
            tts_service = self.config["speech"]["synthesis"]["api_type"]

            if tts_service == "google":
                result = await self.text_to_speech_google(text, output_file)
            elif tts_service == "minimax":
                result = await self.text_to_speech_minimax(text, output_file)
            else:
                print(f"不支持的语音合成服务: {tts_service}")
                return None

            if result:
                # 尝试播放音频（如果系统支持）
                try:
                    os.system(f"mpg321 {output_file}")
                except:
                    pass  # 忽略播放错误
                return output_file
            return None

        except Exception as e:
            print(f"语音合成错误: {str(e)}")
            return None
