# ----------------------
# API Gateway REST API
# ----------------------
resource "aws_api_gateway_rest_api" "api" {
  name        = "${var.project_name}-api"
  description = "REST API para ${var.project_name}"
}

# ----------------------
# Recursos principales
# ----------------------
locals {
  main_routes = {
    login         = local.routes.login
    shipment_root = local.routes.create_shipment
  }
}

resource "aws_api_gateway_resource" "main" {
  for_each    = local.main_routes
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = each.value.path
}

# ----------------------
# Sub-recursos /shipment/list y /shipment/{id}
# ----------------------
resource "aws_api_gateway_resource" "shipment_list" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_resource.main["shipment_root"].id
  path_part   = "list"
}

resource "aws_api_gateway_resource" "shipment_id" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_resource.main["shipment_root"].id
  path_part   = "{id}"
}

# ----------------------
# Métodos POST
# ----------------------
locals {
  all_routes = merge(
    local.main_routes,
    {
      shipment_list = local.routes.list_shipments
      shipment_id   = local.routes.update_shipment
    }
  )
}

resource "aws_api_gateway_method" "post" {
  for_each    = local.all_routes
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = lookup({
      login         = aws_api_gateway_resource.main["login"].id
      shipment_root = aws_api_gateway_resource.main["shipment_root"].id
      shipment_list = aws_api_gateway_resource.shipment_list.id
      shipment_id   = aws_api_gateway_resource.shipment_id.id
    }, each.key)
  http_method   = "POST"
  authorization = "NONE"
}

# ----------------------
# Métodos OPTIONS (CORS)
# ----------------------
resource "aws_api_gateway_method" "options" {
  for_each    = local.all_routes
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = lookup({
      login         = aws_api_gateway_resource.main["login"].id
      shipment_root = aws_api_gateway_resource.main["shipment_root"].id
      shipment_list = aws_api_gateway_resource.shipment_list.id
      shipment_id   = aws_api_gateway_resource.shipment_id.id
    }, each.key)
  http_method   = "OPTIONS"
  authorization = "NONE"
}

# ----------------------
# Integración POST con Lambda
# ----------------------
resource "aws_api_gateway_integration" "post" {
  for_each = local.all_routes
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = lookup({
      login         = aws_api_gateway_resource.main["login"].id
      shipment_root = aws_api_gateway_resource.main["shipment_root"].id
      shipment_list = aws_api_gateway_resource.shipment_list.id
      shipment_id   = aws_api_gateway_resource.shipment_id.id
    }, each.key)
  http_method             = "POST"
  type                    = "AWS"
  integration_http_method = "POST"
  uri                     = aws_lambda_function.fn[each.value.lambda].invoke_arn
  passthrough_behavior    = "WHEN_NO_MATCH"
  request_templates = {
    "application/json" = "{ \"body\": $input.json('$') }"
  }
  depends_on = [
    aws_api_gateway_method.post
  ]
}

# ----------------------
# Integración OPTIONS MOCK para CORS
# ----------------------
resource "aws_api_gateway_integration" "options" {
  for_each = local.all_routes
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = lookup({
      login         = aws_api_gateway_resource.main["login"].id
      shipment_root = aws_api_gateway_resource.main["shipment_root"].id
      shipment_list = aws_api_gateway_resource.shipment_list.id
      shipment_id   = aws_api_gateway_resource.shipment_id.id
    }, each.key)
  http_method = "OPTIONS"
  type        = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

# ----------------------
# Method Responses
# ----------------------
resource "aws_api_gateway_method_response" "post" {
  for_each    = local.all_routes
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = lookup({
      login         = aws_api_gateway_resource.main["login"].id
      shipment_root = aws_api_gateway_resource.main["shipment_root"].id
      shipment_list = aws_api_gateway_resource.shipment_list.id
      shipment_id   = aws_api_gateway_resource.shipment_id.id
    }, each.key)
  http_method = "POST"
  status_code = "200"
  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = true
  }
}

resource "aws_api_gateway_method_response" "options" {
  for_each    = local.all_routes
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = lookup({
      login         = aws_api_gateway_resource.main["login"].id
      shipment_root = aws_api_gateway_resource.main["shipment_root"].id
      shipment_list = aws_api_gateway_resource.shipment_list.id
      shipment_id   = aws_api_gateway_resource.shipment_id.id
    }, each.key)
  http_method = "OPTIONS"
  status_code = "200"
  response_parameters = local.cors_headers
}

# ----------------------
# Integration Responses
# ----------------------
resource "aws_api_gateway_integration_response" "post" {
  for_each = local.all_routes
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = lookup({
      login         = aws_api_gateway_resource.main["login"].id
      shipment_root = aws_api_gateway_resource.main["shipment_root"].id
      shipment_list = aws_api_gateway_resource.shipment_list.id
      shipment_id   = aws_api_gateway_resource.shipment_id.id
    }, each.key)
  http_method = "POST"
  status_code = "200"
  response_templates = {
    "application/json" = "$input.body"
  }
  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = "'*'"
  }
  depends_on = [
    aws_api_gateway_integration.post
  ]
}

resource "aws_api_gateway_integration_response" "options" {
  for_each = local.all_routes
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = lookup({
      login         = aws_api_gateway_resource.main["login"].id
      shipment_root = aws_api_gateway_resource.main["shipment_root"].id
      shipment_list = aws_api_gateway_resource.shipment_list.id
      shipment_id   = aws_api_gateway_resource.shipment_id.id
    }, each.key)
  http_method = "OPTIONS"
  status_code = "200"
  response_parameters = local.integration_headers
  response_templates = {
    "application/json" = ""
  }
  depends_on = [
    aws_api_gateway_integration.options
  ]
}

# ----------------------
# Deployment y Stage
# ----------------------
resource "aws_api_gateway_deployment" "deployment" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  depends_on  = [
    aws_api_gateway_integration.post,
    aws_api_gateway_integration.options
  ]
}

resource "aws_api_gateway_stage" "stage" {
  stage_name    = local.stage_name
  rest_api_id   = aws_api_gateway_rest_api.api.id
  deployment_id = aws_api_gateway_deployment.deployment.id
  
  depends_on = [aws_api_gateway_deployment.deployment]
}
