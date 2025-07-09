import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
from src.normalize import title_normalize
from src.utils import pre_load_csv_data, load_transactions
from src.category import save_categories, add_keyword_to_category
import src.models

src.models.create_tables()
st.set_page_config(page_title="Simple Finance App", page_icon="💰", layout="wide")

category_file = "categories.json"

if "categories" not in st.session_state:
    st.session_state.categories = {
        "Uncategorized": [],
    }


# if os.path.exists(category_file):
#     with open(category_file, "r") as f:
#         st.session_state.categories = json.load(f)

def main():
    st.title("Simple Finance Dashboard")

    # botao de upload de csv
    uploaded_file = st.file_uploader("Upload your transaction CSV file", type=["csv"])
    #carrega os dados da base de dados
    df_pre_loaded = src.models.get_transactions()

    if uploaded_file is not None or df_pre_loaded is not None:
        df = []
        if uploaded_file is not None:
            #carrega o arquivo e salva na base de dados
            df = src.utils.load_transactions(uploaded_file)
            df = title_normalize(df)
            df = src.models.save_transactions(df)

        df = src.models.get_transactions()
        print(df)

        if df is not None:
            df = title_normalize(df)
            categories = src.models.get_categories()

            new_category = st.text_input("New Category Name")
            add_button = st.button("Add Category")

            if add_button and new_category:
                if new_category not in categories['name']:
                    save_category(new_category)
                    st.rerun()

            credit_df = src.models.get_transactions_data()
            st.subheader("Your Expenses")
            edited_df = st.data_editor(
                credit_df,
                column_config={
                    "title": st.column_config.TextColumn("Detalhe"),
                    "date": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
                    "amount": st.column_config.NumberColumn("Valor", format="R$%.2f"),
                    "category": st.column_config.SelectboxColumn(
                        "Categoria",
                        options=list(categories['name'])
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
                    if new_category == credit_df.at[idx, "category"]:
                        continue

                    details = row["title"]
                    credit_df.at[idx, "category"] = new_category
                    src.models.add_keyword_to_category(new_category, details)

            st.subheader('Expense Summary')
            category_totals = credit_df.groupby("category")["amount"].sum().reset_index()
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