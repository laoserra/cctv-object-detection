docker run \
--mount type=bind,source="$(pwd)",target=/home/schcrwlr \
--rm -it --network=host \
schemacrawler/schemacrawler:v16.19.7 \
/opt/schemacrawler/bin/schemacrawler.sh \
--server postgresql \
--host 127.0.0.1 \
--user postgres \
--password \
--database detections \
--info-level standard \
--command schema \
--output-file output.png
