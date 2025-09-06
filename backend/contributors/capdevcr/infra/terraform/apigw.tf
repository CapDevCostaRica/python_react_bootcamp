resource "aws_apigatewayv2_api" "http_api" {
  name          = "${var.project_name}-http"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "fn" {
  for_each               = aws_lambda_function.fn
  api_id                 = aws_apigatewayv2_api.http_api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = each.value.invoke_arn
  payload_format_version = "2.0"
}

locals {
  routes = {
    "POST /login"         = "login"
    "POST /shipment/list" = "list_shipments"
  }
}

resource "aws_apigatewayv2_route" "route" {
  for_each = local.routes
  api_id   = aws_apigatewayv2_api.http_api.id
  route_key= each.key
  target   = "integrations/${aws_apigatewayv2_integration.fn[each.value].id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.http_api.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_lambda_permission" "apigw" {
  for_each      = aws_lambda_function.fn
  statement_id  = "AllowAPIGatewayInvoke-${each.key}"
  action        = "lambda:InvokeFunction"
  function_name = each.value.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}
