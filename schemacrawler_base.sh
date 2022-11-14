docker run \
-v "$(pwd)/output_folder/":/home/schcrwlr/ \
--rm -it \
schemacrawler/schemacrawler \
/opt/schemacrawler/schemacrawler.sh \
--server=sqlite \
--database=validation.db \
--info-level=standard \
--command=schema \
--output-file=output2.png
