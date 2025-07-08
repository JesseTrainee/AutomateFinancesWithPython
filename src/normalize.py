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