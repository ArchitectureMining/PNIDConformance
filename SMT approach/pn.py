from xml.dom import minidom
from html import unescape
import re
import sys
import pandas as pd
import printing as printer

class PN:
	def __init__(self, pn_as_array, identifier_bound):
		self.net = pn_as_array
		self._places = pn_as_array["places"] if len(pn_as_array) > 0 else []
		self._transitions = pn_as_array["transitions"] if len(pn_as_array) > 0 else []
		self._arcs = pn_as_array["arcs"] if len(pn_as_array) > 0 else []
		self.add_invisible_transitions()
		self.add_dist_structure()
		self.identifier_bound = identifier_bound

	def places(self):
		return self._places

	def transitions(self):
		return self._transitions

	def arcs(self):
		return self._arcs

	# We add an invisible transition to every transition such that an transition is allowed to match without matching the rest
	def add_invisible_transitions(self):
		id = len(self.transitions()) + 1
		for p in self._places:
			if "initial" not in p:
				t = {"id": id, "invisible": True, "label": None}
				self._transitions.append(t)
				self._arcs.append({"source": { "id": p["id"] }, "target": { "id": id }})
				self._arcs.append({"target": { "id":  p["id"] }, "source": { "id": id }})
				id += 1

	# We add these parameters to each transitions for creating the reachability data structure
	def add_dist_structure(self):
		for t in self._transitions:
			t["idist"] = 0
			t["fdist"] = 0

	def read_pnml_input(pnmlfile):
		dom = minidom.parse(pnmlfile)
		pn = {"variables": [], "places": [], "transitions": [], "arcs": []}

		# Arcs
		for a in dom.getElementsByTagName("arc"):
			src = a.getAttribute("source")
			tgt = a.getAttribute("target")
			id = a.getAttribute("id")
			pn["arcs"].append({"source": src, "target": tgt, "id": id})

		# Transitions
		for a in dom.getElementsByTagName("transition"):
			id = a.getAttribute("id")
			t = {"id": id}
			pn["transitions"].append(t)

		# Places
		for a in dom.getElementsByTagName("page")[0].getElementsByTagName("place"):
			id = a.getAttribute("id")
			p = {"id": id}
			name = a.getElementsByTagName("name")
			if name:
				p["name"] = name[0].getElementsByTagName("text")[0].firstChild.nodeValue
			init = a.getElementsByTagName("initialMarking")
			if len(init) > 0:
				p["initial"] = int(
					init[0].getElementsByTagName("text")[0].firstChild.nodeValue
				)
			pn["places"].append(p)

		return pn

	def get_valuations(variables, state):
		valuations = []
		for p in state:
			if p["resources"] == None:
				continue

			for token in p["resources"]:
				if len(token["vector"]) == len(variables.replace(",","")):
					valuations.append(token["vector"])

		return valuations

	def token_exists_with_identical_vector_as_valuation(resources, variables, state):
		exists = False
		for token in resources:
			for valuation in PN.get_valuations(variables, state):
				if token["vector"] == valuation:
					exists = True

		return exists

	def remove_token_with_identical_vector_as_valuation(resources, variables, state):
		if len(variables) > 1:
			for token in resources:
				for valuation in PN.get_valuations(variables, state):
					if token["vector"] == valuation:
						resources.remove(token)
						return token
			return []
		else:
			for token in resources:
				resources.remove(token)
				return token

	def arc_is_enabled(a, state):
		(current, id) = state
		for p in current:
			if (
				(p["place"]["id"] == a["src"])
				and (p["amount"] > 0)
				and (len(a["inscription"]) == 0 or PN.token_exists_with_identical_vector_as_valuation(
					p["resources"], a["inscription"], current
				))
			):
				return True

		return False

	def fire_transition(t, inArcs, state, rg, maxID):
		orig_state = state
		vars = []
		tokens = []

		def manual_copy(original_list):
			l = []
			for item in original_list:
				l.append(item.copy())
			return l

		(current_state, state_id) = (manual_copy(state[0]), state[1])

		# Move a token from each in arc
		for a in inArcs:
			for p in current_state:
				if p["place"]["id"] == a["src"]:
					p["amount"] = p["amount"] - 1
					(
						removedToken
					) = PN.remove_token_with_identical_vector_as_valuation(
						p["resources"], a["inscription"], current_state
					)
					if p["resources"] == None:
						p["resources"] = []
					if(len(a["inscription"]) > 0):
						vars.extend(a["inscription"].split(","))
					if removedToken != []:
						tokens.append((removedToken, a["inscription"]))

		# Move a token to each place of out arcs
		valuation = []

		for a in t["outArcs"]:
			for p in current_state:
				if p["place"]["id"] == a["tgt"]:
					p["amount"] = p["amount"] + 1

					if all(c in vars for c in a["inscription"].split(",")) == False:
						# New variables after transition, so modify state
						splitA = set(vars)
						splitB = set([ x for x in a["inscription"].split(",") if x != ''])
						newVars = splitB.difference(splitA)

						# Adjust max ID
						for token in tokens:
							for id in token[0]["vector"]:
								id = id
								if id > maxID:
									maxID = id

						# Add new identifiers to corresponding token
						for token in tokens:
							if token[1] == a["inscription"]:
								for id in newVars:
									token[0]["vector"].append(maxID + 1)
									# token[1] = token[1] + id
									maxID = maxID + 1
									vars.append(id)
									splitA.add(id)
							if token[1] == '':
								token[0]["vector"] = []
								for id in newVars:
									token[0]["vector"].append(maxID + 1)
									token = (token[0]["vector"], token[1] + id)
									maxID = maxID + 1
									vars.append(id)
									splitA.add(id)

					trimmed_tokens = tokens
					if len([ x for x in a["inscription"].split(",") if x != '']) < len(vars):
						# Less variables after transition, so modify state
						splitA = set([ x for x in a["inscription"].split(",") if x != ''])
						splitB = set(vars)
						removedVars = splitB.difference(splitA)
						if len(tokens) > 1:
							trimmed_tokens = [t for t in tokens if t[1] == a["inscription"] or t[1] == '']
						else:
							if len(tokens[0][0]["vector"]) - len(removedVars) >= len(a["inscription"]):
								trimmed_tokens[0][0]["vector"] = tokens[0][0]["vector"][:-(len(removedVars))]
					
					ids = []
					for token in [i for n, i in enumerate(tokens) if i not in tokens[n + 1:]]:
						ids.extend(token[0]["vector"])

					if len([ x for x in a["inscription"].split(",") if x != '']) == len(vars) and len(ids) == len(vars):
						p["resources"].append({'vector': ids})
					else:
						p["resources"].append(trimmed_tokens[0][0])

					if len(ids) >= len(valuation):
						valuation = ids

		similar_states = [(s,id) for (s,id) in rg["states"] if s == current_state]
		if len(similar_states) > 0:
			action = {"trans": t, "src": orig_state, "tgt": similar_states[0], "valuation": str(valuation)}
			return (similar_states[0], action, maxID, len(similar_states) > 0)
		else:		
			action = {"trans": t, "src": orig_state, "tgt": (current_state, len(rg["states"])+1), "valuation": str(valuation)}
			return ((current_state, len(rg["states"])+1), action, maxID, len(similar_states) > 0)

	def state_exists_token_within_bound(state, bound):
		(current, id) = state
		if bound != None:
			for p in current:
				if p["resources"] == None:
					return True

				for token in p["resources"]:
					if all(id <= bound for id in token["vector"]) == True:
						return True

			return False
		else:
			return True

	def valuation_within_bound(valuation, bound):
		resources_list = eval(valuation)

		if bound != None:
			if all(id <= bound for id in resources_list) == True:
				return True
		
			return False
		else:
			return True

	def build_rg(rg, pnid, state, bound, maxID, state_exists):
		if state_exists == False:
			rg["states"] += [state]

		enabledTransitions = []
		for t in pnid._transitions:
			enabledInArcs = []
			for a in t["inArcs"]:
				if PN.arc_is_enabled(a, state):
					enabledInArcs += [a]

			if len(enabledInArcs) == len(t["inArcs"]):  # t is enabled
				enabledTransitions.append((t,enabledInArcs))

		# if multiple enabled transitions, multiple ways of firing
		for (t,enabledInArcs) in enabledTransitions:
			(newState, newAction, newMaxID, state_exists) = PN.fire_transition(
				t, enabledInArcs, state, rg, maxID
			)
			
			if PN.valuation_within_bound(newAction["valuation"], bound):
				maxID = newMaxID
				rg["actions"] += [newAction]
				PN.build_rg(rg, pnid, newState, bound, maxID, state_exists)

		return rg

	def max_identifier_trace(trace, debug):
		min = sys.maxsize
		max = -1
		no_resources = True

		for event in trace:
			if pd.isna(event["org:resource"]) == False:
				resources = event["org:resource"].split(",")
				if len(resources) != 0:
					no_resources = False
					for r in resources:
						split = re.split("(\d.*)", r)
						if len(split) > 1:
							id = int(split[1])
							if id > max:
								max = id
							if id < min:
								min = id
						else:
							if debug:
								print("Error: an identifier in resources field of trace is not a number!")
							return (-1, -1)
				else:
					 return (None, None)
			
		if no_resources == True:
			return (None, None)

		return (max - min, min)

	def convert_action_to_transition(
		pn, actions, counter, created_transitions, forced_input_place, init
	):
		if len(actions) > 0:
			
			# Lookup next action in list
			action = actions[0]
			if len(actions) > 1:
				nextAction = actions[1]
			else:
				nextAction = None

			# Construct transition label
			transition_name = action["trans"]["id"] + " " + action["valuation"]

			# ID of transition is new, except when the transition has been created before
			id = len(pn["transitions"])
			if (transition_name in created_transitions):
				arc = [
						a
						for a in pn["arcs"]
						if "label" in a["target"] and a["target"]["label"] == transition_name
					][0]
				id = arc["target"]["id"]

			# Create transition if it does not exist yet
			if (transition_name not in created_transitions):
				pn["transitions"].append(
					{"id": id, "label": transition_name}
				)
				created_transitions.add(transition_name)
			
			# First round of the algorithm there could be multiple initial places so we create multiple arcs
			pn["arcs"].append(
				{
					"source": {
						"id": forced_input_place
						if forced_input_place != ""
						else "p" + str(counter)
					},
					"target": {
						"id": id,
						"label": transition_name,
					},
				}
			)

			# If transition already was created, connect arcs to that input place
			next_transition_name = (
				nextAction["trans"]["id"] + " " + nextAction["valuation"]
				if nextAction != None
				else None
			)
			if (
				(next_transition_name == None or next_transition_name not in created_transitions)
			):
				counter = counter + 1
				pn["arcs"].append(
					{
						"source": {
							"id": id,
							"label": transition_name,
						},
						"target": {"id": "p" + str(counter)},
					}
				)
				pn["places"].append({"id": "p" + str(counter)})
				# Recursively call for next action until no actions remain
				pn = PN.convert_action_to_transition(
					pn, actions[1:], counter, created_transitions, "", False
				)
			else:
				input_arc = [
					a
					for a in pn["arcs"]
					if "label" in a["target"] and a["target"]["label"] == next_transition_name
				][0]
				input_place = input_arc["source"]["id"]

				pn["arcs"].append(
					{"source": {"id": id, "label": transition_name}, "target": {"id": input_place}}
				)
				# Recursively call for next action until no actions remain, but with forced input place
				pn = PN.convert_action_to_transition(
					pn, actions[1:], counter, created_transitions, input_place, False
				)

			# Filter duplicate transitions
			unduplicated_transitions = []
			seen_transitions = set()

			for t in pn["transitions"]:
				if t["label"] not in seen_transitions:
					unduplicated_transitions.append(t)
					seen_transitions.add(t["label"])

			pn["transitions"] = unduplicated_transitions

			# Filter duplicate arcs
			unduplicated_arcs = []
			seen_arcs = set()

			for t in pn["arcs"]:
				if str(t) not in seen_arcs:
					unduplicated_arcs.append(t)
					seen_arcs.add(str(t))

			pn["arcs"] = unduplicated_arcs

		return pn

	def convert_rg_to_pn(rg):
		pn = {"places": [], "transitions": [], "arcs": []}
		placeCount = 1

		pending_out_arcs = []
		places_for_states = []

		first = True
		for state in rg["states"]:
			if first:
				newPlace = {"id": "p" + str(placeCount), "initial": 1}
				first = False
			else:
				newPlace = {"id": "p" + str(placeCount)}

			pn["places"].append(newPlace)
			places_for_states.append((newPlace, state, placeCount))
			placeCount = placeCount+1

			correspondingActions = [action for action in rg["actions"] if action["src"][1] == state[1]]
			for action in correspondingActions:
				id = len(pn["transitions"])

				# Construct transition name
				transition_name = action["trans"]["id"] + " " + action["valuation"]

				# Create arc from place to the new transition
				pn["arcs"].append(
					{
						"source": newPlace,
						"target": {
							"id": id,
							"label": transition_name,
						},
					})

				# Create transition
				newTransition = {"id": id, "label": transition_name}
				pn["transitions"].append(newTransition)
				
				# We dont have the place to the outgoing state yet. Instead, we keep a list of pending out arcs to states
				pending_out_arcs.append((newTransition, action["tgt"][1]))

		for (t, state_id) in pending_out_arcs:
			matchingPlace = [(p,s,id2) for (p,s, id2) in places_for_states if s[1] == state_id][0]
			pn["arcs"].append(
				{"source": t, "target": matchingPlace[0]}
			)

		return pn

	def generate_tokens(n, vector_size, start):
		if vector_size == 0:
			return ([{"vector": [] * n}] * n, 0)
		else:
			return ([{"vector": [n for n in range(start, vector_size+start)]}] * n, vector_size)

	def reduce_id_in_trace(trace, reduce):
		for event in trace:
			result = ""
			index = 0
			if event["org:resource"] != None:
				for resource in event["org:resource"].split(","):
					resource = re.sub(r'[0-9]+$',
						lambda x: f"{str(int(x.group())-reduce).zfill(len(x.group()))}", resource)
					if index == 0:
						result = result + resource
					else:
						result = result + "," + resource
					index = index + 1
					
				event["org:resource"] = result

	def pnid_to_bounded_rg_pn(pnid, trace, manualBound, debug):

		if (manualBound == -1):
			# Determine max identifier in trace for upper bound
			(bound, reduce_trace_id) = PN.max_identifier_trace(trace, debug)

			if bound == -1:
				return PN([], -1)

			if bound != None:
				# Reduce the identifiers in trace after normalizing to 0
				PN.reduce_id_in_trace(trace, reduce_trace_id)
		else:
			bound = manualBound

		if debug:
			printer.print_trace_info(trace, bound)

		# Instead of first generating a graph with states and action we simplify by generating a petri net that represents the bounded reachability graph
		# Init place(s)
		initState = []
		lastID = 0
		generated_vars = []
		for p in pnid._places:
			if "initial" in p.keys():
				for arc in pnid._arcs:
					if arc["src"] == p["id"] and arc["inscription"] in [v for (v,id) in generated_vars]:
						current_id = [id for (v,id) in generated_vars if v == arc["inscription"]][0]
						(resources, lastID) = PN.generate_tokens(p["initial"], p["vector_size"], current_id)
					if arc["src"] == p["id"] and arc["inscription"] not in [v for (v,id) in generated_vars]:
						generated_vars.append((arc["inscription"], lastID))
						(resources, lastID) = PN.generate_tokens(p["initial"], p["vector_size"], lastID)
				initState.append(
					{
						"place": p,
						"amount": p["initial"],
						"resources": resources,
					}
				)
			else:
				initState.append({"place": p, "amount": 0, "resources": []})

		rg = {"states": [], "actions": []}

		# Add init state to RG
		rg = PN.build_rg(rg, pnid, (initState, 1), bound, -1, False)

		if debug and len(rg["states"]) == 1:
			print(
				"Warning: the init state of given trace does not allow for any path in the model, so petri net will only contain a place and no sync moves will be found."
			)
			print(
				"A possible cause is that the normalized bound determined from the trace is less than the amount of variables required for a transition in the model."
			)

		# Convert to PN
		pn = PN.convert_rg_to_pn(rg)

		return  PN(pn, bound)

	def get_identifier_bound(self):
		return self.identifier_bound

	def reachable_in_steps(self, i):
		return self._reachable_in_steps[i]

	def compute_reachable_in_steps(self, num_steps):
		self._reachable_in_steps = []
		dists = dict([(t["id"], t["fdist"]) for t in self.transitions()])
		transs = dict([(t["id"], t) for t in self._transitions])
		(src, tgt) = ("source", "target")
		places = [p["id"] for p in self._places if "initial" in p]
		for i in range(0, num_steps):
			remaining = num_steps - i
			transitions = [l[tgt]["id"] for l in self._arcs if l[src]["id"] in places]
			self._reachable_in_steps.append(
				[transs[t] for t in set(transitions) if dists[t] < remaining]
			)
			places = [a[tgt]["id"] for a in self._arcs if a[src]["id"] in transitions]