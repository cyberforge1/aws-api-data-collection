# terraform/vpc.tf

# Fetch information about subnets in the specified VPC
data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [var.VPC_ID]  # Reference the VPC_ID variable from variables.tf
  }
}

# Fetch information about the specified security group
data "aws_security_group" "rds_security_group" {
  filter {
    name   = "group-id"
    values = [var.SECURITY_GROUP_ID]  # Reference the SECURITY_GROUP_ID variable from variables.tf
  }
}
