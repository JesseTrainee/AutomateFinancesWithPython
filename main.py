import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
import glob

st.set_page_config(page_title="Simple Finance App", page_icon="💰", layout="wide")

category_file = "categories.json"
data_file_path = glob.glob('./data/*.csv')

if "categories" not in st.session_state:
    st.session_state.categories = {
        "Uncategorized": [],
    }

if os.path.exists(category_file):
    with open(category_file, "r") as f:
        st.session_state.categories = json.load(f)

def pre_load_csv_data():
    df = []
    for file in data_file_path:
        data = load_transactions(file)
        # print(data)
        df.append(data)

    df = pd.concat(df, ignore_index=True)

    return df

def save_categories():
    with open(category_file, "w") as f:
        json.dump(st.session_state.categories, f)

def categorize_transactions(df):
    df["category"] = "Uncategorized"

    for category, keywords in st.session_state.categories.items():
        if category == "Uncategorized" or not keywords:
            continue

        lowered_keywords = [keyword.lower().strip() for keyword in keywords]

        for idx, row in df.iterrows():
            details = row["title"].lower().strip()
            if details in lowered_keywords:
                df.at[idx, "category"] = category

    return df

def title_normalize(df):
    forbidden_words = ['Pagamento recebido', 'Estorno']
    df = df[~df['title'].isin(forbidden_words)]
    df['title'] = (
        df['title']
        .replace(r'\s*- Parcela\s*\d+/\d+', '', regex=True)
        .str.lower()
        .str.strip()
    )

    return df

def load_transactions(file):
    try:
        df = pd.read_csv(file)
        print(df)
        df.columns = [col.strip() for col in df.columns]
        df["date"] = pd.to_datetime(df["date"])

        return categorize_transactions(df)
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None

def add_keyword_to_category(category, keyword):
    keyword = keyword.strip()
    if keyword and keyword not in st.session_state.categories[category]:
        st.session_state.categories[category].append(keyword)
        save_categories()
        return True

    return False

def main():
    st.title("Simple Finance Dashboard")

    uploaded_file = st.file_uploader("Upload your transaction CSV file", type=["csv"])
    df_pre_loaded = pre_load_csv_data()

    if uploaded_file is not None or df_pre_loaded is not None:
        df = []
        if uploaded_file is not None:
            df = load_transactions(uploaded_file)
        else:
            df = df_pre_loaded

        if df is not None:
            # debits_df = df[df["Debit/Credit"] == "Debit"].copy()
            # credits_df = df[df["Debit/Credit"] == "Credit"].copy()
            df = title_normalize(df)
            st.session_state.debits_df = df.copy()

            # tab1, tab2 = st.tabs(["Expenses (Debits)", "Payments (Credits)"])
            # tab1 = st.tabs(["Expenses"])
            # with tab1:
            new_category = st.text_input("New Category Name")
            add_button = st.button("Add Category")

            if add_button and new_category:
                if new_category not in st.session_state.categories:
                    st.session_state.categories[new_category] = []
                    save_categories()
                    st.rerun()

            st.subheader("Your Expenses")
            edited_df = st.data_editor(
                st.session_state.debits_df[["title", "amount", "date", "category"]],
                column_config={
                    "title": st.column_config.TextColumn("Detalhe"),
                    "date": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
                    "amount": st.column_config.NumberColumn("Valor", format="R$%.2f"),
                    "category": st.column_config.SelectboxColumn(
                        "Categoria",
                        options=list(st.session_state.categories.keys())
                    )
                },
                hide_index=True,
                use_container_width=True,
                key="category_editor"
            )

            save_button = st.button("Apply Changes", type="primary")
            if save_button:
                for idx, row in edited_df.iterrows():
                    new_category = row["category"]
                    if new_category == st.session_state.debits_df.at[idx, "category"]:
                        continue

                    details = row["title"]
                    st.session_state.debits_df.at[idx, "category"] = new_category
                    add_keyword_to_category(new_category, details)

            st.subheader('Expense Summary')
            category_totals = st.session_state.debits_df.groupby("category")["amount"].sum().reset_index()
            category_totals = category_totals.sort_values("amount", ascending=False)

            st.dataframe(
                category_totals,
                column_config={
                    "amount": st.column_config.NumberColumn("amount", format="R$%.2f")
                },
                use_container_width=True,
                hide_index=True
            )

            fig = px.pie(
                category_totals,
                values="amount",
                names="category",
                title="Expenses by Category"
            )
            st.plotly_chart(fig, use_container_width=True)

            # with tab2:
            #     st.subheader("Payments Summary")
            #     total_payments = credits_df["Amount"].sum()
            #     st.metric("Total Payments", f"{total_payments:,.2f} AED")
            #     st.write(credits_df)

main()