#!/bin/bash -x

docker run -d --name origin --privileged --net=host \
    -v /:/rootfs:ro -v /var/run:/var/run:rw \
    -v /sys:/sys:ro -v /var/lib/docker:/var/lib/docker:rw \
    -v /var/lib/openshift/openshift.local.volumes:/var/lib/openshift/openshift.local.volumes openshift/origin start

# wait for OSE to start up
sleep 10

OSE_EXEC="docker exec -it origin openshift"

$OSE_EXEC admin registry --credentials=/var/lib/openshift/openshift.local.config/master/openshift-registry.kubeconfig --config=/var/lib/openshift/openshift.local.config/master/openshift-master.kubeconfig
$OSE_EXEC cli login localhost:8443 -u test -p test --insecure-skip-tls-verify=true
$OSE_EXEC cli new-project test
$OSE_EXEC cli policy add-role-to-user edit system:serviceaccount:test:default
$OSE_EXEC cli create -n test -f https://raw.githubusercontent.com/aweiteka/ose-build-pipeline/master/ose-build-template.yaml
# Creating the app is problematic using redirects in a container exec context
#$OSE_EXEC cli create -f `$OSE_EXEC cli process automated-build -v SOURCE_URI=https://github.com/aweiteka/ose-build-pipeline.git,BASE_DOCKER_IMAGE=openshift/jenkins-1-centos7,BUILD_CONTEXT_DIR=jenkins/master,BUILD_IMAGE_NAME=acmeapp,NAME=acme`

