import pandas as pd
import json

FILE_PATH = r"./snapchat/json/chat_history.json"
MESSAGE_FLAG = "TEXT"
TIMEZONE_SHIFT = pd.Timedelta('01:00:00')

OWN_NAME = "Aaron Zipp"
PERSON = "SC name"
PERSON_NAME = "Real name"

def get_df_from_chatlog(filepath = FILE_PATH, *, own_name = OWN_NAME,
                        person = PERSON, person_name = PERSON_NAME,
                        timezone_shift = TIMEZONE_SHIFT):
    with open(FILE_PATH) as file:
        data = json.load(file)

    df_rec = pd.DataFrame(data['Received Saved Chat History'])
    df_sent = pd.DataFrame(data['Sent Saved Chat History'])

    df_rec = df_rec[(df_rec["Media Type"] == MESSAGE_FLAG) & (df_rec["From"] == person)][["From", "Created", "Text"]]
    df_sent = df_sent[(df_sent["Media Type"] == MESSAGE_FLAG) & (df_sent["To"] == person)][["To", "Created", "Text"]]

    df_rec["From"] = person_name
    df_rec.rename(columns = {"From": "author"}, inplace = True)
    df_sent["To"] = own_name
    df_sent.rename(columns = {"To": "author"}, inplace = True)

    df = df_rec.append(df_sent, ignore_index = True)
    df.rename(columns = {"Created": "datetime", "Text": "message"}, inplace = True)
    df["datetime"] = pd.to_datetime(df["datetime"], infer_datetime_format = True) + timezone_shift
    df.sort_values(by = "datetime", inplace = True, ignore_index = True)
    df['weekday'] = df['datetime'].dt.day_name()
    df['words'] = df['message'].apply(lambda s: len(s.split(' ')))
    df['letters'] = df['message'].apply(lambda s: len(s))
    df["hour"] = df["datetime"].dt.hour
    return df
