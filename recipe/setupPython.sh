###     
###     Set up a virtual environment with the newest version of rootpy
###     
###     Author: Nate Woods, U. Wisconsin
###     

if [ "$zza" == "" ]; then
    echo "Please set up this package with setup.sh before running this script."
    exit 2
fi

export vpython="$zza"/recipe/vpython

python "$zza"/recipe/virtualenv/virtualenv.py "$vpython"

source "$vpython"/bin/activate

pip install -U pip
pip install -U rootpy

