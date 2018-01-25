import os
import ruamel.yaml as yaml
import docker
import time
import requests

yaml.default_flow_style = False


def read_container_policy(container_scaling_file):
    container_scaling_file = os.getenv(container_scaling_file,
                                       '/var/lib/micado/alert-generator/scaling_policy.yaml')
    with open(container_scaling_file, 'r') as f:
        scaling_policy = yaml.round_trip_load(f, preserve_quotes=True)
        return scaling_policy


def generate_alert(service_name, scaleup, scaledown, duration):
    s = ""
    s += str("ALERT {0}_overloaded\n".format(service_name))
    s += str("IF avg(rate(container_cpu_usage_seconds_total"
             "{{container_label_com_docker_swarm_service_name="'"{0}"'"}}[30s]))*100 > {1}\n".format(service_name, scaleup))
    s += str("FOR {0}\n".format(duration))
    s += str("LABELS {{alert="'"overloaded"'", type="'"docker"'", application="'"{0}"'"}}\n".format(service_name))
    s += str("ANNOTATIONS {summary = "'"overloaded"'"}\n"+"\n")

    s += str("ALERT {0}_underloaded\n".format(service_name))
    s += str("IF avg(rate(container_cpu_usage_seconds_total"
             "{{container_label_com_docker_swarm_service_name="'"{0}"'"}}[30s]))*100 < {1}\n".
             format(service_name,scaledown))
    s += str("FOR {0}\n".format(duration))
    s += str("LABELS {{alert="'"underloaded"'", type="'"docker"'", application="'"{0}"'"}}\n".format(service_name))
    s += str("ANNOTATIONS {summary = "'"underloaded"'"}\n")
    return s


client = docker.from_env()

while True:
    # Get alerts, policies and services
    alerts = []
    alert_files_dir = os.getenv('ALERTS_FILE_PATH', '/etc/prometheus/')
    for file in os.listdir(alert_files_dir):
        if file.endswith(".rules"):
            alerts.append(file[:-6])

    try:
        container_scaling_policy = read_container_policy('CONTAINER_SCALING_FILE')
    except IOError:
        print("No scaling policy file. Only default alerts will be generated.")

    service_list = client.services.list()

    auto_generate_alerts = os.getenv('AUTO_GENERATE_ALERT', 'True') in ('True', 'true')
    # Generate alerts
    for i in service_list:
        if i.name not in alerts:
            if i.name in container_scaling_policy.get("services"):
                # Create rules with described parameters
                with open("{0}{1}.rules".format(alert_files_dir, i.name), "w") as file:
                    file.write(generate_alert(i.name, container_scaling_policy.get("services").get(i.name).get("scaleup"),
                                              container_scaling_policy.get("services").get(i.name).get("scaledown"), "30s"))
                print("Generated {0}.rules with specified parameters.".format(i.name))
            elif auto_generate_alerts:
                # Create rule with default parameter
                with open("{0}{1}.rules".format(alert_files_dir, i.name), "w") as file:
                    file.write(generate_alert(i.name, os.getenv('DEFAULT_SCALEUP', '90'),
                                              os.getenv('DEFAULT_SCALEDOWN', '10'), "30s"))
                print("Generated {0}.rules with default parameters.".format(i.name))

    # Remove old alerts
    for i in alerts:
        j = 0
        while (j < len(service_list)) and (i != service_list[j].name):
            j += 1
        if i != "prometheus":
            if len(service_list) == 0:
                os.remove(alert_files_dir + i + ".rules")
                print("{0} alert is removed.".format(i))
            elif j == len(service_list):
                os.remove(alert_files_dir + i + ".rules")
                print("{0} alert is removed.".format(i))

    try:
        requests.post("http://{0}:9090/-/reload".format(os.getenv('PROMETHEUS', 'localhost')))
        print("Alerts reload in Prometheus.")
    except requests.ConnectionError:
        print("Prometheus is unreachable.")

    time.sleep(10)
