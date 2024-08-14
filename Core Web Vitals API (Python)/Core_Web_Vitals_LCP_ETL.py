#------------------------------------------------------------EXTRACT------------------------------------------------------------------------------------
import numpy as np
import pandas as pd
import os
import datetime
import asyncio
import pyarrow
import logging
from pandas_gbq import to_gbq
from google.oauth2 import service_account
from google.cloud import bigquery
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
    Filter,
    FilterExpression
    
)
  
  #Setting script directory
  # Define the path to the script
  script_path = '~/projects/looker-studio-pyscripts/Core Web Vitals/Core_Web_Vitals_LCP_ETL.py'

  # Expand the ~ to the full path
  expanded_script_path = os.path.expanduser(script_path)
  
  # Get the absolute path to the script
  absolute_script_path = os.path.abspath(expanded_script_path)
  
  # Get the directory containing the script
  script_dir = os.path.dirname(absolute_script_path)
  
  # Change the working directory to the script's directory
  os.chdir(script_dir)
  
  #Set-up logs
  logging.basicConfig(filename = 'LCP_ETL_logs.log', level = logging.INFO, format = '%(asctime)s - %(message)s', datefmt = '%d-%b-%y %H:%M:%S1')
  
  #GA4 API credentials
  os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'service_account.json'
  property_id="300253194"
  client = BetaAnalyticsDataClient()
  
  # Big Query credentials
  scopes = ["https://www.googleapis.com/auth/bigquery"]
  key_path = os.path.expanduser('~/projects/looker-studio-pyscripts/Core Web Vitals/service_account.json')
  
  # Use the correct import and method call for service account credentials
  credentials = service_account.Credentials.from_service_account_file(key_path, scopes=scopes)
  
  project_id = 'core-web-vitals--1721718217423'
  dataset_id = 'Core_Web_Vitals'
  table_id = 'lcp_aggregated'
  dataset_table = f'{project_id}.{dataset_id}.{table_id}'

  # Instantiate the BigQuery client using the credentials
  client_bq = bigquery.Client(credentials=credentials, project=project_id)
  
  

  #API Request
  request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[
          Dimension(name="eventName"),
          Dimension(name="date"),
          Dimension(name="customEvent:metric_id"),
          Dimension(name="deviceCategory"),
          Dimension(name="firstUserDefaultChannelGroup"),
          Dimension(name="browser"),
          Dimension(name="customEvent:element"),
          Dimension(name="customEvent:element_url"),
          Dimension(name="customEvent:page_location_clean"),
          ],
        metrics=[
          Metric(name="customEvent:metric_value"),
          Metric(name="customEvent:element_render_delay"),
          Metric(name="customEvent:element_time_to_first_byte"),
          
        ],
        date_ranges=[DateRange(start_date="2024-08-05", end_date="today")],
        dimension_filter=FilterExpression(
            filter=Filter(
                field_name="eventName",
                string_filter=Filter.StringFilter(value="CLS"))),
    )

def run_request():
    print('Starting API request...')
    response = client.run_report(request)
    print('Request completed')
    return response

if __name__ == "__main__":
    response = run_request()

  
  #API Response transformation
async def header_aggregation():
   logging.info('Header aggregation finished')
   await asyncio.sleep(4)
   header = [header.name for header in response.dimension_headers] + [header.name for header in response.metric_headers]
   return header


async def row_aggregation():
  logging.info('Row aggregation finished')
  await asyncio.sleep(4)
  rows = []
  for row in response.rows:[rows.append([dimension_value.value for dimension_value in row.dimension_values] + [metric_value.value for metric_value in row.metric_values])]
  return rows


header = asyncio.run(header_aggregation())
rows = asyncio.run(row_aggregation())
  
  #Creating a DataFrame
output = {}
output['headers'] = header
output['rows'] = rows
df_raw = pd.DataFrame(np.array(output['rows']), columns = output['headers'])
df_raw.info()
  
#------------------------------------------------------------TRANFORM-----------------------------------------------------------------------------------  
  #Changing date string column to date dimension
df_raw['date'] = pd.to_datetime(df_raw['date'], format='%Y%m%d')
df_raw['customEvent:metric_value'] = df_raw['customEvent:metric_value'].astype('float')
df_raw['customEvent:element_render_delay'] = df_raw['customEvent:element_render_delay'].astype('float')
df_raw['customEvent:element_time_to_first_byte'] = df_raw['customEvent:element_time_to_first_byte'].astype('float')

  #Making sure only the biggest value of indicator is taken
df_raw['biggest_value_check'] = df_raw.sort_values('customEvent:metric_value', ascending = False).groupby(['customEvent:metric_id']).cumcount()+1
df_raw.reset_index()
df_raw = df_raw.loc[df_raw['biggest_value_check'] <= 1]
df_raw.drop(columns = 'biggest_value_check', inplace = True)
  
  #Changing date string column to date dimension
df_perc = df_raw[['date','eventName','customEvent:page_location_clean','customEvent:metric_value']]
  
  #Creating 90th percentile for unique values of date, event_name and page_location_clean
def percentile_90(x):
  return np.percentile(x, 90)
  
df_percentile = df_perc.groupby(['date', 'eventName', 'customEvent:page_location_clean'])['customEvent:metric_value'].agg(p90=percentile_90).reset_index()
  
  #Merging page percentile with element level data
df_combined = df_raw.merge(df_percentile, how = 'left', left_on = ['date', 'eventName', 'customEvent:page_location_clean'], right_on = ['date', 'eventName', 'customEvent:page_location_clean'])
df_combined['sub_value'] = df_combined['customEvent:metric_value'] - df_combined['p90']
df_combined = df_combined.loc[df_combined['sub_value'] <= 0]
df_combined.info()

  #Cleaning data for better understanding
df_combined.rename(columns = {'eventName': 'event_name'}, inplace = True)
df_combined.rename(columns = {'customEvent:metric_id': 'metric_id'}, inplace = True)
df_combined.rename(columns = {'deviceCategory': 'device'}, inplace = True)
df_combined.rename(columns = {'firstUserDefaultChannelGroup': 'source_medium'}, inplace = True)
df_combined.rename(columns = {'customEvent:element_render_delay': 'element_render_delay'}, inplace = True)
df_combined.rename(columns = {'customEvent:element_time_to_first_byte': 'element_time_to_first_byte'}, inplace = True)
df_combined.rename(columns = {'customEvent:page_location_clean' : 'page_location_clean'}, inplace = True)
df_combined.rename(columns = {'customEvent:element' : 'element'}, inplace = True)
df_combined.rename(columns = {'customEvent:element_url' : 'element_url'}, inplace = True)
df_combined.rename(columns = {'customEvent:metric_value': 'metric_value'}, inplace = True)
df_combined.drop(columns = ['p90','sub_value'], inplace = True)
df_combined.info()
  
#------------------------------------------------------------LOAD------------------------------------------------------------------------------------
  
  #Creating config for big query data injection 
  
table_ref = bigquery.TableReference(client_bq.dataset(dataset_id), table_id)
schema=[
        bigquery.SchemaField("event_name","STRING", mode="REQUIRED"),
        bigquery.SchemaField("date", "DATE", mode="REQUIRED"),
        bigquery.SchemaField("metric_id","STRING", mode="REQUIRED"),
        bigquery.SchemaField("device","STRING", mode="REQUIRED"),
        bigquery.SchemaField("source_medium","STRING", mode="REQUIRED"),
        bigquery.SchemaField("browser","STRING", mode="REQUIRED"),
        bigquery.SchemaField("element","STRING", mode="REQUIRED"),
        bigquery.SchemaField("element_url","STRING", mode="REQUIRED"),
        bigquery.SchemaField("page_location_clean","STRING", mode="REQUIRED"),
        bigquery.SchemaField("element_render_delay","INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("element_time_to_first_byte","INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("metric_value","INTEGER", mode="REQUIRED")]

  
try:
    client_bq.get_table(table_ref)
    logging.info(f"Table {dataset_table} already exists. No need to create a new one.")
except Exception:
    # Table does not exist, create it
    table = client_bq.create_table(table)
    logging.info(f"Created table {table.project}.{table.dataset_id}.{table.table_id}")

try:   
    to_gbq(df_combined, dataset_table, project_id = project_id, if_exists = 'replace')
    logging.info(f"Table {dataset_table} has been successfully updated")
except: 
    logging.info(f"Error accured while updating {dataset_table}, debug the code")




