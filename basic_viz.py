import pandas as pd
from bs4 import BeautifulSoup
import tqdm
from gensim.corpora import Dictionary
from nltk.corpus import stopwords
from wordcloud import WordCloud
from gensim.parsing.preprocessing import remove_stopwords
import matplotlib.pyplot as plt


names_dict = {'Alexandr': 'Саша А.',
 'Руслан Пепа': 'Руслан',
 'Миша Макареев': 'Миша',
 'Антон Романов': 'Антон',
 'Саша Щукин': 'Саша Щ.',
 'Стася': 'Стася',
 'Анюта': 'Аня Ч.',
 'Ваня(о)': 'Ваня',
 'Вика': 'Вика',
 'Аня Бодунова': 'Аня Б.'}

full_df = pd.DataFrame()
for fnum in ['', 2, 3, 4, 5]:
    with open(f'./ChatExport_23_04_2020/messages{fnum}.html', encoding='utf8') as f:
        mhtml = f.read()

    soup = BeautifulSoup(mhtml, 'html')
    msgs = soup.find_all('div', {'class': 'body'})
    lines = []
    for msg in tqdm.tqdm(msgs):
        try:
            text = msg.find_all('div', {'class': 'text'})[0].text.replace('\n', '')
        except IndexError:
            text = None
        try:
            sender = msg.find_all('div', {'class': 'from_name'})[0].text.replace('\n', '')
        except IndexError:
            sender = None
        try:
            dt = msg.find_all('div', {'class':'pull_right date details'})[0]['title']
        except IndexError:
            dt = None
        lines.append((dt, sender, text))

    df = pd.DataFrame([i for i in lines if i != (None, None, None)], columns=['dt', 'sender', 'text'])
    df['sender'] = df['sender'].fillna(method='ffill').str.strip()
    df['text'] = df['text'].str.strip()
    df['dt'] = pd.to_datetime(df['dt'], dayfirst=True)
    full_df = full_df.append(df)

full_df['cdate'] = full_df['dt'].dt.date
full_df['chour'] = full_df['dt'].dt.hour
full_df['dow'] = full_df['dt'].dt.weekday  # ['Воскресенье', 'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
full_df['dt_hour'] = full_df['dt'].dt.round('1h')
full_df['text_len'] = full_df['text'].str.len()
full_df = full_df.replace(names_dict, regex=True).replace('Ваня(о)','Ваня')
print('Первое сообщение:', full_df['dt'].min())
print('Последнее сообщение:', full_df['dt'].max())
print('Прошло полных дней:', (full_df['dt'].max() - full_df['dt'].min()).days)
print('Из них с сообщениями:', full_df['cdate'].unique().shape[0])
print('Всего написали сообщений:', full_df.shape[0])
print(f'''А это значит в среднем {round(full_df.shape[0] / (full_df['dt'].max() - full_df['dt'].min()).days)} сообщений в день''')
print(f'''Если взять только активные дни, то в среднем {round(full_df.shape[0] / full_df['cdate'].unique().shape[0])} сообщений''')
print('Больше всего сообщений отправлено', full_df['cdate'].value_counts().index[0], f'''({full_df['cdate'].value_counts().max()} сообщений)''')

# print(df.replace({'[\s\t]{2,}':''}, regex=True))
# print(df.values)
# print([i for i in lines if i != ('', '', '')])
#
# full_df.groupby('sender')['text_len'].sum().sort_values()
# (full_df.groupby('sender')['text_len'].sum() / full_df.groupby('sender')['sender'].count()).sort_values()

tmp = full_df.groupby('dow')['sender'].count()
tmp.index = ['Воскресенье', 'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
fig, ax = plt.subplots(figsize=(8, 6))
tmp.plot(
    kind='bar',
    # xticks=full_df.index,
    rot=90,
    color='g',
    ec='black',
    alpha=0.5,
)
plt.title('Количество сообщений по дням недели', size=14)
plt.xlabel('День недели', size=10)
plt.ylabel('Количество сообщений', size=10)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.show()

tmp = full_df.groupby('chour')['sender'].count()
fig, ax = plt.subplots(figsize=(8, 6))
tmp.plot(
    kind='bar',
    # xticks=full_df.index,
    rot=90,
    color='g',
    ec='black',
    alpha=0.5,
)
plt.title('Количество сообщений по часам', size=14)
plt.xlabel('Час', size=10)
plt.ylabel('Количество сообщений', size=10)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.show()

base_dt = pd.DataFrame(pd.date_range(start='2019-11-03', end='2020-04-23', freq='d').date, columns=['base_dt'])
tmp = full_df.groupby('cdate')['sender'].count().reset_index()
timeline = pd.merge(base_dt, tmp, left_on='base_dt', right_on='cdate', how='left')
timeline['sender'] = timeline['sender'].fillna(0)
timeline['base_dt'] = pd.to_datetime(timeline['base_dt'])
timeline = timeline.drop('cdate', axis=1)
timeline = timeline.set_index('base_dt')
fig, ax = plt.subplots(figsize=(8, 6))
timeline['sender'].plot(
    kind='area',
    rot=90,
    alpha=0.5,
)
plt.title('Динамика количества сообщений', size=14)
plt.xlabel('Дата', size=10)
plt.ylabel('Количество сообщений', size=10)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.show()

names = full_df['sender'].value_counts()[full_df['sender'].value_counts() > 5].index.tolist()
fig, ax = plt.subplots(figsize=(8, 6))
full_df[full_df['sender'].isin(names)].groupby('sender')['text_len'].sum().sort_values(ascending=False).plot(
    kind='bar',
    # xticks=full_df.index,
    rot=90,
    color='g',
    ec='black',
    alpha=0.5,
)
plt.title('Количество написанных символов', size=14)
plt.xlabel('Участник', size=10)
plt.ylabel('Количество символов', size=10)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.show()

fig, ax = plt.subplots(figsize=(8, 6))
full_df[full_df['sender'].isin(names)].groupby('sender')['sender'].count().sort_values(ascending=False).plot(
    kind='bar',
    # xticks=df.index,
    rot=90,
    color='g',
    ec='black',
    alpha=0.5,
)
plt.title('Количество сообщений', size=14)
plt.xlabel('Участник', size=10)
plt.ylabel('Количество символов', size=10)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.show()

fig, ax = plt.subplots(figsize=(8, 6))
(full_df[full_df['sender'].isin(names)].groupby('sender')['text_len'].sum() / full_df[full_df['sender'].isin(names)].groupby('sender')['sender'].count()).sort_values(ascending=False).plot(
    kind='bar',
    # xticks=df.index,
    rot=90,
    color='g',
    ec='black',
    alpha=0.5,
)
plt.title('В среднем символов в сообщении', size=14)
plt.xlabel('Участник', size=10)
plt.ylabel('Количество символов', size=10)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.show()

russian_stopwords = stopwords.words("russian")
task_stopwords = ['пока', 'кажется', 'вообще', 'кстати', 'очень', 'это', 'тебе', 'почему', 'ru', 'http', 'https']
for sender in ['all'] + full_df['sender'].value_counts()[full_df['sender'].value_counts() > 5].index.tolist():
    print(sender)
    if sender == 'all':
        texts = full_df['text'].dropna().replace({'[.,-:!?]':' ', 'ё':'е'}, regex=True).str.lower().str.split().values.tolist()
    else:
        texts = full_df.loc[full_df['sender'] == sender, 'text'].dropna().replace({'[.,-:!?]':' ', 'ё':'е'}, regex=True).str.lower().str.split().values.tolist()
    texts_flatten = [t for i in texts for t in i]
    one_line = ' '.join(texts_flatten)

    wordcloud_all = WordCloud(stopwords=russian_stopwords + task_stopwords, background_color="white", width=1600, height=800).generate(one_line)
    plt.figure(figsize=(20, 10))
    plt.imshow(wordcloud_all, interpolation='bilinear')
    plt.axis("off")
    plt.savefig(f"imgs/{sender}.png", format="png")


# dct = Dictionary(texts)
# freq_dict = {i: dct.cfs[dct.token2id[i]] for i in dct.token2id if dct.cfs[dct.token2id[i]] > 10}
# freq_df = pd.DataFrame(freq_dict, index=['token_count']).T
# freq_wostopwords_df = freq_df[~freq_df.index.isin(russian_stopwords + task_stopwords)]
# freq_wostopwords_df.sort_values('token_count')