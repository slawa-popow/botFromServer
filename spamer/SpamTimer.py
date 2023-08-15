
from typing import Callable
from aio_timers import Timer
import time

class SpamTimer:
    PERIOD = 30

    def __init__(self, name: str, callback: Callable, time_s: int, callback_args: tuple = tuple() ) -> None:
        self.name = name
        self.duration = time_s
        self._curr_time = None
        self.is_run: bool = False
        self.timer: Timer = Timer(time_s, callback, callback_args=callback_args)


    @property
    def passed_time(self) -> int:
        if self._curr_time:
            return time.time() - self._curr_time
        return -999


    async def run_timer(self) -> None:
        self._curr_time = time.time()
        await self.timer.wait()
        self.is_run = True


    async def stop_timer(self) -> None:
        await self.timer.cancel()
        self.is_run = False