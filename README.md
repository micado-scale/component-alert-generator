# MiCADO alert-generator component

This component used to generate Prometheus rules for scaling docker services since MiCADO 0.3.1.

# Usage

The generator can be configured through environment variables and uses docker volumes.

## ENV

* CONTAINER_SCALING_FILE: /var/lib/micado/alert-generator/scaling_policy.yaml
Set the path of the scaling_policy.yaml file inside the container.

* ALERTS_FILE_PATH: /etc/prometheus/
Set the path of the Prometheus rules inside the container.

* AUTO_GENERATE_ALERT: 'True'
Auto generate rules to every docker service which non defined in the scaling_policy file. (True/False)

* DEFAULT_SCALEUP: 90
The scale up parameter for the auto generated rules if AUTO_GENERATE_ALERT is True.

* DEFAULT_SCALEDOWN: 10
The scale down parameter for the auto generated rules if AUTO_GENERATE_ALERT is True.

* PROMETHEUS: localhost
The address of Prometheus.

## Volumes 

The generator needs the following volumes:

* /var/run/docker.sock:/var/run/docker.sock
The host docker socket for list docker services.

* /etc/prometheus/:/etc/prometheus/
For the generated Prometheus rules.
 
* /var/lib/micado/alert-generator/:/var/lib/micado/alert-generator/
For the input scaling policy file.