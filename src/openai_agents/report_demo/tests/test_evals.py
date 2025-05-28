import json, pathlib
from agents import Runner
from planner_report.planner_agent import planner_agent
from planner_report.context import UserContext
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

SAMPLES = pathlib.Path(__file__).with_name("eval_samples.jsonl")

def test_planner_quality():
    ctx = UserContext()
    passed, total = 0, 0
    for line in SAMPLES.read_text().splitlines():
        sample = json.loads(line)
        result = Runner.run_sync( starting_agent= planner_agent,
                                 input= sample["input"],
                                 context= ctx).final_output.lower()
        total += 1
        if all(k.lower() in result for k in sample["ideal"]):
            passed += 1
    pass_rate = passed / total
    assert pass_rate >= 0.9, f"通过率 {passed}/{total} ({pass_rate:.0%}) 低于 90%"
