.PHONY: help run start stop logs lint test test-unit test-unit-watch test-acceptance test-integration cov docs docs-acceptance clean reset release dist check-deps clean-build clean-pyc clean-test

.DEFAULT_GOAL := help


#############################
# Open a URL in the browser #
#############################
define BROWSER_PYSCRIPT
import os, webbrowser, sys
try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT


##################################
# Display help for this makefile #
##################################
define PRINT_HELP_PYSCRIPT
import re, sys

print("Planetmint 2.0 developer toolbox")
print("--------------------------------")
print("Usage:  make COMMAND")
print("")
print("Commands:")
for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("    %-16s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

##################
# Basic commands #
##################
DOCKER := docker
DC := docker-compose
BROWSER := python -c "$$BROWSER_PYSCRIPT"
HELP := python -c "$$PRINT_HELP_PYSCRIPT"
ECHO := /usr/bin/env echo

IS_DOCKER_COMPOSE_INSTALLED := $(shell command -v docker-compose 2> /dev/null)
IS_BLACK_INSTALLED := $(shell command -v black 2> /dev/null)

################
# Main targets #
################

help: ## Show this help
	@$(HELP) < $(MAKEFILE_LIST)

test: check-deps test-acceptance ## Run unit and acceptance tests

prepare:
	wget https://raw.githubusercontent.com/planetmint/planetmint/main/planetmint/backend/tarantool/init.lua


test-acceptance: check-deps prepare ## Run all acceptance tests
	docker-compose up -d planetmint
	docker-compose run --rm python-acceptance pytest /src
	docker-compose down


test-integration: check-deps prepare ## Run all integration tests
	docker-compose -f docker-compose.integration.yml up test
	docker-compose -f docker-compose.integration.yml down


clean: check-deps ## Remove all build, test, coverage and Python artifacts
	@$(DC) up clean
	@$(ECHO) "Cleaning was successful."

reset: check-deps ## Stop and REMOVE all containers. WARNING: you will LOSE all data stored in Planetmint.
	@$(DC) down

###############
# Sub targets #
###############

check-deps:
ifndef IS_DOCKER_COMPOSE_INSTALLED
	@$(ECHO) "Error: docker-compose is not installed"
	@$(ECHO)
	@$(ECHO) "You need docker-compose to run this command. Check out the official docs on how to install it in your system:"
	@$(ECHO) "- https://docs.docker.com/compose/install/"
	@$(ECHO)
	@$(DC) # docker-compose is not installed, so we call it to generate an error and exit
endif


