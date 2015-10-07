FROM centos:centos7

MAINTAINER Aaron Weitekamp <aweiteka@redhat.com>

RUN echo -e "[epel]\nname=epel\nenabled=1\nbaseurl=https://dl.fedoraproject.org/pub/epel/7/x86_64/\ngpgcheck=0" > /etc/yum.repos.d/epel.repo

RUN yum install -y --setopt=tsflags=nodocs python-pip gcc && \
    pip install jenkins-job-builder && \
    yum clean all

WORKDIR /jjb

LABEL RUN="docker run -it --rm -v `pwd`:/jjb:Z --net=host --name NAME -e NAME=NAME -e IMAGE=IMAGE IMAGE

ENTRYPOINT ["/usr/bin/jenkins-jobs"]
CMD ["--conf", "config/jenkins-jobs.ini", "--ignore-cache", \
     "update", "--delete-old", "jenkins-jobs.yaml"]

