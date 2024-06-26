from __future__ import annotations

import collections
import os
from enum import Enum
from textwrap import indent
from typing import TextIO

from cnl2asp.utility.utility import Utility
from lark import Lark, UnexpectedCharacters
from lark.exceptions import VisitError

from cnl2asp.ASP_elements.asp_program import ASPProgram
from cnl2asp.converter.cnl2json_converter import Cnl2jsonConverter
from cnl2asp.exception.cnl2asp_exceptions import ParserError, EntityNotFound
from cnl2asp.proposition.attribute_component import AttributeComponent
from cnl2asp.proposition.entity_component import EntityComponent, EntityType
from cnl2asp.converter.asp_converter import ASPConverter
from cnl2asp.parser.parser import CNLTransformer
from cnl2asp.proposition.problem import Problem
from cnl2asp.proposition.signaturemanager import SignatureManager


class SymbolType(Enum):
    DEFAULT = 0
    TEMPORAL = 1


class Symbol:
    def __init__(self, predicate: str, keys: list[str | Symbol], attributes: list[str | Symbol], symbol_type: SymbolType):
        """
        Class for representing the concepts (ASP atoms) structure.

        :param predicate:
        :param keys: the list of attributes that are keys.
        :param attributes: the FULL list (including the keys) of attributes of the atom.
        """
        self.predicate = predicate
        self.keys = keys
        self.attributes = attributes
        self.symbol_type = symbol_type

    def __repr__(self):
        attributes = f'\n{indent(str(self.attributes), "    ")}'
        return f'\n{self.predicate} [{self.symbol_type.name}]: {indent(attributes, "    ")}'


class Cnl2asp:
    def __init__(self, cnl_input: TextIO | str):
        if isinstance(cnl_input, str):
            self.cnl_input = cnl_input
        else:
            self.cnl_input = cnl_input.read()

    def parse_input(self):
        cnl_parser = Lark(open(os.path.join(os.path.dirname(__file__), "grammar.lark"), "r").read(),
                          propagate_positions=True)
        problem: Problem = CNLTransformer().transform(cnl_parser.parse(self.cnl_input))
        return problem

    def __is_predicate(self, name: str):
        try:
            SignatureManager.get_signature(name)
            return True
        except:
            return False

    def __get_predicate(self, entity_name: str, attribute: AttributeComponent):
        split_name = attribute.get_name().split('_')
        if len(split_name) > 1:
            for name in split_name:
                if self.__is_predicate(name):
                    return SignatureManager.get_signature(name)
        signature_name = attribute.get_name()
        if attribute.origin != entity_name:
            signature_name = attribute.origin.name
        if self.__is_predicate(signature_name):
            return SignatureManager.get_signature(signature_name)
        return None


    def cnl_to_json(self):
        problem = self.parse_input()
        converter = Cnl2jsonConverter()
        json = problem.convert(converter)
        return json

    def check_syntax(self) -> bool:
        if self.parse_input():
            return True
        return False

    def compile(self, auto_link_entities: bool = True) -> str:
        Utility.AUTO_ENTITY_LINK = auto_link_entities
        try:
            problem: Problem = self.parse_input()
        except UnexpectedCharacters as e:
            print(ParserError(e.char, e.line, e.column, e.get_context(self.cnl_input), self.cnl_input.splitlines()[e.line-1], list(e.allowed)))
            return ''
        except VisitError as e:
            print(e.args[0])
            return ''
        try:
            asp_converter: ASPConverter = ASPConverter()
            program: ASPProgram = problem.convert(asp_converter)
            SignatureManager().signatures = []
            return str(program)
        except Exception as e:
            print("Error in asp conversion:", str(e))
            return ''

    def __get_type(self, name: str):
        if SignatureManager.is_temporal_entity(name):
            return SymbolType.TEMPORAL
        return SymbolType.DEFAULT

    def __convert_attribute(self, entity_name: str, attribute: AttributeComponent) -> str | Symbol:
        if attribute.origin and entity_name != attribute.origin.name:
            return Symbol(attribute.origin.name,
                          [self.__convert_attribute(entity_name, AttributeComponent(attribute.get_name(),
                                                                                    attribute.value,
                                                                                    attribute.origin.origin))],
                          [self.__convert_attribute(entity_name, AttributeComponent(attribute.get_name(),
                                                                                    attribute.value,
                                                                                    attribute.origin.origin))],
                          self.__get_type(attribute.origin.name)
                          )
        return attribute.get_name()

    def __convert_signature(self, entity: EntityComponent) -> Symbol:
        keys = []
        attributes = []
        for attribute in entity.get_attributes():
            attributes.append(self.__convert_attribute(entity.get_name(), attribute))
        entity_type = SymbolType.DEFAULT
        if SignatureManager.is_temporal_entity(entity.get_name()):
            entity_type = SymbolType.TEMPORAL
        if entity.get_attributes() != entity.get_keys():
            for key in entity.get_keys():
                keys.append(self.__convert_attribute(entity.get_name(), key))
        return Symbol(entity.get_name(), keys, keys + attributes, entity_type)

    def get_symbols(self) -> list[Symbol]:
        self.compile()
        signatures: list[Symbol] = []
        for signature in SignatureManager().signatures:
            signatures.append(self.__convert_signature(signature))
        SignatureManager().signatures = []
        return signatures
