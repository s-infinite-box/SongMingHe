.DEFAULT_GOAL := build

HUGO ?= hugo
BIND ?= 127.0.0.1
PORT ?= 1313
PREVIEW_URL ?= http://localhost:$(PORT)/
HUGO_FLAGS ?=
ifndef BUILD_CLOCK
BUILD_CLOCK := $(shell date --iso-8601=seconds)
endif
export HUGO_CACHEDIR := $(CURDIR)/resources/_gen/hugo_cache
TEST_TMPDIR ?= $(abspath ../../.tmp/blog-theme-review-fixes)

.PHONY: build check test serve serve-drafts clean help

build:
	HUGO_ENVIRONMENT=production TZ=Asia/Shanghai $(HUGO) --gc --minify --cleanDestinationDir --clock "$(BUILD_CLOCK)" $(HUGO_FLAGS)
	HUGO_ENVIRONMENT=production TZ=Asia/Shanghai $(HUGO) list published --clock "$(BUILD_CLOCK)" > .build-published.csv
	python3 scripts/prepare-legacy-paths.py

check: test build
	python3 scripts/verify-build.py

test:
	node --test tests/*.test.cjs
	HUGO="$(HUGO)" TEST_TMPDIR="$(TEST_TMPDIR)" python3 -m unittest discover -s tests -p 'test_*.py'

serve:
	$(HUGO) server --bind "$(BIND)" --port "$(PORT)" --baseURL "$(PREVIEW_URL)" --renderToMemory --disableFastRender $(HUGO_FLAGS)

serve-drafts:
	$(HUGO) server --buildDrafts --bind "$(BIND)" --port "$(PORT)" --baseURL "$(PREVIEW_URL)" --renderToMemory --disableFastRender $(HUGO_FLAGS)

clean:
	rm -rf -- public resources/_gen

help:
	@printf '%s\n' \
		'make              构建正式站点，输出到 public/' \
		'make check        构建并核验链接、RSS、搜索、旧分页和资源' \
		'make test         运行评论、目录和发布时间回归测试' \
		'make serve        启动本地预览' \
		'make serve-drafts  启动本地预览，包含草稿' \
		'make clean        清理 public/ 和 resources/_gen/' \
		'make help         显示命令说明' \
		'' \
		'可覆盖变量：HUGO、BIND、PORT、PREVIEW_URL、HUGO_FLAGS、BUILD_CLOCK、TEST_TMPDIR' \
		'例如：make serve PORT=1314'
