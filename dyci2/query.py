from abc import ABC
from enum import Enum
from typing import List

from label import Label


class TimeMode(Enum):
    RELATIVE = "relative"
    ABSOLUTE = "absolute"

    @classmethod
    def from_string(cls, time_mode: str) -> 'TimeMode':
        """ raises: ValueError if input doesn't match an existing TimeMode """
        return TimeMode(time_mode.lower())


class Query(ABC):
    def __init__(self, start_date: int = 0, time_mode: TimeMode = TimeMode.ABSOLUTE, print_info: bool = True):
        self.start_date: int = start_date
        self.time_mode: TimeMode = time_mode
        self.print_info: bool = print_info

    def parse(self, *args, **kwargs):
        # TODO
        pass

    def to_absolute(self, performance_time: int) -> None:
        if self.time_mode == TimeMode.RELATIVE:
            self.start_date: int = max(performance_time + self.start_date, performance_time)
            self.time_mode = TimeMode.ABSOLUTE


class FreeQuery(Query):
    def __init__(self, num_events: int, start_date: int = 0, time_mode: TimeMode = TimeMode.ABSOLUTE,
                 print_info: bool = True):
        super().__init__(start_date=start_date, time_mode=time_mode, print_info=print_info)
        self.num_events: int = num_events


class LabelQuery(Query):
    def __init__(self, labels: List[Label], start_date: int = 0, time_mode: TimeMode = TimeMode.ABSOLUTE,
                 print_info: bool = True):
        """ raises: AttributeError if list is empty """
        super().__init__(start_date=start_date, time_mode=time_mode, print_info=print_info)
        self.labels: List[Label] = labels
        if len(self.labels) < 0:
            raise AttributeError(f"{self.__class__.__name__} must contain at least one label")

    def __repr__(self):
        return f"{self.__class__.__name__}(labels={self.labels},start_date={self.start_date},...)"
