
terraform {
  required_version = ">= 1.10.0"

  backend "s3" {
    bucket         = "capstone-project-4-tfstate-782208973324-ap-south-1"
    key            = "capstone-project-4/dev/terraform.tfstate"
    region         = "ap-south-1"
    encrypt        = true
    dynamodb_table = "capstone-project-4-tf-lock"
    use_lockfile   = true
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}
