data "archive_file" "lambda_add_rule_zip" {
  type        = "zip"
  source_file = "lambda_add_rule.py"
  source_file = "rule.py"
  output_path = "lambda_add_rule.zip"
}

resource "aws_lambda_function" "lambda_add_rule" {
  filename         = "lambda_add_rule.zip"
  source_code_hash = "${data.archive_file.lambda_add_rule_zip.output_base64sha256}"
  function_name    = "${format("%s-lambda-add-rule" ,var.name)}"
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
    }
  }
}

data "archive_file" "lambda_clean_rules_zip" {
  type        = "zip"
  source_file = "lambda_clean_rules.py"
  source_file = "rule.py"
  output_path = "lambda_clean_rules.zip"
}

resource "aws_lambda_function" "lambda_clean_rules" {
  filename         = "lambda_clean_rules.zip"
  source_code_hash = "${data.archive_file.lambda_clean_rules_zip.output_base64sha256}"
  function_name    = "${format("%s-lambda-clean-rules" ,var.name)}"
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

# TODO: add CloudWatch Event & scheduling

