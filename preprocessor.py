import re
import pandas as pd

def preprocess(data):
    # Updated regex for 2-digit year
    pattern = r'\d{1,2}/\d{1,2}/\d{2},\s\d{1,2}:\d{2}\s-\s'

    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # Updated date format to match your input (DD/MM/YY)
    df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%y, %H:%M - ')
    df.rename(columns={'message_date': 'date'}, inplace=True)

    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split('([\w\W]+?):\s', message)
        if entry[1:]:  # user name present
            users.append(entry[1])
            messages.append(" ".join(entry[2:]))
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # AM/PM format period
    period = []
    for hour in df['hour']:
        start = pd.to_datetime(str(hour), format='%H').strftime('%I %p')
        end_hour = (hour + 1) % 24
        end = pd.to_datetime(str(end_hour), format='%H').strftime('%I %p')
        period.append(f"{start} - {end}")
    df['period'] = period
    
    # # Remove empty, whitespace-only, or 'null' messages
    # df = df[df['message'].notna()]
    # df = df[df['message'].str.strip() != '']
    # df = df[~df['message'].str.lower().eq('null')]

    #    # Clean message text early
    df['message'] = df['message'].astype(str).str.strip()

    # Remove empty or null-like messages
    stop_words = [
        '', 'null', 'None', '<Media omitted>', 
        'Messages and calls are end-to-end encrypted',
        'This message was deleted'
    ]
    df = df[~df['message'].str.lower().isin([w.lower() for w in stop_words])]

    return df
