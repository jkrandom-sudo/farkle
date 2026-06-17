"""Terminal-bell sound effects."""
import sys


class Sound:
    def __init__(self, enabled: bool = True, volume: int = 1, output=None):
        self.enabled = enabled
        self.volume = max(0, min(3, int(volume)))
        self.output = output if output is not None else sys.stdout

    def beep(self, count: int = 1) -> None:
        if not self.enabled or self.volume <= 0:
            return
        try:
            n = max(0, int(count)) * self.volume
            self.output.write("\a" * n)
            try:
                self.output.flush()
            except Exception:
                pass
        except Exception:
            pass

    def roll(self) -> None:
        self.beep(1)

    def keep(self) -> None:
        self.beep(1)

    def farkle(self) -> None:
        self.beep(2)

    def bank(self) -> None:
        self.beep(2)

    def hot_dice(self) -> None:
        self.beep(3)

    def win(self) -> None:
        self.beep(3)
