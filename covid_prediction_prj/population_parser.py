import re
import pandas as pd
url = 'https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_population'
# Без надобности НЕ ЗАПУСКАТЬ!!!!!

df = pd.read_html(url)[0]
df.drop(['% of world', 'Source(official or United Nations)', 'Rank'], axis=1, inplace=True)
df_csv = df.to_csv()
for row in df_csv:
    r = re.sub('[|]', '', row, flags=re.DOTALL).strip()
    print(r)

print(df_csv)

#DATA_PATH.mkdir(parents=True, exist_ok=True)
#csv_file = DATA_PATH.joinpath(datetime.today().strftime('%y_%m_%d.data'))
#if csv_file.exists():
#    with csv_file.open() as f:
#        return read_csv(f)

#req = request('GET', url)
#soup = BeautifulSoup(req.content, 'html.parser')

#texts = soup.find('China')
#print(texts)
#df.rename(columns={'Country(or dependent territory)': 'Country'}, inplace=True)
##df.to_csv('population.csv', index=False)

#from sqlalchemy import create_engine
#engine = create_engine('sqlite:///data/Countries_Popul.db', echo=False)
#df.to_sql('population', con=engine, if_exists='append')
#engine.execute('SELECT * FROM population').fetchall()



