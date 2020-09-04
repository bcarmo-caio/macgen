default: help


.PHONY: help ## Help message
help:
	@grep -E '^.PHONY.*##' $(abspath $(filter Makefile,$(MAKEFILE_LIST))) | \
		sed -r 's/\.PHONY: //' | \
		sort | \
		awk 'BEGIN {FS = " ## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


# If you want a static configuration, include it in .flake8 configuration file.
# The following variable is dymanic and we can not achieve that using flake8 configuration file
# that is why we are building it here.
LINT_EXCLUDE_FROM_GITIGNORE := $(shell cat .gitignore | sed -r "s/\#.*//g" | grep . |tr "\n" ",")
# LINT_EXCLUDE_FROM_GITIGNORE ends with ',' when executing shell command above.
LINT_EXCLUDE := $(LINT_EXCLUDE_FROM_GITIGNORE).gitignore,.git/
# If you want to expand this list, do it in another line like this: (mind comma ',')
# LINT_EXCLUDE := $(LINT_EXCLUDE),exclude_me_too
LINT_EXCLUDE := $(LINT_EXCLUDE),levenshtein_fallback.py
.PHONY: lint ## run lint in project
lint:
	@flake8 --exclude=$(LINT_EXCLUDE)
