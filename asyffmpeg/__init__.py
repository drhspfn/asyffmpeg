import asyncio
from datetime import timedelta, datetime
import logging
from .statistic import Statistics
import aiofiles
from typing import Awaitable, Callable, Dict, List, Literal, Union
from .tempf import TempFile
from ffprobe import FFProbe

from .util import convert_to_seconds

class AsyFFmpeg:
    """
    A class for asynchronous FFmpeg processing.

    This class provides functionality for executing FFmpeg commands asynchronously,
    including setting input and output files, adding additional arguments, and handling progress events.

    Usage:
        ```python
        async def progress(progress: float, elapsed_time: timedelta, remaining_time: timedelta,
                           frame: int, is_finished: bool, bitrate: float):
            # Event handler for progress events

        async def main():
            ffmpeg = AsyFFmpeg(debug=True)
            ffmpeg.input("input.mp4")
            ffmpeg.output("output.mp4")
            ffmpeg.args({'vf': 'scale=1920:1080', 'codec:a': 'aac'})
            ffmpeg.on_event('progress', progress)
            await ffmpeg.run()

        asyncio.run(main())
        ```
    """
    def __init__(self, debug:bool=False, logger:logging.Logger=None) -> None:
        """
        Initializes an instance of the AsyFFmpeg class.

        Args:
            debug (`bool, optional`): Whether debugging is enabled. Defaults to False.
            logger (`logging.Logger, optional`): The logger object for logging debug messages. Defaults to None.
        """
        self.__logger = logger
        self.__debug = debug

        self._input = ""
        self._output = ""
        self._args: Dict[str, str] = {}

        self.__events:Dict[str, Callable[[None], Awaitable[None]]] = {}

        self.__start_time:datetime = 0

        self.__preffix = "AsyFFmpeg"


    def _debug(self, data:str) -> None:
        """
        Logs debug information if debugging is enabled.

        This method logs debug information to the specified logger (if available) or prints it to the console
        with a custom prefix. Debugging must be enabled for this method to log information. If no logger is provided,
        debug messages are printed to the console with a custom prefix.

        Args:
            data (`str`): The debug information to log.

        Returns:
            `None`
        """
        if self.__debug:
            if self.__logger:
                self.__logger.debug(data)
            else:
                print(f'[{self.__preffix}]: {data}')

    
    def __build_command(self) -> None:
        """
        Builds the FFmpeg command based on input parameters.

        This method constructs the FFmpeg command by assembling the input file, output file, 
        and additional arguments into a list of command-line arguments. If additional arguments 
        are provided, they are included in the command along with their corresponding values.
        If the value for an argument is `None`, only the key will be included in the command.

        Returns:
            `None`
        """
        args = ['-y', '-i', self._input]

        if self._args:
            for key, value in self._args.items():
                if value is not None:
                    args.extend(['-' + key, value])
                else:
                    args.append('-' + key)

        args.append(self._output)
        self._args = args

    def add_arg(self, arg_key: str, arg_value: str = None) -> None:
        """
        Adds an argument to the FFmpeg command.

        This method adds an argument to the FFmpeg command with the specified key and value.

        Args:
            arg_key (`str`): The key of the argument to add.
            arg_value (`str, optional`): The value of the argument. If not provided, only the key is added.

        Returns:
            `None`
        """
        self._args[arg_key] = arg_value

    def input(self, path: str) -> None:
        """
        Sets the input file path for FFmpeg.

        This method sets the input file path for FFmpeg to the specified path.

        Args:
            path (`str`): The path to the input file.

        Returns:
            `None`
        """
        self._input = path

    def output(self, path: str) -> None:
        """
        Sets the output file path for FFmpeg.

        This method sets the output file path for FFmpeg to the specified path.

        Args:
            path (`str`): The path to the output file.

        Returns:
            `None`
        """
        self._output = path

    def args(self, args: Dict[str, Union[str, None]] = {}) -> None:
        """
        Sets additional arguments for FFmpeg.

        This method sets additional arguments for FFmpeg using a dictionary of key-value pairs.
        If the value for an argument key is `None`, only the key will be included in the command.

        Args:
            args (`Dict[str, Union[str, None]], optional`): A dictionary containing additional arguments and their values.
                If a value is `None`, only the key will be included in the command.

        Returns:
            `None`
        """
        self._args = args


    async def read_progress(self, progress_file_path: str) -> None:
        """
        Reads progress information from a file and triggers events accordingly.

        This method continuously reads progress information from the specified file path,
        parsing the lines and extracting relevant data. It calculates the progress of encoding
        based on the number of frames processed, the frame rate, and the duration of the input video.
        Then, it triggers the 'progress' event with details such as progress percentage, elapsed time,
        remaining time, current frame, encoding status, and bitrate.

        Args:
            progress_file_path (`str`): The file path to read progress information from.

        Returns:
            `None`
        """
        while True:
            async with aiofiles.open(progress_file_path, mode='r') as progress_file:
                lines = []
                progress = None
                async for line in progress_file:
                    lines.append(line.strip())
                    if len(lines) >= 12:
                        progress = Statistics.from_line(' '.join(lines))
                        lines = []  
                if lines:
                    progress = Statistics.from_line(' '.join(lines))
                
                if progress and self.__events.get('progress', None):
                    _progress:float = round(progress.frame / (self.file_framerate * self.file_duration), 2) 
                    elapsed_time = datetime.now() - self.__start_time
                    if _progress > 0 and _progress < 1:
                        remaining_time = timedelta(seconds=(elapsed_time.total_seconds() / _progress)) - elapsed_time
                    else:
                        remaining_time = timedelta()
                       

                    self._debug("Progress intercepted...")
                    await self.__events['progress'](_progress, elapsed_time, remaining_time, 
                                            progress.frame, not progress.progress, progress.bitrate)

                    if progress.progress is False:
                        self._debug("Encoding completed...")
                        if self.__events.get('end', None):
                            await self.__events['end'](datetime.now() - self.__start_time)

                        await progress_file.close()
                        break
            await asyncio.sleep(1)

    async def _prepare(self) -> None:
        """
        Prepares necessary information before encoding.

        This method extracts essential information about the input video, such as frame rate and duration,
        using FFProbe utility.

        Returns:
            `None`
        """
        ffprobe = FFProbe(self._input)
        
        self.file_framerate = ffprobe.streams[0].framerate
        self.file_duration = convert_to_seconds(ffprobe.metadata['Duration'])
        
        del ffprobe

    def on_event(self, event:Literal['progress', 'start', 'end'], func):
        """Event wiretaps
        
        Args:
            event (`str`): Event name, can be `progress`, `start` or `end`
            func (`_type_`): Asynchronous function called when an event is picked up

        Usage example
        ```python
        from asyffmpeg import FFmpeg
        from datetime import timedelta
        
        async def progress(progress:float, elapsed_time:timedelta, remaining_time:timedelta,
                   frame:int, is_finished:bool, bitrate:float):
            ...

        def main():
            ffmpeg = FFmpeg()
            ffmpeg.on_event('progress', progress)
        ```
        """
        if event in ['progress', 'start', 'end']:
            self.__events[event] = func


    async def run(self) -> None:
        """
        Executes the FFmpeg command asynchronously.

        This method prepares necessary information before encoding, builds the FFmpeg command,
        and starts the encoding process asynchronously. It triggers the `start` event if registered,
        indicating the start of encoding. Progress information is read from a temporary progress file,
        and `progress` events are triggered accordingly. Finally, upon completion of encoding,
        the `end` event is triggered if registered.

        Returns:
            `None`
        """
        await self._prepare()

        self.__build_command()
        self.__start_time = datetime.now()
        async with TempFile() as progress_file_path:
            print(progress_file_path.file.name)
            self._debug("Encoding started...")
            async def _run(args_list, f_path):
                if self.__events.get('start', None):
                    await self.__events['start'](self._input, self._output)

                proc = await asyncio.create_subprocess_exec(
                    "ffmpeg", *args_list, "-progress", f"{f_path}",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await proc.communicate()

            tasks = []
        
            tasks.append(asyncio.create_task(_run(self._args, str(progress_file_path))))
            tasks.append(asyncio.create_task(self.read_progress(str(progress_file_path))))
            await asyncio.gather(*tasks)
    