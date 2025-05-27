variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "instance_type" {
  type    = string
  default = "t2.micro"
}

variable "ssh_public_key_path" {
  description = "Path to your SSH public key"
  type        = string
}

variable "repo_url" {
  description = "HTTPS URL of your GitHub repo"
  type        = string
}
