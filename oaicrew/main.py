#!/usr/bin/env python
import json
import os
import subprocess
import sys
import requests
import warnings

from datetime import datetime

from oaicrew.crew import Oaicrew

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information
API_URL = "http://localhost:8081/task/index/"
def run():
    """
    Run the crew.
    """
    for index in range(1,31):
        api_url = f"{API_URL}{index}"
        print(f"Fetching test case {index} from {api_url}")
        start_dir = os.getcwd()     #get current working directory
        repo_dir = os.path.join(start_dir, f"repos\\repo_{index}")
        LOG_FILE = start_dir + "\\crewLog.txt"
        print(f"{start_dir}      {repo_dir}")
        try:
            responseJSON = requests.get(f"{api_url}").json()
            taskNumber = responseJSON['taskNumber']
            instance_id = responseJSON['instance_id']
            prompt = responseJSON["Problem_statement"]
            git_clone = responseJSON["git_clone"]
            fail_to_pass = json.loads(responseJSON.get("FAIL_TO_PASS","[]"))
            pass_to_pass = json.loads(responseJSON.get("PASS_TO_PASS","[]"))
            print("\n-<Task Number>-------------------------------\n")
            print(taskNumber)
            print("\n-<Instance ID>-------------------------------\n")
            print(instance_id)
            print("\n-<Problem Statement>-------------------------\n")
            print(prompt)
            print("\n-<Git Clone>---------------------------------\n")
            print(git_clone)
            print("\n-<Fail to Pass>------------------------------\n")
            print(fail_to_pass)
            print("\n-<Pass to Pass>------------------------------\n")
            print(pass_to_pass)

            # Extract repo URL and commit hash
            parts = git_clone.split("&&")
            clone_part = parts[0].strip()
            checkout_part = parts[-1].strip() if len(parts) > 1 else None
            repo_url = clone_part.split()[2]
            print(f"Cloning repository {repo_url} into {repo_dir}...")
            env = os.environ.copy()
            env["GIT_TERMINAL_PROMT"] = "0"
            subprocess.run(["git", "clone", repo_url, repo_dir], check=True, env= env)

            if checkout_part:
                commit_hash = checkout_part.split()[-1]
                print(f"Checking out commit: {commit_hash}")
                subprocess.run(["git", "checkout", commit_hash], cwd=repo_dir, check=True, env=env)

        except:
            raise Exception("Invalid response")

        inputs = {
            'index': index,
            'prompt': prompt # type: ignore
        }

        try:
            kik = Oaicrew().crew().kickoff(inputs=inputs)
            tokens = kik.token_usage
            print(kik.token_usage)

            print(f"Calling SWE-Bench REST service with repo: {repo_dir}")
            test_payload = {
                "instance_id": instance_id, # type: ignore
                "repoDir" : f"/repos/repo_{index}",  # mount with docker?
                "FAIL_TO_PASS" : fail_to_pass, # type: ignore
                "PASS_TO_PASS" : pass_to_pass, # type: ignore
            }
            print(test_payload)
            result = requests.post("http://localhost:8082/test", json=test_payload)
            result.raise_for_status()
            print(f"benchresponse: {result.content}")
            if len(result.json()) == 1:
                os.chdir(start_dir)
                with open(LOG_FILE, "a", encoding="utf-8") as log:
                    log.write(f"\n---< TESTCASE {index} >------------")
                    log.write(f"\nFailed to make any changes to the repository or")
                    log.write("\nencountered errors during evaluation")
                    log.write(f"\nTotal Tokens used: {tokens.total_tokens}")
                print(f"Test case {index} unchanged and logged")
            else:
                result_raw = result.json().get("harnessOutput", "{}")
                result_json = json.loads(result_raw)
                if not result_json:
                    print(f"BenchResponseError: {result.json().get("error")}")
                    raise ValueError(f"No data in harnessOutput - possible evaluation error\nTotal Tokens used: {tokens.total_tokens}")
                print(result_json)
                instance_id = next(iter(result_json))
                tests_status = result_json[instance_id]["tests_status"]
                fail_pass_results = tests_status["FAIL_TO_PASS"]
                fail_pass_passed = len(fail_pass_results["success"])
                fail_pass_total = fail_pass_passed + len(fail_pass_results["failure"])
                pass_pass_results = tests_status["PASS_TO_PASS"]
                pass_pass_passed = len(pass_pass_results["success"])
                pass_pass_total = pass_pass_passed + len(pass_pass_results["failure"])

                # log results
                os.chdir(start_dir)
                with open(LOG_FILE, "a", encoding="utf-8") as log:
                    log.write(f"\n---< TESTCASE {index} >------------")
                    log.write(f"\nFAIL_TO_PASS passed: {fail_pass_passed}/{fail_pass_total}")
                    log.write(f"\nPASS_TO_PASS passed: {pass_pass_passed}/{pass_pass_total}")
                    log.write(f"\nTotal Tokens used: {tokens.total_tokens}")
                    log.write(f"\nSuccessful requests: {tokens.successful_requests}")
                print(f"Test case {index} completed and logged")
        except Exception as e:
            os.chdir(start_dir)
            with open(LOG_FILE, "a", encoding="utf-8") as log:
                log.write(f"\n---< TESTCASE {index} >------------")
                log.write(f"\nError: {e}")
            print(f"Error in test case {index}: {e}")
            raise e







def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs",
        'current_year': str(datetime.now().year)
    }
    try:
        Oaicrew().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        Oaicrew().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }
    
    try:
        Oaicrew().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")
