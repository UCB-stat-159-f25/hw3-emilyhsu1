# ===============================================
# Makefile 
# ===============================================
# Variables
ENV_NAME := ligo
ENV_FILE := environment.yml

# Content files that trigger an HTML rebuild if changed:
CONTENT := $(wildcard *.md) $(wildcard *.ipynb) \
           $(wildcard notebooks/*.ipynb) $(wildcard docs/*.md)

# Let multiple lines in a recipe share the same shell:
.ONESHELL:
SHELL = /bin/bash

# Self-documenting help:
.PHONY: help
## help               : Show this help
help: Makefile
	@sed -n 's/^##//p' $<

# -------------------------
# Env:
# -------------------------
# .env-ready is a *file target* that marks a successful env setup/update.
# It depends on environment.yml so any change there re-runs the recipe.
.env-ready: $(ENV_FILE)
	@echo ">>> Ensuring conda environment '$(ENV_NAME)' from $<"
	source /srv/conda/etc/profile.d/conda.sh
	if conda env list | awk '{print $$1}' | grep -qx '$(ENV_NAME)'; then
		echo "Environment exists — updating from $<"
		conda env update -n $(ENV_NAME) -f $< --prune
	else
		echo "Creating new environment '$(ENV_NAME)' from $<"
		conda env create -n $(ENV_NAME) -f $<
	fi
	echo ">>> Installing Jupyter kernel for '$(ENV_NAME)' (idempotent)"
	conda run -n $(ENV_NAME) python -m ipykernel install --user --name $(ENV_NAME) --display-name "Python ($(ENV_NAME))"
	touch $@

.PHONY: env
## env                : Create or update the conda env from environment.yml (no activation)
env: .env-ready
	@echo "✓ Env up to date: $^"

# -------------------------
# HTML:
# -------------------------
# Build a concrete target that depends on config + content.
# If myst.yml or any content changes, this rebuilds.
_build/html/index.html: myst.yml $(CONTENT) | .env-ready
	@echo ">>> Building local MyST site because of changed deps:"
	@echo "    $^"
	myst build --html
	@echo "✓ Built $@"

.PHONY: html
## html               : Build a local HTML site (myst build --html)
html: _build/html/index.html
	@echo "Open _build/html/index.html in the JupyterLab file browser to preview."

# -------------------------
# Clean:
# -------------------------
.PHONY: clean
## clean              : Remove generated artifacts (figures, audio, _build)
clean:
	@echo ">>> Cleaning generated artifacts..."
	rm -rf figures audio _build .env-ready
	@echo "✓ Clean complete."
