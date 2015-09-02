## Jenkins Job Builder Image

Jenkins Job Builder is a tool to manage Jenkins Jobs using a YAML or JSON syntax. [Refer to documentation](http://docs.openstack.org/infra/jenkins-job-builder/quick-start.html) on building your jobs YAML file.

## In Use

1. From the directory with a `jenkins-jobs.yaml` file and a configuration file in `config/jenkins-jobs.ini` run this command to upload Jenkins jobs to a Jenkins master.

        [sudo] atomic run aweiteka/jjb

If you do not have the atomic command or need to run the image in a different way use straight docker and customize as needed:

```
docker run -it --rm -v `pwd`:/jjb:Z --net=host aweiteka/jjb
```
