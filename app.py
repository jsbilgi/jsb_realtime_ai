from flask import Flask, send_from_directory, request, render_template
import sys

from utils.chat_agent import ChatAgent
from utils.editor_chain import execute_editor_chain
import logging
import json
import re

import os



logger = logging.getLogger()

app = Flask(__name__, template_folder='vite/dist')
app.config.from_object(__name__)
if __name__ == '__main__':
    app.run(debug=True)


@app.route('/write')
def root():
    return send_from_directory('vite/dist', 'write.html')


@app.route('/')
@app.route('/chat/<id>')
def howdoi(id=None):
    # return send_from_directory('./vite/dist', 'howdoi.html')
    if id is None:
        return render_template('howdoi.html')

@app.route('/chatnew')
def chatnew():
    return send_from_directory('./vite/dist', 'chat.html')

# Path for the rest of the static files (JS/CSS)
@app.route('/<path:path>')
def assets(path):
    return send_from_directory('./vite/dist', path)

# This is the endpoint that powers the / UI - everything is inside utils/chat_agent.py
@ app.route('/chat', methods=['POST', 'GET'])
def chat():
    json = request.get_json(force=True)
    history_array = json.get('history')

    input = json.get('prompt')
    print("\n\n#### INPUT ####\n")
    print(input)
    print("\n\n#### INPUT ####\n")

    chat_agent = ChatAgent(history_array=history_array)

    try:
        reply = chat_agent.agent_executor.run(input=input)

    except ValueError as inst:
        print('ValueError:\n')
        print(inst)
        reply = "Sorry, there was an error processing your request."

    print("\n\n#### REPLY ####\n")
    print(reply)
    print("\n\n#### REPLY ####\n")

    pattern = r'\(([a-z]{2}-[A-Z]{2})\)'
    # Search for the local pattern in the string
    match = re.search(pattern, reply)

    language = 'en-US'  # defaut
    if match:
        # Get the language code
        language = match.group(1)

        # Remove the language code from the reply
        reply = re.sub(pattern, '', reply)

    print("LANG: ", language)

    sys.stdout.flush()
    return {
        'input': input,
        'text': reply.strip(),
        'language': language
    }


# this is for the /write UI - a document editor that uses GPT to help write
@app.route('/editor', methods=['POST', 'GET'])
def prompt():
    prompt = request.get_json(force=True)

    # print the prompt to the console
    print(prompt)

    # run the editor chain 
    completion = execute_editor_chain(input= prompt.get('prompt'), 
                                        instruction= prompt.get('instruction'), 
                                        operation=prompt.get('operation'))
    
    print(completion)

    # check if the  last line of completion starts with Output:
    if completion.split('\n')[-1].startswith("Output:"):
        # if so, remove the Output: prefix
        output = completion.split("Output:")[1].strip()        
        status = 200
    else:
        # otherwise, return the completion as is
        output = completion
        status = 500

    return {
        'input': prompt.get('prompt'),
        'text': output
    }, status


