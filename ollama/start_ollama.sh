./bin/ollama serve &

pid=$!

sleep 5


echo "Pulling llama3 model"
ollama pull qwen2:0.5b

wait $pid