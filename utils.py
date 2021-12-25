import pandas as pd
import os
import wa_parser
import sc_parser
import visualizations_setup
from functools import reduce

FILETYPE_SC = "json"
FILETYPE_WA = "txt"

def write_to_csv(df, path):
    dir = "/".join(path.split("/")[:-1])

    if not os.path.exists(dir):
        os.mkdir(dir)

    if os.path.exists(path):
        overwrite_file = input("File already exist. Overwrite? [Y/n]")
        if overwrite_file.upper() == "Y" or overwrite_file == "":
            print("File written")
            df.to_csv(path)
        else:
            print("Not written to file")


def load_data(path):
    assert path.endswith(".csv"), \
        "Data needs to be in a csv file"
    return pd.read_csv(path)


def _get_full_(folder, *, text_only = False, messenger):
    if not os.path.exists(folder):
        print(f"Folder {folder} does not exist")

    if messenger == "wa" or messenger == "sc":
        pass
    else:
        raise NotImplementedError("Only WhatsApp (wa) and Snapchat (sc) implemented so far.")

    # Needs editing if not using the standard values for kwargs
    kwargs = None
    dataframes = []
    if messenger == "wa":
        parser = wa_parser
        filetype = FILETYPE_WA
        kwargs = {"dateformat": visualizations_setup.DATEFORMAT, \
                "timeformat": visualizations_setup.TIMEFORMAT}
    else:
        parser = sc_parser
        filetype = FILETYPE_SC
        if text_only:
            kwargs = {"message_flag": None}

    for filename in os.listdir(folder):
        f = os.path.join(folder, filename)
        if not os.path.isfile(f):
            print(f"{f} is not a file, it got skipped.")
            continue
        if not f.endswith(filetype):
            print(f"The file has to be of type {filetype}.")
            continue

        print(f)
        if kwargs is None:
            df = parser.get_df_from_chatlog(f)
        else:
            df = parser.get_df_from_chatlog(f, **kwargs)
        dataframes.append(df)

    df = reduce(lambda x, y: x.append(y).drop_duplicates(), dataframes)
    df.reset_index(inplace = True)
    return df


def get_full_wa(folder, *, text_only = False):
    return _get_full_(folder, text_only = text_only, messenger = "wa")


def get_full_sc(folder, *, text_only = False):
    return _get_full_(folder, text_only = text_only, messenger = "sc")


def get_all_data(*, folder_wa, folder_sc, text_only = False):
    df_wa = get_full_wa(folder_wa, text_only = text_only)
    df_sc = get_full_sc(folder_sc, text_only = text_only)
    return combine_messenger(df_wa = df_wa, df_sc = df_sc)

def combine_messenger(*, df_wa, df_sc):
    return df_wa.join(df_sc, how = "inner")
