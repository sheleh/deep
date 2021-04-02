from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import pandas as pd

engine = create_engine('sqlite:///DB/prediction_data.db', echo=False)
#engine = create_engine('sqlite:///prediction_data', echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()
conn = engine.connect()


def save_prediction_to_db(country, data, type_of):
    with engine.begin() as connection:
        print(f'ILL SAVE CALCULATIONS to DB')
        data.to_sql(country + '_calculation_data_' + type_of, con=connection, if_exists='replace', index=True)


def read_pd_prediction_from_sql(country, type_of):
    with engine.begin() as connection:
        df = pd.read_sql_table(country + '_calculation_data_' + type_of, connection)
        print('ILL READ CALCULATIONS FROM DB')
    return df


def tablename_check_prediction(country, type_of):
    with engine.begin() as connection:
        inspection = inspect(connection)
        res = inspection.has_table(country + '_calculation_data_' + type_of)
    return res
