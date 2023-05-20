import abc


class BaseUI(abc.ABC):
    @abc.abstractmethod
    def flush(self):
        pass

    @abc.abstractmethod
    def write(self, s: str):
        pass

    @abc.abstractmethod
    def width(self) -> int:
        pass

    @abc.abstractmethod
    def height(self) -> int:
        pass

    @abc.abstractmethod
    def clear(self):
        pass

    @abc.abstractmethod
    def move_xy(self, x: int, y: int):
        pass
