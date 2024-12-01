# lambda_data_collection/lambda_data_collection.py

import boto3
import json
import os

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
        # Modify the print statement to avoid json.dumps on the entire response
        # This prevents serialization errors due to non-serializable objects like datetime
        print("Debug: Secrets Manager response received.")
        
        # Optionally, log specific parts of the response if needed
        # For example, you can log the SecretString
        print(f"Debug: SecretString: {response.get('SecretString', 'No SecretString found')}")

        secret_data = json.loads(response['SecretString'])
        print("Debug: Parsed secret data successfully.")
        return secret_data
    except Exception as e:
        print(f"Error: Failed to fetch secrets. Exception: {e}")
        return None

def lambda_handler(event, context):
    print("Lambda `lambda_data_collection` started.")
    print(f"Event received: {json.dumps(event, indent=2)}")
    
    # Access and log secrets
    secret_data = get_secrets()
    if secret_data:
        print("Debug: Successfully retrieved secrets:")
        for key, value in secret_data.items():
            print(f"Secret Variable - {key}: {value}")
    else:
        print("Error: Failed to retrieve secrets.")

    # Extract information from the event if necessary
    source = event.get('source', 'Unknown Source')
    detail_type = event.get('detail-type', 'Unknown DetailType')
    detail = event.get('detail', {})
    message_detail = detail.get('message', 'No details provided.')
    
    print(f"Debug: Event Source: {source}")
    print(f"Debug: Event DetailType: {detail_type}")
    print(f"Debug: Event Detail: {json.dumps(detail, indent=2)}")
    
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
        print("Error: SNS_TOPIC_ARN environment variable is not set.")
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
        print(f"Debug: SNS Publish Response: {json.dumps(response, indent=2)}")
        return {
            "statusCode": 200,
            "body": "Lambda executed successfully and notification sent via SNS"
        }
    except Exception as e:
        print(f"Error: Failed to publish message to SNS. Exception: {e}")
        return {
            "statusCode": 500,
            "body": f"Error: Failed to publish message to SNS. Exception: {e}"
        }
