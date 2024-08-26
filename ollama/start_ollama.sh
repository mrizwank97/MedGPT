./bin/ollama serve &

pid=$!

sleep 3

echo "Pulling MedGPT"
ollama run qwen2:0.5b &
#ollama pull mrizwank97/medgpt:latest

wait $pid