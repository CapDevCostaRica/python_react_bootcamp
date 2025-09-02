variable "project_name"        { type = string  default = "capdevcr-shipments" }
variable "aws_region"          { type = string  default = "us-east-1" }
variable "use_localstack"      { type = bool    default = true }
variable "localstack_endpoint" { type = string  default = "http://localhost:4566" }

variable "function_zips" {
  type = object({
    login          = string
    list_shipments = string
  })
  default = {
    login          = "${path.module}/../build/login.zip"
    list_shipments = "${path.module}/../build/list_shipments.zip"
  }
}

variable "db_user"     { type = string default = "postgres" }
variable "db_password" { type = string default = "postgres" }
variable "db_name"     { type = string default = "shipments" }

variable "db_host"     { type = string default = "flask_db" }
variable "db_port"     { type = string default = "5432" }
variable "secret_key"  { type = string default = "dev-secret" }
variable "token_ttl"   { type = number default = 900 }
