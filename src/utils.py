import glob
import pandas as pd
import streamlit as st
from datetime import date, timedelta

data_file_path = glob.glob('./data/*.csv')

def pre_load_csv_data():
    df = []
    for file in data_file_path:
        data = load_transactions(file)
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

def get_last_month_date():
    today = date.today()
    return today - timedelta(days=30)