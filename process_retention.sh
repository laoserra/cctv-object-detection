#!/bin/sh
export DATETIME=`date +%Y-%m-%d-%H%M`

# Note: Methods 1 and 2 can result in "Argument list too long" if too many files, so using method 3

# Delete over 14 days (method 1)
#find /home/datasci/Work/cctv-object-detection/output_folder/*.jpg -type f -mtime +14 -exec rm -f {} \;
#find /home/datasci/Work/cctv-object-detection/archive_folder/*.jpg -type f -mtime +14 -exec rm -f {} \;

# Delete over 14 days (method 2)
#find /home/datasci/Work/cctv-object-detection/output_folder/ -mtime +14 -delete
#find /home/datasci/Work/cctv-object-detection/archive_folder/ -mtime +14 -delete

# Delete over 14 days (method 3)
find /home/datasci/Work/cctv-object-detection/output_folder/ -mindepth 1 -name "*.jpg" -mtime +14 | xargs -0 -r rm -rf
find /home/datasci/Work/cctv-object-detection/archive_folder/ -mindepth 1 -name "*.jpg" -mtime +14 | xargs -0 -r rm -rf


