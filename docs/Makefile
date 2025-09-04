# Math Exercise Generator Documentation Makefile
#
# You can set these variables from the command line.
SPHINXOPTS    ?= -W --keep-going
SPHINXBUILD  ?= py -m sphinx
SOURCEDIR    = source
BUILDDIR     = build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Generate HTML documentation
html:
	@echo "Building HTML documentation..."
	@$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)
	@echo "Build finished. HTML pages are in $(BUILDDIR)/"

# Clean build directory
clean:
	@echo "Cleaning build directory..."
	@if exist "$(BUILDDIR)" rmdir /s /q "$(BUILDDIR)"
	@echo "Clean finished."

# Watch for changes and rebuild automatically
watch:
	@echo "Starting documentation watch mode..."
	@py -c "import subprocess, time, os; import watchdog.observers; import watchdog.events; \
class Handler(watchdog.events.FileSystemEventHandler): \
    def on_modified(self, event): \
        if event.src_path.endswith(('.rst', '.md', '.py')): \
            print('File changed, rebuilding...'); \
            subprocess.run(['make', 'html'], shell=True); \
observer = watchdog.observers.Observer(); \
observer.schedule(Handler(), '$(SOURCEDIR)', recursive=True); \
observer.schedule(Handler(), '../utils', recursive=True); \
observer.start(); \
print('Watching for changes...'); \
try: \
    while True: time.sleep(1) \
except KeyboardInterrupt: \
    observer.stop(); \
observer.join()"

# Generate API documentation from source
apidoc:
	@echo "Generating API documentation..."
	@py -m sphinx.ext.apidoc -o "$(SOURCEDIR)/api" "../utils" --force --module-first
	@echo "API documentation generated."

# Build and open in browser
serve: html
	@echo "Opening documentation in browser..."
	@start "" "$(BUILDDIR)/index.html"

# Check for broken links
linkcheck:
	@$(SPHINXBUILD) -b linkcheck "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)