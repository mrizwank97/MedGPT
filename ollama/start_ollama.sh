./bin/ollama serve &

pid=$!

sleep 10

echo "Pulling MedGPT"
#ollama run qwen2:0.5b &
ollama run mrizwank97/medgpt:latest

wait $pid