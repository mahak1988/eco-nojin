terraform {
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.5"
    }
  }
}

provider "local" {}

resource "local_file" "placeholder" {
  content  = "This Terraform folder is a starter placeholder for infrastructure-as-code definitions."
  filename = "${path.module}/README.txt"
}
