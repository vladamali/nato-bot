from typing import List

import pandas as pd
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


class GetStatistics(StatesGroup):
    waiting_for_stat = State()
    waiting_for_country = State()

def load_data(filepath: str):
    df = pd.read_csv(filepath, index_col=0)
    names = df.columns[0]
    headers = df.columns[1:].tolist()
    countries_list = df[names].tolist()
    
    return countries_list, headers, df

def create_keyboard(statistics: List[str]):
    stats_kb = ReplyKeyboardMarkup(resize_keyboard=True)

    for stat in statistics:
        button = KeyboardButton(stat)
        stats_kb.insert(button)

    return stats_kb