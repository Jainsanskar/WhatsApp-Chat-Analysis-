from urlextract import URLExtract
import emoji
import pandas as pd
from wordcloud import WordCloud, STOPWORDS
from collections import Counter


extract = URLExtract()

def fetch_stats(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Total messages
    num_messages = df.shape[0]

    # Total words
    words = []
    for message in df['message']:
        words.extend(message.split())

    # Media messages
    num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]

    # Links
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))

    # Emojis
    emoji_count = 0
    for message in df['message']:
        emoji_count += len([char for char in message if emoji.is_emoji(char)])


    # Chat duration (days)
    start_date = df['date'].min().date()
    end_date = df['date'].max().date()
    duration_days = (end_date - start_date).days + 1  # +1 to include both ends

    return num_messages, len(words), num_media_messages, len(links), emoji_count, duration_days


# function to fetuch most busy user
def most_busy_users(df):
    x = df['user'].value_counts().head()
    df = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(
        columns={'index': 'name', 'user': 'percent'})
    return x,df


def create_wordcloud(selected_user, df):
    # Load custom Hinglish stop words
    with open('stop_hinglish.txt', 'r', encoding='utf-8') as f:
        custom_stopwords = set(f.read().split())

    # Combine with WordCloud's built-in stopwords
    all_stopwords = STOPWORDS.union(custom_stopwords)

    # Filter messages for selected user
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Clean and filter messages
    df = df[df['message'].notna()]
    df = df[~df['message'].str.lower().isin(['null', '<media omitted>', '', 'messages and calls are end-to-end encrypted', 'this message was deleted'])]
    df = df[df['user'] != 'group_notification']

    # Remove stopwords from messages
    def clean_message(message):
        words = [word for word in message.lower().split() if word not in all_stopwords]
        return " ".join(words)

    df['cleaned_message'] = df['message'].astype(str).apply(clean_message)

    # Generate WordCloud
    wc = WordCloud(
        width=600,
        height=400,
        min_font_size=10,
        background_color='white',
        colormap='viridis',
        max_words=150,
        stopwords=all_stopwords,
        contour_color='steelblue',
        contour_width=1
    )

    text = df['cleaned_message'].str.cat(sep=" ")
    return wc.generate(text)


def most_common_words(selected_user,df):

    f = open('stop_hinglish.txt','r')
    stop_words = f.read()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    words = []

    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

    most_common_df = pd.DataFrame(Counter(words).most_common(20))
    return most_common_df

def emoji_helper(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if emoji.is_emoji(c)])


    emoji_counter = Counter(emojis).most_common(20)
    return pd.DataFrame(emoji_counter)


def monthly_timeline(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))

    timeline['time'] = time

    return timeline

def daily_timeline(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('only_date').count()['message'].reset_index()

    return daily_timeline

def week_activity_map(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()

def month_activity_map(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()

def activity_heatmap(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

    return user_heatmap


