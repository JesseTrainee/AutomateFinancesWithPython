import streamlit as st
import pandas as pd
import plotly.express as px
from src.normalize import title_normalize
import src.models
import src.utils

src.models.create_tables()
st.set_page_config(page_title="Simple Finance App", page_icon="💰", layout="wide")

def save_input_categories(categories):
    print(type(categories))
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

    st.markdown("### Categories")

    for idx, row in categories.iterrows():
        if row['name'] == 'Uncategorized':
            continue
        col1, col2 = st.columns([0.9, 0.1])

        with col1:
            st.markdown(f"**{row['name']}**")

        with col2:
            if st.button("X", key=f"delete_{row['id']}"):
                src.models.delete_category(int(row['id']))
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
            credit_df.at[idx, "category"] = new_category
            keyword = src.models.add_keyword_to_category(new_category, title)
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


# def load_and_process_transactions():
#     df = src.models.get_transactions()
#     if df is not None:
#         df = title_normalize(df)
#         df["date"] = pd.to_datetime(df["date"])
#     return df

def display_group_by_month(df):
    df['date'] = pd.to_datetime(df['date'])
    monthly_summary = df.groupby(df['date'].dt.to_period('M'))['amount'].sum().reset_index()
    st.dataframe(
        monthly_summary,
        column_config={
            "amount": st.column_config.NumberColumn("amount", format="R$%.2f")
        },
        use_container_width=True,
        hide_index=True
    )

def display_years_tab(df):
    st.subheader("Expenses by Month")
    years = df["date"].dt.year.unique()
    if len(years) > 0:
        tabs = st.tabs([str(year) for year in years])
        for tab, year in zip(tabs, years):
            with tab:
                display_group_by_month(df[df["date"].dt.year == year])
    else:
        st.write("No data available.")

def display_expenses(df):
    st.subheader("Your Expenses")
    categories = src.models.get_categories()
    edited_df = st.data_editor(
        df,
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

    add_category_to_transaction(edited_df, df)
    display_expense_summary(df)
    display_years_tab(df)

def show_sidebar_filter():
    with st.sidebar:
        st.title("Filters")
        st.subheader("Period")

        start_dt = st.date_input("Start Date", src.utils.get_last_month_date())
        end_dt = st.date_input("End Date")

        range = {
            'start_dt': pd.to_datetime(start_dt),
            'end_dt': pd.to_datetime(end_dt)
        }
        return range

        # st.subheader("Categories")
        # # categories = src.models.get_categories()
        # # categories = src.models.get_categories()
        # # selected_categories = st.multiselect(
        # #     "Select Categorie",
        # #     options=list(categories['name']),
        # #     default=list(categories['name'])
        # # )

def filter_transactions(df, range):
    if df is not None:
        df = df[(df['date'] >= range['start_dt']) & (df['date'] <= range['end_dt'])]

    return df

def main():
    st.title("Personal Finance Dashboard")
    initialize_session_state()
    range = show_sidebar_filter()
    df = src.models.get_transactions_data()
    df = filter_transactions(df, range)
    tab_summary, tab_categ, tab_upload = st.tabs(["Summary", "Categories", "Upload Data"])
    with tab_upload:
        handle_file_upload()
    with tab_summary:
        if df is not None and len(df) > 0:
            display_expenses(df)
        else:
            st.warning("No data available from this range. Please, upload CSV data.")
    with tab_categ:
        categories = src.models.get_categories()
        save_input_categories(categories)
main()