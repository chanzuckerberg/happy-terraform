variable "stack_resource_prefix" {
  type        = string
  description = "Prefix for account-level resources"
}

variable "name" {
  type        = string
  description = "Task name"
}

variable "image" {
  type        = string
  description = "Image name"
}

variable "task_role_arn" {
  type        = string
  description = "ARN for the role assumed by tasks"
}

variable "cmd" {
  type        = list(string)
  description = "Command to run"
  default     = []
}

variable "custom_stack_name" {
  type        = string
  description = "Please provide the stack name"
}

variable "deployment_stage" {
  type        = string
  description = "The name of the deployment stage of the Application"
}

variable "memory" {
  type        = number
  description = "megabytes of memory to allocate to this task"
  default     = 512
}

variable "extra_env_vars" {
  type        = map(string)
  description = "Env vars to merge with defaults for this task"
  default     = {}
}
