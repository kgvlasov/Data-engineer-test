import requests
import pandas as pd
from sqlalchemy import create_engine
from datetime import date, datetime, timedelta
import psycopg2
from airflow import DAG
from airflow.operators.python import PythonOperator
import os
from airflow.utils.dates import days_ago


USER = os.getenv('AIRFLOW_DATABASE_USERNAME')
PSWD = os.getenv('AIRFLOW_DATABASE_PASSWORD')
DBN = os.getenv('AIRFLOW_DATABASE_NAME')

def get_weather_data(city='Moscow',aqi='no'):
    key = os.getenv('WEATHER_API_KEY')
    try:
        request = requests.get("http://api.weatherapi.com/v1/current.json", params={'q': city, 'key': key, 'aqi': aqi})
        result = request.json()
        temp = pd.DataFrame.from_dict(result['current']).reset_index(drop=True).loc[0:0,['last_updated','temp_c','feelslike_c']]
        temp['date'] = datetime.today().strftime('%Y-%m-%d %H:%M')
        write_to_sql(temp,'weather_raw_data')
    except Exception as e:
        print("Request problem:", e)
        pass 

def get_sql_conn():
    creds = {'usr': USER,
             'pswd': PSWD,
             'hst': 'postgresql',
             'prt': 5432,
             'dbn': DBN}
    connstr = 'postgresql+psycopg2://{usr}:{pswd}@{hst}:{prt}/{dbn}'
    engine = create_engine(connstr.format(**creds))
    return engine

def write_to_sql(data, table):
    data.to_sql(table, con=get_sql_conn(), schema='test_task_kgvlasov', if_exists='append', index=False)

default_args = {
    'owner': 'airflow',
}

with DAG(
        'weather_api_raw_data',
        default_args=default_args,
        max_active_runs=1,
        description='Downloading raw data from Weatherapi.com',
        schedule_interval='*/1 * * * *',
        start_date=datetime(2022,1,27),
        tags=['raw_data'],
) as dag:
    download_from_weather_api = PythonOperator(
        task_id='download_from_weather_api',
        python_callable=get_weather_data
    )

download_from_weather_api

