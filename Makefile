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
S3_BUCKET = $(shell grep -r S3_bucket_uri config.toml | awk -F '"' '{print $$2}')
S3_PACKAGE_PATH = $(shell grep -r S3_folder_path config.toml | awk -F '"' '{print $$2}')
BINARY_FOLDER = ./bin
PACKAGE_FOLDER_NAME = packages

TERRAFORM_BINARY_PATH = $(binary_folder)/terraform
TERRAFORM_MODULE_PATH = ./terraform/$(PROJECT_NAME)
TERRAFORM_VERSION_FILE = $(TERRAFORM_MODULE_PATH)/variable.version.tf
TERRAFORM_MODULE_PACKAGES = $(TERRAFORM_MODULE_PATH)/$(PACKAGE_FOLDER_NAME)
OUTPUT_PKG_PATH = $(TERRAFORM_MODULE_PACKAGES)

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
FUNCTIONS_REQUIREMENTS = requirements.functions.txt
GIT_HASH_COMMIT = $(shell git rev-parse --short HEAD)
S3_BASE_URI =  $(S3_BUCKET)/$(S3_PACKAGE_PATH)
VERSION = $(CONFIG_VERSION).$(GIT_HASH_COMMIT)
PYTESTS_RESULT_FILE_NAME = pytest.report.html
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
PYTESTS_RESULT_FILES := $(subst  $(REQUIREMENTS_FILE_NAME),$(PYTESTS_RESULT_FILE_NAME),$(REQUIREMENTS_FILES))
SETUP_CFG_FILES := $(subst  $(REQUIREMENTS_FILE_NAME),$(SETUP_CFG_FILE_NAME),$(REQUIREMENTS_FILES))
FUNCTION_ACTIVATE_PATH = $(subst  $(REQUIREMENTS_FILE_NAME),$(VENV_ACTIVATE_PATH),$(REQUIREMENTS_FILES))
FUNCTION_PKG_ACTIVATE_PATH = $(subst  $(REQUIREMENTS_FILE_NAME),$(VENV_PKG_ACTIVATE_PATH),$(REQUIREMENTS_FILES))
VENV_ROOT_PATH = $(subst  /bin/activate,,$(FUNCTION_ACTIVATE_PATH))
VENV_PKG_ROOT_PATH = $(subst  /bin/activate,,$(FUNCTION_PKG_ACTIVATE_PATH))

DIRECTORY_EXCLUSION = -path ./.venv $(patsubst  %,-o -path %,$(VENV_ROOT_PATH)) $(patsubst  %,-o -path %,$(VENV_PKG_ROOT_PATH)) -o -path ./.venv_aws
PROJECT_PYTHON_FILES = $(shell find . -type d \( $(DIRECTORY_EXCLUSION) \) -prune -o -name $(PYTHON_FILE_EXTENSION) -print)

MASTER_ACTIVATE_PATH = $(VENV_ACTIVATE_PATH)

######################################################################################
###############              Create virtual envs             #########################
######################################################################################

$(FUNCTIONS_REQUIREMENTS): $(REQUIREMENTS_FILES) $(REQUIREMENTS_TESTS_FILES)
	@echo -e "\e[32m==> Create file $@ \e[0m"
	@rm $@ -f
	@echo $(patsubst %,-r %,$(REQUIREMENTS_FILES)) > $@
	@echo $(patsubst %,-r %,$(REQUIREMENTS_TESTS_FILES)) >> $@

$(FUNCTION_ACTIVATE_PATH):
	@echo -e "\e[32m==> Create virtual env $@\e[0m"
	@virtualenv $(subst /bin/activate,, $@)
	@source $@ && pip install --upgrade pip
	@echo -e "\e[32m====> touch $@\e[0m"
	@touch $@ # touch activate file to be sure make record it

$(MASTER_ACTIVATE_PATH) : $(FUNCTIONS_REQUIREMENTS) $(REQUIREMENTS_DEV_FILE_NAME)
	@echo -e "\e[32m==> Create virtual env $@\e[0m"
	@virtualenv $(subst /bin/activate,, $@)
	@source $@ && pip install --upgrade pip
	@source $@ && pip install -r $(REQUIREMENTS_DEV_FILE_NAME)
	@source $@ && pip install -r $(FUNCTIONS_REQUIREMENTS)
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

$(LAMBDA_PKG_ZIPS_PUBLISHED) : %.published : %.zip $(REQUIREMENTS_AWS_CLI_FREEZE_FILE_NAME)
	@echo -e "\e[32m==> publishing package $< to S3\e[0m"
	@source $(VENV_AWS_CLI_ACTIVATE_PATH)  && aws s3 cp $< $(subst $(PACKAGE_FOLDER_NAME),$(S3_BASE_URI)/$(VERSION),$<)
	@touch $@

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
	 pip install $(patsubst %,-r %,$(REQUIREMENTS_FREEZE_FILES)) $(patsubst %,-r %,$(REQUIREMENTS_TESTS_FREEZE_FILES))
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

define Create_Result_File
$(1): $$(filter $$(subst $$(PYTESTS_RESULT_FILE_NAME),,$(1))%,$$(PROJECT_PYTHON_FILES)) \
	$$(filter $$(subst $$(PYTESTS_RESULT_FILE_NAME),,$(1))%,$$(FUNCTION_ACTIVATE_PATH)) \
	$$(subst $$(PYTESTS_RESULT_FILE_NAME),,$(1))$(SETUP_CFG_FILE_NAME) \
	$$(subst $$(PYTESTS_RESULT_FILE_NAME),,$(1))$(REQUIREMENTS_FREEZE_FILE_NAME) \
	$$(subst $$(PYTESTS_RESULT_FILE_NAME),,$(1))$(REQUIREMENTS_TESTS_FREEZE_FILE_NAME)
	@echo -e "\e[32m==> Test $$@ $$(@D)\e[0m"
	@cd $$(@D) &&\
	 source $(VENV_ACTIVATE_PATH) &&\
	 pytest --html=$$(@F) $(PYTEST_ARGUMENTS) ./tests
endef
$(foreach result_file_path,$(PYTESTS_RESULT_FILES),$(eval $(call Create_Result_File,$(result_file_path))))

$(PYTESTS_RESULT_FILE_NAME): $(MASTER_ACTIVATE_PATH) $(PROJECT_PYTHON_FILES) $(SETUP_CFG_FILE_NAME)
	@echo -e "\e[32m==> Test master venv $$@ $$(@D)\e[0m"
	@source $(MASTER_ACTIVATE_PATH) && \
	 pytest --html=$@ $(PYTEST_ARGUMENTS) .


######################################################################################
###############           Create lambda package              #########################
######################################################################################

$(OUTPUT_PKG_PATH)/.touch:
	@echo -e "\e[32m==> Create ouput package folder $$@ $$(@D)\e[0m"
	@mkdir $(OUTPUT_PKG_PATH)
	@touch $@

$(LAMBDA_PKG_ZIPS): ./$(OUTPUT_PKG_PATH)/%.$(VERSION).zip: ./%/$(VENV_PKG_ACTIVATE_PATH) ./%/$(PYTESTS_RESULT_FILE_NAME) %/$(REQUIREMENTS_PKG_FREEZE_FILE_NAME) $(OUTPUT_PKG_PATH)/.touch
	@echo -e "\e[32m==> Create lambda package $@ \e[0m"
	@echo -e "\e[32m====> add site-package \e[0m"
	@cd $$(source $< && python -m site | grep "$$(pwd).*site-packages" | sed "s/^.*'\(.*\)'.*$$/\1/") && \
	 zip -r9 $(shell pwd)/$@ .
	@echo -e "\e[32m====> add lambda module files \e[0m"
	@cd $(subst $(VENV_PKG_ACTIVATE_PATH),,$<) && \
	 zip -g $(shell pwd)/$@  $(subst $(subst $(VENV_PKG_ACTIVATE_PATH),,$<),,$(filter-out  ./$(subst $(VENV_PKG_ACTIVATE_PATH),,$<)tests/%,$(filter ./$(subst $(VENV_PKG_ACTIVATE_PATH),,$<)%,$(PROJECT_PYTHON_FILES))))


$(TERRAFORM_VERSION_FILE): $(LAMBDA_PKG_ZIPS)
	@echo -e "\e[32m==> Create terraform variable version file $@ \e[0m"
	@printf '%b\n' "variable \"module_version\" { \n  type = \"string\" \n  description = \"version of the module\" \n  default = \"$(VERSION)\" \n }" > $@


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

clean-pytest-result: ## Clean pytest result to force retest.
	@echo -e "\e[32m==> Remove pytest.result.html\e[0m"
	@rm $(PYTESTS_RESULT_FILE_NAME) $(PYTESTS_RESULT_FILES) -f

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

	@echo -e "\e[32m====> Remove output path folder $(FUNCTIONS_REQUIREMENTS)\e[0m"
	@rm $(FUNCTIONS_REQUIREMENTS) -f

format-code: $(REQUIREMENTS_FREEZE_FILE_NAME) ## format all the code using black
	@echo -e "\e[32m==> Reformat code using black\e[0m"
	@source $(MASTER_ACTIVATE_PATH) && black .

test-local-venv: $(PYTESTS_RESULT_FILES) ## Test local the functions using their local venv
	@echo -e "\e[32m==> Test using local venv\e[0m"

test-master-venv: $(PYTESTS_RESULT_FILE_NAME) ## Test master the functions using the master venv
	@echo -e "\e[32m==> Test master venv\e[0m"

test-all-venv: test-local-venv test-master-venv ## Test all the functions using the master venv
	@echo -e "\e[32m==> Test all venv\e[0m"

print-value:
	@echo $(filter $(subst $(PYTESTS_RESULT_FILE_NAME),,./lambda_function2/$(PYTESTS_RESULT_FILE_NAME))%,$(PROJECT_PYTHON_FILES))
	@echo $(subst $(PYTESTS_RESULT_FILE_NAME),,$(PYTESTS_RESULT_FILES))
	@echo $(REQUIREMENTS_FREEZE_FILE_NAME)
	@echo $(REQUIREMENTS_FILE_NAME)
	@echo $(REQUIREMENTS_FREEZE_FILES)
	@echo $(VERSION)
	@echo $(LAMBDA_FUNCTIONS)
	@echo $(LAMBDA_PKG_ZIPS)

create-packages: $(TERRAFORM_VERSION_FILE)  ## Create all the packages
	@echo -e "\e[32m==> Create packages \e[0m"

publish-packages-to-s3: $(LAMBDA_PKG_ZIPS_PUBLISHED) ## publish all the package to S3
	@echo -e "\e[32m==> publish packages to S3 \e[0m"