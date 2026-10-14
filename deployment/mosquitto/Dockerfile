FROM eclipse-mosquitto:2.0.22

COPY --chown=1883:1883 --chmod=640 mosquitto.conf /mosquitto/config/mosquitto.conf
COPY --chown=1883:1883 --chmod=640 acl /mosquitto/config/acl

USER 1883:1883
CMD ["mosquitto", "-c", "/mosquitto/config/mosquitto.conf"]
