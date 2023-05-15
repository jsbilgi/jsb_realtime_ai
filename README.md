# Iris (fork of HowdoI.ai) is a reference implementation of a data augmented generative AI.

This is an experiment in building a large-language-model-backed chatbot. It can hold a conversation, remember previous comments/questions, and answer all types of queries (history, web search, movie data, weather, news, and more).

This app relies on the amazing [LangChain Python library](https://langchain.readthedocs.io/en/latest/index.html), which powers all the interesting AI stuff.


## Getting API Keys 

For those who want to use this to it's fullest ability you'll need to get API keys.

| Key Name  |  Where to Get It | Works?  |
|-----------|------------------|---------|
| OPENAI_API_KEY | https://openai.com | Yes |
| SERPAPI_API_KEY | https://serpapi.com/ | Yes |
| GIPHY_API_KEY | https://developers.giphy.com/ | Mostly |
| NEWS_API_KEY | https://newsapi.org | Yes |
| TMDB_API_KEY | https://www.themoviedb.org/settings/api | Yes |
| WOLFRAM_ALPHA_APPID | https://products.wolframalpha.com/api | Yes |
| GOOGLE_API_KEY | https://console.cloud.google.com/apis/credentials | Todo |
| GOOGLE_CSE_ID | ??? | Todo |
| FOURSQUARE_API_KEY | https://developer.foursquare.com | Yes |

More on GOOGLE (in General) https://stackoverflow.com/questions/37083058/programmatically-searching-google-in-python-using-custom-search

## Running locally

First, add your API keys in the `.env` file.

Then, install the Python requirements and start the app. You'll want a Procfile manager like [Foreman](https://github.com/ddollar/foreman) or [Hivemind](https://github.com/DarthSim/hivemind) installed.

```
pip install -r requirements.txt
foreman start -f Procfile.local
```

Once it's running, open up [http://127.0.0.1:9000/](http://127.0.0.1:9000/) and you'll be able to start interacting with the bot. There's also a writing assistant endpoint at [http://127.0.0.1:9000/write](http://127.0.0.1:9000/write).


## Running in Gitpod

[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/xingh/iris)

First, add your API keys in the `.env` file.

Then, install the Python requirements and start the app. You can use a Procfile manager like [Foreman](https://github.com/ddollar/foreman) or [Hivemind](https://github.com/DarthSim/hivemind) installed. My prerence was to keep it with the Python theme. [Honcho](https://github.com/nickstenning/honcho) is a tool that does the same thing. 

I preppedd the Gitpod this way, but also have added it to the .gitpod.yml
```
pyenv install 3.9
pyenv local 3.9
pip install --upgrade pip
pip install honcho 
```

To fix node/vite issues
```
rm -rf node_modules
cd vite
rm -rf node_modules
rm -rf dist/assets/*
npm install -g vite
npm install
yarn global add vite
```

```
pip install -r requirements.txt
honcho start -f Procfile.local
```

Once it's running, open up [http://127.0.0.1:9000/](http://127.0.0.1:9000/) and you'll be able to start interacting with the bot. There's also a writing assistant endpoint at [http://127.0.0.1:9000/write](http://127.0.0.1:9000/write).

## API Endpoint

The api endpoint will be up at `http://<hostname>/chat` and you can send data to it like this. Replace with the loopback address (127.0.0.1) if you are doing it locally or in gitpod, or the full gitpod preview / API url otherwise. 

```
curl -X POST http://<hostname>/chat \
   -H "Content-Type: application/json" \
   -d '{"prompt":"Show me a cat gif","model":"text-davinci-003","temperature":0.5, "max_tokens":512,"history":[]}'  

```


## Cassandra CQLSH / Schema setup

```
cd tools
wget https://downloads.datastax.com/enterprise/cqlsh-6.8.31-bin.tar.gz
tar xvfz cqlsh-6.8.31-bin.tar.gz
./cqlsh-6.8.31/bin/cqlsh <hostname> -u <username> -p <password> 
```

Either copy and paste `data/cassandra.cql` or do this 
```
./cqlsh-6.8.31/bin/cqlsh <hostname> -u <username> -p <password> -f ../data/cassandra.cql
```

For [Connecting to Astra Cassandra as a Service with CQLSH](https://docs.datastax.com/en/astra-serverless/docs/connect/cql/connect-cqlsh.html#_standalone_cql_shell)


## Example prompts

### Conversation with memory

Q: `hi, my name is bob`

A: `Hi Bob! Nice to meet you! How can I help you today?`

Q: `what's the last letter of my name?`

A: `b`

Q: `show me a cat gif`

A: `Here is a cat gif: <iframe src="https://giphy.com/embed/ICOgUNjpvO0PC" width="480" height="480" frameBorder="0" class="giphy-embed" allowFullScreen></iframe><br /><a href="https://giphy.com/embed/ICOgUNjpvO0PC">powered by GIPHY</a>`

Q: `actually, can you make it a dolphin?`

A: `Here is a dolphin gif: <iframe src="https://giphy.com/embed/11ctq1pDmD3cB2" width="480" height="480" frameBorder="0" class="giphy-embed" allowFullScreen></iframe><br /><a href="https://giphy.com/embed/11ctq1pDmD3cB2">powered by GIPHY</a>`

### Movies

Q: `what year was Dr. Strangelove released?`

A: `Dr. Strangelove was released in 1964.`

### Math

Q: `what's the sum of the first six prime numbers?`

A: `The sum of the first six prime numbers is 41.`

## Deploying

This repository is set up to deploy on [Fly.io](https://fly.io/). You should be able to follow [their docs and get it running there very quickly](https://fly.io/docs/languages-and-frameworks/python/).

## Experiments Folder

This folder has a few attempts at generating/testing LLM examples programmatically. You can probably ignore this unless you're just curious.
