output "lambda_add_rule_arn" {
  value = ["${aws_lambda_function.lambda_add_rule.arn}"]
}

output "lambda_add_rule_api_endpoint" {
  value = "${aws_api_gateway_deployment.add_rule_api_deployment.invoke_url}"
}
