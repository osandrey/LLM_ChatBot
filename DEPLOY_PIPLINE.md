STEP 1: ```docker build . --platform=linux/amd64 -t osandreyman/llm_chat_bot_backend:0.0.1```
STEP 2: ```docker push osandreyman/llm_chat_bot_backend:0.0.1```
STEP 3: ```sudo docker run -d --name llm_chat_bot_backend  -p 8000:8000 osandreyman/llm_chat_bot_backend:0.0.1```

```Dockerfile changes for front```
CMD ["strimlit", "run", "./src/front_test/main_app.py"]
in browser ```134.122.104.117:8000/docs```