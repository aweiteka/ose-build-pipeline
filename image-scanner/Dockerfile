FROM centos:centos7

MAINTAINER Aaron Weitekamp <aweiteka@redhat.com>

ADD /*.py /opt/

LABEL RUN="docker run -it --rm --privileged -v /:/host --name NAME -e NAME=NAME -e IMAGE=IMAGE IMAGE

ENTRYPOINT ["/opt/scan.py"]
CMD ["/host"]

