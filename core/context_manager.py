class ContextManager:

    def __init__(self):
        self.context = {}
        
    def get_context(self):
        return self.context

    def get_new_context(self):
        self.context = {}
        return self.context

    def add_context(self, key, value):
        self.context[key] = value
        print(f"Add '{key}' into the context.")

    def remove_context(self, key):
        if key in self.context:
            del self.context[key]
            print(f"Remove '{key}' from the context.")
        else:
            print(f"Key '{key}' not found in context.")

    def context_to_str(self):
        contextStr = "<context>\n"
        for key, value in self.context.items():
            contextStr += f"<{key}>\n{value}\n</{key}>\n"
        contextStr += "</context>"
        return contextStr

    def print_context(self):
        print(f"Here is the context:")
        print(self.context_to_str())