#!/bin/bash
while getopts s:e:r: flag
do
    case "${flag}" in
        s) START_YEAR=${OPTARG};;
        e) END_YEAR=${OPTARG};;
        r) RESCRAPE=${OPTARG};;
    esac
done
for i in $(seq "${START_YEAR}" "${END_YEAR}")
do
    echo "$i"
    git pull
    python python/scrape_wbb_schedules.py -s $i -e $i
    python python/scrape_wbb_json.py -s $i -e $i -r $RESCRAPE
    git pull
    git add .
    bash scripts/daily_wbb_R_processor.sh -s $i -e $i
done