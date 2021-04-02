import pathlib
import warnings
import pandas as pd
from datetime import date
import datetime as dt
from covid_prediction_prj.functions import predict, pr_time_grow_loss_weeks_active, predicted_epidemic_treshold,\
    current_epidemic_treshold, f_grow_loss_weeks_active, f_grow_loss_weeks_confirmed, increase_formula, make_plot,\
    data_preparing
from parse import save_to_csv, DATA_PATH
from covid_prediction_prj.DB.db_engine import get_population, save_to_db, readPd_from_sql, tablename_check,\
    get_last_insertion_date, get_countries_exist
from covid_prediction_prj.DB.prediction_data_db_engine import save_prediction_to_db, tablename_check_prediction, \
    read_pd_prediction_from_sql

warnings.filterwarnings('ignore')

PREDICT_DAYS = 180
date_to_go = date.fromisoformat('2021-09-07')
country = 'Japan'

# get population from db
get_countries_exist(country)
count_pop = get_population(country)


pd_date_to_go = pd.to_datetime(date_to_go)
print(pd_date_to_go)


current_date = pd.to_datetime(dt.date.today()).normalize()
print(current_date)


if not tablename_check(country):
    save_to_db(country)
last_date_bd = pd.to_datetime(get_last_insertion_date(country))

if current_date - pd.DateOffset(days = 1) > last_date_bd:
    save_to_db(country)

df = readPd_from_sql(country)

# получаем прогноз на:
# подтвержденные
#forecast_confirmed = predict(confirmed, PREDICT_DAYS)
# выздоровевшие
#forecast_recovered = predict(recovered, PREDICT_DAYS)
# умершие
#forecast_deaths = predict(deaths, PREDICT_DAYS)
# больные на текущий момент
#forecast_active = predict(active, PREDICT_DAYS)


confirmed, recovered, deaths, active = data_preparing(df)

if not tablename_check_prediction(country, '_confirmed'):
    forecast_confirmed = predict(confirmed, PREDICT_DAYS)
    save_prediction_to_db(country, forecast_confirmed, '_confirmed')
if not tablename_check_prediction(country, '_recovered'):
    forecast_recovered = predict(recovered, PREDICT_DAYS)
    save_prediction_to_db(country, forecast_recovered, '_recovered')
if not tablename_check_prediction(country, '_deaths'):
    forecast_deaths = predict(deaths, PREDICT_DAYS)
    save_prediction_to_db(country, forecast_deaths, '_deaths')
if not tablename_check_prediction(country, '_active'):
    forecast_active = predict(active, PREDICT_DAYS)
    save_prediction_to_db(country, forecast_active, '_active')


forecast_confirmed = read_pd_prediction_from_sql(country, '_confirmed')
forecast_recovered = read_pd_prediction_from_sql(country, '_recovered')
forecast_deaths = read_pd_prediction_from_sql(country, '_deaths')
forecast_active = read_pd_prediction_from_sql(country, '_active')


current_period_active = pr_time_grow_loss_weeks_active(active, forecast_active)
predicted_period_active = f_grow_loss_weeks_active(forecast_active, pd_date_to_go)
predicted_period_cases = f_grow_loss_weeks_confirmed(forecast_confirmed, pd_date_to_go, country)

# вызов Функций Эпидемиологического пороговово значения
predicted_epidemic_treshold(count_pop, predicted_period_cases)
current_epidemic_treshold(count_pop, current_period_active)

# вызов функции подсчета прироста ПОДТВЕРЖДЕННЫХ случаев в БУДУЩЕМ
increase_formula(predicted_period_cases)


make_plot(forecast_confirmed, confirmed, forecast_recovered, recovered,
          forecast_deaths, deaths, forecast_active, active, country)


#confirmed_forecast_plot = m.plot(forecast_confirmed)
# confirmed_forecast_plot = m.plot_components(forecast)
# forecast['yhat'].apply('{:.10f}'.format).tolist()
# forecast_confirmed[forecast_confirmed.ds == '2021-03-21']['yhat']

#PLOTS_PATH = pathlib.Path(__file__).parent.joinpath('plots')
#csv_file = DATA_PATH.joinpath(country + '_' + datetime.today().strftime('%y_%m_%d.data'))



