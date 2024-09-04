from typing import Literal

from langgraph.graph import StateGraph, END, START

from strategy.lats.lats import TreeState, generate_initial_response, expand

class LATSGraph:

    def should_loop(self, state: TreeState) -> Literal["expand", "__end__"]:
        """Determine whether to continue the tree search."""
        root = state["root"]
        if root.is_solved:
            return END
        if root.height > 5:
            return END
        return "expand"
    
    def build_graph(self):
        builder = StateGraph(TreeState)
        builder.add_node("start", generate_initial_response)
        builder.add_node("expand", expand)
        builder.add_edge(START, "start")

        builder.add_conditional_edges(
            "start",
            # Either expand/rollout or finish
            self.should_loop,
        )
        builder.add_conditional_edges(
            "expand",
            # Either continue to rollout or finish
            self.should_loop,
        )

        graph = builder.compile()
        return graph