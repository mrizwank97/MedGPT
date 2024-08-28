from app.app import app
from fastapi.testclient import TestClient


client = TestClient(app)


def test_ask():
    prefix_text = "Below is an instruction that describes a task. Write a response that appropriately completes the request.\n\n"
    instruction = "Please answer with one of the option in the bracket. Write reasoning in between <analysis></analysis>. Write answer in between <answer></answer>."
    input1 = "Q:An 8-month-old boy is brought to a medical office by his mother. The mother states that the boy has been very fussy and has not been feeding recently. The mother thinks the baby has been gaining weight despite not feeding well. The boy was delivered vaginally at 39 weeks gestation without complications. On physical examination, the boy is noted to be crying in his mother’s arms. There is no evidence of cyanosis, and the cardiac examination is within normal limits. "
    input2 = "The crying intensifies when the abdomen is palpated. The abdomen is distended with tympany in the left lower quadrant. You suspect a condition caused by the failure of specialized cells to migrate. What is the most likely diagnosis?? {'A': 'Meckel diverticulum', 'B': 'DiGeorge syndrome', 'C': 'Pyloric stenosis', 'D': 'Duodenal atresia', 'E': 'Hirschsprung disease'},"
    text = f"""<start_of_turn>user {prefix_text} {instruction} here are the inputs {input1+input2} <end_of_turn>\n<start_of_turn>"""
    response = client.get("/ask", params={"prompt": text})
    assert "response" in response.json()
    assert response.status_code == 200
