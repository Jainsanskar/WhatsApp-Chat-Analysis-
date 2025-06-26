from urlextract import URLExtract
import emoji
import pandas as pd
from wordcloud import WordCloud, STOPWORDS

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