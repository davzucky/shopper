SHELL := /bin/bash
BUILD_HARNESS_PATH := $(PWD)/aws_terraform_harness

TERRAFORM_CONFIG_FOLDER = $(abspath ./terraform/$(PROJECT_NAME))

-include $(BUILD_HARNESS_PATH)/Makefile
-include $(BUILD_HARNESS_PATH)/Makefile.helpers
-include $(BUILD_HARNESS_PATH)/modules/Makefile.share.variables


format-code: ## Format terraform code of the lamdba and terraform
	@echo -e "\e[32m==> Format code $@\e[0m"
	@echo -e "\e[32m====> Format Lambda code $@\e[0m"
	$(SELF) python/lambda/format-code
	@echo -e "\e[32m====> Format terraform code $@\e[0m"
	$(SELF) terraform/format-code
	@echo -e "\e[32m====> Format terraform test code $@\e[0m"
	$(SELF) python/format-code BLACK_FOLDER=./terraform
	@echo -e "\e[32m====> Format shared code $@\e[0m"
	$(SELF) python/format-code BLACK_FOLDER=./shared

linter: ## Format terraform code of the lamdba and terraform
#	$(SELF) python/lambda/format-code
	@echo $(TERRAFORM_CONFIG_FOLDER)
	$(SELF) terraform/linter
#	 TERRAFORM_CONFIG_FOLDER=terraform/shopper/



apply-staging: ## Apply config to staging
	$(SELF) terraform/apply-workspace TERRAFORM_WORKSPACE_NAME=staging

