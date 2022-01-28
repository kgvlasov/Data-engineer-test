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


def transform_weather_data():
    raw_data_query = '''
    select * 
    from test_task_kgvlasov.weather_raw_data
    where date > (now() - interval '10 minute')
    '''
    avg_temp = pd.read_sql_query(raw_data_query, get_sql_conn())['temp_c'].mean()

    marts_query = '''
    select *
    from test_task_kgvlasov.data_mart 
    order by date DESC
    limit 1
    '''
    ten_min_temp = pd.read_sql_query(marts_query, get_sql_conn())

    result = pd.DataFrame(columns = ['date','state','value'])

    if (ten_min_temp.empty):
        result.loc[0,'state'] = 'first_dimention'
        result.loc[0,'value'] = avg_temp
        result.loc[0,'date'] = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        write_to_sql(result,'data_mart')
    else:
        last_mean_temp = ten_min_temp['value'].mean() 

        if (avg_temp > last_mean_temp):
            result.loc[0,'state'] = 'up'            
        elif(avg_temp < last_mean_temp):
            result.loc[0,'state'] = 'down'
        else:
            result.loc[0,'state'] = 'same'

        result.loc[0,'value'] = avg_temp
        result.loc[0,'date'] = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        write_to_sql(result,'data_mart')

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
        'weather_api_transform',
        default_args=default_args,
        max_active_runs=1,
        description='Transforming raw data from Weatherapi.com',
        schedule_interval='*/10 * * * *',
        start_date=datetime(2022,1,27),
        tags=['transforming'],
) as dag:
    transform_data = PythonOperator(
        task_id='Transforming_weatherapi_data',
        python_callable=transform_weather_data
    )

transform_data

