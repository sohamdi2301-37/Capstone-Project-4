variable "aws_region" {
  description = "AWS region for the capstone"
  type        = string
  default     = "ap-south-1"
}
variable "project_name" {
  type    = string
  default = "infra-as-code-pipeline"
}
variable "github_owner" {
  description = "GitHub user or organization that owns this repository"
  type        = string
}
variable "github_repo" {
  description = "Repository name only, without owner/"
  type        = string
}
variable "container_port" {
  type    = number
  default = 8080
}
variable "desired_count" {
  type    = number
  default = 1
}
