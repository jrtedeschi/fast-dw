from faker import Faker
import pandas as pd
faker = Faker()
import logging
import yaml
from google.cloud import storage
from google.cloud import bigquery
from google.oauth2 import service_account

# generate fake data

credentials = service_account.Credentials.from_service_account_file(
    'gcloud_credentials.json',
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_ingestions_config():
    with open('ingestions/params.yaml', 'r') as file:
        ingestions_config = yaml.safe_load(file)
    return ingestions_config

def generate_fake_data(num_records):
    fake_data = []
    logging.info(f'Generating {num_records} fake records')
    for _ in range(num_records):
        fake_data.append({
            'id': faker.uuid4(),
            'name': faker.name(),
            'address': faker.address(),
            'email': faker.email(),
            'profile': faker.profile(),
            'phone_number': faker.phone_number(),
            'job': faker.job(),
            'company': faker.company(),
            'status': faker.random_element(elements=('active', 'inactive', 'pending')),
        })
    dataframe = pd.DataFrame(fake_data)
    logging.info(f'Generated {len(dataframe)} fake records')
    return dataframe


def upload_to_gcs(dataframe, bucket_name, filename):
    dataframe.to_parquet(filename)
    logging.info(f'Uploading {filename} to GCS bucket {bucket_name}')
    ## TODO: upload to GCS bucket

def upload_to_bq(dataframe, table_name, project_id, dataset_id, method = 'append'):
    logging.info(f'Uploading {len(dataframe)} records to BigQuery table {dataset_id}.{table_name}')
    dataframe.to_gbq(f'{dataset_id}.{table_name}', project_id=project_id, if_exists=method)
    logging.info(f'Uploaded {len(dataframe)} records to BigQuery table {dataset_id}.{table_name}')

if __name__ == '__main__':

    ingestions = load_ingestions_config()

    for ingestion in ingestions:
        num_records = 1000000
        logging.info(f'Ingestion: {ingestion}')
        logging.info(f'Generating {ingestion["num_records"]} fake records')
        dataframe = generate_fake_data(num_records=num_records)
        upload_to_bq(dataframe, table_name=ingestion['bigquerytable'], project_id=ingestion['googleprojectid'], dataset_id=ingestion['bigquerdataset'], method='append')

