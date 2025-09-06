
# Outputs
output "api_urls" {
  value = {
    login           = "http://localhost:4566/restapis/${aws_api_gateway_rest_api.api.id}/${local.stage_name}/login"
    create_shipment = "http://localhost:4566/restapis/${aws_api_gateway_rest_api.api.id}/${local.stage_name}/shipment"
    list_shipments  = "http://localhost:4566/restapis/${aws_api_gateway_rest_api.api.id}/${local.stage_name}/shipment/list"
    update_shipment = "http://localhost:4566/restapis/${aws_api_gateway_rest_api.api.id}/${local.stage_name}/shipment/{id}"
  }
}
