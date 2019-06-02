'''
Tom Granot-Scalosub - 308020734
Daniel Bachar - 201242120
Compiler - Symbol Table
'''
CLASS_IDENTIFIERS = ['static', 'field']
FUNC_IDENTIFIERS = ['local', 'argument']
SEGMENT_TO_IDENTIFIER_MAP = {
    'static': 'static',
    'field': 'this',
    'local': 'local',
    'argument': 'argument'
}

class SymbolTable:

    def __init__(self):
        self._class_table = {}
        self._func_table = {}

        # Init Counters
        self._index_map = {}
        self._reset_index_map_count(
            CLASS_IDENTIFIERS + FUNC_IDENTIFIERS
        )

    # Private
    def _is_class(self, kind):
        return (kind in CLASS_IDENTIFIERS)

    def _is_function(self, kind):
        return (kind in FUNC_IDENTIFIERS)

    def _reset_index_map_count(self, identifiers):
        for id in identifiers:
            self._index_map[id] = 0

    # Public
    def define(self, identifier_details):
        name, id_type, kind = identifier_details[0], identifier_details[1], identifier_details[2]
        idx = self._index_map[kind]
        if self._is_class(kind):
            self._class_table[name] = (id_type, kind, idx)
        elif self._is_function(kind):
            self._func_table[name] = (id_type, kind, idx)
        else:
            raise Exception("Symbol Table UNKNOW kind = ", kind)

        # Inc Count
        self._index_map[kind] += 1

    def startSubRoutine(self):
        self._func_table = {}
        self._reset_index_map_count(FUNC_IDENTIFIERS)

    def indexOf(self, identifier):

        if identifier in self._class_table:
            return self._class_table[identifier][-1]
        elif identifier in self._func_table:
            return self._func_table[identifier][-1]
        else:
            return None

    def kindOf(self, identifier):
        if identifier in self._class_table:
            return SEGMENT_TO_IDENTIFIER_MAP[self._class_table[identifier][1]]
        elif identifier in self._func_table:
            return SEGMENT_TO_IDENTIFIER_MAP[self._func_table[identifier][1]]
        else:
            return None

    def typeOf(self, identifier):

        if identifier in self._class_table:
            return self._class_table[identifier][0]
        elif identifier in self._func_table:
            return self._func_table[identifier][0]
        else:
            return None

    def varCount(self, kind):
        return self._index_map[kind]
