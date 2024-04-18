# AsyFFmpeg

AsyFFmpeg is a Python library for interacting asynchronously with FFmpeg to perform various operations on media files.

## Installation

To install AsyFFmpeg, run the following command:

```bash
pip install asyffmpeg
```

## Usage
An example of how to use the library:
```python
import asyncio
from asyffmpeg import AsyFFmpeg

async def start(input:str, output:str):
    print(f'[start]: {input} -> {output}')

async def end(encoding_time:timedelta):
    print(f'[end]: {encoding_time}')

async def progress(progress:float, elapsed_time:timedelta, remaining_time:timedelta,
                   frame:int, is_finished:bool, bitrate:float):
    print(f'#{frame} | [{progress}] [{elapsed_time}] [{bitrate}]: [{remaining_time}] [?:{is_finished}]')


async def encode_video():
    ffmpeg = AsyFFmpeg(debug=False)
    ffmpeg.input("input.mp4")
    ffmpeg.output("output.mp4")
    ffmpeg.args({'vf': 'scale=1920:1080', 'codec:a': 'aac'})
    ffmpeg.on_event('start', start)
    ffmpeg.on_event('end', end)
    ffmpeg.on_event('progress', progress)
    await ffmpeg.run()

asyncio.run(encode_video())
```

## Features
* Asynchronous interface for interacting with FFmpeg.
* User-friendly API for controlling video and audio encoding.
* Support for various FFmpeg parameters and filters.
* Support for events such as `progress`, `start` and `end`.


## License
AsyFFmpeg is distributed under the MIT license.