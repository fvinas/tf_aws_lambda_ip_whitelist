variable "region" {
  description = "AWS region"
}

variable "security_group_id" {
  description = "ID of the SG the lambda functions will modify"
}

variable "port" {
  description = "TCP port (or ports, or range of ports) on which the traffic will be authorized"
  default     = "22"
}

variable "name" {
  description = "Name to be used as a basename on all the resources identifiers"
  default     = "TF_AWS_LAMBDA_IP_WHITELIST"
}

variable "expiry_duration" {
  description = "Duration, in minutes, before a rule is considered as expired"

  # Default is 1 day
  default = "1440"
}

variable "cleaning_rate" {
  description = "CloudWatch Events rate to run the cleaning lambda function"

  # Default is every 2 hours
  default = "cron(0 0/2 * * ? *)"
}
