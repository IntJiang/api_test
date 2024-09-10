import sys
import paramiko
import yaml
from csv import DictReader

global server
global name
global password
# global csrf_token
global session
global ssh
global token


def load_config():
    config = read_yaml(sys.path[0] + "test_interface/config.yaml")
    set_server(config["ssm"]["host"])
    set_root_name(config["ssm"]["host"]["login"]["username"])
    set_root_password(config["ssm"]["host"]["login"]["password"])


def load_test_cases():
    cases = read_csv(sys.path[0] + "test_interface/test_cases.csv")
    return cases


def load_token():
    global token
    ssh_connect()
    _, stdout, _ = ssh.exec_command("cat /root/token.txt")
    token = stdout.read().decode()
    ssh_close()


def load_case_ids():
    cases = load_test_cases()
    case_ids = []
    for case in cases:
        case_ids.append(case["id"])
    return case_ids


# Format data from string:
#    period:day
#    startDate:2023-11-01
#    endDate:2023-11-21
# to dictionary:
#   {"period":"day","startDate":"2023-11-01","endDate":"2023-11-21"}
def format_data(data):
    dict1 = {}
    if data != "":
        raws = data.split("\n")
        for raw in raws:
            key = raw.split(":", 1)[0].strip()
            value = raw.split(":", 1)[1].strip()
            dict1[key] = value
    return dict1


def read_yaml(path):
    with open(path) as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
        return data


# Please enter the core path of the csv file.
def read_csv(path):
    with open(path) as file:
        reader = DictReader(file)
        dicts = list(reader)
        return dicts


def get(uri, params=None):
    if params is None:
        params = {}
    return session.get(f'https://{server}:8443{uri}', verify=False, params=params, stream=True)


def post(uri, headers=None, body=None, params=None):
    if params is None:
        params = {"_csrf": f"{csrf_token}"}
    else:
        params["_csrf"] = f"{csrf_token}"
    if body is None:
        body = {}
    return session.post(f'https://{server}:8443{uri}', headers=headers, data=body, params=params, verify=False,
                        stream=True)


def ssh_connect():
    global ssh
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    ssh.connect(server, username=name, password=password)


def ssh_close():
    ssh.close()


# def get_latest_log():
#     ssh_connect()
#     _, stdout, _ = ssh.exec_command("cat /opt/ssm/server/log/java/osa-module-gateway-syslog.log | tail -n 1")
#     return stdout.read().decode()
#
#
# def get_content_id(log):
#     return log.split("contentid=\"", 1)[1]


def set_server(new):
    global server
    server = new


def set_root_name(new):
    global name
    name = new


def set_root_password(new):
    global password
    password = new


# def set_csrf_token(new):
#     global csrf_token
#     csrf_token = new


def set_session(new):
    global session
    session = new


