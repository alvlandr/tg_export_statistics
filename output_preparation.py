# -*- coding: utf-8 -*-

"""Functions to process Telegram raw export data."""
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud


def word_cloud(text: str, stopwords: list, output_path: str) -> None:
    wordcloud = WordCloud(
        stopwords=stopwords,
        background_color="white",
        width=1600,
        height=800,
    ).generate(text)
    plt.figure(figsize=(20, 10))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.savefig(output_path, format="png")


def plot_stats(
        df: pd.core.series.Series,
        figsize: tuple,
        title: str,
        xlabel: str,
        ylabel: str,
        output_path: str,
        kind: str = 'bar') -> None:
    fig, ax = plt.subplots(figsize=figsize)
    if kind == 'bar':
        df.plot(
            kind=kind,
            rot=90,
            color='g',
            ec='black',
            alpha=0.5,
        )
    else:
        df.plot(
            kind=kind,
            color='g',
            alpha=0.5,
        )
    plt.title(title, size=14)
    plt.xlabel(xlabel, size=10)
    plt.ylabel(ylabel, size=10)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    fig.tight_layout()
    plt.savefig(output_path, format='png')


def print_base_stats(df: pd.DataFrame) -> None:
    print(
        'Первое сообщение:',
        df['dt'].min(),
    )
    print(
        'Последнее сообщение:',
        df['dt'].max(),
    )
    print(
        'Прошло полных дней:',
        (df['dt'].max() - df['dt'].min()).days,
    )
    print(
        'Из них с сообщениями:',
        df['cdate'].unique().shape[0],
    )
    print(
        'Всего написали сообщений:',
        df.shape[0],
    )
    print(
        'А это значит в среднем',
        round(df.shape[0] / (df['dt'].max() - df['dt'].min()).days),
        'сообщений в день')
    print(
        'Если взять только активные дни, то в среднем',
        round(df.shape[0] / df['cdate'].unique().shape[0]),
        'сообщений',
    )
    print(
        'Больше всего сообщений отправлено',
        df['cdate'].value_counts().index[0],
        '(' + str(df['cdate'].value_counts().max()),
        'сообщений)',
    )
