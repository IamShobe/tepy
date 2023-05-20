import abc
from subprocess import call


class BaseEditor(abc.ABC):
    @abc.abstractmethod
    def edit(self, file: str):
        pass


class TextEditor(BaseEditor):
    def __init__(self, editor: str = 'vim'):
        self.editor = editor

    def edit(self, file: str):
        call([self.editor, file])
