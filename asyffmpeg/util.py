import re
from datetime import timedelta

def convert_to_seconds(time_str) -> int:
    """
    Converts a time string to seconds.

    This function takes a time string in the format "hours:minutes:seconds.milliseconds" and converts it to seconds.

    Args:
        time_str (`str`): A time string in the format "hours:minutes:seconds.milliseconds".

    Returns:
        `int`: The time converted to seconds.
    """
    match = re.match(r'(\d+):(\d+):(\d+\.\d+)', time_str)
    if match:
        hours, minutes, seconds = map(float, match.groups())
        return hours * 3600 + minutes * 60 + seconds

    return 0

def parse_time(time: str) -> timedelta:
    """
    Parses a time string and returns a timedelta object.

    This function parses a time string in the format "-hours:minutes:seconds.milliseconds" 
    or "hours:minutes:seconds.milliseconds" and returns a timedelta object representing the time.

    Args:
        time (`str`): A time string in the format "-hours:minutes:seconds.milliseconds" or "hours:minutes:seconds.milliseconds".

    Returns:
        `timedelta`: A timedelta object representing the parsed time.
    """
    match = re.search(r"(-?\d+):(\d+):(\d+)\.(\d+)", time)
    assert match is not None

    return timedelta(
        hours=int(match.group(1)),
        minutes=int(match.group(2)),
        seconds=int(match.group(3)),
        milliseconds=int(match.group(4)) * 10,
    )

# https://github.com/FFmpeg/FFmpeg/blob/d38bf5e08e768722096723b5c8781cd2eb18d070/fftools/ffmpeg.c#L618C53-L618C56
def parse_size(item: str) -> int:
    """
    Parses a size string and returns the size in bytes.

    This function parses a size string in kilobytes (kB) or kibibytes (KiB) format and returns 
    the size in bytes.

    Args:
        item (`str`): A size string.

    Returns:
        `int`: The size in bytes.
    """
    if "kB" in item:
        return int(item.replace("kB", "")) * 1024
    elif "KiB" in item:
        return int(item.replace("KiB", "")) * 1024
    else:
        return int(item) * 1024
        # raise ValueError(f"Unknown size format: {item}")