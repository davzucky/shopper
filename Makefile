SHELL := /bin/bash
BUILD_HARNESS_PATH := $(PWD)/aws_terraform_harness

TERRAFORM_CONFIG_FOLDER = $(abspath ./terraform)

#-include aws_terraform_harness
-include aws_terraform_harness/Makefile
-include aws_terraform_harness/Makefile.helpers


## Format terraform code
format-code:
	$(SELF) terraform/format-code

## Apply config to staging
apply-staging:
	$(SELF) terraform/apply-workspace TERRAFORM_WORKSPACE_NAME=staging
