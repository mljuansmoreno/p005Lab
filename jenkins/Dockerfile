FROM jenkins/jenkins:2.580.2-jdk21@sha256:74401de6a6f92e1afe1b02d1c8e3d0c33f263bfb5275dd8813f9150355f2367b
COPY --chown=jenkins:jenkins plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN awk '{print $2 ":" $1}' < /usr/share/jenkins/ref/plugins.txt > /tmp/plugins.txt \
    && jenkins-plugin-cli --plugin-file /tmp/plugins.txt --latest=false \
    && rm /tmp/plugins.txt
COPY --chown=jenkins:jenkins controlador.groovy /usr/share/jenkins/ref/init.groovy.d/controlador.groovy
