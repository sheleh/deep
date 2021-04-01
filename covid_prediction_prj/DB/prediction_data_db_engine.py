from sqlalchemy import create_engine, Column, String, Integer, Date, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from covid_prediction_prj.parse import concatenated_pd
from sqlalchemy.sql import text
import pandas as pd

engine = create_engine('sqlite:///DB/prediction_data.db', echo=False)
#engine = create_engine('sqlite:///prediction_data', echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()
conn = engine.connect()


def save_prediction_to_db(country, data):
    with engine.begin() as connection:
        print(f'ILL SAVE CALCULATIONS to DB')
        data.to_sql(country + '_calculation_data', con=connection, if_exists='replace', index=True)


def read_pd_prediction_from_sql(country):
    with engine.begin() as connection:
        df = pd.read_sql_table(country + '_calculation_data', connection)
        print('ILL READ CALCULATIONS FROM DB')
    return df


def tablename_check_prediction(country):
    with engine.begin() as connection:
        inspection = inspect(connection)
        return inspection.has_table(country + '_calculation_data')

