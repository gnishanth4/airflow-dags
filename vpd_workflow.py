import datetime as dt
import os
import airflow
import json
import boto3
import requests
from airflow.models import Variable
from pathlib import Path
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
#from airflow.contrib.operators.ecs_operator import ECSOperator
from airflow.providers.amazon.aws.operators.ecs import ECSOperator
#import airflow.providers.amazon.aws.operators.ecs.ECSOperator
default_args = {
        'owner': 'airflow',
        'start_date': airflow.utils.dates.days_ago(2),
        'retries': 1
}
CONFIG_FILE = 'airflowconfig.json'
path = Path(__file__).with_name(CONFIG_FILE)
with path.open() as f:
    default_conf = json.load(f)
 
'''def fetch_lambda_parameters( **kwargs):
    print("S3 Bucket Name and Key passed by Remote Trigger as Conf: {}, {} ".format(kwargs['dag_run'].conf['s3bucket'], kwargs['dag_run'].conf['s3key']))
    bucket = kwargs['dag_run'].conf['s3bucket']
    bucket_key = "-tco="+kwargs['dag_run'].conf['s3key']
    bucket_name = "-tcb="+kwargs['dag_run'].conf['s3bucket']
    Variable.set('vpd_tc_input_bucket_name', bucket_name)
    Variable.set('vpd_tc_input_bucket_key', bucket_key)
    Variable.set('vpd_output_bucket_name', "-ob="+bucket)
    #Variable.set('vpd_input_context_bucket_name', "-cdb="+bucket)
    Variable.set('vpd_input_ftd_bucket_name', "-ftdb="+bucket)
'''
with DAG('vnv_validation_plan_definition_workflow',
        default_args=default_args,
        schedule_interval=None,
        ) as dag:
    '''task0 = PythonOperator(task_id='fetch_parameters',
            python_callable=fetch_lambda_parameters,
            provide_context=True)'''
    task1 = ECSOperator(
            task_id="validation_plan_definintion_ecs_task",
            task_definition = default_conf["ecs"][0]["validation_plan_definintion_ecs_task"]["task_definition"],
            cluster = default_conf["ecs"][0]["validation_plan_definintion_ecs_task"]["cluster"],
            overrides = {
                "containerOverrides": [
                        {
                        "name": default_conf["ecs"][0]["validation_plan_definintion_ecs_task"]["container_name"],
                        "command":["python3","/src/define_validation_plan.py","--bucket=vnv-airflow-e2e","--ftd=SysEng/Functions_flow_table_definition.xlsx","--tc=SysEng/Test_Cases.xlsx","--outbucket=vpd/output"]
                        },
                        ]},
            network_configuration={
                "awsvpcConfiguration": {
                        "securityGroups": [os.environ.get("SECURITY_GROUP_ID", default_conf["ecs"][0]["validation_plan_definintion_ecs_task"]["SECURITY_GROUP_ID"])],
                            "subnets": [os.environ.get("SUBNET_ID", default_conf["ecs"][0]["validation_plan_definintion_ecs_task"]["SUBNET_ID"])],
                                "assignPublicIp":"ENABLED"
                                }},
            #aws_conn_id= default_conf["aws_conn_id"],
            region_name= default_conf["region_name"],
            launch_type= default_conf["ecs"][0]["validation_plan_definintion_ecs_task"]["launch_type"],
            platform_version = default_conf["platform_version"],
            awslogs_group = default_conf["ecs"][0]["validation_plan_definintion_ecs_task"]["awslogs_group"],
            awslogs_region = default_conf["awslogs_region"],
            awslogs_stream_prefix = default_conf["ecs"][0]["validation_plan_definintion_ecs_task"]["awslogs_stream_prefix"]
            )
task1
