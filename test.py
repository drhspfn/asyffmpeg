from datetime import timedelta
from asyffmpeg import AsyFFmpeg
import asyncio



async def start(input:str, output:str):
    print(f'[start]: {input}')

async def end(encoding_time:timedelta):
    print(f'[end]: {encoding_time}')

async def progress(progress:float, elapsed_time:timedelta, remaining_time:timedelta,
                   frame:int, is_finished:bool, bitrate:float):
    print(f'#{frame} | [{progress}] [{elapsed_time}] [{bitrate}]: [{remaining_time}] [?:{is_finished}]')


async def main():
    ffmpeg = AsyFFmpeg(debug=False)
    ffmpeg.input("input.mp4")
    ffmpeg.output("output.mp4")
    ffmpeg.args({'vf': 'scale=1920:1080', 'codec:a': 'aac'})
    ffmpeg.on_event('start', start)
    ffmpeg.on_event('end', end)
    ffmpeg.on_event('progress', progress)
    await ffmpeg.run()


asyncio.run(main())
