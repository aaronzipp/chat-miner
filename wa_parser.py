import pandas as pd
from parse import compile

from typing import (
    Callable,
    Dict,
    Optional,
    List,
    NewType,
    Union,
    Tuple,
)

# Types
FilePath = NewType('FilePath', str)


VIEW_ONCE_FLAG = "<View once>"
MEDIA_FLAGS = ["<Media omitted>", "<Medien ausgeschlossen>"]

TIME_FORMAT = "{time:tt}"
MESSAGE_FORMAT = "{author}: {message}"

MAX_HOUR = 24
MAX_MONTH = 12

DATE_FORMATS = ["{day:d}.{month:d}.{year:d}",
                "{day:d}/{month:d}/{year:d}"]


DATE_AND_TIME = [f"{date_format}, {TIME_FORMAT}"
                 for date_format in DATE_FORMATS]

FORMATS = [f"{date_and_time} - {MESSAGE_FORMAT}"
           for date_and_time in DATE_AND_TIME]

date_dot, date_slash = [compile(date_and_time).search
                        for date_and_time in DATE_AND_TIME]


def _parse_message(
    message_lines: List[str],
    parser: Callable,
    max_hour: int = MAX_HOUR,
) -> Dict:

    message = "".join(message_lines).strip("\n")
    parsed_message_dict = parser(message).named
    if parsed_message_dict["year"] < 1000:
        parsed_message_dict["year"] += 2000
    return parsed_message_dict


def _parse_messages(
    text: str,
    parser: Callable,
    max_hour: int = MAX_HOUR,
) -> List[Dict]:

    parsed_messages = []
    message_lines = []
    for line in text.split("\n"):
        line = line.strip()
        if line == "":
            continue
        # Check for view once messages
        if line[0].isdigit() and line.endswith(":"):
            line = " ".join([line, VIEW_ONCE_FLAG])
        # Check if next line is not a new message
        if not parser(line):
            # Check if this line is an info from WhatsApp
            if date_dot(line) or date_slash(line):
                continue
            message_lines.append(line)
            continue
        # Check for first message
        if not message_lines:
            message_lines.append(line)
            continue
        parsed_message_dict = _parse_message(message_lines, parser)
        parsed_messages.append(parsed_message_dict)
        message_lines = [line]
    # the last message needs to get parsed as well
    parsed_message_dict = _parse_message(message_lines, parser)
    parsed_messages.append(parsed_message_dict)
    return parsed_messages


def _parse_messages_from_file(
    filepath: FilePath,
    parser: Callable,
    max_hour: int = MAX_HOUR,
):

    text: str
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    return _parse_messages(text, parser, max_hour)


def _get_uncleaned_df_from_chat_log(
    filepath: FilePath,
    fmt: str,
    max_hour: int = MAX_HOUR,
) -> Union[pd.DataFrame, Tuple[pd.DataFrame, bool]]:

    parser = compile(fmt).parse
    parsed_messages = _parse_messages_from_file(
        filepath, parser, max_hour
    )
    parsed_messages_df = pd.DataFrame(parsed_messages)
    return parsed_messages_df


def _get_df_from_chat_log_without_format(
    filepath: FilePath,
    max_hour: int = MAX_HOUR
) -> Optional[pd.DataFrame]:

    text: str
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    for fmt in FORMATS:
        parser = compile(fmt)
        if not parser.search(text):
            continue

        parsed_messages_df = _get_uncleaned_df_from_chat_log(
            filepath, fmt, max_hour
        )
        max_day = parsed_messages_df.day.max()
        max_month = parsed_messages_df.month.max()
        if max_day > MAX_MONTH and max_month <= MAX_MONTH:
            return parsed_messages_df

        if max_day > MAX_MONTH or max_month <= MAX_MONTH:
            print("Unambiguos date format, please specify file format.")
            return None

        parsed_messages_df.rename(columns={"day": "month", "month": "day"},
                                  inplace=True)
        return parsed_messages_df


def get_df_from_chat_log(
    filepath: FilePath,
    fmt: Optional[str] = None,
    max_hour: int = MAX_HOUR,
) -> Optional[pd.DataFrame]:

    if fmt is None:
        parsed_messages_df = _get_df_from_chat_log_without_format(filepath, max_hour)
    else:
        parsed_messages_df = _get_uncleaned_df_from_chat_log(filepath, fmt, max_hour)

    parsed_messages_df = parsed_messages_df.pipe(_df_cleaning)
    return parsed_messages_df


def _df_cleaning(
    df: pd.DataFrame
):

    df = (
        df.assign(messenger="wa")
        .assign(date=pd.to_datetime(df[["year", "month", "day"]], errors="coerce"))
    )
    df = (
        df.assign(datetime=df.date.astype(str) + ' ' + df.time.astype(str))
        .drop(["day", "month", "year", "time", "date"], axis=1)
        .astype(
            {"author": "category", "messenger": "category", "datetime": "datetime64"}
        )
    )
    return df


def _message_length(
    message: str
) -> int:

    message = message.replace(VIEW_ONCE_FLAG, "")
    for flag in MEDIA_FLAGS:
        message = message.replace(flag, "")
    return len(message)
