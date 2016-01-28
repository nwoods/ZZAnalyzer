#!/bin/bash

### Little script to submit all necessary ntuplization jobs for the 2016 ZZ analysis
###     Specify an identifier for the jobs (e.g. 18JAN2016_0) and, optionally,
###     which types of ntuples to submit. Options are --data, --mc, --zz, --zl, and --z,
###     or a combination, for running data, monte carlo, 4l final states, 3l final states,
###     and 2l final states; e.g., --data --zz --zl would run only 4l and 3l final states
###     for data, no 2l final states and no monte carlo. If none of those are specified, 
###     all are run


if [ "$1" == "" ] || [ "$1" == "-h" ] || [ "$1" == "--help" ]
then
    echo "$0 usage: ./$0 [-h|--help] id [--data] [--mc] [--zz] [--zl] [--z]"
    echo "    id: string identifying this set of ntuples, e.g. a date."
    echo "    --[data/mc]: run only on data/mc."
    echo "    --[zz/zl/z]: run only 4l/3l/2l ntuples. More than one may be specified."
    exit 1
fi

ID="$1"
shift

while [ "$1" ]
do
    case "$1" in
        --data)
            DATA=1
            ;;
        --mc)
            MC=1
            ;;
        --zz)
            ZZ=1
            ;;
        --zl)
            ZL=1
            ;;
        --z)
            Z=1
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
    
    shift
done

if [ "$DATA" == '' ] && [ "$MC" == '' ]
then
    DATA=1
    MC=1
fi

if [ "$ZZ" == '' ] && [ "$ZL" == '' ] && [ "$Z" == '' ]
then
    ZZ=1
    ZL=1
    Z=1
fi

# Check to make sure we're in the right directory to run this
ELESS=$( ls | grep make_ntuples_cfg.py )
if [ ! "$ELESS" ]
then
    echo "Please go into the correct NtupleTools/test directory"
    exit 1
fi

# Check for a valid voms proxy (not a perfect check; just makes sure there's
# regular output from voms-proxy-info but no error output.
VOMS_OUT=$( voms-proxy-info 2> /dev/null )
VOMS_ERR=$( voms-proxy-info 2>&1 > /dev/null )
if [ ! "$VOMS_OUT" ] || [ "$VOMS_ERR" ]
then
    echo 'Something is wrong with your VOMS proxy -- please renew it or check it'
    exit 1
fi

if [ "$DATA" ]
then
    
    if [ "$ZZ" ]
    then
        echo Submitting ZZ Data Ntuples as ZZNTUPLES_DATA_2015silver_"$ID"

        submit_job.py ZZNTUPLES_DATA_2015silver_"$ID" make_ntuples_cfg.py channels='zz' paramFile="$CMSSW_VERSION"/src/FinalStateAnalysis/NtupleTools/python/parameters/zz.py isMC=0 hzz=1 eCalib=1 use25ns=1 --data --das-replace-tuple=/afs/cern.ch/user/n/nawoods/fsa7416p2/src/FinalStateAnalysis/MetaData/tuples/MiniAOD-13TeV_Data.json --apply-cmsRun-lumimask --silver --samples "data_MuonEG*25ns" "data_SingleElectron*25ns" "data_Double*25ns" --extra-usercode-files 'src/ZZMatrixElement/MEKD/src/Cards' 'src/ZZMatrixElement/MEKD/src/PDFTables' 'src/FinalStateAnalysis/NtupleTools/python/parameters' --output-dir=. -o /data/nawoods/zzntuples_data_2015silver_"$ID".sh

        nohup bash /data/nawoods/zzntuples_data_2015silver_"$ID".sh &
    fi

    if [ "$ZL" ]
    then
        echo Submitting Z+L Data Ntuples as ZPLUSL_DATA_2015gold_"$ID"

        submit_job.py ZPLUSL_DATA_2015gold_"$ID" make_ntuples_cfg.py channels='eee,eem,emm,mmm' paramFile="$CMSSW_VERSION"/src/FinalStateAnalysis/NtupleTools/python/parameters/zz.py isMC=0 hzz=1 eCalib=1 use25ns=1 --data --das-replace-tuple=/afs/cern.ch/user/n/nawoods/fsa7416p2/src/FinalStateAnalysis/MetaData/tuples/MiniAOD-13TeV_Data.json --apply-cmsRun-lumimask --samples "data_MuonEG*25ns" "data_SingleElectron*25ns" "data_Double*25ns" --extra-usercode-files 'src/ZZMatrixElement/MEKD/src/Cards' 'src/ZZMatrixElement/MEKD/src/PDFTables' 'src/FinalStateAnalysis/NtupleTools/python/parameters' --output-dir=. -o /data/nawoods/zplusl_data_2015gold_"$ID".sh

        nohup bash /data/nawoods/zplusl_data_2015gold_"$ID".sh &
    fi

    if [ "$Z" ]
    then
        echo Submitting Single Z Data Ntuples as SINGLEZ_DATA_2015silver_"$ID"

        submit_job.py SINGLEZ_DATA_2015silver_"$ID" make_ntuples_cfg.py channels='ee,mm' paramFile="$CMSSW_VERSION"/src/FinalStateAnalysis/NtupleTools/python/parameters/zz.py isMC=0 hzz=1 eCalib=1 use25ns=1 --data --das-replace-tuple=/afs/cern.ch/user/n/nawoods/fsa7416p2/src/FinalStateAnalysis/MetaData/tuples/MiniAOD-13TeV_Data.json --apply-cmsRun-lumimask --silver --samples "data_Double*25ns" --extra-usercode-files 'src/ZZMatrixElement/MEKD/src/Cards' 'src/ZZMatrixElement/MEKD/src/PDFTables' 'src/FinalStateAnalysis/NtupleTools/python/parameters' --output-dir=. -o /data/nawoods/singlez_data_2015silver_"$ID".sh

        nohup bash /data/nawoods/singlez_data_2015silver_"$ID".sh &
    fi
fi

if [ "$MC" ]
then
    
    if [ "$ZZ" ]
    then
        echo Submitting ZZ MC Ntuples as ZZNTUPLES_MC_"$ID"

        submit_job.py ZZNTUPLES_MC_"$ID" make_ntuples_cfg.py channels='zz' paramFile="$CMSSW_VERSION"/src/FinalStateAnalysis/NtupleTools/python/parameters/zz.py isMC=1 hzz=1 eCalib=1 use25ns=1 --campaign-tag="RunIISpring15MiniAODv2-74X_mcRun2_asymptotic_v2-v*" --samples "ZZTo4L*powheg*" "GluGluToZZTo*" "DYJetsToLL_M-10to*" "DYJetsToLL_M-50_T*amcatnlo*" "WZTo3LNu*" "TTJets_TuneCUET*amcatnlo*" "WWZ*" "WZZ*" "ZZZ*" "GluGluHToZZTo4L_M125*" --extra-usercode-files 'src/ZZMatrixElement/MEKD/src/Cards' 'src/ZZMatrixElement/MEKD/src/PDFTables' 'src/FinalStateAnalysis/NtupleTools/python/parameters' --output-dir=. -o /data/nawoods/zzntuples_mc_"$ID".sh

        nohup bash /data/nawoods/zzntuples_mc_"$ID".sh &
    fi

    if [ "$ZL" ]
    then
        echo Submitting Z+L Data Ntuples as ZPLUSL_MC_"$ID"

        submit_job.py ZPLUSL_MC_"$ID" make_ntuples_cfg.py channels='eee,eem,emm,mmm' paramFile="$CMSSW_VERSION"/src/FinalStateAnalysis/NtupleTools/python/parameters/zz.py isMC=1 hzz=1 eCalib=1 use25ns=1 --campaign-tag="RunIISpring15MiniAODv2-74X_mcRun2_asymptotic_v2-v*" --samples "ZZTo4L*powheg*" "GluGluToZZTo*" "DYJetsToLL_M-10to*" "DYJetsToLL_M-50_T*amcatnlo*" "WZTo3LNu*" "TTJets_TuneCUET*amcatnlo*" --extra-usercode-files 'src/ZZMatrixElement/MEKD/src/Cards' 'src/ZZMatrixElement/MEKD/src/PDFTables' 'src/FinalStateAnalysis/NtupleTools/python/parameters' --output-dir=. -o /data/nawoods/zplusl_mc_"$ID".sh

        nohup bash /data/nawoods/zplusl_mc_"$ID".sh &
    fi

    if [ "$Z" ]
    then
        echo Submitting Single Z Data Ntuples as SINGLEZ_MC_"$ID"

        submit_job.py SINGLEZ_MC_"$ID" make_ntuples_cfg.py channels='ee,mm' paramFile="$CMSSW_VERSION"/src/FinalStateAnalysis/NtupleTools/python/parameters/zz.py isMC=1 hzz=1 eCalib=1 use25ns=1 --campaign-tag="RunIISpring15MiniAODv2-74X_mcRun2_asymptotic_v2-v*" --samples "ZZTo4L*powheg*" "GluGluToZZTo4[em]*" "GluGluToZZTo2e2m*" "DYJetsToLL_M-10to*" "DYJetsToLL_M-50_T*amcatnlo*" "WZTo3LNu*" "TTJets_TuneCUET*amcatnlo*" --extra-usercode-files 'src/ZZMatrixElement/MEKD/src/Cards' 'src/ZZMatrixElement/MEKD/src/PDFTables' 'src/FinalStateAnalysis/NtupleTools/python/parameters' --output-dir=. -o /data/nawoods/singlez_mc_"$ID".sh

        nohup bash /data/nawoods/singlez_mc_"$ID".sh &
    fi
fi