.DEFAULT_GOAL := build

HUGO ?= hugo
BIND ?= 127.0.0.1
PORT ?= 1313
PREVIEW_URL ?= http://localhost:$(PORT)/SongMingHe/
HUGO_FLAGS ?=

.PHONY: build check serve serve-drafts clean help

build:
	HUGO_ENVIRONMENT=production TZ=Asia/Shanghai $(HUGO) --gc --minify $(HUGO_FLAGS)

check: build
	python3 scripts/verify-build.py

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
		'make serve        启动本地预览' \
		'make serve-drafts  启动本地预览，包含草稿' \
		'make clean        清理 public/ 和 resources/_gen/' \
		'make help         显示命令说明' \
		'' \
		'可覆盖变量：HUGO、BIND、PORT、PREVIEW_URL、HUGO_FLAGS' \
		'例如：make serve PORT=1314'
