from core.planner import Planner

def run():
    planner = Planner()

    request = "Build a react web applicaiton, click button will popup hello world on the screen."

    steps = planner.plan(request)
    print(steps)

    background = "You are a web developer, alway deliver best quality web applicaiton"

    steps = planner.plan(request, background=background)
    print(steps)

    knowledge = """
    To build a web applicaiton, you need to follow the following steps
    1. pick web development framework
    2. install local environment
    3. create scratch
    4. according to user request to add functionalites

    """

    steps = planner.plan(request, background=background, knowledge=knowledge)
    print(steps)

if __name__ == "__main__":
    run()