
# AutomateFinancesWithPython
This project was created with the goal of helping to organize and categorize finances. The main financial institution is Nubank.

## Useful Commands

### Ambiente
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install SQLAlchemy matplotlib alembic
```

### Aplicação
```bash
streamlit run main.py
```

### Migrations (Alembic)
```bash
# Aplicar todas as migrations pendentes
alembic upgrade head

# Gerar nova migration automaticamente após alterar src/models.py
alembic revision --autogenerate -m "descricao_da_mudanca"

# Ver o histórico de migrations aplicadas
alembic history

# Ver qual migration está aplicada atualmente
alembic current

# Reverter a última migration
alembic downgrade -1

# Reverter todas as migrations
alembic downgrade base
```

## Todo
- Change the database from sqlite to postgresql;
- Add login page;


📊 Indicadores (KPIs)
Use st.metric ou st.columns do Streamlit para mostrar indicadores rápidos:

### Total de despesas no mês atual

Despesa média mensal

Categoria com maior gasto no mês

Média de gastos diários

Comparativo com o mês anterior (crescimento ou redução em %)

### 📈 Gráficos sugeridos
1. Gastos por categoria (Pizza ou Barra)
Mostra quais áreas consomem mais do seu orçamento.

Pode ser um gráfico de pizza (plt.pie) ou barras (plt.bar).

2. Evolução temporal (Linha)
Gastos por mês (soma de valores agrupados por mês).

Pode adicionar uma linha de média móvel (por exemplo, 3 meses) para suavizar a tendência.

3. Gastos por dia da semana
Ajuda a entender se você gasta mais nos fins de semana, por exemplo.

4. Comparativo mês a mês por categoria (Stacked Bar)
Ideal para ver se alguma categoria está crescendo consistentemente com o tempo.

5. Distribuição dos gastos (Histograma ou Boxplot)
Mostra a variabilidade dos gastos (tem muitos picos? É constante?).

6. Top 10 maiores despesas
Um gráfico de barras com as 10 maiores compras pode ser útil para identificar gastos pontuais altos.

🧮 Análises mais avançadas (opcional)
Detecção de anomalias: detectar gastos fora do padrão.

Projeção de despesas com base em média diária/mensal.

Simulação de orçamento: permitir que o usuário defina limites e veja se está estourando em tempo real.

> Inspired by [Tech With Tim's AutomateFinancesWithPython](https://github.com/techwithtim/AutomateFinancesWithPython).
> This project started as a fork, but has been extensively modified since then.