#  ECSTATIC: Extensible, Customizable STatic Analysis Tester Informed by Configuration
#
#  Copyright (c) 2022.
#
#  This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.


from typing import Dict, Optional
import logging
import os
import re
import xml.etree.ElementTree as ElementTree


class Flow:
    """
    Class that represents a flow returned by AQL.
    """
    logger = logging.getLogger(__name__)
    register_regex = re.compile(r"\$[a-z]\d+")

    def __init__(self, element):
        self.element = element
        self.update_file()

    def get_file(self) -> str:
        f = self.element.find("reference").findall("app")[0].findall("file")[0].text
        f = f.replace('\\', '/')
        f = f.split('/')[-1]
        return f

    def get_full_file(self) -> str:
        f = self.element.find("reference").findall("app")[0].findall("file")[0].text
        f = f.replace('\\', '/')
        return f

    def get_classification(self) -> Optional[str]:
        for e in self.element:
            if e.tag == 'classification':
                return e.text

    def add_classification(self, classification: str) -> None:
        for e in self.element:
            if e.tag == 'classification':
                e.text = classification
                return

        # We have to add it if it doesn't exist.
        cl = ElementTree.Element('classification')
        cl.text = classification
        self.element.append(cl)

    def update_file(self):
        for e in self.element:
            if e.tag == "reference":
                f = e.find("app").find("file").text
                e.find("app").find("file").text = os.path.basename(f)

    @classmethod
    def clean(cls, stmt: str) -> str:
        c = Flow.register_regex.sub("", stmt)
        c = re.sub(r"_ds_method_clone_\d*", "", c)
        logging.debug(f"Before clean: {stmt}\nAfter clean: {c}")
        return c.strip()

    def get_source_and_sink(self) -> Dict[str, str]:
        result = dict()
        references = self.element.findall("reference")
        source = [r for r in references if r.get("type") == "from"][0]
        sink = [r for r in references if r.get("type") == "to"][0]

        def get_statement_generic(a: ElementTree.Element) -> str:
            return a.find("statement").find("statementgeneric").text

        result["source_statement_generic"] = Flow.clean(get_statement_generic(source))
        logging.debug(f"Source: {result}")
        result["source_method"] = source.find("method").text
        result["source_classname"] = source.find("classname").text
        result["sink_statement_generic"] = Flow.clean(get_statement_generic(sink))
        result["sink_method"] = sink.find("method").text
        result["sink_classname"] = sink.find("classname").text
        return result

    def __str__(self) -> str:
        return f'File: {self.get_file()}, Flow: {str(self.get_source_and_sink())}'

    def __eq__(self, other):
        """
        Return true if two flows are equal
            
        Criteria:
        1. Same apk.
        2. Same source and sink.
        3. Same method and class.
        """

        if not isinstance(other, Flow):
            return False
        else:
            if not self.get_file() == other.get_file():
                logging.debug(f'My file ({self.get_file()}) does not equal the other file ({other.get_file()})')
            if not self.get_source_and_sink() == other.get_source_and_sink():
                logging.debug(f'My source and sink ({self.get_source_and_sink()} does not equal the other '
                              f'source and sink ({other.get_source_and_sink()})')
            return os.path.basename(self.get_file()) == os.path.basename(other.get_file()) and self.get_source_and_sink() == other.get_source_and_sink()

    def __hash__(self):
        sas = self.get_source_and_sink()
        return hash((self.get_file(), frozenset(sas.items())))

    def __gt__(self, other):
        """ Sort by file, then by sink, class, then by sink method, then by sink statement, then by source."""
        if not isinstance(other, Flow):
            raise TypeError(f"{other} is not of type Flow")

        if self.get_file() != other.get_file():
            return self.get_file() > other.get_file()
        else:
            d1 = self.get_source_and_sink()
            d2 = other.get_source_and_sink()
            if d1['sink_classname'] != d2['sink_classname']:
                return d1['sink_classname'] > d2['sink_classname']
            elif d1['sink_method'] != d2['sink_method']:
                return d1['sink_method'] != d2['sink_method']
            elif d1['sink_statement_generic'] != d2['sink_statement_generic']:
                return d1['sink_statement_generic'] != d2['sink_statement_generic']
            elif d1['source_classname'] != d2['source_classname']:
                return d1['source_classname'] > d2['source_classname']
            elif d1['source_method'] != d2['source_method']:
                return d1['source_method'] != d2['source_method']
            elif d1['source_statement_generic'] != d2['source_statement_generic']:
                return d1['source_statement_generic'] != d2['source_statement_generic']
            else:  # completely equal in every way
                return False

    def __lt__(self, other):
        return not (self == other) and not (self > other)

    def __le__(self, other):
        return self == other or self < other

    def __ge__(self, other):
        return self == other or self > other
