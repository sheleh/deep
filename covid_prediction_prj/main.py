import pathlib
import warnings
import pandas as pd
from datetime import date
import datetime as dt
from covid_prediction_prj.functions import predict, pr_time_grow_loss_weeks_active, predicted_epidemic_treshold,\
    current_epidemic_treshold, f_grow_loss_weeks_active, f_grow_loss_weeks_confirmed, increase_formula, make_plot
from parse import save_to_csv, DATA_PATH
from covid_prediction_prj.DB.db_engine import get_population, save_to_db, readPd_from_sql, tablename_check,\
    get_last_insertion_date
from covid_prediction_prj.DB.prediction_data_db_engine import save_prediction_to_db, tablename_check_prediction, \
    read_pd_prediction_from_sql

warnings.filterwarnings('ignore')

PREDICT_DAYS = 180

country = 'Ukraine'

#PLOTS_PATH = pathlib.Path(__file__).parent.joinpath('plots')
#csv_file = DATA_PATH.joinpath(country + '_' + datetime.today().strftime('%y_%m_%d.data'))


date_to_go = date.fromisoformat('2021-09-07')

pd_date_to_go = pd.to_datetime(date_to_go)
print(pd_date_to_go)
# get population from db
count_pop = get_population(country)

last_date_bd = pd.to_datetime(get_last_insertion_date(country))

print(last_date_bd)

current_date = pd.to_datetime(dt.date.today()).normalize()
print(current_date)


if not tablename_check(country) or current_date - pd.DateOffset(days = 1) > last_date_bd:
    save_to_db(country)
df = readPd_from_sql(country)


df.columns = ['Date', 'Total confirmed', 'Recovered', 'Deaths', 'Active']
confirmed = df.groupby('Date').sum()['Total confirmed'].reset_index()
recovered = df.groupby('Date').sum()['Recovered'].reset_index()
deaths = df.groupby('Date').sum()['Deaths'].reset_index()
active = df.groupby('Date').sum()['Active'].reset_index()


# confirmed['ds'] = confirmed['ds'].dt.date
confirmed.columns = ['ds', 'y']
confirmed['ds'] = pd.to_datetime(confirmed['ds'])

recovered.columns = ['ds', 'y']
recovered['ds'] = pd.to_datetime(recovered['ds'])

deaths.columns = ['ds', 'y']
deaths['ds'] = pd.to_datetime(deaths['ds'])

active.columns = ['ds', 'y']
active['ds'] = pd.to_datetime(active['ds'])

# получаем прогноз на:
# подтвержденные
#forecast_confirmed = predict(confirmed, PREDICT_DAYS)
# выздоровевшие
forecast_recovered = predict(recovered, PREDICT_DAYS)
# умершие
forecast_deaths = predict(deaths, PREDICT_DAYS)
# больные на текущий момент
forecast_active = predict(active, PREDICT_DAYS)


if not tablename_check_prediction(country):
    forecast_confirmed = predict(confirmed, PREDICT_DAYS)
    save_prediction_to_db(country, forecast_confirmed)
else:
    forecast_confirmed = read_pd_prediction_from_sql(country)

print(forecast_confirmed)


current_period_active = pr_time_grow_loss_weeks_active(active, forecast_active)
predicted_period_active = f_grow_loss_weeks_active(forecast_active, pd_date_to_go)
predicted_period_cases = f_grow_loss_weeks_confirmed(forecast_confirmed, pd_date_to_go, country)

# вызов Функций Эпидемиологического пороговово значения
predicted_epidemic_treshold(count_pop, predicted_period_cases)
current_epidemic_treshold(count_pop, current_period_active)

# вызов функции подсчета прироста ПОДТВЕРЖДЕННЫХ случаев в БУДУЩЕМ
increase_formula(predicted_period_cases)


make_plot(forecast_confirmed, confirmed, forecast_recovered, recovered, forecast_deaths, deaths, forecast_active, active, country)


#confirmed_forecast_plot = m.plot(forecast_confirmed)
# confirmed_forecast_plot = m.plot_components(forecast)
# forecast['yhat'].apply('{:.10f}'.format).tolist()
# forecast_confirmed[forecast_confirmed.ds == '2021-03-21']['yhat']



