import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
from src.normalize import title_normalize
from src.utils import pre_load_csv_data, load_transactions
from src.category import save_categories, add_keyword_to_category

st.set_page_config(page_title="Simple Finance App", page_icon="💰", layout="wide")

category_file = "categories.json"

if "categories" not in st.session_state:
    st.session_state.categories = {
        "Uncategorized": [],
    }

if os.path.exists(category_file):
    with open(category_file, "r") as f:
        st.session_state.categories = json.load(f)

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
            df = title_normalize(df)
            st.session_state.debits_df = df.copy()

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

main()