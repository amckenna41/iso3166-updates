#!/usr/bin/env bash

'''
Shell script that pulls all the latest ISO 3166-2 data for all countries using the two data sources. This script 
calls the get_all_iso3166_updates.py Python script, individally passing in the 2 letter alpha-2 codes one by one.
A random delay is introduced between each script execution to introduce some randomness which is required when 
using Python Selenium. Each countries individual updates are exported to a JSON and then concatenated into 
one JSON. 
'''

#iterate over all script positional arguments 
for i in "$@"
do
case $i in
    --export_filename=*)
    EXPORT_FILENAME="${i#*=}"
    shift # past argument=value
    ;;
    --export_folder=*)
    EXPORT_FOLDER="${i#*=}"
    shift # past argument=value
    ;;
    -h|--h)
    Help
    shift # past argument=value
    ;;
    --default)
    DEFAULT=YES
    shift # past argument with no value
    ;;
    *)
          # unknown option
    ;;
esac
done

if [[ -n $1 ]]; then
    echo "Last line of file specified as non-opt/last argument:"
    tail -1 $1
fi

#set default script variable names if empty
if [ -z "$EXPORT_FILENAME" ]; then
  EXPORT_FILENAME="iso3166-updates.json"
fi
if [ -z "$EXPORT_FOLDER" ]; then
  EXPORT_FOLDER="test-iso3166-updates"
fi

#list of 2 letter alpha-2 ISO 3166 codes
ALL_ISO3166_CODES="AD,AE,AF,AG,AI,AL,AM,AO,AQ,AR,AS,AT,AU,AW,AX,AZ,BA,BB,BD,BE,BF,BG,BH,BI,BJ,BL,BM,BN,BO,BQ,BR,BS,BT,BV,BW,BY,BZ,CA,CC,CD,
CF,CG,CH,CI,CK,CL,CM,CN,CO,CR,CU,CV,CW,CX,CY,CZ,DE,DJ,DK,DM,DO,DZ,EC,EE,EG,EH,ER,ES,ET,FI,FJ,FK,FM,FO,FR,GA,GB,GD,GE,GF,GG,GH,GI,GL,GM,GN,
GP,GQ,GR,GS,GT,GU,GW,GY,HK,HM,HN,HR,HT,HU,ID,IE,IL,IM,IN,IO,IQ,IR,IS,IT,JE,JM,JO,JP,KE,KG,KH,KI,KM,KN,KP,KR,KW,KY,KZ,LA,LB,LC,LI,LK,LR,LS,
LT,LU,LV,LY,MA,MC,MD,ME,MF,MG,MH,MK,ML,MM,MN,MO,MP,MQ,MR,MS,MT,MU,MV,MW,MX,MY,MZ,NA,NC,NE,NF,NG,NI,NL,NO,NP,NR,NU,NZ,OM,PA,PE,PF,PG,PH,PK,
PL,PM,PN,PR,PS,PT,PW,PY,QA,RE,RO,RS,RU,RW,SA,SB,SC,SD,SE,SG,SH,SI,SJ,SK,SL,SM,SN,SO,SR,SS,ST,SV,SX,SY,SZ,TC,TD,TF,TG,TH,TJ,TK,TL,TM,TN,TO,
TR,TT,TV,TW,TZ,UA,UG,UM,US,UY,UZ,VA,VC,VE,VG,VI,VN,VU,WF,WS,XK,YE,YT,ZA,ZM,ZW"

#maximum delay between script execution
MAXWAIT=7

#start execution timer
start=`date +%s`

#iterate over all ISO 3166 alpha-2 codes and run get_all_iso3166_updates.py script to get its updates from data sources, export json to $EXPORT_FOLDER
for i in ${ALL_ISO3166_CODES//,/ }
do
    sleep $((RANDOM % MAXWAIT)) #wait a random number of seconds between country, between 1 and 7 seconds to introduce pseudo randomness
    python3 get_all_iso3166_updates.py --alpha2="$line" --export_filename=$EXPORT_FILENAME --export_folder=$EXPORT_FOLDER --export_json --verbose
done

#concatenate all individual country updates jsons into one 
jq -s 'reduce .[] as $item ({}; . * $item)' $EXPORT_FOLDER/*.json > $EXPORT_FODLER/$EXPORT_FILENAME

#delete individual country jsons in $EXPORT_FODLER, keep concatenated json
find $EXPORT_FOLDER -type f ! -name $EXPORT_FILENAME -delete

#calculate total runtime for script exection
end=`date +%s`
runtime=$((end-start))
echo "Script executed successfully after $runtime seconds."

#Help Funtion showing script usage
Help()
{
   echo "Shell Script for pulling all the latest ISO 3166 updates data from data sources."
   echo ""
   echo "Basic Usage, using default parameters: ./get_all_iso3166_updates "
   echo "Usage: ./get_all_iso3166_updates [--export_filename --export_folder]"
   echo ""
   echo "Options:"
   echo "-h                   help."
   echo "-export_filename     Filename for exported JSON/CSVs files containing updates data (default="iso3166-updates.json")."
   echo "-export_folder       Folder name to store exported JSON/CSVs files containing updates data (default="iso3166-updates")."
   exit
}