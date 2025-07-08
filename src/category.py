import json
import streamlit as st

category_file = "categories.json"

def save_categories():
    with open(category_file, "w") as f:
        json.dump(st.session_state.categories, f)

def add_keyword_to_category(category, keyword):
    keyword = keyword.strip()
    if keyword and keyword not in st.session_state.categories[category]:
        st.session_state.categories[category].append(keyword)
        save_categories()
        return True

    return False

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