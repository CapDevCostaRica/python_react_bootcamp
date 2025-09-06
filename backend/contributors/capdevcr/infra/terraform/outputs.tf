output "http_api_url" {
  description = "Base URL for the HTTP API in LocalStack"
  value       = aws_apigatewayv2_api.http_api.api_endpoint
}
