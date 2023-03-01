#!/bin/bash

function write() {
    file=$1
    msg=$2
    ignore_if_exists=${3:-true}

    if [[ -f $file ]] && [[ "$ignore_if_exists" = "true" ]]; then
        echo "skipping $file"
    else
        echo "writing $file"
        echo "$msg" >> $file
    fi
}

# directories
mkdir .vscode/
mkdir src/
mkdir src/classes/
touch src/classes/__init__.py
mkdir src/cache/
mkdir src/config
touch src/config/__init__.py
mkdir src/data/
mkdir src/docs/
mkdir src/tests/
touch src/tests/__init__.py
mkdir src/tools/
mkdir src/utils/
touch src/utils/__init__.py

# python
[[ ! -d ./venv ]] && python3 -m venv venv
[[ ! -f ./requirements.txt ]] && touch requirements.txt
contents='black'
write "dev_requirements.txt" "$contents"

# git
[[ ! -d ./.git ]] && git init
contents='venv/

*.log
*.pyc
'
write ".gitignore" "$contents"

# vscode (settings.json)
contents='{
  "[python]": {
    "editor.wordBasedSuggestions": false,
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  },
  "python.sortImports.args": ["--profile", "black"],
  "python.analysis.autoImportCompletions": true,
  "autoDocstring.docstringFormat": "numpy-notypes",
  "autoDocstring.customTemplatePath": ".vscode/docstrings.mustache"
}
'
write ".vscode/settings.json" "$contents"

# vscode (launch.json)
contents='{
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "justMyCode": true,
            "env": {
                "PYTHONPATH": "./src"
            }
        }
    ]
}
'
write ".vscode/launch.json" "$contents"

# paths.py
contents='from pathlib import Path

PROJ_DIR = Path(__file__).parent.parent.parent
SRC_DIR = PROJ_DIR / "src"

CACHE_DIR = SRC_DIR / "cache"
CONFIG_DIR = SRC_DIR / "config"
DATA_DIR = SRC_DIR / "data"
LOG_DIR = SRC_DIR / "logs"

for name, path in list(locals().items()):
    if name.endswith("_DIR"):
        path.mkdir(exist_ok=True)
'
write "src/config/paths.py" "$contents"
