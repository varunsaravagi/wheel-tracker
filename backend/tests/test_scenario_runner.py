import yaml
import pytest
import re
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from main import app

import os

client = TestClient(app)

SCENARIOS_FILE = os.path.join(os.path.dirname(__file__), "scenarios.yaml")

def load_scenarios(file_path=SCENARIOS_FILE):
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)

def _substitute_variables(data, context):
    """Recursively substitutes variables in the format {{variable.field}}."""
    if isinstance(data, dict):
        return {k: _substitute_variables(v, context) for k, v in data.items()}
    elif isinstance(data, list):
        return [_substitute_variables(i, context) for i in data]
    elif isinstance(data, str):
        for match in re.finditer(r"{{\s*([\w\.]+)\s*}}", data):
            variable_path = match.group(1)
            parts = variable_path.split('.')
            value = context
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    value = None
                    break
            if value is not None:
                # If the string is just the variable, replace it with the value directly
                if data.strip() == match.group(0):
                    return value
                # Otherwise, replace it as a string
                data = data.replace(match.group(0), str(value))
    return data

@pytest.mark.parametrize("scenario", load_scenarios())
def test_scenario(scenario, db_session: Session):
    """Main test function to run a scenario from the YAML file."""
    print(f"Running scenario: {scenario['name']}")
    context = scenario.get('variables', {})

    for step in scenario.get("steps", []):
        print(f"  - Executing step: {step.get('name', 'Unnamed Step')}")
        
        # Substitute variables in the current step
        current_step = _substitute_variables(step, context)
        
        action_response = _execute_action(current_step, context)

        if 'save_as' in current_step:
            context[current_step['save_as']] = action_response

        _process_expectations(current_step, action_response, context)

def _execute_action(step, context):
    """Executes the action defined in a step."""
    action = step["action"]
    
    if action == "new_trade":
        response = client.post("/api/trades/", json=step["payload"])
        assert response.status_code == 200
        return response.json()
        
    elif action == "assign":
        response = client.put(f"/api/trades/{step['trade_id']}/assign")
        assert response.status_code == 200
        return response.json()

    elif action == "expire":
        response = client.put(f"/api/trades/{step['trade_id']}/expire")
        assert response.status_code == 200
        return response.json()

    elif action == "verify_state":
        # This is a read-only action, it doesn't have its own response
        return None
        
    else:
        raise ValueError(f"Unknown action: {action}")

def _process_expectations(step, action_response, context):
    """Processes the expectations for a step."""
    if "expectations" not in step:
        return

    for expectation in step["expectations"]:
        exp_type = expectation["type"]
        exp_value = expectation["value"]

        if exp_type == "premium_received":
            assert action_response["premium_received"] == pytest.approx(exp_value)
            
        elif exp_type == "net_premium":
            assert action_response["net_premium_received"] == pytest.approx(exp_value)

        elif exp_type == "cumulative_pnl":
            response = client.get(f"/api/cumulative_pnl/{step['ticker']}")
            assert response.status_code == 200
            actual_pnl = response.json()["cumulative_pnl"]
            assert actual_pnl == pytest.approx(exp_value)
            
        else:
            raise ValueError(f"Unknown expectation type: {exp_type}")
