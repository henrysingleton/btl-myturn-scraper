# Variables
LAMBDA_FUNCTION_NAME = lambda_function
ZIP_FILE = dist/$(LAMBDA_FUNCTION_NAME).zip
SRC_DIR = src
VENV_DIR = venv

# Create a virtual environment and install dependencies
.PHONY: setup
setup:
	python3 -m venv $(VENV_DIR)
	$(VENV_DIR)/bin/pip install -r requirements.txt

# Package the Lambda function into a zip file
.PHONY: package
package: setup
	@echo "Packaging Lambda function..."
	@rm -f $(ZIP_FILE)  # Remove old zip file if it exists
	@cd $(VENV_DIR)/lib/python$(shell python3 -c "import sys; print('{}.{}'.format(*sys.version_info[:2]))")/site-packages && \
		zip -r $(OLDPWD)/$(ZIP_FILE) . -x "setuptools/*" -x "pip/*" -x "*.dist-info/*" -x "__pycache__/*" -x "bs4/tests/*" && \
		cd $(OLDPWD) && \
		cd $(SRC_DIR) && \
		zip -g ../$(ZIP_FILE) ./*

# Clean up the virtual environment and zip file
.PHONY: clean
clean:
	rm -rf $(VENV_DIR) $(ZIP_FILE)

# Default target
.PHONY: all
all: package