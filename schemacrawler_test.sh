docker run \
--rm -it --network=host \
-v "$(pwd):/home/schcrwlr" \
schemacrawler/schemacrawler:v16.19.7 \
/opt/schemacrawler/bin/schemacrawler.sh \
--server=postgresql \
--host=127.0.0.1 \
--user=postgres \
--password= \
--database=detections \
--info-level=standard \
--command=schema \
--output-file=schema_postgres.png \
