# MedGPT - Medical Reasoning Model

## Project Description

**Project Name:** MedGPT - Medical Reasoning Model

**Purpose:**  
The MedGPT project focuses on developing and fine-tuning a language model specialized in medical reasoning. The goal is to assist healthcare professionals by providing accurate and contextually relevant answers to medical queries. The project leverages state-of-the-art techniques for model fine-tuning, evaluation, and deployment. The main objectives include improving the model's performance on medical reasoning tasks and providing a robust platform for evaluating and deploying the model in a production environment.

## Prerequisites

### Step 1:
- **Docker:** Ensure Docker is installed on your machine. If not, download and install Docker from Docker's [official website](https://www.docker.com/).
- **Docker Compose:** Install Docker Compose, which usually comes bundled with Docker Desktop.
- **Caution**: The repo might not work for window based system because of the difference in exporting environment variables

### Step 2:
- Clone the repository:
  ```bash
  git clone https://github.com/mrizwank97/MedGPT.git
  cd MedGPT/

### Step 3:
Navigate to the config directory and update the necessary configuration files:
- Groq API Key: Update the Groq API key in the configuration file.
- Weave Configuration: Set your Weave team name and project name in the respective fields.

### Step 4:
To start the application, use the provided shell script:
 ```bash
  ./medgpt.sh up
 ```
This command will start two service containers:
- **Ollama Service:** Handles model inference.
- **FastAPI Service:** Provides an API interface to interact with the model.

Once the services are up, you can interact with the FastAPI server by navigating to:
```bash
http://localhost:8000/docs
```

### Step 5: Evaluation Running
- Look for the container ID associated with "medgpt-web".
- Access the container’s shell:
```bash
docker exec -it container_id bash
```
- Once inside the container, run the evaluation script:
```bash
python evaluator.py
```
- **Weave Login:** Since the evaluator uses Weave for tracking, you may need to log using below command. In config directory, change the entity to your W & B organization 
```bash
wandb login
```
### Step 5:
To stop the running services, you can bring down the Docker containers:
```bash
./medgpt.sh down
```
## Model Selection
Google **Gemma 2b** model. Gemma 2 is the new suite of open models launched by Google. Gemma 2 2B model showcases its exceptional conversational AI prowess by outperforming all GPT-3.5 models on the Chatbot Arena at a size runnable on edge devices.
-	Gemma 2 shares a similar architectural foundation with the original Gemma models, including the implementation of Rotary Positioning Embeddings (RoPE) and the approximated GeGLU non-linearity. However, it introduces novel architectural innovations that set it apart from its predecessors.
-	Gemma 2B is trained on 3T tokens of primarily-English data from web documents, mathematics, and code. 
-	2B and 9B models were trained with knowledge distillation from the larger model (27B).
-	In the self-attention mechanism, Gemma 2 uses Grouped Query Attention (GQA). Replacing Mulit-headed attention with Grouped query attention (GQA) results in comparable performance while offering parameter efficiency and faster inference times, making GQA the preferred choice.
-	Another significant distinction is the inclusion of additional RMSNorm in Gemma 2, which enhances the stability of the training process.
-	Instead of considering all words in a text at once, it sometimes focuses on a small window of words (local attention) and sometimes considers all words (global attention). This combination helps the model understand both the immediate context and the overall meaning of the text efficiently.
-	**Ollama** can load the quantized finetuned model and run it for inference, providing a streamlined pipeline from fine-tuning to deployment.

## Model Finetuning
### Dataset
The chosen dataset for this task is **"mamachang/medical-reasoning"** from HuggingFace, which contains approximately 3,700 instructions.
### Preprocessing:
-	Tokenization: The text data was tokenized into a suitable format for input into the model. Special tokens like <start_of_turn>, <end_of_turn>, user, and model were added to structure the conversational format. 
-	Formatting: Two custom functions, generate_prompt and generate_output_prompt, were written to prepare the data for training and inference respectively. These functions ensure that the model receives the input in a consistent and logical format, reflecting the structure of the medical reasoning tasks.
-	The "mamachang/medical-reasoning" dataset was selected due to its focus on medical instructions, which aligns with the task of developing a model capable of handling medical reasoning scenarios. The dataset's size and variety of instructions make it ideal for fine-tuning a model to improve its performance in this specialized area.
### Finetune:
-	The google colab was utilized to finetune gemma 2b model for medical reasoning.
-	Unsloth Library: The Unsloth library was used for finetuning due to its efficiency in reducing memory requirements by half. This library leverages Triton to optimize computation, making it ideal for finetuning large models with limited resources.
-	Quantization Technique: A variant of QLoRA was used along with RSLoRA, which adjusts the scaling factor to the square root of the rank rather than the rank itself. This approach helps in better managing the model's parameters during fine-tuning, leading to improved performance with reduced computational overhead.
-	Training Prompts: The generate_prompt function creates the full conversational input, including both the instruction and expected output. This function is used to prepare data points for training
-	Inference Prompts: The generate_output_prompt function generates the input text without the model's output, allowing the model to predict the response during inference.

## Quantization
After the model has been finetuned, Quantization was need to run the model on local machine. I have **Macboook M1 with 8 GB** of memory with no gpu. So, I had to look for quantization formats that support inference on CPUs. GGUF (Generalized Generic Unified Format) is a format that supports efficient model loading and inference across various frameworks.
-	The q4_k_m method is a specific quantization technique that compresses the model weights to 4-bit while maintaining high accuracy. This is particularly useful in scenarios where reducing model size and inference time is critical. 
-	Unsloth python library supports direct export to the GGUF format, which streamlines the quantization process.
-	After exporting, the GGUF model file can be utilized by Ollama. Ollama is a platform that allows for efficient model inference using the GGUF format.
### Step for pushing model to Ollama:
- Use buil-in function of Unsloth to merge the finetuned adapter and save the LLM in GGUF format
```bash
model.save_pretrained_gguf("model", tokenizer, quantization_method = "q4_k_m")
```
- Create a Modelfile with following content
```bash
FROM unsloth.Q4_K_M.gguf
TEMPLATE """<start_of_turn>user
{{ if .System }}{{ .System }} {{ end }}{{ .Prompt }}<end_of_turn>
<start_of_turn>model
{{ .Response }}<end_of_turn>"""
SYSTEM """You are a MedGPT. You provide analysis to the case and give the diagnoses among the 4 diseases mentioned"""
```
- use ollama to create and push the model using your ollama username
```bash
ollama create medgpt -f Modelfile
ollama push mrizank97/medgpt
```


## Model Evaluation 
### Evaluation Setup:
-	**Groq Library:** The Groq library was used for this evaluation. Groq provides a inference platform that allows integration with various famous LLMs, making it a suitable choice for this task.
-	**Mixtral 8x7B:** The Mixtral 8x7B model was chosen as the LLM-as-Judge. This model is known for its robust language understanding capabilities, making it ideal for evaluating the nuanced responses required in medical reasoning tasks.
-	subset of **90 questions** from the **"mamachang/medical-reasoning"** dataset was selected for evaluation. These questions were representative of the dataset's complexity and covered a broad range of medical reasoning scenarios.
-	To track the evaluation experiment and provide insights, the Weights and Biases (W&B) Weave package was used. This package allowed for real-time monitoring of the evaluation process, providing a comprehensive view of metrics such as grading scores, response times, and overall model performance

### Evaluation
-	LLM-as-Judge: The evaluation of the fine-tuned model was performed using the LLM-as-Judge technique. This method involves using a large language model to grade the outputs of both the original and finetuned models. The judge model observes both the ground truth (expected answer) and the model responses, then provides a grade based on their accuracy and relevance.
-	Reference-Guided Grading: Refer to ```bash app/config/tester.yaml``` file for prompt used for evaluation. Model was prompted to score on a scale of 1-5.

### Analysis
-	Strengths: The fine-tuned model showed significant improvements in accuracy and relevance compared to the original model. This was particularly evident in complex reasoning tasks where the fine-tuned model provided more precise and contextually appropriate responses. The average scare of non-finetuned model was **2.26** for finetuned model it increases singificantly to **3.91** and is visible in the image below.
![Alt text](images/weave1.png)
- Weave also give tool tool to compare multiple iterations. Using the Weave integration, the evaluation provided detailed insights into where the fine-tuned model outperformed the original and where it still had gaps. 
![Alt text](images/weave2.png)

## API Creation
Framework: The API was implemented using FastAPI, a modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints. FastAPI was chosen for its simplicity, speed, and built-in support for asynchronous operations.
Endpoint:
-	The main endpoint created is /ask.
-	Route: /ask
-	Method: POST
-	Description: This endpoint receives a medical case description along with multiple-choice options (a, b, c, d) for diagnosis. The fine-tuned model (Gemma 2, deployed on Ollama) then provides an analysis and predicts the most appropriate diagnosis.
## API Demonstration
- Lets test one medical case below
```bash
Q:A 45-year-old man comes to the physician for the evaluation of difficulty swallowing that has worsened over the past year. He also reports some hoarseness and generalized bone, muscle, and joint pain. During the past six months, he has had progressive constipation and two episodes of kidney stones. He also reports recurrent episodes of throbbing headaches, diaphoresis, and palpitations. He does not smoke or drink alcohol. He takes no medications. His vital signs are within normal limits. Physical examination and an ECG show no abnormalities. Laboratory studies show calcium concentration of 12 mg/dL, phosphorus concentration of 2 mg/dL, alkaline phosphatase concentration of 100 U/L, and calcitonin concentration of 11 pg/mL (N < 8.8). Ultrasonography of the neck shows hypoechoic thyroid lesions with irregular margins and microcalcifications. Which of the following is the most likely underlying cause of this patient's condition??  {'A': 'Mutated NF1 gene', 'B': 'Exposure to ionizing radiation', 'C': 'Deleted VHL gene', 'D': 'Altered RET proto-oncogene expression', 'E': 'Disrupted menin protein function'}
```
- if you look at the output, the model correctly predicted D option. It can be verified from ```bash app/dataset/test_data_gemma.csv```. This is the first row of from the csv file. 
![Alt text](images/fastapi1.png)
![Alt text](images/fastapi2.png)