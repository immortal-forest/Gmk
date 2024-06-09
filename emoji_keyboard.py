import gi

gi.require_version('Gtk', '4.0')

from gi.repository import Gtk

import sys
import emoji
import subprocess
from threading import Thread

from emoji_parser import EmojiParser
from utils import threaded, minimize, is_minimized, maximize


class EmojiKeyboardWindow(Gtk.Window):
    def __init__(self, application: Gtk.Application):
        super().__init__(title='Emoji Keyboard', application=application)
        self.connect("close-request", self.listen_change)
        self.set_hide_on_close(True)

        self.set_default_size(265, 380)
        self.set_size_request(265, 380)
        self.emojis = EmojiParser()
        self.emoji_data = self.emojis.load_emojis()
        self.default_category: str = self.emojis.groups[0]
        self.current_category = self.default_category

        # Main layout container
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        self.set_child(self.main_box)

        # Search bar (optional)
        self.search_bar = Gtk.Entry(
            margin_start=6,
            margin_end=6,
            margin_top=6
        )
        self.search_bar.set_property("placeholder-text", "Search emoji")
        self.search_bar.connect("changed", self.on_search)
        self.main_box.append(self.search_bar)

        # Category buttons
        self.scrolled_category_box = Gtk.ScrolledWindow(
            margin_start=6,
            margin_end=6,
        )
        self.scrolled_category_box.set_size_request(265, 50)
        self.category_box = Gtk.Box(
            spacing=6,
            hexpand=False
        )
        self.scrolled_category_box.set_child(self.category_box)
        self.main_box.append(self.scrolled_category_box)

        self.category_buttons = {}
        self.current_clicked: Gtk.ToggleButton | None = None
        for category in self.emojis.groups:
            button = Gtk.ToggleButton(label=category)
            button.set_halign(Gtk.Align.CENTER)
            button.set_valign(Gtk.Align.CENTER)
            button.connect("toggled", self.on_category_clicked, category)
            self.category_box.append(button)
            self.category_buttons[category] = button
        self.category_buttons[self.current_category].set_active(True)
        self.main_box.append(self.category_box)

        self.emoji_flow_scroll = Gtk.ScrolledWindow(
            margin_start=6,
            margin_end=6,
            margin_bottom=6,
            min_content_width=265,
            min_content_height=330
        )
        self.emoji_flow = Gtk.FlowBox(homogeneous=True, hexpand=True, vexpand=True)
        self.emoji_flow_scroll.set_child(self.emoji_flow)
        self.main_box.append(self.emoji_flow_scroll)
        self.fill_emoji(self.emojis.groups[0], None)
        self.show()

    def on_category_clicked(self, button: Gtk.ToggleButton, category):
        if self.current_clicked is not None:
            self.current_clicked.set_active(False)

        if button.get_active():
            self.current_category = category
            self.current_clicked = button
            try:
                self.emoji_flow.remove_all()
            except AttributeError:
                pass
            self.fill_emoji(category, None)

    @threaded
    def fill_emoji(self, category: str | None, data: list | None):
        if data is not None:
            for item in data:
                emoji_button = Gtk.Button(label=emoji.emojize(item), tooltip_text=item, has_tooltip=True)
                emoji_button.connect("clicked", self.on_emoji_clicked, emoji.emojize(item))
                self.emoji_flow.append(emoji_button)
            return
        data = self.emojis.emojis_data
        emojis = data[category]
        for em in emojis:
            emoji_button = Gtk.Button(label=emoji.emojize(em), tooltip_text=em, has_tooltip=True)
            emoji_button.connect("clicked", self.on_emoji_clicked, emoji.emojize(em))
            self.emoji_flow.append(emoji_button)

    def on_emoji_clicked(self, _, emoji):
        self.set_focusable(False)
        clip = self.get_clipboard()
        clip.set(emoji)

    @threaded
    def on_search(self, search_bar: Gtk.Entry):
        text = search_bar.get_text().lower()
        if text.isspace() or text == "":
            self.emoji_flow.remove_all()
            self.fill_emoji(self.current_category, None)
            return

        text_lst = text.split(" ")
        filter_data = []
        values = [item for emojis in self.emoji_data.values() for item in emojis]
        for item in values:
            for t in text_lst:
                if t in item:
                    filter_data.append(item)
        self.emoji_flow.remove_all()
        self.fill_emoji(None, filter_data)

    @threaded
    def listen_change(self, _):
        minimize()

        def inner(window: EmojiKeyboardWindow):
            while True:
                if is_minimized():
                    continue
                break
            window.show()

        t = Thread(target=inner, args=(self,))
        t.start()


if __name__ == '__main__':
    args = sys.argv[1:]

    if args[0] == "update":
        EmojiParser().update_emojis_list()
        exit(0)
    elif args[0] == "show":
        # check if a process already exists
        proc_id = subprocess.run(['pgrep', '-f', 'emoji_keyboard.py'], capture_output=True)

        processes = list(filter(
            lambda x: x != '',
            proc_id.stdout.decode().split("\n")
        ))

        maximize()
        if len(processes) < 2:
            app = Gtk.Application(application_id='gtk-emoji-keyboard')
            app.connect("activate", EmojiKeyboardWindow)
            app.run(None)
        else:
            exit(0)
    elif args[0] == "kill":
        subprocess.run(['pkill', '-f', 'emoji_keyboard.py'])
        exit(0)
    else:
        exit(1)
