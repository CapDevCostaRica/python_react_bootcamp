provider "aws" {
  region                      = var.aws_region
  access_key                  = "test"
  secret_key                  = "test"
  s3_use_path_style           = true
  skip_credentials_validation = var.use_localstack
  skip_requesting_account_id  = var.use_localstack

  endpoints {
    apigateway   = var.localstack_endpoint
    apigatewayv2 = var.localstack_endpoint
    cloudwatch   = var.localstack_endpoint
    logs         = var.localstack_endpoint
    iam          = var.localstack_endpoint
    lambda       = var.localstack_endpoint
    s3           = var.localstack_endpoint
    sts          = var.localstack_endpoint
  }
}
