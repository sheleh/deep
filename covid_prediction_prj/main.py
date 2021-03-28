import pathlib
import pandas as pd
from datetime import date
import plotly.graph_objects as go
from datetime import datetime
from fbprophet import Prophet
from parse import save_to_csv, DATA_PATH
from DB.db_engine import get_population
PREDICT_DAYS = 180

country = 'Egypt'

PLOTS_PATH = pathlib.Path(__file__).parent.joinpath('plots')
csv_file = DATA_PATH.joinpath(country + '_' + datetime.today().strftime('%y_%m_%d.data'))


date_to_go = date.fromisoformat('2021-09-07')

pd_date_to_go = pd.to_datetime(date_to_go)

# get population from db
count_pop = get_population(country)

if csv_file.exists():
    df = pd.read_csv(csv_file, sep=';')
else:
    save_to_csv(country)
    df = pd.read_csv(csv_file, sep=';')


df.columns = ['Date', 'Total confirmed', 'Recovered', 'Deaths']
confirmed = df.groupby('Date').sum()['Total confirmed'].reset_index()
recovered = df.groupby('Date').sum()['Recovered'].reset_index()
deaths = df.groupby('Date').sum()['Deaths'].reset_index()


confirmed.columns = ['ds', 'y']
# confirmed['ds'] = confirmed['ds'].dt.date
confirmed['ds'] = pd.to_datetime(confirmed['ds'])

recovered.columns = ['ds', 'y']
recovered['ds'] = pd.to_datetime(recovered['ds'])

deaths.columns = ['ds', 'y']
deaths['ds'] = pd.to_datetime(deaths['ds'])


def predict(ds):
    m = Prophet(interval_width=0.95)
    m.fit(ds)
    future = m.make_future_dataframe(periods=PREDICT_DAYS)
    forecast = m.predict(future)
    return forecast

# получаем прогноз на:
# подтвержденные
forecast_confirmed = predict(confirmed)
# выздоровевшие
forecast_recovered = predict(recovered)
# умершие
forecast_deaths = predict(deaths)
# больные на текущий момент(калькулируем только YHAT )
forecast_active = forecast_confirmed['yhat'] - forecast_recovered['yhat'] - forecast_deaths['yhat']


def grow_loss_weeks_confirmed():
    date_forecast_max = forecast_confirmed.get('ds').max()
    if pd_date_to_go + pd.DateOffset(weeks=2) < date_forecast_max:
        result = []
        # даты за предшествующие дни
        observing_date_past7 = pd_date_to_go - pd.DateOffset(weeks=1)
        observing_date_past14 = pd_date_to_go - pd.DateOffset(weeks=2)
        # даты за следующие дни
        observing_date_next7 = pd_date_to_go + pd.DateOffset(weeks=1)
        observing_date_next14 = pd_date_to_go + pd.DateOffset(weeks=2)
        # количество случаев в расчетный день
        predict_cases_confirmed = forecast_confirmed[forecast_confirmed.ds == pd_date_to_go]['yhat']
        result.append(predict_cases_confirmed)
        # расчет количество случаев за 7 и 14 предидущих дней
        observing_cases_past7 = forecast_confirmed[forecast_confirmed.ds == observing_date_past7]['yhat']
        result.append(observing_cases_past7)
        observing_cases_past14 = forecast_confirmed[forecast_confirmed.ds == observing_date_past14]['yhat']
        result.append(observing_cases_past14)
        # расчет количество случаев за 7 и 14 следующих дней
        observing_cases_next7 = forecast_confirmed[forecast_confirmed.ds == observing_date_next7]['yhat']
        result.append(observing_cases_next7)
        observing_cases_next14 = forecast_confirmed[forecast_confirmed.ds == observing_date_next14]['yhat']
        result.append(observing_cases_next14)
        #print(f'On {pd_date_to_go} {country} maybe will have {predict_cases_confirmed.item()}')
        # 0day_-7day_-14day_+7day_+14day
        return result
    else:
        print('too big period for forecasting')
        return f'too big period for forecasting'


def grow_loss_weeks_active():
    date_forecast_max_active = forecast_recovered.get('ds').max()
    if pd_date_to_go + pd.DateOffset(weeks=2) < date_forecast_max_active:
        result = []
        # даты за предшествующие дни
        observing_date_past7_act = pd_date_to_go - pd.DateOffset(weeks=1)
        observing_date_past14_act = pd_date_to_go - pd.DateOffset(weeks=2)
        # даты за следующие дни
        observing_date_next7_act = pd_date_to_go + pd.DateOffset(weeks=1)
        observing_date_next14_act = pd_date_to_go + pd.DateOffset(weeks=2)
        # количество случаев в расчетный день
        predict_cases_act = forecast_active[forecast_confirmed.ds == pd_date_to_go]
        result.append(predict_cases_act)
        # расчет количество случаев за 7 и 14 предидущих дней
        observing_cases_past7_act = forecast_active[forecast_confirmed.ds == observing_date_past7_act]
        result.append(observing_cases_past7_act)
        observing_cases_past14_act = forecast_active[forecast_confirmed.ds == observing_date_past14_act]
        result.append(observing_cases_past14_act)
        # расчет количество случаев за 7 и 14 следующих дней
        observing_cases_next7_act = forecast_active[forecast_confirmed.ds == observing_date_next7_act]
        result.append(observing_cases_next7_act)
        observing_cases_next14_act = forecast_active[forecast_confirmed.ds == observing_date_next14_act]
        result.append(observing_cases_next14_act)

        # 0day_-7day_-14day_+7day_+14day
        return result
    else:
        print('too big period for forecasting')
        return f'too big period for forecasting'


predicted_period_active = grow_loss_weeks_active()
predicted_period_cases = grow_loss_weeks_confirmed()


def epidemic_treshold(count_pop, predicted_period_active):
    # (cases/population)*100000
    # Для нинішнього епідемічного сезону поріг становить 518,68 хворих на 100 000 населення, вказує МОЗ.
    # Розрізняють такі рівні інтенсивності епідемічного підйому захворюваності на грип:
        #* середня – 649,71 на 100 000 населення;
        #* висока – 845,25 на 100 000 населення;
        #* дуже висока – 921,59 на 100 000 населення.

    result = (predicted_period_active[4]/count_pop)*100000
    print(f'active cases per 100.000 people = {result.item()}')
    return result


epidemic_treshold(count_pop, predicted_period_cases)


# increase_formula(predicted_period_cases)
def increase_formula(predicted_period_cases):
    # темп прироста заболеваемости в анализируемую неделю по отношению к предыдущей в %
    increase_past14 = ((predicted_period_cases[1].item() - predicted_period_cases[2].item()) /
                       predicted_period_cases[2].item()) * 100
    increase_next14 = ((predicted_period_cases[4].item() - predicted_period_cases[3].item()) /
                       predicted_period_cases[3].item()) * 100
    print(f'increase in past {increase_past14}')  # float
    print(f'increase in future {increase_next14}')
    return increase_past14, increase_next14


increase_formula(predicted_period_cases)


def make_plot():
    fig = go.Figure()
    #fig.add_trace(go.Scatter(x=forecast_confirmed['ds'], y=forecast_confirmed['yhat'], mode='lines',
    #                         name='Predicted_confirmed', line=dict(color='Red')))
    fig.add_trace(go.Scatter(x=forecast_confirmed['ds'], y=forecast_confirmed['trend'], mode='lines',
                             name='Predicted_confirmed', line=dict(color='Red')))
    fig.add_trace(go.Scatter(x=confirmed['ds'], y=confirmed['y'], mode='markers',
                             name='Confirmed', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=forecast_recovered['ds'], y=forecast_recovered['yhat'], mode='lines',
                             name='Predicted_recovered', line=dict(color='Red')))
    fig.add_trace(go.Scatter(x=recovered['ds'], y=recovered['y'], mode='markers',
                             name='Confirmed', line=dict(color='green')))
    fig.add_trace(go.Scatter(x=forecast_deaths['ds'], y=forecast_deaths['yhat'], mode='lines',
                             name='Predicted_deaths', line=dict(color='Red')))
    fig.add_trace(go.Scatter(x=deaths['ds'], y=deaths['y'], mode='markers',
                             name='Confirmed', line=dict(color='black')))
    fig.add_trace(go.Scatter(x=forecast_confirmed['ds'], y=forecast_active, mode='lines', name='Active', line=dict(color='Purple')))
    fig.update_layout(title=f'{country} covid cases', xaxis_tickfont_size=14, yaxis=dict(title='Number of predicted cases'))
    fig.show(renderer='browser')


make_plot()


#confirmed_forecast_plot = m.plot(forecast_confirmed)
# confirmed_forecast_plot = m.plot_components(forecast)
# forecast['yhat'].apply('{:.10f}'.format).tolist()
# forecast_confirmed[forecast_confirmed.ds == '2021-03-21']['yhat']

