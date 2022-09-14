terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.27"
    }
  }

  required_version = ">= 0.14.9"
}

# TODO: Rename to revelant vars

#Header resource
provider "aws" {
  profile = "default"
  region  = "us-east-1"
  #access_key = var.AWS_ACCESS_KEY_ID
  #secret_key = var.AWS_SECRET_ACCESS_KEY
}

#
#
#### COMPUTING ENVIRONMENT RESOURCES ####
#
#

resource "aws_iam_role" "ecs_instance_role" {
  name = "ecs_instance_role"

  assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
    {
        "Action": "sts:AssumeRole",
        "Effect": "Allow",
        "Principal": {
            "Service": "ec2.amazonaws.com"
        }
    }
    ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "ecs_instance_role" {
  role       = aws_iam_role.ecs_instance_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
}

resource "aws_iam_instance_profile" "ecs_instance_role" {
  name = "ecs_instance_role"
  role = aws_iam_role.ecs_instance_role.name
}

resource "aws_iam_role" "aws_batch_service_role" {
  name = "aws_batch_service_role"

  assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
    {
        "Action": "sts:AssumeRole",
        "Effect": "Allow",
        "Principal": {
        "Service": "batch.amazonaws.com"
        }
    }
    ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "aws_batch_service_role" {
  role       = aws_iam_role.aws_batch_service_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSBatchServiceRole"
}

resource "aws_security_group" "cf-metrics-env" {
  name   = "aws_batch_compute_environment_security_group"
  vpc_id = aws_vpc.cf-metrics-env.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_vpc" "cf-metrics-env" {
  cidr_block = "10.1.0.0/16"
}

resource "aws_subnet" "cf-metrics-env" {
  vpc_id     = aws_vpc.cf-metrics-env.id
  cidr_block = "10.1.1.0/24"
}

#MAIN RESOURCE - computing environment
resource "aws_batch_compute_environment" "cf-metrics-env" {
  compute_environment_name = "cf-metrics-env"

  compute_resources {
    max_vcpus = 6

    security_group_ids = [
      aws_security_group.cf-metrics-env.id
    ]

    subnets = [
      aws_subnet.cf-metrics-env.id
    ]

    type = "FARGATE"
  }

  service_role = aws_iam_role.aws_batch_service_role.arn
  type         = "MANAGED"
  depends_on   = [aws_iam_role_policy_attachment.aws_batch_service_role]
}

#
#
#### JOB DEFINITION RESOURCES ####
#
#
resource "aws_iam_role" "ecs_task_execution_role" {
  name               = "batch_exec_role"
  assume_role_policy = data.aws_iam_policy_document.assume_role_policy.json
}

data "aws_iam_policy_document" "assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_batch_job_definition" "test" {
  name = "cf-metric-report"
  type = "container"
  platform_capabilities = [
    "FARGATE",
  ]
  timeout {
    attempt_duration_seconds = 60
  }

  retry_strategy {
    attempts = 1
  }

  #implement version for ecr

  container_properties = <<CONTAINER_PROPERTIES
{
  "command": [ ],
  "image": "ACCOUNTID.dkr.ecr.us-east-1.amazonaws.com/devops-monthlyreport:latest",
  "fargatePlatformConfiguration": {
    "platformVersion": "1.4.0"
  },
  "environment":[
      {
          "name": "URLSLACK",
          "value": "${var.URLSLACK}"
      },
      {
          "name": "X_AUTH_KEY",
          "value": "${var.X_AUTH_KEY}"
      },
      {
         "name": "X_AUTH_EMAIL",
         "value": "${var.X_AUTH_EMAIL}" 
      },
      {
        "name": "AWS_ACCESS_KEY_ID",
        "value": "${var.AWS_ACCESS_KEY_ID}"
      },
      {
        "name": "AWS_SECRET_ACCESS_KEY",
        "value": "${var.AWS_SECRET_ACCESS_KEY}"
      }
  ],
  "resourceRequirements": [
    {"type": "VCPU", "value": "1"},
    {"type": "MEMORY", "value": "2048"}
  ],
  "executionRoleArn": "arn:aws:iam::ACCOUNTID:role/ECS-TaskRole",
  "networkConfiguration": { 
         "assignPublicIp": "ENABLED"
      }
}
CONTAINER_PROPERTIES
}

#
#
#### JOB QUEUE RESOURCES ####
#
#
resource "aws_batch_job_queue" "queue" {
  name     = "cf-metrics-report-queue"
  state    = "ENABLED"
  priority = 1
  compute_environments = [
    aws_batch_compute_environment.cf-metrics-env.arn
  ]
}

#
#
#### IMPLEMENT EVENT BRIDGE (RULE) ####
#
#
resource "aws_cloudwatch_event_rule" "console" {
  name        = "cl-metrics"
  description = "Monthly run showcasing Cloudflare Metrics in Slack"

  schedule_expression = "cron(0 12 1 * ? *)"

  #   event_pattern = <<EOF
  # {
  #   "detail-type": [
  #     "AWS Console Sign In via CloudTrail"
  #   ]
  # }
  # EOF
}

#thinks its target bus
resource "aws_cloudwatch_event_target" "batch-job" {
  rule      = aws_cloudwatch_event_rule.console.name
  target_id = "SendtoBatch"
  # Job queue arn
  arn = aws_batch_job_queue.queue.arn
  # Eventbridge arn
  role_arn = "arn:aws:iam::ACCOUNTID:role/EventBridge_Batch"

  batch_target {
    job_name       = "cl-tf-job"
    job_definition = aws_batch_job_definition.test.arn
  }
}
