# terraform/lambda.tf

resource "aws_lambda_function" "lambda_trigger" {
  function_name    = "lambda_trigger"
  role             = aws_iam_role.lambda_execution_role.arn
  handler          = "lambda_trigger.lambda_handler"
  runtime          = "python3.8"
  filename         = "${path.module}/../zipped_lambda_functions/lambda_trigger.zip"
  source_code_hash = filebase64sha256("${path.module}/../zipped_lambda_functions/lambda_trigger.zip")

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

  environment {
    variables = {
      CUSTOM_AWS_REGION = var.CUSTOM_AWS_REGION
      SNS_TOPIC_ARN     = aws_sns_topic.eventbridge_notifications.arn
    }
  }

  tags = {
    Environment = "production"
  }
}
