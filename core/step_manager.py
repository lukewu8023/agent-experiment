class Step:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.sub_steps = []

    def add_sub_step(self, sub_step):
        self.sub_steps.append(sub_step)

    def add_sub_steps(self, sub_steps):
        self.sub_steps.append(sub_steps)
        
    def remove_sub_step(self, sub_step):
        if sub_step in self.sub_steps:
            self.sub_steps.remove(sub_step)

    def __repr__(self):
        return f"Step(name='{self.name}', description='{self.description}', sub_steps={self.sub_steps})"


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