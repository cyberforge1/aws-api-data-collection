# terraform/variables.tf

variable "AWS_ACCOUNT_ID" {
  type        = string
  description = "The AWS account ID"
}

variable "CUSTOM_AWS_REGION" {
  type        = string
  description = "The AWS region to use"
}

variable "API_KEY" {
  type        = string
  description = "The API key to store in Secrets Manager"
}

variable "API_SECRET" {
  type        = string
  description = "The API secret to store in Secrets Manager"
}

variable "SECRET_NAME" {
  type        = string
  description = "The name of the secret in AWS Secrets Manager"
}
