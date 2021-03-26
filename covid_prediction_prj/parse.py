import pandas as pd
import mwclient
from mwtemplates import TemplateEditor
from datetime import datetime
import pathlib
import re

DATA_PATH = pathlib.Path(__file__).parent.joinpath('data/' + datetime.today().strftime('%y_%m_%d'))
PLOTS_PATH = pathlib.Path(__file__).parent.joinpath('plots')


def parse_jhu_confirmed(country):
    url_raw_confirmed = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data' \
              '/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
    data_confirmed = pd.read_csv(url_raw_confirmed, sep=",")
    data_confirmed.drop(['Province/State', 'Lat', 'Long'], axis=1, inplace=True)
    data_aggregated_confirmed = data_confirmed.groupby('Country/Region').sum()
    res_confirmed = data_aggregated_confirmed.loc[country]
    return res_confirmed


def parse_jhu_recovered(country):
    url_raw_recovered = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data' \
                        '/csse_covid_19_time_series/time_series_covid19_recovered_global.csv'
    data_recovered = pd.read_csv(url_raw_recovered, sep=',')
    data_recovered.drop(['Province/State', 'Lat', 'Long'], axis=1, inplace=True)
    data_recovered_aggregated = data_recovered.groupby('Country/Region').sum()
    res_recovered = data_recovered_aggregated.loc[country]
    return res_recovered


def parse_jhu_deaths(country):
    url_raw_deaths = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data' \
                     '/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
    data_deaths = pd.read_csv(url_raw_deaths, sep=',')
    data_deaths.drop(['Province/State', 'Lat', 'Long'], axis=1, inplace=True)
    data_deaths_aggregated = data_deaths.groupby('Country/Region').sum()
    res_deaths = data_deaths_aggregated.loc[country]
    return res_deaths


def save_to_csv(country):
    confirmed = parse_jhu_confirmed(country)
    recovered = parse_jhu_recovered(country)
    deaths = parse_jhu_deaths(country)
    DATA_PATH.mkdir(parents=True, exist_ok=True)
    csv_file = DATA_PATH.joinpath(country + '_' + datetime.today().strftime('%y_%m_%d.data'))
    final = pd.concat([confirmed, recovered, deaths], axis=1)
    csv_data = final.to_csv(date_format='%Y-%m-%d', header=False, sep=';')
    with csv_file.open('w') as f:
        f.write(csv_data)


def parse_wiki(country):
    DATA_PATH.mkdir(parents=True, exist_ok=True)
    csv_file = DATA_PATH.joinpath(country + '_' + datetime.today().strftime('%y_%m_%d.data'))
    site = mwclient.Site('en.wikipedia.org')
    page = site.pages[u'Template:COVID-19_pandemic_data/{}_medical_cases_chart'.format(country)]

    assert page.exists
    template_data = page.text()

    te = TemplateEditor(template_data)
    template = te.templates['Medical cases chart'][0]
    csv_data = template.parameters['data'].value
    csv_data = re.sub("(<!--.*?-->)", "", csv_data, flags=re.DOTALL)
    # print(csv_data)
    csv_data = csv_data.replace('+', ';;;')
    # print(csv_data)
    csv_data = re.sub("(;;;;;;.*?\n$)", "", csv_data, flags=re.DOTALL)
    csv_data = re.sub("(;;;.*?\n$)", "", csv_data, flags=re.DOTALL)
    # csv_data = re.sub("/\w++\..*/", "", csv_data, flags=re.DOTALL).strip()
    # csv_data = re.sub("+.*?}}", "", csv_data, flags=re.DOTALL).strip()
    print(csv_data)
    with csv_file.open('w') as f:
        f.write(csv_data)


