import asyncio
import sys
import tempfile
from subprocess import call
from typing import List, Protocol

from blessed import Terminal
from colored import attr

from tepy.components.custom_string import String
from tepy.components.editor import TextEditor, BaseEditor
from tepy.components.renderer import Renderer
from tepy.components.utils import FPS
from tepy.ui.base_ui import BaseUI


class App:
    def __init__(
            self,
            render_list: list[Renderer],
            *,
            editor: BaseEditor = TextEditor(),
            ui: BaseUI = sys.stdout,
    ):
        self.term = Terminal()
        self.render_list: list[Renderer] = render_list
        self.should_run = True
        self.editor = editor
        self.ui = ui

        self.buffer = []
        self.on_resize()

    def on_resize(self):
        self.buffer = [[' ' for _ in range(self.term.width)] for _ in range(self.term.height)]
        for rendered in self.render_list:
            rendered.onresize()
        self.ui.write(self.term.clear)

    def dump_to_screen(self):
        for line_num, line in enumerate(self.buffer):
            self.ui.write(self.term.move_xy(0, line_num) + "".join(line) + attr("reset"))

        self.ui.write(attr("reset"))

    def echo(self, x, y, to_print):
        if isinstance(to_print, str):
            to_print = String(to_print)

        if y >= len(self.buffer) or x + len(to_print) > len(self.buffer[0]):
            return

        line = self.buffer[y]
        to_print.reset_style_on_end()
        for i, char in enumerate(to_print):
            actual_x = x + i
            line[actual_x] = str(char)

    def add_to_render(self, renderer: Renderer):
        self.render_list.append(renderer)

    def add_multiple(self, renders: List[Renderer]):
        self.render_list.extend(renders)

    def get_editor_input(self, initial_text: str = ""):
        if self.editor is None:
            raise RuntimeError("No editor was provided")

        with tempfile.NamedTemporaryFile(suffix=".tmp") as tf:
            tf.write(initial_text.encode())
            tf.flush()
            self.editor.edit(tf.name)
            tf.seek(0)
            return tf.read().decode()

    async def draw_loop(self):
        with self.term.fullscreen():
            while self.should_run:
                with self.term.hidden_cursor():
                    await asyncio.gather(asyncio.sleep(FPS), *[renderer.update_data() for renderer in self.render_list])
                    for renderer in self.render_list:
                        renderer.render(self.echo)

                    self.dump_to_screen()
                    self.ui.flush()

    async def input_loop(self):
        def _blocking_input_loop():
            with self.term.cbreak(), self.term.raw():
                while self.should_run:
                    key = self.term.inkey(timeout=FPS)
                    if key in [chr(3)]:
                        self.should_run = False
                        break

                    self.on_tick(key)

        await asyncio.create_task(asyncio.to_thread(_blocking_input_loop))

    def on_tick(self, key):
        pass

    async def run(self):
        for renderer in self.render_list:
            print(renderer)
            renderer.initialize(editor=self.editor)

        await asyncio.gather(self.input_loop(), self.draw_loop())
