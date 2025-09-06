locals {
  functions = {
    login = {
      zip     = var.function_zips.login
      handler = "app.functions.login.src.app.handler"
    }
    list_shipments = {
      zip     = var.function_zips.list_shipments
      handler = "app.functions.list_shipments.src.app.handler"
    }
  }
}

resource "aws_lambda_function" "fn" {
  for_each         = local.functions

  function_name    = "${var.project_name}-${each.key}"
  filename         = each.value.zip
  source_code_hash = filebase64sha256(each.value.zip)

  role    = aws_iam_role.lambda_exec.arn
  handler = each.value.handler
  runtime = "python3.11"
  timeout = 30

  environment {
    variables = {
      SECRET_KEY        = var.secret_key
      TOKEN_TTL_SECONDS = tostring(var.token_ttl)

      POSTGRES_USER     = var.db_user
      POSTGRES_PASSWORD = var.db_password
      POSTGRES_DB       = var.db_name
      POSTGRES_HOST     = var.db_host
      POSTGRES_PORT     = var.db_port
    }
  }
}
