import json
import os
from functools import cache

import emoji
import requests

from utils import threaded


class EmojiParser:
    def __init__(self):
        self.data_dir = "./data/"
        self.groups = ["Smileys & Emotion", "People & Body", "Component", "Animals & Nature", "Food & Drink",
                       "Travel & Places", "Activities", "Objects", "Symbols", "Flags"]
        self.emojis_data = {}
        try:
            os.mkdir("./data")
        except FileExistsError:
            pass
        return

    @cache
    def load_emojis(self) -> dict[str, list[str]]:
        with open(self.data_dir + "emojis.json") as file:
            emojis_data = json.load(file)
        self.emojis_data = emojis_data
        return emojis_data

    @threaded
    def update_emojis_list(self):
        url = 'https://unicode.org/Public/emoji/latest/emoji-test.txt'
        try:
            raw_data = requests.get(url).text
        except Exception:
            with open(os.path.join(self.data_dir + "emoji.txt")) as file:
                raw_data = file.read()
        else:
            with open(os.path.join(self.data_dir + "emoji.txt"), 'w') as file:
                file.write(raw_data)

        emoji_list = raw_data.split("# group:")[1:]
        emoji_data = {}
        for group in emoji_list:
            group_lst = []
            group_name = group[:group.find("\n")].strip()
            group_data = group[group.find("\n"):].strip()
            subgroup_lst = filter(lambda i: i != '', group_data.split("# subgroup:"))
            for subgroup in subgroup_lst:
                emojis = set(map(
                    lambda i: emoji.demojize(i['emoji']),
                    emoji.emoji_list(subgroup)
                ))

                group_lst.extend(emojis)
            emoji_data[group_name] = group_lst
        with open(os.path.join(self.data_dir, "emojis.json"), 'w') as file:
            json.dump(emoji_data, file)

    @cache
    def get_group(self, group: str) -> list[str]:
        return self.emojis_data[group]
