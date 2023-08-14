# Iris (fork of HowdoI.ai) is a reference implementation of a data augmented generative AI.

This is an experiment in building a large-language-model-backed chatbot. It can hold a conversation, remember previous comments/questions, and answer all types of queries (history, web search, movie data, weather, news, and more).

This app relies on the amazing [LangChain Python library](https://langchain.readthedocs.io/en/latest/index.html), which powers all the interesting AI stuff.


## Getting API Keys 

For those who want to use this to it's fullest ability you'll need to get API keys.

| Key Name  |  Where to Get It | Works?  |
|-----------|------------------|---------|
| OPENAI_API_KEY | https://openai.com | Yes |
| ASTRA_* | https://astra.datastax.com | Works? |

## Running in Gitpod

[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/xingh/iris)


## Using Chainlit - Quick and Dirty 
First, add your API keys in the `.env` file. OPENAI, ASTRA DB details. 

research.py uses Langchain. 

`chainlit run research.py -w` 

This will open up another URL / Port which you can start using. 

You can also try using the Llamaindex version which loads in PDFs.

## API Endpoint

The api endpoint will be up at `http://<hostname>/chat` and you can send data to it like this. Replace with the loopback address (127.0.0.1) if you are doing it locally or in gitpod, or the full gitpod preview / API url otherwise. 

```
curl -X POST http://<hostname>/chat \
   -H "Content-Type: application/json" \
   -d '{"prompt":"Show me a cat gif","model":"text-davinci-003","temperature":0.5, "max_tokens":512,"history":[]}'  

```
## Example prompts

### Conversation with memory

## Deploying

This repository is set up to deploy on [Fly.io](https://fly.io/). You should be able to follow [their docs and get it running there very quickly](https://fly.io/docs/languages-and-frameworks/python/).
