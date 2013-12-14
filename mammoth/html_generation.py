import cgi


class HtmlGenerator(object):
    def __init__(self):
        self._stack = []
        self._fragments = []
    
    def text(self, text):
        if text:
            self._write_all()
            self._fragments.append(_escape_html(text))
    
    def start(self, name, attributes=None):
        self._stack.append(_Element(name, attributes))

    def end(self):
        element = self._stack.pop()
        if element.written:
            self._fragments.append("</{0}>".format(element.name))
    
    def end_all(self):
        while self._stack:
            self.end()
    
    def self_closing(self, name, attributes=None):
        attribute_string = _generate_attribute_string(attributes)
        self._fragments.append("<{0}{1} />".format(name, attribute_string))
    
    def _write_all(self):
        for element in self._stack:
            if not element.written:
                element.written = True
                self._write_element(element)
    
    def _write_element(self, element):
        attribute_string = _generate_attribute_string(element.attributes)
        self._fragments.append("<{0}{1}>".format(element.name, attribute_string))
    
    def append(self, other):
        if other._fragments:
            self._write_all()
            for fragment in other._fragments:
                self._fragments.append(fragment)
    
    def html_string(self):
        return "".join(self._fragments)


class _Element(object):
    def __init__(self, name, attributes):
        self.name = name
        self.attributes = attributes
        self.written = False


def _escape_html(text):
    return cgi.escape(text, quote=True)


def _generate_attribute_string(attributes):
    if attributes is None:
        return ""
    else:
        return "".join(
            ' {0}="{1}"'.format(key, _escape_html(value))
            for key, value in attributes.iteritems()
        )


def satisfy_html_path(generator, path):
    first_unsatisfied_index = _find_first_unsatisfied_index(generator, path)
    while len(generator._stack) > first_unsatisfied_index:
        generator.end()
    
    for element in path.elements[first_unsatisfied_index:]:
        attributes = {}
        if element.class_names:
            attributes["class"] = " ".join(element.class_names)
        generator.start(element.names[0], attributes=attributes)
    

def _find_first_unsatisfied_index(generator, path):
    for index, (generated_element, path_element) in enumerate(zip(generator._stack, path.elements)):
        if generated_element.name not in path_element.names or path_element.fresh:
            return index
    
    return len(generator._stack)
