#!/bin/bash

# Get directory of script (rather than directory the script is run from)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export zza="${DIR}"
export PYTHONPATH="${PYTHONPATH}":"${zza}"/analyzers:"${zza}"/ZZUtils:"${zza}"/ZZMetadata

echo "ZZAnalyzer setup complete"
