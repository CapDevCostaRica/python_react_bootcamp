output "http_api_url" {
  description = "URL base de la API HTTP en LocalStack"
  value       = aws_apigatewayv2_api.http_api.api_endpoint
}
