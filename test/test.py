from app.app import app
from fastapi.testclient import TestClient


client = TestClient(app)


def ask_gemma():
    model_name = "mrizwank97/medgpt"
    input1 = "Q:An 8-month-old boy is brought to a medical office by his mother. The mother states that the boy has been very fussy and has not been feeding recently. The mother thinks the baby has been gaining weight despite not feeding well. The boy was delivered vaginally at 39 weeks gestation without complications. On physical examination, the boy is noted to be crying in his mother’s arms. There is no evidence of cyanosis, and the cardiac examination is within normal limits. "
    input2 = "The crying intensifies when the abdomen is palpated. The abdomen is distended with tympany in the left lower quadrant. You suspect a condition caused by the failure of specialized cells to migrate. What is the most likely diagnosis?? {'A': 'Meckel diverticulum', 'B': 'DiGeorge syndrome', 'C': 'Pyloric stenosis', 'D': 'Duodenal atresia', 'E': 'Hirschsprung disease'},"
    response = client.get(
        "/ask", params={"model": model_name, "prompt": input1 + input2}
    )
    print(response.json())
    assert "response" in response.json()
    assert response.status_code == 200


def ask_qwent_throws_error():
    model_name = "qwen2:0.5b"
    input1 = "Q:An 8-month-old boy is brought to a medical office by his mother. The mother states that the boy has been very fussy and has not been feeding recently. The mother thinks the baby has been gaining weight despite not feeding well. The boy was delivered vaginally at 39 weeks gestation without complications. On physical examination, the boy is noted to be crying in his mother’s arms. There is no evidence of cyanosis, and the cardiac examination is within normal limits. "
    input2 = "The crying intensifies when the abdomen is palpated. The abdomen is distended with tympany in the left lower quadrant. You suspect a condition caused by the failure of specialized cells to migrate. What is the most likely diagnosis?? {'A': 'Meckel diverticulum', 'B': 'DiGeorge syndrome', 'C': 'Pyloric stenosis', 'D': 'Duodenal atresia', 'E': 'Hirschsprung disease'},"
    response = client.get(
        "/ask", params={"model": model_name, "prompt": input1 + input2}
    )
    assert "error" in response.json()
    assert response.status_code == 200
