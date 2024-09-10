"""
     @author:
         Zixiang Jiang
     @date:
         2024-08-13 14:00:00
"""
import json
import pytest
import requests
from .interface import *


class TestInterface:

    @pytest.fixture(autouse=True)
    def precondition(self):
        load_test_cases()
        load_config()
        load_token()

        set_session(requests.Session())
        r = get("/login")
        set_csrf_token(r.text.split("name=\"_csrf\"", 1)[1].split("\"", 2)[1])

        body = {
            "username": self.webui_resource.ssm.login.username,
            "password": self.webui_resource.ssm.login.password,
        }
        r = post('/login', body=body)
        set_csrf_token(r.text.split("name=\"_csrf\"", 1)[1].split("\"", 2)[1])
        assert r.status_code == 200

        yield get_latest_log()

        ssh_close()

    @pytest.mark.parametrize("case", load_test_cases(), ids=load_case_ids())
    @pytest.mark.caseinfo()
    def test_input_validation(self, precondition, case):
        uri = case["uri"].strip()
        method = case["method"].strip().lower()
        params = format_data(case["params"])

        data_type = case["data_type"]
        body = case["body"]
        headers = {}
        if data_type == "form":
            body = format_data(body)
        elif data_type == "json":
            headers = {"Content-Type": "application/json"}
            js = json.loads(body)
            body = json.dumps(js)

        code = int(case["code"].strip())
        expect_content_id = case["log"].strip().replace("\"", "")
        previous_log = precondition

        if method == "get":
            r = get(uri, params=params)
        elif method == "post":
            r = post(uri, headers=headers, body=body, params=params)
        else:
            assert False
        assert r.status_code == code

        if expect_content_id == "":
            assert previous_log == get_latest_log()
        else:
            current_log = get_latest_log()
            assert previous_log != current_log
            assert get_content_id(current_log).startswith(expect_content_id)
