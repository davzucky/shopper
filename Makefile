######################################################################################
######################################################################################
###############      Makefile used for lambda function development     ###############
######################################################################################
######################################################################################

.PHONY: help clean create-master-venv test-master-venv reformat-code create-packages

.DEFAULT_GOAL := help
# Force shell to be bash
SHELL := /bin/bash


######################################################################################
###############              Variable section                #########################
######################################################################################

CONFIG_VERSION = $(shell grep -r version config.toml | awk -F '"' '{print $$2}')
PROJECT_NAME = $(shell grep -r name config.toml | awk -F '"' '{print $$2}')
S3_BUCKET_URL = $(shell grep -r S3_bucket_uri config.toml | awk -F '"' '{print $$2}')
S3_PACKAGE_PATH = $(shell grep -r S3_folder_path config.toml | awk -F '"' '{print $$2}')
BINARY_FOLDER = ./bin
PACKAGE_FOLDER_NAME = packages
PYTESTS_RESULT_FILE_NAME = pytest.report.xml

TERRAFORM_VERSION = 0.12.2
TERRAFORM_URL = https://releases.hashicorp.com/terraform/$(TERRAFORM_VERSION)/terraform_$(TERRAFORM_VERSION)_linux_amd64.zip
TERRAFORM_TEMP_ZIP = $(BINARY_FOLDER)/terraform.zip
TERRAFORM_BINARY_VERSION_FILE = $(BINARY_FOLDER)/terraform_$(TERRAFORM_VERSION)
TERRAFORM_BINARY_PATH = $(BINARY_FOLDER)/terraform
TERRAFORM_MODULE_PATH = ./terraform/$(PROJECT_NAME)
TERRAFORM_VERSION_FILE = $(TERRAFORM_MODULE_PATH)/variable.version.tf
TERRAFORM_MODULE_PACKAGES = $(TERRAFORM_MODULE_PATH)/$(PACKAGE_FOLDER_NAME)
TERRAFORM_PYTEST_RESULT = ./results/terraform/$(PYTESTS_RESULT_FILE_NAME)
TERRAFORM_TESTING_REQUIREMENTS = ./terraform/test/requirements.infra.txt
OUTPUT_PKG_PATH = $(TERRAFORM_MODULE_PACKAGES)
TERRAFORM_FILES = $(shell find ./terraform -name '*.tf')
TERRAFORM_TEST_FILES = $(shell find ./terraform -name '*.py')


OUTPUT_TEST_RESULT_PATH = ./test_reports
VENV_TEST_FOLDER_NAME = .venv
VENV_PKG_FOLDER_NAME = .venv_pkg
VENV_AWS_CLI_FOLDER_NAME = .venv_aws


PYTEST_ARGUMENTS = --flake8 --mypy --mypy-ignore-missing-imports --self-contained-html
SETUP_CFG_FILE_NAME = setup.cfg
REQUIREMENTS_FILE_NAME = requirements.txt
REQUIREMENTS_DEV_FILE_NAME = requirements.dev.txt
REQUIREMENTS_TESTS_FILE_NAME = requirements.tests.txt
REQUIREMENTS_AWS_CLI_FILE_NAME = requirements.awscli.txt
REQUIREMENTS_FREEZE_FILE_NAME = $(subst requirements,requirements.freeze,$(REQUIREMENTS_FILE_NAME))
REQUIREMENTS_TESTS_FREEZE_FILE_NAME = $(subst requirements,requirements.freeze,$(REQUIREMENTS_TESTS_FILE_NAME))
REQUIREMENTS_PKG_FREEZE_FILE_NAME = $(subst requirements,requirements.pkg.freeze,$(REQUIREMENTS_FILE_NAME))
REQUIREMENTS_AWS_CLI_FREEZE_FILE_NAME = $(subst requirements,requirements.pkg.freeze,$(REQUIREMENTS_AWS_CLI_FILE_NAME))
REQUIREMENTS_FUNCTIONS = requirements.functions.txt
GIT_HASH_COMMIT = $(shell git rev-parse --short HEAD)
S3_BASE_URI =  $(S3_BUCKET)/$(S3_PACKAGE_PATH)
VERSION = $(CONFIG_VERSION).$(GIT_HASH_COMMIT)
VENV_ACTIVATE_PATH = $(VENV_TEST_FOLDER_NAME)/bin/activate
VENV_PKG_ACTIVATE_PATH = $(VENV_PKG_FOLDER_NAME)/bin/activate
VENV_AWS_CLI_ACTIVATE_PATH = $(VENV_AWS_CLI_FOLDER_NAME)/bin/activate
PYTHON_FILE_EXTENSION = '*.py'
#python -m site | grep "$(pwd).*site-packages" | sed "s/^.*'\(.*\)'.*$/\1/"
#basename $(dirname "./lambda_function2/requirements.txt")
#for path in $(find -name requirements.txt); do basename $(dirname $path); done


LAMBDA_FUNCTIONS = $(shell for path in $$(find -name $(REQUIREMENTS_FILE_NAME)); do basename $$(dirname $$path); done)
LAMBDA_PKG_ZIPS = $(foreach FUNCTION_NAME,$(LAMBDA_FUNCTIONS), ./$(OUTPUT_PKG_PATH)/$(FUNCTION_NAME).$(VERSION).zip)
LAMBDA_PKG_ZIPS_PUBLISHED = $(subst .zip,.published,$(LAMBDA_PKG_ZIPS))

REQUIREMENTS_FILES := $(shell find -name $(REQUIREMENTS_FILE_NAME))
REQUIREMENTS_FREEZE_FILES := $(subst  $(REQUIREMENTS_FILE_NAME),$(REQUIREMENTS_FREEZE_FILE_NAME),$(REQUIREMENTS_FILES))
REQUIREMENTS_TESTS_FILES := $(shell find -name $(REQUIREMENTS_TESTS_FILE_NAME))
REQUIREMENTS_TESTS_FREEZE_FILES := $(subst  $(REQUIREMENTS_TESTS_FILE_NAME),$(REQUIREMENTS_TESTS_FREEZE_FILE_NAME),$(REQUIREMENTS_TESTS_FILES))
REQUIREMENTS_PKG_FREEZE_FILES := $(subst  $(REQUIREMENTS_FILE_NAME),$(REQUIREMENTS_PKG_FREEZE_FILE_NAME),$(REQUIREMENTS_FILES))

PYTEST_RESULT_FOLDER = ./results
PYTESTS_RESULT_FILES := $(subst ./, $(PYTEST_RESULT_FOLDER)/, $(subst  $(REQUIREMENTS_FILE_NAME),$(PYTESTS_RESULT_FILE_NAME),$(REQUIREMENTS_FILES)))
SETUP_CFG_FILES := $(subst  $(REQUIREMENTS_FILE_NAME),$(SETUP_CFG_FILE_NAME),$(REQUIREMENTS_FILES))
FUNCTION_ACTIVATE_PATH = $(subst  $(REQUIREMENTS_FILE_NAME),$(VENV_ACTIVATE_PATH),$(REQUIREMENTS_FILES))
FUNCTION_PKG_ACTIVATE_PATH = $(subst  $(REQUIREMENTS_FILE_NAME),$(VENV_PKG_ACTIVATE_PATH),$(REQUIREMENTS_FILES))
VENV_ROOT_PATH = $(subst  /bin/activate,,$(FUNCTION_ACTIVATE_PATH))
VENV_PKG_ROOT_PATH = $(subst  /bin/activate,,$(FUNCTION_PKG_ACTIVATE_PATH))

DIRECTORY_EXCLUSION = -path ./.venv $(patsubst  %,-o -path %,$(VENV_ROOT_PATH)) $(patsubst  %,-o -path %,$(VENV_PKG_ROOT_PATH)) -o -path ./.venv_aws
PROJECT_PYTHON_FILES = $(shell find . -type d \( $(DIRECTORY_EXCLUSION) \) -prune -o -name $(PYTHON_FILE_EXTENSION) -print)

MASTER_ACTIVATE_PATH = $(VENV_ACTIVATE_PATH)

TERRAFORM_MODULE_PACKAGE_FOLDER = ./terraform_module
TERRAFORM_MODULE_PACKAGE_PATH = $(TERRAFORM_MODULE_PACKAGE_FOLDER)/$(PROJECT_NAME).$(VERSION).zip
TERRAFORM_MODULE_PACKAGE_PUBLISHED = $(TERRAFORM_MODULE_PACKAGE_PATH).published


define \n


endef
######################################################################################
###############              Create virtual envs             #########################
######################################################################################

$(REQUIREMENTS_FUNCTIONS): $(REQUIREMENTS_FILES) $(REQUIREMENTS_TESTS_FILES)
	@echo -e "\e[32m==> Create file $@ \e[0m"
	@rm $@ -f
	@echo -e $(patsubst %,-r % \\n,$(REQUIREMENTS_FILES)) > $@
	@echo -e $(patsubst %,-r % \\n,$(REQUIREMENTS_TESTS_FILES)) >> $@
	@echo -e $(patsubst %,-r % \\n,$(TERRAFORM_TESTING_REQUIREMENTS)) >> $@

$(FUNCTION_ACTIVATE_PATH):
	@echo -e "\e[32m==> Create virtual env $@\e[0m"
	@virtualenv $(subst /bin/activate,, $@)
	@source $@ && pip install --upgrade pip
	@echo -e "\e[32m====> touch $@\e[0m"
	@touch $@ # touch activate file to be sure make record it

$(MASTER_ACTIVATE_PATH) : $(REQUIREMENTS_FUNCTIONS) $(REQUIREMENTS_DEV_FILE_NAME)
	@echo -e "\e[32m==> Create virtual env $@\e[0m"
	@virtualenv $(subst /bin/activate,, $@)
	@source $@ && pip install --upgrade pip
	@source $@ && pip install -r $(REQUIREMENTS_DEV_FILE_NAME)
	@source $@ && pip install -r $(REQUIREMENTS_FUNCTIONS)
	@echo -e "\e[32m====> touch $@\e[0m"
	@touch $@ # touch activate file to be sure make record it

$(VENV_AWS_CLI_ACTIVATE_PATH) :
	@echo -e "\e[32m==> Create virtual env $@\e[0m"
	@virtualenv $(subst /bin/activate,, $@)
	@source $@ && pip install --upgrade pip
	@echo -e "\e[32m====> touch $@\e[0m"
	@touch $@ # touch activate file to be sure make record it

$(REQUIREMENTS_AWS_CLI_FREEZE_FILE_NAME) : $(REQUIREMENTS_AWS_CLI_FILE_NAME) $(VENV_AWS_CLI_ACTIVATE_PATH)
	@echo -e "\e[32m==> Create install package $@\e[0m"
	@source $(VENV_AWS_CLI_ACTIVATE_PATH)  && pip install -r $<
	@echo -e "\e[32m====> generate freeze file $@\e[0m"
	@source $(VENV_AWS_CLI_ACTIVATE_PATH) && pip freeze > $@

#$(LAMBDA_PKG_ZIPS_PUBLISHED) : %.published : %.zip $(REQUIREMENTS_AWS_CLI_FREEZE_FILE_NAME)
#	@echo -e "\e[32m==> publishing package $< to S3\e[0m"
#	@source $(VENV_AWS_CLI_ACTIVATE_PATH)  && aws s3 cp $< $(subst $(PACKAGE_FOLDER_NAME),$(S3_BASE_URI)/$(VERSION),$<)
#	@touch $@

$(FUNCTION_PKG_ACTIVATE_PATH):
	@echo -e "\e[32m==> Create virtual env $@\e[0m"
	@virtualenv $(subst /bin/activate,, $@)
	@source $@ && pip install --upgrade pip
	@echo -e "\e[32m====> touch $@\e[0m"
	@touch $@ # touch activate file to be sure make record it

$(REQUIREMENTS_PKG_FREEZE_FILES): %$(REQUIREMENTS_PKG_FREEZE_FILE_NAME): %$(REQUIREMENTS_FILE_NAME) %$(VENV_PKG_ACTIVATE_PATH)
	@echo -e "\e[32m==> Install pip requirement from $@ $<\e[0m"
	@source $(subst $(REQUIREMENTS_PKG_FREEZE_FILE_NAME),$(VENV_PKG_ACTIVATE_PATH), $@) && \
	 pip install -r $<
	@source $(subst $(REQUIREMENTS_PKG_FREEZE_FILE_NAME),$(VENV_PKG_ACTIVATE_PATH), $@) && \
	 pip freeze > $@

$(REQUIREMENTS_FREEZE_FILES): %$(REQUIREMENTS_FREEZE_FILE_NAME): %$(REQUIREMENTS_FILE_NAME) %$(VENV_ACTIVATE_PATH)
	@echo -e "\e[32m==> Install pip requirement from $@ $<\e[0m"
	@source $(subst $(REQUIREMENTS_FREEZE_FILE_NAME),$(VENV_ACTIVATE_PATH), $@) && \
	 pip install -r $<
	@source $(subst $(REQUIREMENTS_FREEZE_FILE_NAME),$(VENV_ACTIVATE_PATH), $@) && \
	 pip freeze > $@

$(REQUIREMENTS_TESTS_FREEZE_FILES): %$(REQUIREMENTS_TESTS_FREEZE_FILE_NAME): %$(REQUIREMENTS_TESTS_FILE_NAME) %$(VENV_ACTIVATE_PATH) %$(REQUIREMENTS_FREEZE_FILE_NAME)
	@echo -e "\e[32m==> Install pip requirement from $@\e[0m"
	@echo -e "\e[32m====> Install pip requirement file $<\e[0m"
	@source $(subst $(REQUIREMENTS_TESTS_FREEZE_FILE_NAME),$(VENV_ACTIVATE_PATH), $@) && \
	 pip install -r $<
	@echo -e "\e[32m====> Install pip requirement file $(REQUIREMENTS_DEV_FILE_NAME) \e[0m"
	@source $(subst $(REQUIREMENTS_TESTS_FREEZE_FILE_NAME),$(VENV_ACTIVATE_PATH), $@) && \
	 pip install -r $(REQUIREMENTS_DEV_FILE_NAME)
	@echo -e "\e[32m====> Create freeze file $@ e[0m"
	@source $(subst $(REQUIREMENTS_TESTS_FREEZE_FILE_NAME),$(VENV_ACTIVATE_PATH), $@) && \
	 pip freeze > $@

$(REQUIREMENTS_FREEZE_FILE_NAME): $(MASTER_ACTIVATE_PATH) $(REQUIREMENTS_DEV_FILE_NAME) $(REQUIREMENTS_FREEZE_FILES) $(REQUIREMENTS_TESTS_FREEZE_FILES)
	@echo -e "\e[32m==> create $@ \e[0m"
	@echo -e "\e[32m====> Install requirements from sub functions \e[0m"
	@source $(MASTER_ACTIVATE_PATH) && \
	 pip install --ignore-installed $(patsubst %,-r %,$(REQUIREMENTS_FREEZE_FILES)) $(patsubst %,-r %,$(REQUIREMENTS_TESTS_FREEZE_FILES))
	@echo -e "\e[32m====> Install requirements $(REQUIREMENTS_DEV_FILE_NAME)\e[0m"
	@source $(MASTER_ACTIVATE_PATH) && \
	 pip install -r $(REQUIREMENTS_DEV_FILE_NAME)
	@source $(subst $(REQUIREMENTS_FREEZE_FILE_NAME),$(VENV_ACTIVATE_PATH), $@) && \
	 pip freeze > $@

######################################################################################
###############               Testing venv                   #########################
######################################################################################

$(SETUP_CFG_FILES): $(SETUP_CFG_FILE_NAME)
	@echo -e "\e[32m==> Copy $< to $@ \e[0m"
	@cp $< $@

#  $$(subst $$(PYTESTS_RESULT_FILE_NAME),,$(1))%
define Create_Result_File
$(1): $$(filter $$(shell basename $$(shell dirname $(1)))%,$$(PROJECT_PYTHON_FILES)) \
	$$(filter $$(shell basename $$(shell dirname $(1)))%,$$(FUNCTION_ACTIVATE_PATH)) \
	$(PYTEST_RESULT_FOLDER)/.touch \
	$$(shell basename $$(shell dirname $(1)))/$(SETUP_CFG_FILE_NAME) \
	$$(shell basename $$(shell dirname $(1)))/$(REQUIREMENTS_FREEZE_FILE_NAME) \
	$$(shell basename $$(shell dirname $(1)))/$(REQUIREMENTS_TESTS_FREEZE_FILE_NAME)
	@echo -e "\e[32m==> Test $$@ $$(@D)\e[0m"
	@mkdir -p $$(shell dirname $(1))
	@cd $$(shell basename $$(shell dirname $(1))) &&\
	 source $(VENV_ACTIVATE_PATH) &&\
	 pytest -m "not terraform_unittest" --junitxml=$$(abspath $(1))  $(PYTEST_ARGUMENTS) ./tests
endef
$(foreach result_file_path,$(PYTESTS_RESULT_FILES),$(eval $(call Create_Result_File,$(result_file_path))))

$(PYTESTS_RESULT_FILE_NAME): $(MASTER_ACTIVATE_PATH) $(PROJECT_PYTHON_FILES) $(SETUP_CFG_FILE_NAME)
	@echo -e "\e[32m==> Test master venv $$@ $$(@D)\e[0m"
	@source $(MASTER_ACTIVATE_PATH) && \
	 pytest -m "not terraform_unittest" --html=$@ $(PYTEST_ARGUMENTS) .

$(PYTEST_RESULT_FOLDER)/.touch:
	@echo -e "\e[32m==> Create ouput package folder $$@ $$(@D)\e[0m"
	@mkdir $(PYTEST_RESULT_FOLDER)
	@touch $@

######################################################################################
###############           Create lambda package              #########################
######################################################################################

$(OUTPUT_PKG_PATH)/$(VERSION):
	@echo -e "\e[32m==> Create touch file $$@ $$(@D)\e[0m"
	@if [ ! -d $(OUTPUT_PKG_PATH) ]; then \
		mkdir $(OUTPUT_PKG_PATH); \
	 else \
	 	rm $(OUTPUT_PKG_PATH)/* -f; \
	 fi
	@touch $@

$(LAMBDA_PKG_ZIPS): ./$(OUTPUT_PKG_PATH)/%.$(VERSION).zip: ./%/$(VENV_PKG_ACTIVATE_PATH) ./results/%/$(PYTESTS_RESULT_FILE_NAME) %/$(REQUIREMENTS_PKG_FREEZE_FILE_NAME) $(OUTPUT_PKG_PATH)/$(VERSION)
	@echo -e "\e[32m==> Create lambda package $@ \e[0m"
	@echo -e "\e[32m====> add site-package \e[0m"
	@cd $$(source $< && python -m site | grep "$$(pwd).*site-packages" | sed "s/^.*'\(.*\)'.*$$/\1/") && \
	 zip -r9 $(shell pwd)/$@ .
	@echo -e "\e[32m====> add lambda module files \e[0m"
	@zip -g $(shell pwd)/$@  $(filter-out  ./$(subst $(VENV_PKG_ACTIVATE_PATH),,$<)tests/%,$(filter ./$(subst $(VENV_PKG_ACTIVATE_PATH),,$<)%,$(PROJECT_PYTHON_FILES)))

$(TERRAFORM_VERSION_FILE): $(LAMBDA_PKG_ZIPS)
	@echo -e "\e[32m==> Create terraform variable version file $@ \e[0m"
	@printf '%b\n' "variable \"module_version\" { \n  type = \"string\" \n  description = \"version of the module\" \n  default = \"$(VERSION)\" \n }" > $@


######################################################################################
###############           Terraform testing                  #########################
######################################################################################

$(TERRAFORM_PYTEST_RESULT): $(TERRAFORM_VERSION_FILE) $(TERRAFORM_BINARY_PATH) $(TERRAFORM_FILES) $(TERRAFORM_TEST_FILES)
	@echo -e "\e[32m==> Create terraform test $@ \e[0m"
	@source $(MASTER_ACTIVATE_PATH) && \
	 pytest -m "terraform_unittest" --junitxml=$@ $(PYTEST_ARGUMENTS) .

######################################################################################
###############           Binary management                  #########################
######################################################################################

$(BINARY_FOLDER)/.touch:
	@echo -e "\e[32m==> Create ouput package folder $$@ $$(@D)\e[0m"
	@mkdir $(BINARY_FOLDER)
	@touch $@

$(TERRAFORM_BINARY_VERSION_FILE): $(BINARY_FOLDER)/.touch
	@echo -e "\e[32m==> Create Terraform version file $$@ $$(@D)\e[0m"
	@touch $@

$(TERRAFORM_TEMP_ZIP): $(TERRAFORM_BINARY_VERSION_FILE)
	@echo -e "\e[32m==> Download terraform binary\e[0m"
	@curl $(TERRAFORM_URL) -o $(TERRAFORM_TEMP_ZIP)

$(TERRAFORM_BINARY_PATH): $(TERRAFORM_TEMP_ZIP)
	@echo -e "\e[32m==> Extract terraform binary\e[0m"
	@unzip -o $(TERRAFORM_TEMP_ZIP) -d $(BINARY_FOLDER)
	@touch $(TERRAFORM_BINARY_PATH)

######################################################################################
###############           Terraform Package creation         #########################
######################################################################################
$(TERRAFORM_MODULE_PACKAGE_FOLDER)/.touch:
	@echo -e "\e[32m==> Create ouput package folder $$@ $$(@D)\e[0m"
	@mkdir $(TERRAFORM_MODULE_PACKAGE_FOLDER)
	@touch $@

$(TERRAFORM_MODULE_PACKAGE_PATH): $(TERRAFORM_MODULE_PACKAGE_FOLDER)/.touch $(TERRAFORM_PYTEST_RESULT)
	@echo -e "\e[32m==> Create terraform package $$@ $$(@D)\e[0m"
	@cd $(TERRAFORM_MODULE_PATH) && \
	 zip -r9 $(shell pwd)/$@ .



######################################################################################
###############           S3 package publishing              #########################
######################################################################################

$(TERRAFORM_MODULE_PACKAGE_PUBLISHED): $(REQUIREMENTS_AWS_CLI_FREEZE_FILE_NAME)
	@echo -e "\e[32m==> publishing package $< to S3\e[0m"
#	$(TERRAFORM_MODULE_PACKAGE_PATH)
	@source $(VENV_AWS_CLI_ACTIVATE_PATH)  && aws s3 cp $< $(S3_BUCKET_URL)/$(S3_PACKAGE_PATH)/$(PROJECT_NAME)/$(shell basename $<)
	@touch $@

######################################################################################
###############           Main entries points                #########################
######################################################################################

help:
# http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
	@echo "Generic makefile to manage python lambda function development"
	@echo "====================="
	@grep -E '^[a-zA-Z0-9_%/-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

create-aws-cli-venv: $(REQUIREMENTS_AWS_CLI_FREEZE_FILE_NAME) ## Create venv for aws cli
	@echo -e "\e[32m==> Create aws cli venv\e[0m"

create-local-venv: $(REQUIREMENTS_FREEZE_FILES) ## Create locals function venv
	@echo -e "\e[32m==> Create local venv\e[0m"

create-master-venv: $(REQUIREMENTS_FREEZE_FILE_NAME) ## Create master venv
	@echo -e "\e[32m==> Create master venv\e[0m"

create-all-venv: create-master-venv create-local-venv create-aws-cli-venv ## Create all function environment and a master venv
	@echo -e "\e[32m==> Create all venv\e[0m"

initialize-binary: $(TERRAFORM_BINARY_PATH) ## Download required external binary dependencies
	@echo -e "\e[32m==> Download required external dependencies\e[0m"

clean-pytest-result: ## Clean pytest result to force retest.
	@echo -e "\e[32m==> Remove pytest.result.html\e[0m"
	@rm $(PYTESTS_RESULT_FILE_NAME) $(PYTESTS_RESULT_FILES) $(TERRAFORM_PYTEST_RESULT) -f

clean: clean-pytest-result ## Clean all build file created
	@echo -e "\e[32m==> Clean working directory\e[0m"

	@echo -e "\e[32m====> Remove master .venv \e[0m"
	@rm .venv -rf

	@echo -e "\e[32m====> Remove function .venv \e[0m"
	@rm $(subst /bin/activate,, $(FUNCTION_ACTIVATE_PATH))  -rf

	@echo -e "\e[32m====> Remove function .venv_pkg\e[0m"
	@rm $(subst /bin/activate,, $(FUNCTION_PKG_ACTIVATE_PATH))  -rf

	@echo -e "\e[32m====> Remove freeze files\e[0m"
	@rm $(REQUIREMENTS_FREEZE_FILE_NAME) $(REQUIREMENTS_PKG_FREEZE_FILES) $(REQUIREMENTS_FREEZE_FILES) $(REQUIREMENTS_TESTS_FREEZE_FILES) -f

	@echo -e "\e[32m====> Remove output path folder $(OUTPUT_PKG_PATH)\e[0m"
	@rm $(OUTPUT_PKG_PATH) -rf

	@echo -e "\e[32m====> Remove output path folder $(REQUIREMENTS_FUNCTIONS)\e[0m"
	@rm $(FUNCTIONS_REQUIREMENTS) -f$(FUNCTIONS_REQUIREMENTS)

	@echo -e "\e[32m====> Delete bin folder \e[0m"
	@rm $(BINARY_FOLDER) -rf

	@echo -e "\e[32m====> Delete lambda packages\e[0m"
	@rm $(TERRAFORM_MODULE_PACKAGES) -rf

format-code: $(REQUIREMENTS_FREEZE_FILE_NAME) ## format all the code using black
	@echo -e "\e[32m==> Reformat code using black\e[0m"
	@source $(MASTER_ACTIVATE_PATH) && black . --exclude .venv

test-local-venv: $(PYTESTS_RESULT_FILES) ## Test local the functions using their local venv
	@echo -e "\e[32m==> Test using local venv\e[0m"

test-master-venv: $(PYTESTS_RESULT_FILE_NAME) ## Test master the functions using the master venv
	@echo -e "\e[32m==> Test master venv\e[0m"

test-all-venv: test-local-venv test-master-venv ## Test all the functions using the master venv
	@echo -e "\e[32m==> Test all venv\e[0m"

test-terraform-modules: $(TERRAFORM_PYTEST_RESULT) ## Test all module terraform deployment
	@echo -e "\e[32m==> Test module\e[0m"

print-value:
	$(foreach v,                                        \
	  $(filter-out $(VARS_OLD) VARS_OLD,$(.VARIABLES)), \
	  $(info $(v) = $($(v))))
#	@echo $(TERRAFORM_BINARY_VERSION_FILE)
#	@echo $(TERRAFORM_VERSION)
#	@echo $(TERRAFORM_URL)
#	@echo $(TERRAFORM_TEMP_ZIP)
#	@echo $(TERRAFORM_BINARY_VERSION_FILE)
#	@echo $(TERRAFORM_BINARY_PATH)
#
#	@echo $(filter $(subst $(PYTESTS_RESULT_FILE_NAME),,./lambda_function2/$(PYTESTS_RESULT_FILE_NAME))%,$(PROJECT_PYTHON_FILES))
#	@echo $(subst $(PYTESTS_RESULT_FILE_NAME),,$(PYTESTS_RESULT_FILES))
#	@echo $(REQUIREMENTS_FREEZE_FILE_NAME)
#	@echo $(REQUIREMENTS_FILE_NAME)
#	@echo $(REQUIREMENTS_FREEZE_FILES)
#	@echo $(VERSION)
#	@echo $(LAMBDA_FUNCTIONS)
#	@echo $(LAMBDA_PKG_ZIPS)

create-packages: $(TERRAFORM_VERSION_FILE)  ## Create all the packages
	@echo -e "\e[32m==> Create packages \e[0m"

create-terraform-package: $(TERRAFORM_MODULE_PACKAGE_PATH) ## Create the terraform package
	@echo -e "\e[32m==> Create terraform packages \e[0m"

publish-packages-to-s3: $(TERRAFORM_MODULE_PACKAGE_PUBLISHED) ## publish all the package to S3
	@echo -e "\e[32m==> publish packages to S3 \e[0m"