import json

def lambda_handler(event, context):
    print("hello world")
    return {
        "statusCode": 200,
        "body": json.dumps("Hello World from lambda_db_connection!")
    }
