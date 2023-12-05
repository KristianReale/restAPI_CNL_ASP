from asp2cnl.parser import ASPTransformer, ASPContentTree, ClassicalLiteral, Disjunction
from asp2cnl.compiler import compile

from lark import Lark
aspCoreParser = Lark(open("C:\\Users\\Kristian\\git\\cnl\\asp2cnl\\asp2cnl\\src\\asp2cnl\\asp_core_2_grammar\\asp_grammar.lark", "r").read())

if __name__ == '__main__':
    print("ciao")
    program = open(os.path.join(os.path.dirname(__file__), "test.asp"), "r").read()
    
    definitions = ASPParser(program).parse()

    with open(os.path.join(os.path.dirname(__file__), "facts.cnl"), "r") as f:
        symbols = Cnl2asp(f).get_symbols()
        #print(symbols)
        #print(get_symbol(symbols, "work in"))
        #print("ResultsA: \n")       
        for rule in definitions:           
            results.write("RULE: ")
            results.write("\n")
            results.write(rule.toString())
            results.write("\n")
            results.write("\n")
            results.write("TRANSLATED IN: ")
            results.write("\n")
            compiled = compile(rule, symbols)
            results.write(compiled)     
            results.write("\n")
            outFileDisk = os.path.join(os.path.dirname(__file__), "output.cnl")
            with open(outFileDisk, "w") as out_file:
                f.seek(0)                    
                out_file.write(f.read())
            with open(outFileDisk, "a") as out_file:
                out_file.write(compiled)           
            #print("Translating: " + compiled) 
            with open(outFileDisk, "r") as in_file:                    
                cnl2asp = Cnl2asp(in_file)
                result = cnl2asp.compile()            
                results.write("TRANSLATION BACK: ")
                results.write("\n")
                results.write(result)
            results.write("\n")
            results.write("------------------")
            
            results.write("\n")
        print("Results: \n")       
        print(results.getvalue())
    