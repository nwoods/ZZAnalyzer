#!/bin/bash

# Get directory of script (rather than directory the script is run from)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "${DIR}"
export zza="${DIR}"
echo "${zza}"
export PYTHONPATH="${PYTHONPATH}":"${zza}"/analyzers:"${zza}"/ZZUtils
echo $PYTHONPATH
