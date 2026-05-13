import streamlit as st
import pandas as pd
import plotly.express as px
from src.normalize import title_normalize
import src.models
import src.utils
from drive_gmail_sync import sincronizar_faturas
import time

src.models.create_tables()
st.set_page_config(page_title="Simple Finance App", page_icon="💰", layout="wide")

def display_kpi_row(df):
    total = df["amount"].sum()
    count = len(df)
    months = df["date"].dt.to_period("M").nunique()
    avg_monthly = total / months if months > 0 else 0
    top_cat = (
        df.groupby("category")["amount"].sum().idxmax()
        if not df.empty else "—"
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Spent", f"R$ {total:,.2f}")
    c2.metric("Transactions", count)
    c3.metric("Monthly Average", f"R$ {avg_monthly:,.2f}")
    c4.metric("Top Category", top_cat)


def save_input_categories(categories):
    # Checa se precisa limpar o input ANTES de mostrá-lo
    if "clear_new_category" in st.session_state and st.session_state["clear_new_category"]:
        st.session_state["new_category_input"] = ""
        st.session_state["clear_new_category"] = False
        st.rerun()

    col_input, col_btn = st.columns([0.75, 0.25])
    with col_input:
        new_category = st.text_input(
            "New Category Name",
            key="new_category_input",
            label_visibility="collapsed",
            placeholder="New category name...",
        )
    with col_btn:
        add_button = st.button("＋ Add Category", use_container_width=True)

    if add_button and new_category:
        if new_category not in categories['name'].values:
            src.models.save_category(new_category)
            st.session_state["clear_new_category"] = True
            st.rerun()

    st.divider()
    st.subheader("Categories")

    for idx, row in categories.iterrows():
        if row['name'] == 'Uncategorized':
            continue
        col1, col2 = st.columns([0.9, 0.1])
        with col1:
            st.markdown(f"**{row['name']}**")
        with col2:
            if st.button("✕", key=f"delete_{row['id']}", help=f"Delete {row['name']}"):
                src.models.delete_category(int(row['id']))
                st.rerun()
        st.divider()

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
        df = src.utils.load_transactions(uploaded_file)
        df = title_normalize(df)
        src.models.save_transactions(df)
        df = src.models.get_transactions_data()
        st.write('Last 10 transactions from file')
        st.dataframe(df.tail(10),
            column_order=["title", "date", "amount", "category"],
            use_container_width=True,
            hide_index=True
        )

        if uploaded_file.name != st.session_state.last_uploaded_filename:
            st.session_state.last_uploaded_filename = uploaded_file.name
            st.rerun()

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
    st.subheader("Expenses per Month")
    years = df["date"].dt.year.unique()
    if len(years) > 0:
        tabs = st.tabs([str(year) for year in years])
        for tab, year in zip(tabs, years):
            with tab:
                display_group_by_month(df[df["date"].dt.year == year])
    else:
        st.write("No data available.")

def display_expenses(df):
    display_kpi_row(df)
    st.divider()

    col_editor, col_summary = st.columns([2, 1])

    categories = src.models.get_categories()

    with col_editor:
        st.subheader("Transactions")
        edited_df = st.data_editor(
            df,
            column_config={
                "title": st.column_config.TextColumn("Description"),
                "date": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
                "amount": st.column_config.NumberColumn("Amount", format="R$%.2f"),
                "category": st.column_config.SelectboxColumn(
                    "Category",
                    options=list(categories['name'])
                )
            },
            hide_index=True,
            use_container_width=True,
            key="category_editor"
        )
        add_category_to_transaction(edited_df, df)

    with col_summary:
        st.subheader("By Category")
        category_totals = df.groupby("category")["amount"].sum().reset_index()
        category_totals = category_totals.sort_values("amount", ascending=False)
        st.dataframe(
            category_totals,
            column_config={
                "category": st.column_config.TextColumn("Category"),
                "amount": st.column_config.NumberColumn("Total", format="R$%.2f"),
            },
            use_container_width=True,
            hide_index=True
        )

    st.divider()
    display_years_tab(df)

def show_sidebar_filter():
    with st.sidebar:
        st.title("Filters")
        st.subheader("Period")

        start_dt = st.date_input("Start Date", src.utils.get_last_year_date())
        end_dt = st.date_input("End Date")

        date_range = {
            'start_dt': pd.to_datetime(start_dt),
            'end_dt': pd.to_datetime(end_dt)
        }
        return date_range

def filter_transactions(df, date_range):
    if df is not None:
        df = df[(df['date'] >= date_range['start_dt']) & (df['date'] <= date_range['end_dt'])]

    return df

def show_dashboards(df):
    display_kpi_row(df)
    st.divider()

    col_pie, col_bar = st.columns(2)

    with col_pie:
        category_totals = df.groupby("category")["amount"].sum().reset_index()
        category_totals = category_totals.sort_values("amount", ascending=False)
        fig_pie = px.pie(
            category_totals,
            values="amount",
            names="category",
            title="Expenses by Category",
            hole=0.35,
        )
        fig_pie.update_traces(textposition="inside", textinfo="percent+label")
        fig_pie.update_layout(showlegend=False, margin=dict(t=40, b=0, l=0, r=0))
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_bar:
        top_expenses = df.groupby("title", as_index=False)["amount"].sum()
        top_expenses["abs_amount"] = top_expenses["amount"].abs()
        top_expenses = top_expenses.nlargest(10, "abs_amount").sort_values("abs_amount")
        fig_bar = px.bar(
            top_expenses,
            x="abs_amount",
            y="title",
            orientation="h",
            title="Top 10 Expenses by Title",
            labels={"abs_amount": "Amount (R$)", "title": ""},
            text_auto=".2f",
        )
        fig_bar.update_layout(margin=dict(t=40, b=0, l=0, r=0))
        st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    monthly = df.copy()
    monthly["month"] = monthly["date"].dt.to_period("M").dt.to_timestamp()
    monthly_totals = monthly.groupby("month")["amount"].sum().reset_index()
    fig_line = px.line(
        monthly_totals,
        x="month",
        y="amount",
        title="Monthly Spending Trend",
        labels={"month": "Month", "amount": "Total (R$)"},
        markers=True,
    )
    fig_line.update_layout(margin=dict(t=40, b=0, l=0, r=0))
    st.plotly_chart(fig_line, use_container_width=True)


def main():
    st.title("Personal Finance Dashboard")
    initialize_session_state()
    date_range = show_sidebar_filter()
    df = src.models.get_transactions_data()
    df = filter_transactions(df, date_range)

    tab_summary, tab_dash, tab_categ, tab_upload = st.tabs(
        ["Summary", "Dashboard", "Categories", "Upload"]
    )

    with tab_summary:
        if df is not None and len(df) > 0:
            display_expenses(df)
        else:
            st.warning("No data available for this period. Please upload a CSV file.")

    with tab_dash:
        if df is not None and len(df) > 0:
            show_dashboards(df)
        else:
            st.warning("No data available for this period. Please upload a CSV file.")

    with tab_categ:
        categories = src.models.get_categories()
        save_input_categories(categories)

    with tab_upload:
        handle_file_upload()
        st.divider()
        if st.button("🔄 Fetch invoices from Gmail and send to Drive"):
            with st.spinner("Fetching and syncing invoices..."):
                resultado = sincronizar_faturas()
                st.success(resultado)
                st.toast("Sync complete!")
                time.sleep(2)
                st.rerun()

main()
