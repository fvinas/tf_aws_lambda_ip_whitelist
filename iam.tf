data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

# -------------------------------------------------------------------
#                         LAMBDA ADD RULE
# -------------------------------------------------------------------

resource "aws_iam_role" "lambda_add_rule_role" {
  name               = "${format("%s-lambda-add-rule-role" ,var.name)}"
  assume_role_policy = "${data.aws_iam_policy_document.lambda_assume_role.json}"
}

resource "aws_iam_role_policy_attachment" "lambda_add_rule_execution_role" {
  role       = "${aws_iam_role.lambda_add_rule_role.name}"
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_add_rule_sg_alter_role" {
  role       = "${aws_iam_role.lambda_add_rule_role.name}"
  policy_arn = "${aws_iam_policy.lambda_add_rule_sg_alter_policy.arn}"
}

resource "aws_iam_policy" "lambda_add_rule_sg_alter_policy" {
  name        = "LambdaAddRule_AlterSG"
  path        = "/"
  description = "Allow lambda_add_rule to add an ingress rule to a security group"

  policy = <<EOF_POLICY
{
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Action": [
            "ec2:AuthorizeSecurityGroupIngress"
        ],
        "Resource": [
            "arn:aws:ec2:${var.region}:${data.aws_caller_identity.current.account_id}:security-group/${var.security_group_id}"
        ]
    }]
}
EOF_POLICY
}

# -------------------------------------------------------------------
#                        LAMBDA CLEAN RULES
# -------------------------------------------------------------------

resource "aws_iam_role" "lambda_clean_rules_role" {
  name               = "${format("%s-lambda-clean-rules-role" ,var.name)}"
  assume_role_policy = "${data.aws_iam_policy_document.lambda_assume_role.json}"
}

resource "aws_iam_role_policy_attachment" "lambda_clean_rules_execution_role" {
  role       = "${aws_iam_role.lambda_clean_rules_role.name}"
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_clean_rules_sg_alter_role" {
  role       = "${aws_iam_role.lambda_clean_rules_role.name}"
  policy_arn = "${aws_iam_policy.lambda_clean_rules_sg_alter_policy.arn}"
}

resource "aws_iam_policy" "lambda_clean_rules_sg_alter_policy" {
  name        = "LambdaCleanRules_AlterSG"
  path        = "/"
  description = "Allow lambda_clean_rules to remove a ingress rules from a security group"

  policy = <<EOF_POLICY
{
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Action": [
            "ec2:DescribeSecurityGroups"
        ],
        "Resource": [
            "*"
        ]
    }, {
        "Effect": "Allow",
        "Action": [
            "ec2:RevokeSecurityGroupIngress"
        ],
        "Resource": [
            "arn:aws:ec2:${var.region}:${data.aws_caller_identity.current.account_id}:security-group/${var.security_group_id}"
        ]
    }]
}
EOF_POLICY
}
