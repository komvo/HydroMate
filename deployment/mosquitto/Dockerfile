FROM eclipse-mosquitto:2.0.22

# A separate executable path avoids matching the host's mosquitto attachment.
RUN cp /usr/sbin/mosquitto /usr/local/bin/hydromate-mosquitto \
    && chmod 755 /usr/local/bin/hydromate-mosquitto

COPY --chown=1883:1883 --chmod=640 mosquitto.conf /mosquitto/config/mosquitto.conf
COPY --chown=1883:1883 --chmod=640 acl /mosquitto/config/acl

USER 1883:1883
ENTRYPOINT ["/usr/local/bin/hydromate-mosquitto"]
CMD ["-c", "/mosquitto/config/mosquitto.conf"]
