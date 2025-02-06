import pyhop
import json

def check_enough (state, ID, item, num):
	if getattr(state,item)[ID] >= num: return []
	return False

def produce_enough (state, ID, item, num):
	return [('produce', ID, item), ('have_enough', ID, item, num)]

pyhop.declare_methods ('have_enough', check_enough, produce_enough)

def produce (state, ID, item):
	return [('produce_{}'.format(item), ID)]

pyhop.declare_methods ('produce', produce)

def make_method(name, rule):
    def method(state, ID):
        subtasks = []
        if 'Requires' in rule:
            for req, num in rule['Requires'].items():
                subtasks.append(('have_enough', ID, req, num))
        if 'Consumes' in rule:
            for cons, num in rule['Consumes'].items():
                subtasks.append(('have_enough', ID, cons, num))
        subtasks.append(('produce_{}'.format(name), ID))
        return subtasks
    return method

def declare_methods (data):
	# some recipes are faster than others for the same product even though they might require extra tools
	# sort the recipes so that faster recipes go first
			for recipe_name, recipe in data['Recipes'].items():
				method = make_method(recipe_name, recipe)
				pyhop.declare_methods('produce_{}'.format(recipe_name), method)
	# hint: call make_method, then declare the method to pyhop using pyhop.declare_methods('foo', m1, m2, ..., mk)		

def make_operator(rule):
    def operator(state, ID):
        if 'Requires' in rule:
            for req, num in rule['Requires'].items():
                if getattr(state, req)[ID] < num:
                    return False
        if 'Consumes' in rule:
            for cons, num in rule['Consumes'].items():
                if getattr(state, cons)[ID] < num:
                    return False
        if 'Consumes' in rule:
            for cons, num in rule['Consumes'].items():
                setattr(state, cons, {ID: getattr(state, cons)[ID] - num})
        if 'Produces' in rule:
            for prod, num in rule['Produces'].items():
                setattr(state, prod, {ID: getattr(state, prod)[ID] + num})
        state.time[ID] += rule['Time']
        return state
    return operator

def declare_operators(data):
    operators = []
    for recipe_name, recipe in data['Recipes'].items():
        operator = make_operator(recipe)
        operators.append(operator)
    pyhop.declare_operators(*operators)
	# your code here
	# hint: call make_operator, then declare the operator to pyhop using pyhop.declare_operators(o1, o2, ..., ok)

def add_heuristic (data, ID):
	# prune search branch if heuristic() returns True
	# do not change parameters to heuristic(), but can add more heuristic functions with the same parameters: 
	# e.g. def heuristic2(...); pyhop.add_check(heuristic2)
    def heuristic (state, curr_task, tasks, plan, depth, calling_stack):
        if state.time[ID] > 300:
            return True
        return False # if True, prune this branch

    def no_infinite_regression(state, curr_task, tasks, plan, depth, calling_stack):
        # Check if the current task is already in the plan
        if curr_task in plan:
            return True
        return False

    pyhop.add_check(heuristic)
    pyhop.add_check(no_infinite_regression)


def set_up_state (data, ID, time=0):
	state = pyhop.State('state')
	state.time = {ID: time}

	for item in data['Items']:
		setattr(state, item, {ID: 0})

	for item in data['Tools']:
		setattr(state, item, {ID: 0})

	for item, num in data['Initial'].items():
		setattr(state, item, {ID: num})

	return state

def set_up_goals (data, ID):
	goals = []
	for item, num in data['Goal'].items():
		goals.append(('have_enough', ID, item, num))

	return goals

if __name__ == '__main__':
	rules_filename = 'crafting.json'

	with open(rules_filename) as f:
		data = json.load(f)

	state = set_up_state(data, 'agent', time=239) # allot time here
	goals = set_up_goals(data, 'agent')

	declare_operators(data)
	declare_methods(data)
	add_heuristic(data, 'agent')

	# pyhop.print_operators()
	# pyhop.print_methods()

	# Hint: verbose output can take a long time even if the solution is correct; 
	# try verbose=1 if it is taking too long
	pyhop.pyhop(state, goals, verbose=3)
	# pyhop.pyhop(state, [('have_enough', 'agent', 'cart', 1),('have_enough', 'agent', 'rail', 20)], verbose=3)
