import os
import yaml
import weave
import asyncio
import pandas as pd
from dotenv import load_dotenv
from evaluate import CorrectnessLLMJudge


@weave.op()
def function_to_evaluate(model_response: str):
    # here's where you would add your LLM call and return the output
    return {"model_response": model_response}


def main(config, config_eval):
    weave.init(config["entity"] + "/" + config["project_name"])

    df = pd.read_csv("dataset/test_data_gemma.csv")
    dataset = df.to_dict(orient="records")

    evaluation = weave.Evaluation(
        dataset=dataset,
        # dataset = examples_test,
        scorers=[
            CorrectnessLLMJudge(
                prompt=config_eval["relevance_prompt"],
                correctness_llm_config=config_eval["judges"]["correctness_judge"][
                    "llms"
                ],
            ),
        ],
    )
    asyncio.run(evaluation.evaluate(function_to_evaluate))


if __name__ == "__main__":
    # load in configs
    config = {}
    config_eval = {}
    file_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(file_path, "configs/general_config.yaml"), "r") as file:
        config.update(yaml.safe_load(file))

    # load in env vars
    if not load_dotenv(os.path.join(file_path, "configs/benchmark.env")):
        print("Environment variables couldn't be found.")

    # load configs for judges
    with open(os.path.join(file_path, "configs/tester.yaml"), "r") as file:
        config_eval.update(yaml.safe_load(file))

    main(config, config_eval)
