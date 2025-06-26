from urlextract import URLExtract
import emoji
import pandas as pd

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