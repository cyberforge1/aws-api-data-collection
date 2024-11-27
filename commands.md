# COMMANDS

## VENV

python3 -m venv venv

source venv/bin/activate

pip freeze > requirements.txt

pip install -r requirements.txt


## Terraform

terraform -chdir=terraform plan

terraform -chdir=terraform apply

terraform -chdir=terraform destroy

## Zip Lambda functions

(cd lambda_trigger && zip -r ../zipped_lambda_functions/lambda_trigger.zip .)

(cd lambda_test_request && zip -r ../zipped_lambda_functions/lambda_test_request.zip .)






## Trigger

python scripts/invoke_lambda_trigger.py

python scripts/invoke_lambda_test_request.py




# Dependency Installation

pip install requests -t lambda_test_request/
