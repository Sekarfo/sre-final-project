output "instance_public_ip" {
  description = "Public IP of the EC2 instance"
  value       = aws_instance.app.public_ip
}

output "ssh_command" {
  value = "ssh -i ${var.ssh_public_key_path} ubuntu@${aws_instance.app.public_ip}"
}
