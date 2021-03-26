import pathlib
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from fbprophet import Prophet
from parse import save_to_csv, DATA_PATH


country = 'Ukraine'
predict_days = 180

PLOTS_PATH = pathlib.Path(__file__).parent.joinpath('plots')
csv_file = DATA_PATH.joinpath(country + '_' + datetime.today().strftime('%y_%m_%d.data'))

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
    future = m.make_future_dataframe(periods=predict_days)
    forecast = m.predict(future)
    return forecast


forecast_confirmed = predict(confirmed)
forecast_recovered = predict(recovered)
forecast_deaths = predict(deaths)


forecast_confirmed[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail()
d_day = forecast_confirmed['yhat'].max()
print(d_day)

fig = go.Figure()
fig.add_trace(go.Scatter(x=forecast_confirmed['ds'], y=forecast_confirmed['yhat'], mode='lines',
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

fig.update_layout(title=f'{country} covid cases', xaxis_tickfont_size=14, yaxis=dict(title='Number of predicted cases'))
fig.show(renderer='browser')


# confirmed_forecast_plot = m.plot(forecast)
# confirmed_forecast_plot = m.plot_components(forecast)
# forecast['yhat'].apply('{:.10f}'.format).tolist()
# forecast[forecast.ds == '2021-03-21']['yhat']

