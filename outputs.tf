output "lambda_add_rule_arn" {
  value = "${aws_lambda_function.lambda_add_rule.arn}"
}

output "lambda_add_rule_function_name" {
  value = "${aws_lambda_function.lambda_add_rule.function_name}"
}
