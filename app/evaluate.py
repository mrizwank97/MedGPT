import re
import json
import time
import weave
import random
from setup import get_client
from weave.flow.scorer import Scorer


def try_read_json2(str_json):
    try:
        str_json = str(str_json)  # We may received an exception not a string !
        data = json.loads(str_json)
        return data
    except Exception as e:
        try:
            str_json = str(str_json)
            print("error in json loads in read_json2, trying to fix...", e)
            # print(repr(str_json))
            str_json = re.sub(r"\s+", " ", str_json)
            start_index = str_json.find('"score":') + len('"score":')
            end_index = str_json.find(",", start_index)
            if end_index == -1:
                end_index = str_json.find("}", start_index)
            score_str = str_json[start_index:end_index].strip()
            score = int(score_str)

            start_index = str_json.find('"explanation":') + len('"explanation":')
            explanation_str = str_json[start_index:]

            explanation_str = explanation_str.replace("}", "")
            explanation_str = explanation_str.replace("'", "")
            explanation_str = explanation_str.replace('"', "")
            explanation_str = explanation_str.replace("\n", "")
            explanation_str = explanation_str.replace("\\", "")
            # chain =f'{{"score":"{score}","explanation":"{explanation_str}"}}'
            chain = {"score": score, "explanation": explanation_str}
            # data = json.loads(chain)
            return chain
        except Exception as e:
            print("***** json can not be fixed !!!! ******** ")
            print(f" Error is {e}")
            explanation_str = json.loads(
                '{"score":2.5,"explanation":"**** can not read json correcly! *********"}'
            )
            return explanation_str


##############################
# answer quality/correctness #
##############################
class CorrectnessLLMJudge(Scorer):
    prompt: str
    correctness_llm_config: list

    @weave.op()
    def get_single_judge_eval(
        self, eval_model, llm, model_output, ground_truth
    ) -> dict:
        max_attempts = 6
        base_delay = 6
        dict_ret = {}
        for attempt in range(max_attempts):  # needed because of groq restriction
            try:
                if any(
                    model in llm["model_name"]
                    for model in ("gpt-35-turbo", "mixtral-8x7b-32768")
                ):
                    messages = [
                        {
                            "role": "system",
                            "content": self.prompt.format(
                                answer=model_output, ground_truth=ground_truth
                            ),
                        }
                    ]

                    response = eval_model.send_message(prompt=messages)
                    if response.choices[0].finish_reason == "stop":
                        generated = response.choices[0].message.content
                        score_dict = try_read_json2(generated)
                        dict_ret[f"score_{llm['model_name']}"] = score_dict["score"]
                        dict_ret[f"explanations_{llm['model_name']}"] = score_dict[
                            "explanation"
                        ]
                        return dict_ret
                    else:
                        print("PROBLEM is: ", response.choices[0].finish_reason)
                        return None

            except Exception as e:
                if "429" in str(e) or "Rate limit reached" in str(e):
                    delay = base_delay * 2**attempt
                    jitter = random.uniform(0, delay * 0.2)
                    wait_time = delay + jitter
                    print(
                        f"Rate limit reached in Correctness judge, waiting {wait_time:.2f} seconds before retrying..."
                    )
                    time.sleep(wait_time)
                else:  # could be an error 400 from groq...
                    print(f"Problem detected in correctness {e}")
                    score_dict = try_read_json2(e)
                    dict_ret[f"score_{llm['model_name']}"] = score_dict["score"]
                    dict_ret[f"explanations_{llm['model_name']}"] = score_dict[
                        "explanation"
                    ]
                    return dict_ret

    @weave.op()
    async def score(self, model_output: str, input: str, output: str) -> dict:
        total_score = 0
        eval_sum = {}
        num_llms = len(self.correctness_llm_config)
        for llm in self.correctness_llm_config:
            eval_model = get_client(
                chat_model=llm["model_name"],
                temperature=llm.get("temperature", ""),
                max_tokens=2000,
                stream=False,
                top_p=1,
                chat_stop=None,
            )

            gen_answer = self.get_single_judge_eval(
                eval_model, llm, model_output, output
            )
            if gen_answer is not None:
                total_score += gen_answer.get(f"score_{llm['model_name']}", 0)
                eval_sum.update(gen_answer)
            else:
                num_llms -= 1  # Adjust number of LLMs if there was a problem
        print(f"total score is {total_score}")
        average_score = total_score / num_llms if num_llms > 0 else None
        if average_score is not None:
            eval_sum["average_score"] = average_score
            return eval_sum
