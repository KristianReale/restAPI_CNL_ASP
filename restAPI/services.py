import flask
from flask import Flask, jsonify,request
import sys, os
import json

app = flask.Flask(__name__)
app.json.sort_keys = False

from cnl2asp.cnl2asp import Cnl2asp
from asp2cnl.compiler import compile
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
        compiled = compile(definitions[-1], symbols)       
        result = result + compiled + "\n" 
        aspFile.close()

    return result
        