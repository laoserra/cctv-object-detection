docker run \
-v "$(pwd)":/home/schcrwlr \
--rm -it \
schemacrawler/schemacrawler:v16.19.7 \
/opt/schemacrawler/bin/schemacrawler.sh \
--server=postgresql \
--database=detections \
--schemas=public \
--user=postgres \
--password=serra \
--info-level=standard \
--command=schema \
--output-file=detections_schema.png
