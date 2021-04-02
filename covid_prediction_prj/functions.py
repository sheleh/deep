from fbprophet import Prophet
import pandas as pd
import plotly.graph_objects as go


def predict(ds, predict_days):
    '''Facebook timeline prediction '''
    m = Prophet(interval_width=0.98)
    m.fit(ds)
    future = m.make_future_dataframe(periods=predict_days)
    forecast = m.predict(future)
    return forecast


def pr_time_grow_loss_weeks_active(active_c, forecast_active):
    current_date = active_c.get('ds').max()
    result = []
    # даты за предшествующие дни
    observing_date_past7_act = current_date - pd.DateOffset(weeks=1)
    observing_date_past14_act = current_date - pd.DateOffset(weeks=2)
    # даты за следующие дни
    observing_date_next7_act = current_date + pd.DateOffset(weeks=1)
    observing_date_next14_act = current_date + pd.DateOffset(weeks=2)
    # количество случаев в текущий день
    predict_cases_act = active_c[active_c.ds == current_date]['y']
    result.append(predict_cases_act)
    # расчет количество случаев за 7 и 14 предидущих дней
    observing_cases_past7_act = active_c[active_c.ds == observing_date_past7_act]['y']
    result.append(observing_cases_past7_act)
    observing_cases_past14_act = active_c[active_c.ds == observing_date_past14_act]['y']
    result.append(observing_cases_past14_act)
    # расчет количество случаев за 7 и 14 следующих дней
    observing_cases_next7_act = forecast_active[forecast_active.ds == observing_date_next7_act]['yhat']
    result.append(observing_cases_next7_act)
    observing_cases_next14_act = forecast_active[forecast_active.ds == observing_date_next14_act]['yhat']
    result.append(observing_cases_next14_act)
    # 0day_-7day_-14day_+7day_+14day
    return result


def predicted_epidemic_treshold(count_pop, predicted_period_active):
    """
        функция для вычисления порогового значения  количества заболевших на 100000 человек в БУДУЩЕМ
        (cases/population)*100.000
        # LOW 518,68
        # MID – 649,71 на 100 000 населення;
        # HIGH – 845,25 на 100 000 населення
        # EXTRA HIGH – 921,59 на 100 000 населення
    """
    result = (predicted_period_active[0].astype('int64')/count_pop)*100000
    print(f'active cases per 100.000 people = {result.item()}')
    return result


def current_epidemic_treshold(count_pop, current_period_active):
    """
        функция для вычисления порогового значения  количества заболевших на 100000 человек НА ТЕКУЩИЙ МОМЕНТ
        (cases/population)*100.000
        # LOW 518,68
        # MID – 649,71 на 100 000 населення;
        # HIGH – 845,25 на 100 000 населення
        # EXTRA HIGH – 921,59 на 100 000 населення
    """
    result = (current_period_active[0].astype('int64')/count_pop)*100000
    print(f'Current active cases per 100.000 people = {result.item()}')
    return result


def f_grow_loss_weeks_active(forecast_active, pd_date_to_go):
    """
    Подсчет количества АКТИВНЫХ заболевших в периоде -14-7-0+7+14 дней
    """
    date_forecast_max_active = forecast_active.get('ds').max()
    if pd_date_to_go + pd.DateOffset(weeks=2) < date_forecast_max_active:
        result = []
        # даты за предшествующие дни
        observing_date_past7_act = pd_date_to_go - pd.DateOffset(weeks=1)
        observing_date_past14_act = pd_date_to_go - pd.DateOffset(weeks=2)
        # даты за следующие дни
        observing_date_next7_act = pd_date_to_go + pd.DateOffset(weeks=1)
        observing_date_next14_act = pd_date_to_go + pd.DateOffset(weeks=2)
        # количество случаев в расчетный день
        predict_cases_act = forecast_active[forecast_active.ds == pd_date_to_go]
        result.append(predict_cases_act)
        # расчет количество случаев за 7 и 14 предидущих дней
        observing_cases_past7_act = forecast_active[forecast_active.ds == observing_date_past7_act]
        result.append(observing_cases_past7_act)
        observing_cases_past14_act = forecast_active[forecast_active.ds == observing_date_past14_act]
        result.append(observing_cases_past14_act)
        # расчет количество случаев за 7 и 14 следующих дней
        observing_cases_next7_act = forecast_active[forecast_active.ds == observing_date_next7_act]
        result.append(observing_cases_next7_act)
        observing_cases_next14_act = forecast_active[forecast_active.ds == observing_date_next14_act]
        result.append(observing_cases_next14_act)
        # 0day_-7day_-14day_+7day_+14day
        return result
    else:
        print('too big period for forecasting')
        return f'too big period for forecasting'


def f_grow_loss_weeks_confirmed(forecast_confirmed, pd_date_to_go, country):
    """
    Подсчет количества ПОДТВЕРЖДЕННЫХ случаев в периоде -14-7-0+7+14 дней
    """
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
        print(f'On {pd_date_to_go} {country} maybe will have {predict_cases_confirmed.item()}')
        # 0day_-7day_-14day_+7day_+14day
        return result
    else:
        print('too big period for forecasting')
        return f'too big period for forecasting'


def increase_formula(predicted_period_cases):
    """
    темп прироста заболеваемости в анализируемую неделю по отношению к предыдущей в %
    """
    increase_past14 = ((predicted_period_cases[1].item() - predicted_period_cases[2].item()) /
                       predicted_period_cases[2].item()) * 100
    increase_next14 = ((predicted_period_cases[4].item() - predicted_period_cases[3].item()) /
                       predicted_period_cases[3].item()) * 100
    print(f'increase in past {increase_past14}')  # float
    print(f'increase in future {increase_next14}')
    return increase_past14, increase_next14


def data_preparing(df):
    df.columns = ['Date', 'Total confirmed', 'Recovered', 'Deaths', 'Active']
    confirmed = df.groupby('Date').sum()['Total confirmed'].reset_index()
    recovered = df.groupby('Date').sum()['Recovered'].reset_index()
    deaths = df.groupby('Date').sum()['Deaths'].reset_index()
    active = df.groupby('Date').sum()['Active'].reset_index()

    confirmed.columns = ['ds', 'y']
    confirmed['ds'] = pd.to_datetime(confirmed['ds'])

    recovered.columns = ['ds', 'y']
    recovered['ds'] = pd.to_datetime(recovered['ds'])

    deaths.columns = ['ds', 'y']
    deaths['ds'] = pd.to_datetime(deaths['ds'])

    active.columns = ['ds', 'y']
    active['ds'] = pd.to_datetime(active['ds'])
    return confirmed, recovered, deaths, active


def make_plot(forecast_confirmed, confirmed, forecast_recovered, recovered,
              forecast_deaths, deaths, forecast_active, active, country):
    """
    Building a graphic plot

    """
    fig = go.Figure()
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
    fig.add_trace(go.Scatter(x=forecast_active['ds'], y=forecast_active['trend'], mode='lines',
                             name='Predicted_Active', line=dict(color='Purple')))
    fig.add_trace(go.Scatter(x=active['ds'], y=active['y'], mode='markers',
                             name='Active', line=dict(color='yellow')))

    fig.update_layout(title=f'{country} covid cases', xaxis_tickfont_size=14,
                      yaxis=dict(title='Number of predicted cases'))
    fig.show(renderer='browser')

