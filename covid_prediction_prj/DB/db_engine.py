from sqlalchemy import create_engine, Column, String, Integer, Date, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from covid_prediction_prj.parse import concatenated_pd
from sqlalchemy.sql import text
import pandas as pd

engine = create_engine('sqlite:///DB/Countries_Popul.db', echo=False)
#engine = create_engine('sqlite:///Countries_Popul.db', echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()
conn = engine.connect()


class population(Base):
    __tablename__ = 'population'
    index = Column(Integer, primary_key=True)
    Country = Column(String)
    Population_c = Column(Integer)
    Date = Column(String)


class confirmed_cases_table_test(Base):
    __tablename__ = 'confirmed_cases_table_test'
    date = Column(Date, primary_key=True)
    c_cases = Column(Integer)


def get_population(country):
    population_c = session.query(population.Population_c).filter(population.Country == country)
    population_c.all()
    return population_c[0][0]


def get_countries_list():
    c_names = session.query(population.Country)
    return c_names


def save_to_db(country):
    with engine.begin() as connection:
        confirmed = concatenated_pd(country)
        print(f'ILL SAVE to DB')
        confirmed.to_sql(country + '_epidemic_data', con=connection, if_exists='replace', index=True)


def readPd_from_sql(country):
    with engine.begin() as connection:
        df = pd.read_sql_table(country + '_epidemic_data', connection)
        print('ILL READ FROM DB')
    return df


def tablename_check(country):
    with engine.begin() as connection:
        inspection = inspect(connection)
        return inspection.has_table(country + '_epidemic_data')

def get_last_insertion_date(country):
    with engine.begin() as connection:
        table = country + '_epidemic_data'
        query = f'SELECT * FROM {table}'
        row = connection.execute(query).fetchall()
        return row[-1][0]


