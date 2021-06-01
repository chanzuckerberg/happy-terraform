data "aws_region" "current" {}

locals {
  default_env_vars = {
    "AWS_REGION"         = data.aws_region.current.name,
    "AWS_DEFAULT_REGION" = data.aws_region.current.name,
    "REMOTE_DEV_PREFIX"  = var.remote_dev_prefix,
    "DEPLOYMENT_STAGE"   = var.deployment_stage,
  }
  env_vars = [for k, v in merge(local.default_env_vars, var.extra_env_vars) : { "name" : k, "value" : v }]
}

resource "aws_ecs_task_definition" "task_definition" {
  family        = "${var.stack_resource_prefix}-${var.deployment_stage}-${var.custom_stack_name}-${var.name}"
  network_mode  = "awsvpc"
  task_role_arn = var.task_role_arn
  container_definitions = jsonencode([{
    name        = var.name
    essential   = true
    image       = var.image
    memory      = var.memory
    environment = local.env_vars
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group" : "${aws_cloudwatch_log_group.cloud_watch_logs_group.id}"
        "awslogs-region" : data.aws_region.current.name
      }
    }
    "command" = var.cmd
  }])
}

resource "aws_cloudwatch_log_group" "cloud_watch_logs_group" {
  retention_in_days = 365
  name              = "/${var.stack_resource_prefix}/${var.deployment_stage}/${var.custom_stack_name}/${var.name}"
}
