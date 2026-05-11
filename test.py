from sqlalchemy import inspect, create_engine

engine = create_engine('sqlite:///finances.db')
inspector = inspect(engine)
print(inspector.get_table_names())  # mostra todas as tabelas

# mostra colunas da tabela categories
print(inspector.get_columns('categories'))
