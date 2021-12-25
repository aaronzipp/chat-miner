import pandas as pd
import os
import wa_parser
import sc_parser

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


def _get_full_(folder, *, text_only = True, messenger):
    pass
 

def get_full_wa(folder, *, text_only = True):
    return _get_full_(folder, text_only = text_only, messenger = "wa")


def get_full_sc(folder, *, text_only = True):
    return _get_full_(folder, text_only = text_only, messenger = "sc")


def get_all_data(*, folder_wa, folder_sc, text_only = True):
    df_wa = get_full_wa(folder_wa, text_only = text_only)
    df_sc = get_full_sc(folder_sc, text_only = text_only)
    return df_wa.join(df_sc, how = "inner")
