import asyncio
import sys

from app.utils.dependencies import check_and_install_dependencies

# 检查并安装依赖
check_and_install_dependencies()

from app.speech.speech_handler import SpeechHandler


async def test_speech_to_text():
    if len(sys.argv) < 2:
        print("请提供音频文件路径作为参数")
        print("用法: python test_speech.py <音频文件路径>")
        sys.exit(1)

    audio_file = sys.argv[1]
    speech_handler = SpeechHandler()

    print(f"正在处理音频文件: {audio_file}")
    text = await speech_handler.speech_to_text(audio_file)

    if text:
        print(f"识别结果: {text}")
    else:
        print("语音识别失败")


if __name__ == "__main__":
    asyncio.run(test_speech_to_text())
