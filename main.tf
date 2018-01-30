data "aws_caller_identity" "current" {}

# Note that both lambda share the same codebase because Terraform
# cannot zip yet multiple files in separate folders, thus we would
# need to duplicate rule.py

data "archive_file" "lambda_add_rule_zip" {
  type        = "zip"
  source_dir  = "${path.module}/src"
  output_path = "lambda_add_rule.zip"
}

resource "aws_lambda_function" "lambda_add_rule" {
  filename         = "lambda_add_rule.zip"
  source_code_hash = "${data.archive_file.lambda_add_rule_zip.output_base64sha256}"
  function_name    = "${format("%s-lambda-add-rule", var.name)}"
  role             = "${aws_iam_role.lambda_add_rule_role.arn}"
  description      = "A lambda function to add a temporary whitelist rule to a SG."
  handler          = "lambda_add_rule.lambda_handler"
  runtime          = "python2.7"
  timeout          = 10
  memory_size      = 512

  environment {
    variables {
      SECURITY_GROUP_ID = "${var.security_group_id}"
      EXPIRY_DURATION   = "${var.expiry_duration}"
      REGION            = "${var.region}"
      PORT              = "${var.port}"
    }
  }
}

data "aws_iam_policy_document" "lambda_add_rule_invocation_from_api" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["apigateway.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "lambda_add_rule_invocation_role" {
  name               = "${format("%s-API-GATEWAY-ROLE", var.name)}"
  assume_role_policy = "${data.aws_iam_policy_document.lambda_add_rule_invocation_from_api.json}"
}

data "archive_file" "lambda_clean_rules_zip" {
  type        = "zip"
  source_dir  = "${path.module}/src"
  output_path = "lambda_clean_rules.zip"
}

resource "aws_lambda_function" "lambda_clean_rules" {
  filename         = "lambda_clean_rules.zip"
  source_code_hash = "${data.archive_file.lambda_clean_rules_zip.output_base64sha256}"
  function_name    = "${format("%s-lambda-clean-rules", var.name)}"
  role             = "${aws_iam_role.lambda_clean_rules_role.arn}"
  description      = "A lambda function to clean expired rules from a SG."
  handler          = "lambda_clean_rules.lambda_handler"
  runtime          = "python2.7"
  timeout          = 120
  memory_size      = 512

  environment {
    variables {
      SECURITY_GROUP_ID = "${var.security_group_id}"
      REGION            = "${var.region}"
    }
  }
}

resource "aws_cloudwatch_event_rule" "lambda_clean_rules_event" {
  name        = "${format("%s-lambda-clean-rules", var.name)}"
  description = "CloudWatch Event rule for IP whitelisting rules cleaning lambda"

  schedule_expression = "${var.cleaning_rate}"
}

resource "aws_cloudwatch_event_target" "lambda_clean_event_target" {
  target_id = "${format("%s-clean-rules-target", var.name)}"
  rule      = "${aws_cloudwatch_event_rule.lambda_clean_rules_event.name}"
  arn       = "${aws_lambda_function.lambda_clean_rules.arn}"
}

resource "aws_lambda_permission" "allow_cloudwatch_to_call_clean_rules_lambda" {
  statement_id  = "${format("%s-allow-cloudwatch-to-call-lambda-clean-rules", var.name)}"
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.lambda_clean_rules.function_name}"
  principal     = "events.amazonaws.com"
  source_arn    = "${aws_cloudwatch_event_rule.lambda_clean_rules_event.arn}"
}
