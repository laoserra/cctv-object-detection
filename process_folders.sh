#!/usr/bin/env bash

# Folder sorting script by Keith Scott, NRS, 16/01/23
# files matching the criteria below will be moved into a newly created daily folder
# since the mv command below has the potential to wreak havoc, be careful with the input array definitions!

export DATETIME=`date +%Y-%m-%d-%H%M`

# input array
declare -A dirs  
dirs[/home/datasci/Work/cctv-object-detection/output_folder]=*.jpg
dirs[/home/datasci/Work/cctv-object-detection/archive_folder]=*.jpg
dirs[/home/datasci/Work/cctv-object-detection/logs]=*.log


for dr in "${!dirs[@]}"; do
  echo Processing directory: $dr  #  e.g. /home/datasci/Work/cctv-object-detection/logs
  cd ${dr}
  tp="${dirs[$dr]}"
  echo Processing type: $tp  #  e.g. *.log
  filter="$dr"/"$tp"
  for x in $filter; do
    d=$(date -r "$x" +%Y-%m-%d)
    if [[ "$dr" == *"cctv-object-detection"* ]]; then  # only permit this operation if we're a subdirectory of cctv-object-detection 
      mkdir -p "$d"
      mv -- "$x" "$d/"
    fi
  done
done
