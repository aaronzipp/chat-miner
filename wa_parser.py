import re
import pandas as pd


DATEREGEX = {
    'dd/mm/yy':
        r'^([0-2][0-9]|(3)[0-1][0-9])(\/)(([0-1][0-9])|((1)[0-2]))(\/)(\d{2}|\d{4})',
    'dd/mm/yyyy':
        r'^([0-2][0-9]|(3)[0-1][0-9])(\/)(([0-1][0-9])|((1)[0-2]))(\/)(\d{4}|\d{4})',
    'mm/dd/yy':
        r'^(([0-9])|((1)[0-2]))(\/)([0-2][0-9]|(3)[0-1]|[0-9])(\/)(\d{2}|\d{4})',
    'dd.mm.yy':
        r'^([0-2][0-9]|(3)[0-1][0-9])(\.)(([0-1][0-9])|((1)[0-2]))(\.)(\d{2}|\d{4})',
    'dd.mm.yyyy':
        r'^([0-2][0-9]|(3)[0-1][0-9])(\.)(([0-1][0-9])|((1)[0-2]))(\.)(\d{4}|\d{4})',
    'mm.dd.yy':
        r'^(([0-9])|((1)[0-2]))(\.)([0-2][0-9]|(3)[0-1]|[0-9])(\.)(\d{2}|\d{4})'
}

TIMEREGEX = {
    '24-hh:mm':
        r'([0-9][0-9]):([0-9][0-9])',
    '24-hh:mm:ss':
        r'([0-9][0-9]):([0-9][0-9]):([0-9][0-9])',
    '12-hh-mm':
        r'(1[0-2]|0?[1-9]):([0-5][0-9]) ?([AaPp][Mm])'
}


def get_df_from_chatlog(filepath, dateformat='mm/dd/yy',
                        timeformat='24-hh:mm'):

    def get_message_metadata(line):
        date = re.search(DATEREGEX[dateformat], line).group(0)
        time = re.search(TIMEREGEX[timeformat], line).group(0)
        author = get_author_from_line(line)
        return date, time, author

    def get_author_from_line(line):
        patterns = [
            r'- ([+])([0-9 ]+)(:)',
            r'- ([\w]+):',
            r'- ([\w]+[\s]+[\w]+):',
            r'- ([\w]+[\s]+[\w]+[\s]+[\w]+):',
        ]
        pattern = '|'.join(patterns)
        res = re.search(pattern, line)
        return re.sub(r'|\-|\:', '', res.group(0)).strip() if res else 'System'

    assert filepath.endswith('.txt'),\
        "Wrong file type: Specified file does not end with .txt"

    with open(filepath, encoding="utf-8") as f:
        parsed_chat = []
        message_buffer = []
        date, time, author = None, None, None
        for line in f:
            line = line.strip()
            if re.match(DATEREGEX[dateformat], line):
                if message_buffer:
                    parsed_chat.append({
                        'date': date,
                        'time': time,
                        'author': author,
                        'message': ' '.join(message_buffer).strip()
                    })

                message_buffer.clear()
                date, time, author = get_message_metadata(line)
                if author != 'System':
                    message_buffer.append(line.split('-', 1)[1].split(':', 1)[1])
                else:
                    message_buffer.append(line.split('-', 1)[1])
            else:
                message_buffer.append(line)

    df = pd.DataFrame(parsed_chat)
    df = df[df['author'] != 'System']
    df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'],
                                    infer_datetime_format=True)
    df['weekday'] = df['datetime'].dt.day_name()
    df['words'] = df['message'].apply(lambda s: len(s.split(' ')))
    df['letters'] = df['message'].apply(lambda s: len(s))
    df["hour"] = df["datetime"].dt.hour
    return df[["weekday", "datetime", "author", "message", "words", "letters", "hour"]]
