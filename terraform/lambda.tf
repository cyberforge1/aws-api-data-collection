# terraform/lambda.tf

resource "aws_lambda_function" "lambda_trigger" {
  function_name    = "lambda_trigger"
  role             = aws_iam_role.lambda_execution_role.arn
  handler          = "lambda_trigger.lambda_handler"
  runtime          = "python3.8"
  filename         = "${path.module}/../zipped_lambda_functions/lambda_trigger.zip"
  source_code_hash = filebase64sha256("${path.module}/../zipped_lambda_functions/lambda_trigger.zip")

  # Add the timeout parameter (optional)
  # timeout          = 60  # Timeout in seconds

  environment {
    variables = {
      CUSTOM_AWS_REGION = var.CUSTOM_AWS_REGION
      SECRET_NAME       = "api_secrets"
      EVENT_BUS_NAME    = "default"
    }
  }

  tags = {
    Environment = "production"
  }
}

resource "aws_lambda_function" "lambda_test_request" {
  function_name    = "lambda_test_request"
  role             = aws_iam_role.lambda_execution_role.arn
  handler          = "lambda_test_request.lambda_handler"
  runtime          = "python3.8"
  filename         = "${path.module}/../zipped_lambda_functions/lambda_test_request.zip"
  source_code_hash = filebase64sha256("${path.module}/../zipped_lambda_functions/lambda_test_request.zip")

  # Add the timeout parameter (optional)
  # timeout          = 60  # Timeout in seconds

  environment {
    variables = {
      CUSTOM_AWS_REGION = var.CUSTOM_AWS_REGION
    }
  }

  tags = {
    Environment = "production"
  }
}

resource "aws_lambda_function" "lambda_data_collection" {
  function_name    = "lambda_data_collection"
  role             = aws_iam_role.lambda_execution_role.arn
  handler          = "lambda_data_collection.lambda_handler"
  runtime          = "python3.8"
  filename         = "${path.module}/../zipped_lambda_functions/lambda_data_collection.zip"
  source_code_hash = filebase64sha256("${path.module}/../zipped_lambda_functions/lambda_data_collection.zip")

  # Add the timeout parameter here
  timeout          = 60  # Timeout in seconds (e.g., 300 seconds = 5 minutes)

  environment {
    variables = {
      CUSTOM_AWS_REGION = var.CUSTOM_AWS_REGION
      SNS_TOPIC_ARN     = aws_sns_topic.eventbridge_notifications.arn
      SECRET_NAME       = var.SECRET_NAME  # Added Secret Name
      DB_HOST           = var.DB_HOST      # Added DB Host
      DB_PORT           = var.DB_PORT      # Added DB Port
      DB_NAME           = var.DB_NAME      # Added DB Name
      DB_USER           = var.DB_USER      # Added DB User
      DB_PASSWORD       = var.DB_PASSWORD  # Added DB Password
      S3_BUCKET_NAME    = aws_s3_bucket.data_collection_bucket.bucket  # Added S3 bucket name
    }
  }

  tags = {
    Environment = "production"
  }
}

# New Lambda Function: lambda_db_connection
resource "aws_lambda_function" "lambda_db_connection" {
  function_name    = "lambda_db_connection"
  role             = aws_iam_role.lambda_execution_role.arn
  handler          = "lambda_db_connection.lambda_handler"
  runtime          = "python3.8"
  filename         = "${path.module}/../zipped_lambda_functions/lambda_db_connection.zip"
  source_code_hash = filebase64sha256("${path.module}/../zipped_lambda_functions/lambda_db_connection.zip")

  # Add the timeout parameter (optional)
  # timeout          = 60  # Timeout in seconds

  environment {
    variables = {
      DB_HOST     = var.DB_HOST
      DB_PORT     = var.DB_PORT
      DB_NAME     = var.DB_NAME
      DB_USER     = var.DB_USER
      DB_PASSWORD = var.DB_PASSWORD
      # Add any additional environment variables if needed
    }
  }

  tags = {
    Environment = "production"
  }
}
