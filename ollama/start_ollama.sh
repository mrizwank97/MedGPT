./bin/ollama serve &

pid=$!

sleep 10

echo "Pulling MedGPT"
ollama pull mrizwank97/medgpt:latest

wait $pid