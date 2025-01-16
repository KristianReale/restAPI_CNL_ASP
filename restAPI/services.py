import flask
from flask import Flask, jsonify,request
import sys, os
import json
import requests

import sdl.grammar
from cnl2asp.cnl2asp import Cnl2asp
from sdl.grammar import *
import importlib

OPENCHAT_SERVICE_URL = f"http://160.97.63.235:5000/cnl2nl_openchat"

app = flask.Flask(__name__, template_folder='Templates')
app.json.sort_keys = False

import os
#sys.path += [os.path.abspath(__file__ + "/..")]

from cnl2asp import cnl2asp
from asp2cnl.compiler import compile_rule
from asp2cnl.parser import ASPParser

@app.route("/generate_joint", methods=["POST"])
def generate_joint():   
    isCnl2Asp = (request.args.get('cnl2asp') != None)
    input_json = request.get_json()     
    user_input = input_json.get("user_input")
    sentences = input_json.get("sentences")
    sentencesAggr = ""
    for sentence in sentences:
        if isCnl2Asp:
            sentence.get("cnl")
            sentence["asp"] = cnl2aspImpl(user_input, sentence.get("cnl"))
        else:
            sentence.get("asp")
            sentence["cnl"] = asp2cnlImpl(user_input, sentence.get("asp"))
        sentencesAggr = sentencesAggr + "\n" + sentence.get("cnl")

    input_json.update(jointFromCnl(user_input, sentencesAggr))    
    return jsonify(input_json)


def jointFromCnl(user_input, sentences):
    result = ""
    cnlFileDisk = os.path.join(os.path.dirname(__file__), "cnlJoint.cnl")
    with open(cnlFileDisk, "w") as cnlFile:
        cnlFile.seek(0)             
        for ui in user_input:               
            cnlFile.write(ui + "\n")        
        cnlFile.write(sentences)

    with open(cnlFileDisk, "r") as in_file:                    
        cnl2asp = Cnl2asp(in_file)
        result = cnl2asp.cnl_to_json()   
       
    #return json.loads(str(json.dumps(result)))
    return result


@app.route("/cnl2asp", methods=["POST"])
def cnl2asp():    
    input_json = request.get_json()    
    user_input = input_json.get("user_input")
    sentence = input_json.get("cnl")
    return cnl2aspImpl(user_input, sentence)

def cnl2aspImpl(user_input, sentence):
    result = ""
    cnlFileDisk = os.path.join(os.path.dirname(__file__), "cnl.cnl")
    with open(cnlFileDisk, "w") as cnlFile:
        cnlFile.seek(0)             
        for ui in user_input:               
            cnlFile.write(ui + "\n")        
        cnlFile.write(sentence)

    with open(cnlFileDisk, "r") as in_file:                    
        cnl2asp = Cnl2asp(in_file)
        result = cnl2asp.compile()            
    return result  


@app.route("/asp2cnl", methods=["POST"])
def asp2cnl():      
    input_json = request.get_json()    
    user_input = input_json.get("user_input")
    rule = input_json.get("asp") + "\n"    
    return asp2cnlImpl(user_input, rule)  

@app.route("/asp2nl", methods=["POST"])
def asp2nl():    
    global OPENCHAT_SERVICE_URL
    input_json = request.get_json()    
    user_input = input_json.get("user_input")
    rule = input_json.get("asp") + "\n" 
    cnl = asp2cnlImpl(user_input, rule)
    data_to_send = {'cnl': cnl}
    nl = make_request_to_nl_service(service_url=OPENCHAT_SERVICE_URL, data=json.dumps(data_to_send))
    return {'model': 'openchat', 'cnl': cnl.replace('\n',''), 'nl': nl}
     

def make_request_to_nl_service(service_url='', data=None):
    response = requests.post(service_url, data=data, headers={"Content-Type": "application/json"})
    response_dict = json.loads(response.text)
    return response_dict['response'].strip()

def asp2cnlImpl(user_input, rule):      
    result = ""
    uiFileDisk = os.path.join(os.path.dirname(__file__), "user_input.cnl")
    with open(uiFileDisk, "w") as uiFile:
        uiFile.seek(0)     
        for ui in user_input:               
            uiFile.write(ui + "\n")        

    aspFileDisk = os.path.join(os.path.dirname(__file__), "program.asp")
    with open(aspFileDisk, "w") as aspFile:
        aspFile.seek(0)                        
        aspFile.write(rule + "\n")        
    
    symbols = None    
    with open(uiFileDisk, "r") as uiFile:              
        symbols = Cnl2asp(uiFile).get_symbols()

    with open(aspFileDisk, "r") as aspFile2:                   
        definitions = ASPParser(aspFile2.read()).parse()                       
        compiled = compile_rule(definitions[-1], symbols)
        result = result + compiled + "\n" 
        aspFile.close()

    return result

@app.route("/sdl", methods=["POST"])
def sdl():
    input_json = request.get_json()
    user_input = input_json.get("sdl_input")
    return sdlImpl(user_input)

def sdlImpl(code):
    result = ""
    try:
        tree = build_tree(code)
        asp = ""
        if get_asp_block() != "":
            asp += f"""problem{get_number()}.add(\"\"\"{get_asp_block()}\"\"\")"""
        destination_file = "outputsdl.py"
        f = open(f"{destination_file}", "w")
        f.write(str(tree))

        execution_string = execute("sdl/clingo", asp)
        f.write(execution_string)
        f.close()
        reset()
        subprocess.run(["python", f"{destination_file}"])
        result = subprocess.check_output(["python", f"{destination_file}"],  stderr=subprocess.STDOUT, text=True)

    except exceptions.LarkError as e:
        print(f"Parsing error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return result