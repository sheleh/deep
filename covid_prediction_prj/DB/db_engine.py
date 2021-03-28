from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///DB/Countries_Popul.db', echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class population(Base):
    __tablename__ = 'population'
    index = Column(Integer, primary_key=True)
    Country = Column(String)
    Population_c = Column(Integer)
    Date = Column(String)


def get_population(country):
    population_c = session.query(population.Population_c).filter(population.Country == country)
    population_c.all()
    return population_c[0][0]