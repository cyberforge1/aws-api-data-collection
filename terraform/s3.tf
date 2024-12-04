# terraform/s3.tf

resource "aws_s3_bucket" "data_collection_bucket" {
  bucket = "data-collection-bucket-${var.AWS_ACCOUNT_ID}"  # Ensure bucket name uniqueness

  tags = {
    Environment = "production"
    Name        = "DataCollectionBucket"
  }
}
