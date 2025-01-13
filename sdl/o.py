from pyspel.pyspel import *

@atom
class Node:
	id: int
@atom
class Edge:
	first: Node
	second: Node
@atom
class Color:
	value: str
@atom
class Assign:
	node: Node
	color: Color

problem66 = Problem()

with Node() as n_1, Assign() as a_0, Color() as c_2:
	problem66+=When(n_1).guess({a_0:(c_2, Literal(Atom(Predicate(f"{a_0.node}=={n_1}")), True),Literal(Atom(Predicate(f"{a_0.color}=={c_2}")), True))}, exactly=1)
with Assign() as a1_0, Assign() as a2_1, Edge() as e_2:
	problem66+=Assert(False).when(a1_0, a2_1, e_2, Literal(Atom(Predicate(f"{a1_0.node}!={a2_1.node}")), True), Literal(Atom(Predicate(f"{a1_0.color}=={a2_1.color}")), True), Literal(Atom(Predicate(f"{e_2.first}=={a1_0.node}")), True), Literal(Atom(Predicate(f"{e_2.second}=={a2_1.node}")), True))

print(problem66)
