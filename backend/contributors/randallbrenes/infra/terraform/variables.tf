variable "project_name" {
  type    = string
  default = "capdevcr-shipments"
}
variable "aws_region" {
  type = string
  default = "us-east-1" 
}
variable "use_localstack" {
  type = bool
  default = true
}
variable "localstack_endpoint" {
  type = string
  default = "http://localhost:4566" 
}

variable "function_zips" {
  type = object({
    login          = string
    list_shipments = string
    create_shipment = string
    update_shipment = string
  })
  default = {
    login          = "../build/login.zip"
    list_shipments = "../build/list_shipments.zip"
    create_shipment = "../build/create_shipment.zip"
    update_shipment = "../build/update_shipment.zip"
  }
}

variable "db_user"     {
  type = string
  default = "postgres" 
}
variable "db_password" {
  type = string
  default = "postgres" 
}
variable "db_name"     {
  type = string
  default = "shipments" 
}

variable "db_host"     {
  type = string
  default = "flask_db" 
}
variable "db_port"     {
  type = string
  default = "5432" 
}
variable "secret_key"  {
  type = string
  default = "dev-secret" 
}
variable "token_ttl"   {
  type = number
  default = 900 
}

locals {
  # Rutas con su parent_id se definirán directamente en los recursos, no aquí
  routes = {
    login          = { path = "login",        lambda = "login" }
    create_shipment = { path = "shipment",     lambda = "create_shipment" }
    list_shipments  = { path = "list",         lambda = "list_shipments" }
    update_shipment = { path = "{id}",         lambda = "update_shipment" }
  }

  stage_name = var.use_localstack ? "dev" : "dev"

  cors_headers = {
    "method.response.header.Access-Control-Allow-Origin"  = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Headers" = true
  }

  integration_headers = {
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
    "method.response.header.Access-Control-Allow-Methods" = "'POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
  }
}