# lambda_data_collection/lambda_data_collection.py

import boto3
import pymysql
import json
import os
import traceback

def get_secrets():
    aws_region = os.getenv('CUSTOM_AWS_REGION', 'ap-southeast-2')
    secret_name = os.getenv('SECRET_NAME')
    
    if not secret_name:
        print("Error: SECRET_NAME environment variable is not set.")
        return None

    print(f"Debug: AWS_REGION resolved to {aws_region}")
    print(f"Debug: SECRET_NAME resolved to {secret_name}")

    secrets_client = boto3.client('secretsmanager', region_name=aws_region)

    try:
        response = secrets_client.get_secret_value(SecretId=secret_name)
        print("Debug: Secrets Manager response received.")
        
        secret_data = json.loads(response['SecretString'])
        print("Debug: Parsed secret data successfully.")
        return secret_data
    except Exception as e:
        print(f"Error: Failed to fetch secrets. Exception: {e}")
        print(traceback.format_exc())
        return None

def connect_to_rds(secret_data):
    try:
        # Extract RDS connection details from secrets
        rds_host = secret_data.get("host")
        rds_user = secret_data.get("username")
        rds_password = secret_data.get("password")
        rds_database = secret_data.get("database")

        print(f"Debug: Attempting RDS connection to host: {rds_host}, database: {rds_database}")

        # Connect to the RDS instance
        connection = pymysql.connect(
            host=rds_host,
            user=rds_user,
            password=rds_password,
            database=rds_database,
            port=3306,
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=5  # Timeout for connection attempt
        )
        print("Successfully connected to the RDS database.")
        return connection
    except Exception as e:
        print(f"Error: Unable to connect to RDS. Exception: {e}")
        print(traceback.format_exc())
        return None

def query_dams_table(connection):
    try:
        print("Debug: Preparing to query the `dams` table.")
        with connection.cursor() as cursor:
            query = "SELECT * FROM dams;"
            print(f"Debug: Executing query: {query}")
            cursor.execute(query)
            results = cursor.fetchall()
            print("Retrieved rows from the `dams` table:")
            for row in results:
                print(row)
    except Exception as e:
        print(f"Error: Failed to query the dams table. Exception: {e}")
        print(traceback.format_exc())
    finally:
        print("Debug: Closing database connection.")
        connection.close()

def lambda_handler(event, context):
    print("Lambda `lambda_data_collection` started.")
    print(f"Event received: {json.dumps(event, indent=2)}")
    
    try:
        # Access and log secrets
        secret_data = get_secrets()
        if not secret_data:
            print("Error: Secrets retrieval failed. Exiting function.")
            return {
                "statusCode": 500,
                "body": "Failed to retrieve secrets from Secrets Manager."
            }

        # Connect to RDS and query data
        connection = connect_to_rds(secret_data)
        if not connection:
            print("Error: RDS connection failed. Exiting function.")
            return {
                "statusCode": 500,
                "body": "Failed to connect to RDS database."
            }

        query_dams_table(connection)

    except Exception as e:
        print(f"Error: An unexpected error occurred. Exception: {e}")
        print(traceback.format_exc())
        return {
            "statusCode": 500,
            "body": f"An unexpected error occurred. Exception: {str(e)}"
        }

    print("Lambda function executed successfully.")
    return {
        "statusCode": 200,
        "body": "Lambda function executed successfully."
    }
