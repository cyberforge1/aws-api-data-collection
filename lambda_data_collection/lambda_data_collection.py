import boto3
import json
import os
import pymysql  # Ensure this library is included in the deployment package
import logging
from decimal import Decimal

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_secrets():
    aws_region = os.getenv('CUSTOM_AWS_REGION', 'ap-southeast-2')
    secret_name = os.getenv('SECRET_NAME')

    if not secret_name:
        logger.error("SECRET_NAME environment variable is not set.")
        return None

    logger.debug(f"AWS_REGION resolved to {aws_region}")
    logger.debug(f"SECRET_NAME resolved to {secret_name}")

    secrets_client = boto3.client('secretsmanager', region_name=aws_region)

    try:
        response = secrets_client.get_secret_value(SecretId=secret_name)
        logger.debug("Secrets Manager response received.")
        logger.debug(f"SecretString: {response.get('SecretString', 'No SecretString found')}")

        secret_data = json.loads(response['SecretString'])
        logger.debug("Parsed secret data successfully.")
        return secret_data
    except Exception as e:
        logger.error(f"Failed to fetch secrets. Exception: {e}")
        return None

def connect_to_database(db_host, db_port, db_name, db_user, db_password):
    try:
        connection = pymysql.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name,
            connect_timeout=5
        )
        logger.info(f"Successfully connected to the database '{db_name}' at {db_host}:{db_port}.")
        return connection
    except Exception as e:
        logger.error(f"Failed to connect to the database. Exception: {e}")
        return None

def query_dams_table(connection):
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT * FROM dams;")
            dams = cursor.fetchall()
            
            if dams:
                logger.info(f"Retrieved {len(dams)} entries from the 'dams' table:")
                for dam in dams:
                    # Convert Decimal objects to float for JSON serialization
                    dam_serializable = {k: (float(v) if isinstance(v, Decimal) else v) for k, v in dam.items()}
                    logger.info(json.dumps(dam_serializable))
            else:
                logger.info("No entries found in the 'dams' table.")
    except Exception as e:
        logger.error(f"Error querying the 'dams' table. Exception: {e}")

def lambda_handler(event, context):
    logger.info("Lambda `lambda_data_collection` started.")
    logger.info(f"Event received: {json.dumps(event, indent=2)}")

    # Access and log secrets
    secret_data = get_secrets()
    if secret_data:
        logger.info("Successfully retrieved secrets:")
        for key, value in secret_data.items():
            logger.info(f"Secret Variable - {key}: {value}")
    else:
        logger.error("Failed to retrieve secrets.")
        return {
            "statusCode": 500,
            "body": "Failed to retrieve secrets."
        }

    # Extract information from the event if necessary
    source = event.get('source', 'Unknown Source')
    detail_type = event.get('detail-type', 'Unknown DetailType')
    detail = event.get('detail', {})
    message_detail = detail.get('message', 'No details provided.')

    logger.debug(f"Event Source: {source}")
    logger.debug(f"Event DetailType: {detail_type}")
    logger.debug(f"Event Detail: {json.dumps(detail, indent=2)}")

    # Prepare a user-friendly message for email
    email_message = f"""
    Hello,

    This is a notification from your AWS Lambda function.

    Event Source: {source}
    Event Type: {detail_type}
    Message: {message_detail}

    Thank you,
    Your AWS Lambda Function
    """

    # Prepare default message for other protocols
    default_message = {
        "Source": source,
        "DetailType": detail_type,
        "Detail": detail
    }

    # Publish to SNS
    sns_topic_arn = os.getenv('SNS_TOPIC_ARN')
    if not sns_topic_arn:
        logger.error("SNS_TOPIC_ARN environment variable is not set.")
        return {
            "statusCode": 500,
            "body": "SNS_TOPIC_ARN environment variable is not set."
        }

    sns_client = boto3.client('sns')

    try:
        # Create a message structure to customize the email message
        message_structure = {
            "default": json.dumps(default_message),
            "email": email_message
        }

        response = sns_client.publish(
            TopicArn=sns_topic_arn,
            Message=json.dumps(message_structure),
            Subject="Secret Updated Notification",
            MessageStructure='json'
        )
        logger.debug(f"SNS Publish Response: {json.dumps(response, indent=2)}")
    except Exception as e:
        logger.error(f"Failed to publish message to SNS. Exception: {e}")
        return {
            "statusCode": 500,
            "body": f"Error: Failed to publish message to SNS. Exception: {e}"
        }

    # Database Connection and Querying
    db_host = os.getenv('DB_HOST')
    db_port = int(os.getenv('DB_PORT', '3306'))
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')

    # Validate database environment variables
    missing_db_vars = []
    for var, value in [('DB_HOST', db_host), ('DB_NAME', db_name), ('DB_USER', db_user), ('DB_PASSWORD', db_password)]:
        if not value:
            missing_db_vars.append(var)

    if missing_db_vars:
        logger.error(f"Missing environment variables for DB connection: {', '.join(missing_db_vars)}")
        return {
            "statusCode": 500,
            "body": f"Missing environment variables for DB connection: {', '.join(missing_db_vars)}"
        }

    connection = connect_to_database(db_host, db_port, db_name, db_user, db_password)
    if connection:
        query_dams_table(connection)
        connection.close()
        logger.info("Database connection closed.")
    else:
        logger.error("Database connection failed.")
        return {
            "statusCode": 500,
            "body": "Database connection failed."
        }

    return {
        "statusCode": 200,
        "body": "Lambda executed successfully, notification sent via SNS, and database operations completed."
    }
