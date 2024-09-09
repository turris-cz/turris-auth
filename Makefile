PROJECT="turris-auth"
VERSION=$(shell sed -En "s/.*version = ['\"](.+)['\"].*/\1/p" pyproject.toml)
COPYRIGHT_HOLDER="CZ.NIC z.s.p.o. (https://www.nic.cz/)"
MSGID_BUGS_ADDRESS="packaging@turris.cz"

MAKEFLAGS += --no-builtin-rules
null :=
space := $(null) #
comma := ,

.PHONY: all
all:
	@

.PHONY: clean
clean:
	@

.PHONY: install
install:
	@

.PHONY: extract
extract:
	@

.PHONY: update
update:
	@

.PHONY: help
help:
	@echo "Top level targets:"
	@echo "  all: generate *.mo files"
	@echo "  clean: remove generated *.mo files"
	@echo "  extract: extract strings to *.pot files"
	@echo "  update: merge changes from *.pot files to *.po"


define MODULE

$(1)_PATH := $(subst .,/,$(1))
$(1)_SOURCES := $$(foreach path,$$(patsubst %,$$($(1)_PATH)/%,$(2)),$$(wildcard $$(path)))
$(1)_POT := $$($(1)_PATH)/locale/$(1).pot
$(1)_PO := $$(shell find $$($(1)_PATH)/locale -name $(1).po)
$(1)_MO := $$(patsubst %.po,%.mo,$$($(1)_PO))

.PHONY: $(1) install-$(1) update-$(1)

.PHONY: extract-$(1)
extract: extract-$(1)
extract-$(1): $$($(1)_POT)
$$($(1)_POT): $$($(1)_SOURCES)
	pybabel extract \
		--mapping-file="$$($(1)_PATH)/locale/babel.cfg" \
		--msgid-bugs-address=$(MSGID_BUGS_ADDRESS) \
		--copyright-holder=$(COPYRIGHT_HOLDER) \
		--project=$(PROJECT) \
		--version=$(VERSION) \
		--output-file="$$@" \
		--input-dirs "$$(subst $$(space),$$(comma),$$^)"

.PHONY: update-$(1)
update: update-$(1)
update-$(1): $$($(1)_PO)
$$($(1)_PO): %.po: $$($(1)_POT)
	pybabel update \
		--domain "$(1)" \
		--locale $$(shell sed -n 's/"Language: \([a-z]\+\).*/\1/p' "$$@") \
		--input-file="$$<" \
		--update-header-comment \
		--output-file="$$@"

.PHONY: $(1)
all: $(1)
$(1): $$($(1)_MO)
$$($(1)_MO): %.mo: %.po
	pybabel compile \
		--domain "$(1)" \
		--input-file="$$<" \
		--output-file="$$@"

clean: clean-$(1)
clean-$(1):
	rm -f $$($(1)_MO)

endef

$(eval $(call MODULE,turris_auth.server,templates/*.j2))
