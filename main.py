import asyncio
import os
import re
import sys

from app.utils.dependencies import check_and_install_dependencies

# 检查并安装依赖
check_and_install_dependencies()

from app.agent.manus import Manus
from app.logger import logger
from app.speech.speech_handler import SpeechHandler


def process_prompt(text):
    """处理原始文本，生成正式的prompt"""
    logger.info("开始处理原始文本...")
    base_info = """我是一位70岁的武汉居民，见证了城市从老弄堂到现代化的蜕变。虽然我长期与糖尿病作斗争，但我每天坚持晨练，注重饮食，定期就医。我热爱传统生活，也逐渐适应微信等现代工具，与邻里好友保持联系。即使面对空巢生活，我依然乐观自强，享受独立与温情并存的每一天。"""

    # 按照指定格式生成prompt
    prompt = f"""{text}。以下是我的基本情况：{base_info}。你要以口语化像是对朋友讲话那样生成内容，并且把生成的内容以"养生日程.txt"保存起来，这样任务就完成了。"""
    logger.info("原始文本处理完成")
    return prompt.strip()


def extract_filename(response):
    """从响应中提取文件名"""
    logger.info("开始从响应中提取文件名...")
    # 尝试从响应中提取文件名
    # 这里假设文件名在引号中，如 "xxx.txt"
    match = re.search(r'["\'](.*?\.txt)["\']', response)
    if match:
        filename = match.group(1)
        logger.info(f"成功提取文件名: {filename}")
        return filename
    logger.info("未找到指定文件名，使用默认文件名: 养生日程.txt")
    return "养生日程.txt"  # 如果没有找到，使用默认文件名


async def check_and_process_file():
    """检查文件是否存在且有内容，然后进行语音合成"""
    filename = "养生日程.txt"
    workspace_path = os.path.join("workspace", filename)
    logger.info(f"开始检查文件 {workspace_path}...")

    # 检查文件是否存在
    if not os.path.exists(workspace_path):
        logger.warning(f"文件 {workspace_path} 不存在")
        return False

    # 检查文件是否有内容
    with open(workspace_path, "r", encoding="utf-8") as f:
        content = f.read().strip()
        if not content:
            logger.warning(f"文件 {workspace_path} 为空")
            return False

    logger.info(f"文件 {workspace_path} 内容已确认，内容长度: {len(content)} 字符")
    return content


async def main():
    logger.info("程序启动...")

    # 检查是否提供了音频文件路径
    if len(sys.argv) < 2:
        logger.error("未提供音频文件路径")
        print("请提供音频文件路径作为参数")
        print("用法: python main.py <音频文件路径>")
        sys.exit(1)

    audio_file = sys.argv[1]
    logger.info(f"音频文件路径: {audio_file}")

    # 检查音频文件是否存在
    if not os.path.exists(audio_file):
        logger.error(f"音频文件不存在: {audio_file}")
        sys.exit(1)

    # 初始化语音处理器和agent
    logger.info("初始化语音处理器和agent...")
    speech_handler = SpeechHandler()
    agent = Manus()
    logger.info("初始化完成")

    try:
        # 将语音转换为文字
        logger.info("开始语音转文字...")
        raw_text = await speech_handler.speech_to_text(audio_file)
        if not raw_text:
            logger.error("语音识别失败，无法获取文字内容")
            return

        logger.info(f"语音转文字成功，识别结果: {raw_text}")

        # 处理文字，生成正式的prompt
        logger.info("开始生成正式prompt...")
        prompt = process_prompt(raw_text)
        logger.info(f"prompt生成完成: {prompt}")

        # 运行agent
        logger.info("开始运行agent...")
        response = await agent.run(prompt)
        logger.info("agent运行完成")

        # 检查文件并获取内容
        logger.info("开始检查生成的文件...")
        content = await check_and_process_file()
        if not content:
            logger.error("无法获取文件内容，跳过语音合成")
            return

        # 将内容转换为语音并播放
        logger.info("开始文本转语音...")
        await speech_handler.text_to_speech(content)
        logger.info("文本转语音完成")

    except KeyboardInterrupt:
        logger.warning("用户中断操作")
    except Exception as e:
        logger.error(f"发生错误: {str(e)}")
    finally:
        logger.info("程序结束")


if __name__ == "__main__":
    asyncio.run(main())
