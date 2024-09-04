from strategy.lats.graph import LATSGraph

def run():
    question = "Write out magnus carlson series of moves in his game against Alireza Firouzja and propose an alternate strategy"
    # question = "step by step to solve P vs NP Problem, list detaled formular"
    # question = "Build a react web applicaiton, click button will popup hello world on the screen. prove each step is correct"
    
    lats_graph = LATSGraph()
    graph = lats_graph.build_graph()

    last_step = None
    for step in graph.stream({"input": question}):
        last_step = step
        step_name, step_state = next(iter(step.items()))
        print(step_name)
        print("rolled out: ", step_state["root"].height)
        print("---")

    solution_node = None
    if 'start' in last_step:
        solution_node = last_step['start']["root"].get_best_solution()
    elif 'expand' in last_step:
        solution_node = last_step['expand']["root"].get_best_solution()
    best_trajectory = solution_node.get_trajectory(include_reflections=False)
    print(best_trajectory[-1].content)

if __name__ == "__main__":
    run()