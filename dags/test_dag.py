import json
import logging
from datetime import timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

# change these args as needed


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(0),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(hours=1),
}

dag = DAG('test_dag', default_args=default_args)


def test_func():
    import sys
    logging.info(sys.path)


with DAG('test_dag', default_args=default_args) as dag:
    task1 = PythonOperator(
        task_id='save_file',
        python_callable=test_func,
        dag=dag)

    finish_task = BashOperator(
        task_id='denote_finish',
        bash_command='echo "ALL DONE"',
        dag=dag)

    task1 >> finish_task
