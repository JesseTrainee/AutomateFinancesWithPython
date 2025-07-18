import glob
import pandas as pd
import streamlit as st

data_file_path = glob.glob('./data/*.csv')

def pre_load_csv_data():
    df = []
    for file in data_file_path:
        data = load_transactions(file)
        # print(data)
        df.append(data)

    df = pd.concat(df, ignore_index=True)

    return df

def load_transactions(file):
    try:
        df = pd.read_csv(file)
        df.columns = [col.strip() for col in df.columns]
        df["date"] = pd.to_datetime(df["date"])
        return df
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None
