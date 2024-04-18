from dataclasses import dataclass, field
from datetime import timedelta
import re
from typing import Optional
from .util import parse_size, parse_time

_pattern = re.compile(r"(frame|fps|size|time|bitrate|speed|progress)\s*=\s*(\S+)")

_field_factory = {
    "frame": int,
    "fps": float,
    "size": parse_size,
    "time": parse_time,
    "bitrate": lambda item: float(item.replace("kbits/s", "")),
    "speed": lambda item: float(item.replace("x", "")),
    "progress": lambda item: True if item == "continue" else False,
}

@dataclass(frozen=True)
class Statistics:
    frame: int = 0
    fps: float = 0.0
    size: int = 0
    time: timedelta = field(default_factory=timedelta)
    bitrate: float = 0.0
    speed: float = 0.0
    progress: bool = False

    @classmethod
    def from_line(cls, line: str) -> Optional['Statistics']:
        statistics = {key: value for key, value in _pattern.findall(line)}
        if len(statistics) < 4:
            return None

        fields = {key: _field_factory[key](value) for key, value in statistics.items() if value != "N/A"}
        return cls(**fields)