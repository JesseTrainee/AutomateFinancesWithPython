from sqlalchemy import update, create_engine, Column, Integer, String, Float, Date, ForeignKey, select
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import pandas as pd

Base = declarative_base()
class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    transactions = relationship('Transaction', back_populates='category')
    keywords = relationship('Keyword', back_populates='category', cascade="all, delete-orphan")

class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    title = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'))

    category = relationship('Category', back_populates='transactions')

class Keyword(Base):
    __tablename__ = 'keywords'
    id = Column(Integer, primary_key=True)
    word = Column(String, unique=True, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'))

    category = relationship('Category', back_populates='keywords')

    def to_dict(self):
        return {
            "id": self.id,
            "word": self.word,
            "category_id": self.category_id,
        }

# Conexão e criação do banco
engine = create_engine('sqlite:///finances.db')
Session = sessionmaker(bind=engine)
session = Session()

def create_tables():
    Base.metadata.create_all(engine)

def save_category(category_name = 'Uncategorized'):
    category = Category(name=category_name)
    session.add(category)
    session.commit()

    return category

def save_keyword(keyword, category_id):
    keyword = Keyword(word=keyword, category_id=category_id)
    session.add(keyword)
    session.commit()

def get_categories():
    stmt = select(Category)
    result = pd.read_sql(stmt, session.bind)

    return result

def get_category(category_name = 'Uncategorized'):
    return session.query(Category).filter_by(name=category_name).first()

def get_category_by_id(id):
    return session.query(Category, id)

def get_keyword(word):
    return session.query(Keyword).filter_by(word=word).first()

def add_keyword_to_category(category, word):
    category = get_category(category)
    if not category:
        category = save_category(category)

    word = word.strip()
    save_keyword(word, category.id)
    keyword = get_keyword(word)
    return keyword

def get_transactions():
    stmt = select(Transaction)
    result = pd.read_sql(stmt, session.bind)

    return result

def get_keywords():
    stmt = select(Keyword)
    return pd.read_sql(stmt, session.bind)

def save_transactions(df):
    category = None
    if 'category_id' in df and pd.notnull(df['category_id']):
        category = get_category_by_id(int(df['category_id']))
    if not category:
        category = get_category('Uncategorized')
    if not category:
        category = save_category()
    df['category_id'] = category.id
    session = Session()
    for _, row in df.iterrows():
        transaction = Transaction(
            date=row['date'],
            title=row['title'],
            amount=row['amount'],
            category_id=row['category_id']
        )
        session.add(transaction)
    session.commit()
    session.close()

def get_transactions_data():
    results = session.query(
        Transaction.title,
        Transaction.date,
        Transaction.amount,
        Category.name
    ).join(Category).all()

    # Converter para DataFrame
    df = pd.DataFrame(results, columns=['title', 'date', 'amount', 'category'])

    return df

def update_transactions(keyword):
    stmt = (
        update(Transaction)
        .where(Transaction.title == keyword.word)
        .values(category_id=keyword.category_id)
    )
    session.execute(stmt)
    session.commit()