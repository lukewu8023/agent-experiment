class Step:
    def __init__(self, index,name, description,response=""):
        self.index=index
        self.name = name
        self.description = description
        self.response=response
        self.sub_steps = []

    def add_sub_step(self, sub_step):
        self.sub_steps.append(sub_step)

    def add_sub_steps(self, sub_steps):
        self.sub_steps+=sub_steps
        
    def remove_sub_step(self, sub_step):
        if sub_step in self.sub_steps:
            self.sub_steps.remove(sub_step)
    
    def add_response(self,response):
        self.response=response

    def get_context_str(self):
        contextStr = f"<Step {self.index}>\n{self.name}: {self.response}\n</Step {self.index}>\n"

        return contextStr

    def __repr__(self):
        return f"Step(name='{self.name}', description='{self.description}', sub_steps={self.sub_steps})"
    
    def __str__(self):
        return f"Step {self.index} - {self.name}: {self.description}"


class StepManager:
    def __init__(self):
        self.steps = []

    def add_step(self, step):
        self.steps.append(step)

    def add_steps(self, step_list):
        self.steps.extend(step_list)

    def remove_step_by_name(self, step_name):
        for step in self.steps:
            if step.name == step_name:
                self.steps.remove(step)
                break

    def add_step_at_index(self, step, index):
        self.steps.insert(index, step)

    def remove_steps_after_index(self, index):
        self.steps = self.steps[:index+1]

    def get_steps(self):
        return self.steps