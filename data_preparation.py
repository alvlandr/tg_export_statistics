# -*- coding: utf-8 -*-

"""Functions to process Telegram raw export data."""
import os
from typing import Optional
import pandas as pd
import glob
from bs4 import BeautifulSoup
import bs4
import tqdm


def read_html(path: str) -> list:
    """
    Read the .html file and extract blocks of actual messages.

    Args:
        path (str): path to the .html export data file

    Returns:
        list: list of BeautifulSoup tags.
    """
    with open(path, encoding='utf8') as datafile:
        mhtml = datafile.read()

    soup = BeautifulSoup(mhtml, features="lxml")
    msgs = soup.find_all('div', {'class': 'body'})

    return msgs


def extract_text(message: bs4.element.Tag, tag: str) -> Optional[str]:
    text_tag = message.find_all('div', {'class': tag})
    try:
        text = text_tag[0].text.replace('\n', '')
    except IndexError:
        text = None

    return text


def extract_title(message: bs4.element.Tag, tag: str) -> Optional[str]:
    text_tag = message.find_all('div', {'class': tag})
    try:
        title = text_tag[0]['title']
    except IndexError:
        title = None

    return title


def enrich_data(df: pd.DataFrame) -> pd.DataFrame:
    df['cdate'] = df['dt'].dt.date
    df['chour'] = df['dt'].dt.hour
    df['dow'] = df['dt'].dt.weekday
    df['dt_hour'] = df['dt'].dt.round('1h')
    df['text_len'] = df['text'].str.len()

    return df


def parse_export_data(folder_path: str) -> pd.DataFrame:
    r"""
    Parse .html export data files to pandas.DataFrame.

    Args:
        folder_path (str): folder containing export data files
        (e.g.
        'C:\\Users\\User\\Downloads\\Telegram Desktop\\ChatExport_23_04_2020').

    Returns:
        pandas.DataFrame: Prepared data.
    """
    filepath_list = glob.glob(os.path.join(folder_path, '*.html'))

    full_df = pd.DataFrame()
    for filepath in filepath_list:
        msgs = read_html(filepath)
        lines = []
        for msg in tqdm.tqdm(msgs):
            lines.append(
                (
                    extract_title(msg, 'pull_right date details'),
                    extract_text(msg, 'from_name'),
                    extract_text(msg, 'text'),
                )
            )

        lines = [line for line in lines if line != (None, None, None)]
        df = pd.DataFrame(lines, columns=['dt', 'sender', 'text'])
        df['sender'] = df['sender'].fillna(method='ffill').str.strip()
        df['text'] = df['text'].str.strip()
        df['dt'] = pd.to_datetime(df['dt'], dayfirst=True)
        full_df = full_df.append(df)

    full_df = enrich_data(full_df)

    return full_df


def prepare_word_cloud(df: pd.DataFrame, sender: str) -> str:
    if sender == 'all':
        texts = df['text'].dropna().replace(
            {'[.,-:!?]': ' ', 'ё': 'е'},
            regex=True,
        ).str.lower().str.split().values.tolist()
    else:
        texts = df.loc[df['sender'] == sender, 'text'].dropna().replace(
            {'[.,-:!?]': ' ', 'ё': 'е'},
            regex=True,
        ).str.lower().str.split().values.tolist()
    texts_flatten = [t for i in texts for t in i]
    one_line = ' '.join(texts_flatten)

    return one_line
