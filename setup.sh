#!/bin/bash

# Get directory of script (rather than directory the script is run from)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export zza="${DIR}"

if [ -d "$zza"/recipe/vpython ]; then
    echo "Activating python virtual environment"
    source "$zza"/recipe/vpython/bin/activate
fi

export PYTHONPATH="${PYTHONPATH}":"${zza}"

echo "ZZAnalyzer setup complete"
