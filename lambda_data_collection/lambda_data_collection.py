# lambda_data_collection/lambda_data_collection.py

def lambda_handler(event, context):
    print("Hello, world!")
    print(f"Event received: {event}")
    return {
        "statusCode": 200,
        "body": "Lambda executed successfully"
    }
