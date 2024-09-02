FROM docker.elastic.co/kibana/kibana:8.15.0

USER root

# Copy your kibana.yml into the container
COPY kibana/kibana.yml /usr/share/kibana/config/kibana.yml

COPY kibana/kibana.sh /usr/src/app/scripts/kibana.sh
RUN chmod +x /usr/src/app/scripts/kibana.sh

USER kibana

CMD ["/usr/src/app/scripts/kibana.sh", "--silent"]