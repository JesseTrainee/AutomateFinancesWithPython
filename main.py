import streamlit as st
import pandas as pd
import plotly.express as px
from src.normalize import title_normalize
import src.models

src.models.create_tables()
st.set_page_config(page_title="Simple Finance App", page_icon="💰", layout="wide")

def save_input_categories(categories):
    # Checa se precisa limpar o input ANTES de mostrá-lo
    if "clear_new_category" in st.session_state and st.session_state["clear_new_category"]:
        st.session_state["new_category_input"] = ""
        st.session_state["clear_new_category"] = False
        st.rerun()

    # Mostra o campo normalmente
    new_category = st.text_input("New Category Name", key="new_category_input")
    add_button = st.button("Add Category")

    # Lógica do botão
    if add_button and new_category:
        if new_category not in categories['name']:
            src.models.save_category(new_category)
            # Marca para limpar o input na próxima execução
            st.session_state["clear_new_category"] = True
            st.rerun()

def display_expense_summary(credit_df):
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

def add_category_to_transaction(edited_df, credit_df):
    save_button = st.button("Apply Changes", type="primary")
    if save_button:
        for idx, row in edited_df.iterrows():
            new_category = row["category"]
            if new_category == credit_df.at[idx, "category"]:
                continue

            title = row["title"]
            print(title)
            credit_df.at[idx, "category"] = new_category
            keyword = src.models.add_keyword_to_category(new_category, title)
            print(keyword)
            src.models.update_transactions(keyword)
            st.rerun()

def initialize_session_state():
    if "last_uploaded_filename" not in st.session_state:
        st.session_state.last_uploaded_filename = None

def handle_file_upload():
    uploaded_file = st.file_uploader("Upload your transaction CSV file", type=["csv"])
    if uploaded_file is not None:
        if uploaded_file.name != st.session_state.last_uploaded_filename:
            st.session_state.last_uploaded_filename = uploaded_file.name

        df = src.utils.load_transactions(uploaded_file)
        df = title_normalize(df)
        src.models.save_transactions(df)


def load_and_process_transactions():
    df = src.models.get_transactions()
    if df is not None:
        df = title_normalize(df)
    return df

def display_group_by_month(df):
    st.subheader("Expenses by Category")
    df['date'] = pd.to_datetime(df['date'])
    monthly_summary = df.groupby(df['date'].dt.to_period('M'))['amount'].sum().reset_index()
    print(monthly_summary)
    st.dataframe(
        monthly_summary,
        column_config={
            "amount": st.column_config.NumberColumn("amount", format="R$%.2f")
        },
        use_container_width=True,
        hide_index=True
    )


def display_expenses(df):
    categories = src.models.get_categories()
    save_input_categories(categories)

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
    add_category_to_transaction(edited_df, credit_df)
    display_expense_summary(credit_df)
    display_group_by_month(credit_df)

def main():
    st.title("Simple Finance Dashboard")
    initialize_session_state()
    handle_file_upload()
    df = load_and_process_transactions()
    if df is not None:
        display_expenses(df)

main()