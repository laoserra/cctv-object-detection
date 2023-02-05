docker run \
--mount type=bind,source="$(pwd)",target=/home/schcrwlr \
--rm -it \
schemacrawler/schemacrawler:v16.19.7 \
/opt/schemacrawler/bin/schemacrawler.sh \
--server postgresql \
--host localhost \
--user postgres \
--password pass \
--database detections \
--info-level standard \
--command schema \
--output-file output.png
