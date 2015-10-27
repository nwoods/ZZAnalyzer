#!/bin/bash


if [ $1 == "" ] || [ $1 == "-h" ] || [ $1 == "--help" ] || [ $2 == "" ]; then
    echo "$0 usage: ./$0 [-h|--help] destDir srcDir"
    echo "    destDir: location for output files."
    echo "    srcDir: top-level directory made by submit_job.py output."
    exit 1
fi


if [ ! -d $1 ]; then
    mkdir -p $1
fi

let FILES_PER_OUTPUT=200

for s in "$2"/*; do
    SAMPLE_NAME=`basename $s`
    FILES=`find "$s"/submit/*/*.root`
    let N_FILES=`echo $FILES | wc -w`

    if [ $N_FILES -le $FILES_PER_OUTPUT ]; then
        echo $FILES | xargs hadd "$1"/"$SAMPLE_NAME".root 
    else
        let I_FILE=0
        FILE_ARR=( $FILES )
        while [ $((I_FILE*FILES_PER_OUTPUT)) -lt $N_FILES ]; do
            echo "${FILE_ARR[@]:$((I_FILE*FILES_PER_OUTPUT)):$((FILES_PER_OUTPUT))}" | xargs hadd "$1"/"$SAMPLE_NAME"_"$I_FILE".root 
            : $((I_FILE += 1))
        done
    fi
done