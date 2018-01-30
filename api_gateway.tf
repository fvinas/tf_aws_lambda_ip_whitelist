resource "aws_api_gateway_rest_api" "add_rule_api" {
  name        = "${format("%s-add-rule-api", var.name)}"
  description = "API Gateway to expose the IP whitelisting add_rule lambda function"
}

# /
resource "aws_api_gateway_method" "add_rule_api_method" {
  rest_api_id      = "${aws_api_gateway_rest_api.add_rule_api.id}"
  resource_id      = "${aws_api_gateway_rest_api.add_rule_api.root_resource_id}"
  http_method      = "GET"
  authorization    = "AWS_IAM"
  api_key_required = false
}

resource "aws_api_gateway_integration" "add_rule_api_integration" {
  rest_api_id             = "${aws_api_gateway_rest_api.add_rule_api.id}"
  resource_id             = "${aws_api_gateway_rest_api.add_rule_api.root_resource_id}"
  http_method             = "${aws_api_gateway_method.add_rule_api_method.http_method}"
  type                    = "AWS_PROXY"
  uri                     = "arn:aws:apigateway:${var.region}:lambda:path/2015-03-31/functions/${aws_lambda_function.lambda_add_rule.arn}/invocations"
  integration_http_method = "POST"
}

resource "aws_api_gateway_method_response" "200" {
  rest_api_id = "${aws_api_gateway_rest_api.add_rule_api.id}"
  resource_id = "${aws_api_gateway_rest_api.add_rule_api.root_resource_id}"
  http_method = "${aws_api_gateway_method.add_rule_api_method.http_method}"
  status_code = "200"
}

resource "aws_api_gateway_integration_response" "add_rule_api_integration_response" {
  rest_api_id = "${aws_api_gateway_rest_api.add_rule_api.id}"
  resource_id = "${aws_api_gateway_rest_api.add_rule_api.root_resource_id}"
  http_method = "${aws_api_gateway_method.add_rule_api_method.http_method}"
  status_code = "${aws_api_gateway_method_response.200.status_code}"
}

# Deployment
resource "aws_api_gateway_deployment" "add_rule_api_deployment" {
  rest_api_id = "${aws_api_gateway_rest_api.add_rule_api.id}"

  depends_on = [
    "aws_api_gateway_integration.add_rule_api_integration",
  ]

  stage_name = "production"

  # To force redeploy
  stage_description = "Deployed at ${timestamp()}"
}

resource "aws_api_gateway_account" "add_rule_api_account" {
  cloudwatch_role_arn = "${aws_iam_role.cloudwatch.arn}"
}

resource "aws_iam_role" "cloudwatch" {
  name = "${lower(format("%s-api-gateway-cloudwatch", var.name))}"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "Service": "apigateway.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "cloudwatch" {
  name = "${lower(format("%s-api-gateway-cloudwatch-policy", var.name))}"
  role = "${aws_iam_role.cloudwatch.id}"

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:DescribeLogGroups",
                "logs:DescribeLogStreams",
                "logs:PutLogEvents",
                "logs:GetLogEvents",
                "logs:FilterLogEvents"
            ],
            "Resource": "*"
        }
    ]
}
EOF
}
