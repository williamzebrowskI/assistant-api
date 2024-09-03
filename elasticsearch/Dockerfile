FROM docker.elastic.co/elasticsearch/elasticsearch:8.15.0

USER root

COPY elasticsearch/config/elasticsearch.yml /usr/share/elasticsearch/config/elasticsearch.yml
COPY elasticsearch/elasticsearch.sh /usr/src/app/scripts/elasticsearch.sh
RUN chmod +x /usr/src/app/scripts/elasticsearch.sh

USER elasticsearch

CMD ["/bin/bash", "-c", "/usr/src/app/scripts/elasticsearch.sh && exec /usr/local/bin/docker-entrypoint.sh"]