import argparse
import os
import sys
import pandas as pd
from nltk.corpus import stopwords

FILE_PATH = os.path.realpath(__file__)
PROJECT_PATH = os.path.dirname(FILE_PATH)
sys.path.append(PROJECT_PATH)

from data_preparation import parse_export_data, prepare_word_cloud
from output_preparation import print_base_stats, plot_stats, word_cloud


argparser = argparse.ArgumentParser()
argparser.add_argument(
    '-i',
    '--input_folder',
    help='Path to a folder with .html files',
)
argparser.add_argument(
    '-o',
    '--output_folder',
    help='Path to a folder with generated files',
)
args = argparser.parse_args()
path = args.input_folder
output_path = args.output_folder

full_df = parse_export_data(path)
names = full_df['sender'].value_counts()[
    full_df['sender'].value_counts() > 5
    ].index.tolist()

print_base_stats(full_df)

df_dow = full_df.groupby('dow')['sender'].count()
df_dow.index = [
    'Воскресенье',
    'Понедельник',
    'Вторник',
    'Среда',
    'Четверг',
    'Пятница',
    'Суббота',
]
plot_stats(
    df_dow,
    figsize=(8, 6),
    title='Количество сообщений по дням недели',
    xlabel='День недели',
    ylabel='Количество сообщений',
    output_path=os.path.join(output_path, 'dow.png'),
)

df_hour = full_df.groupby('chour')['sender'].count()
plot_stats(
    df_hour,
    figsize=(8, 6),
    title='Количество сообщений по часам',
    xlabel='Час',
    ylabel='Количество сообщений',
    output_path=os.path.join(output_path, 'hour.png'),
)

base_dt = pd.DataFrame(
    pd.date_range(start='2019-11-03', end='2020-04-23', freq='d').date,
    columns=['base_dt'],
)
df_cdate = full_df.groupby('cdate')['sender'].count().reset_index()
timeline = pd.merge(base_dt, df_cdate, left_on='base_dt', right_on='cdate', how='left')
timeline['sender'] = timeline['sender'].fillna(0)
timeline['base_dt'] = pd.to_datetime(timeline['base_dt'])
timeline = timeline.drop('cdate', axis=1)
timeline = timeline.set_index('base_dt')
plot_stats(
    timeline,
    figsize=(8, 6),
    title='Динамика количества сообщений',
    xlabel='Дата',
    ylabel='Количество сообщений',
    output_path=os.path.join(output_path, 'timeline.png'),
    kind='area'
)

df_textlen = full_df[
    full_df['sender'].isin(names)
].groupby('sender')['text_len'].sum().sort_values(ascending=False)
plot_stats(
    df_textlen,
    figsize=(8, 6),
    title='Количество написанных символов',
    xlabel='Участник',
    ylabel='Количество символов',
    output_path=os.path.join(output_path, 'names_textlen.png'),
)

df_msgnum = full_df[
    full_df['sender'].isin(names)
].groupby('sender')['sender'].count().sort_values(ascending=False)
plot_stats(
    df_textlen,
    figsize=(8, 6),
    title='Количество сообщений',
    xlabel='Участник',
    ylabel='Количество сообщений',
    output_path=os.path.join(output_path, 'names_msgnum.png'),
)

df_sympermsg = (df_textlen / df_msgnum).sort_values(ascending=False)
plot_stats(
    df_sympermsg,
    figsize=(8, 6),
    title='В среднем символов в сообщении',
    xlabel='Участник',
    ylabel='Количество символов',
    output_path=os.path.join(output_path, 'names_sympermsg.png'),
)

russian_stopwords = stopwords.words("russian")
task_stopwords = ['пока', 'кажется', 'вообще', 'кстати', 'очень', 'это', 'тебе', 'почему', 'ru', 'http', 'https']
all_stopwords = russian_stopwords + task_stopwords
for sender in ['all'] + names:
    sender_text = prepare_word_cloud(full_df, sender)
    word_cloud(sender_text, all_stopwords, os.path.join(output_path, sender + '.png'))
