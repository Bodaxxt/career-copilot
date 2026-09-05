terraform {
  required_version = ">= 1.5.0"
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

# Example ECR Repository for Web
resource "aws_ecr_repository" "web" {
  name                 = "career-copilot-web"
  image_tag_mutability = "MUTABLE"
}

# Example ECR Repository for API
resource "aws_ecr_repository" "api" {
  name                 = "career-copilot-api"
  image_tag_mutability = "MUTABLE"
}
