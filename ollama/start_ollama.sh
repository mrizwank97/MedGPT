./bin/ollama serve &

pid=$!

sleep 5


echo "Pulling MedGPT"
ollama pull qwen2:0.5b
#ollama pull mrizwank97/medgpt:latest

wait $pid