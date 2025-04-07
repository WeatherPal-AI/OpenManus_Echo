import asyncio
import sys

from speech_handler import SpeechHandler


async def process_audio(audio_file):
    speech_handler = SpeechHandler()

    # 将语音转换为文字
    text = await speech_handler.speech_to_text(audio_file)
    if text:
        print(f"识别结果: {text}")

        # 将文字转换为语音并播放
        await speech_handler.text_to_speech(text)
    else:
        print("语音识别失败")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("请提供音频文件路径作为参数")
        print("用法: python example.py <音频文件路径>")
        sys.exit(1)

    audio_file = sys.argv[1]
    asyncio.run(process_audio(audio_file))
