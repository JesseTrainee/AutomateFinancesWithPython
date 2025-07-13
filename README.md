
# AutomateFinancesWithPython

## Todo
- Salvar os dados na base de dados;
- Criar outras visualizações dos dados;
- Pegar os dados de csv do google drive;
- Colocar os csv pedidos do app recebidos por email no google drive;
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

### 🛠️ Exemplo de agregações úteis com pandas
### Total por categoria
df.groupby('categoria')['valor'].sum().sort_values(ascending=False)

### Total por mês
df['data'] = pd.to_datetime(df['data'])
df['ano_mes'] = df['data'].dt.to_period('M')
df.groupby('ano_mes')['valor'].sum()

### Média diária por mês
df['dia'] = df['data'].dt.date
df.groupby('dia')['valor'].sum().resample('M').mean()

> Inspirado por [Tech With Tim's AutomateFinancesWithPython](https://github.com/techwithtim/AutomateFinancesWithPython). Este projeto começou como um fork, mas foi amplamente modificado desde então.
