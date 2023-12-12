# https://developers.home-assistant.io/docs/add-ons/configuration#add-on-dockerfile
ARG BUILD_FROM
FROM $BUILD_FROM

ARG PIXLET_VERSION BUILD_ARCH

COPY scripts /scripts/
RUN chmod a+x -R /scripts/*

# Add shortcuts to .bashrc so if/when user enters container, they're loaded
RUN echo "#!/usr/bin/with-contenv bashio" >> /root/.bashrc
RUN echo "" >> /root/.bashrc
RUN echo "export PATH=$PATH:/usr/bin/pixlet" >> /root/.bashrc
RUN echo "export PIXLET_FILES_DIR=/config/addons_config/pixlet" >> /root/.bashrc

COPY hello_world.star /root/

RUN mkdir /usr/bin/pixlet
RUN curl -sSLf -o /usr/bin/pixlet/tmp "https://github.com/tidbyt/pixlet/releases/download/v${PIXLET_VERSION}/pixlet_${PIXLET_VERSION}_linux_${BUILD_ARCH}.tar.gz"
RUN tar -zxf /usr/bin/pixlet/tmp --directory /usr/bin/pixlet
RUN chmod a+x /usr/bin/pixlet/pixlet
RUN rm /usr/bin/pixlet/tmp

CMD [ "source", "/root/.bashrc" ]
CMD [ "/scripts/setup.sh" ]
CMD [ "/scripts/serve.sh" ]