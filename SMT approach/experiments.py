import os
import PNIDConformanceSMT as main
import log as Log
from pnid import PNID
import csv
import re
from collections import Counter

def experiment_easy(model_increase, trace_increase, runs, minN, N, interval, init):
	pnid = PNID.read_pnml_input(
		os.path.join("data", "model", "experiments", "easy.pnml")
	)
	log = Log.load_log_from_CSV(os.path.join("data", "log", "experiments", "easy.csv"))

	runs = runs
	debug = False
	
	counter = 0
	if model_increase and trace_increase:
		name = "Easy (model+trace increase)"
		if init == True:			
			init_results_file(name)
		while len(pnid.transitions()) < N and len(log[0]) < N:
			if counter == 0:
				pnid = increase_model(pnid, len(pnid.transitions()), minN-len(pnid.transitions()))
				log = increase_trace_easy(log, len(log[0]), minN-len(log[0]))
				(result, time_info) = main.conformance_check_traces(pnid, log, runs, -1, debug)
				write_result_to_file(name, len(pnid.transitions()), len(log[0]), result, time_info)
			else:
				pnid = increase_model(pnid, len(pnid.transitions()), interval)
				log = increase_trace_easy(log, len(log[0]), interval)
				(result, time_info) = main.conformance_check_traces(pnid, log, runs, -1, debug)
				write_result_to_file(name, len(pnid.transitions()), len(log[0]), result, time_info)

			counter = counter + 1
	else:
		if model_increase:
			name = "Easy (model increase)"
			if init == True:
				init_results_file(name)
			while len(pnid.transitions()) < N:
				if counter == 0:
					pnid = increase_model(pnid, len(pnid.transitions()), minN-len(pnid.transitions()))
					(result, time_info) = main.conformance_check_traces(pnid, log, runs, -1, debug)
					write_result_to_file(name, len(pnid.transitions()), len(log[0]), result, time_info)
				else:
					pnid = increase_model(pnid, len(pnid.transitions()), interval)
					(result, time_info) = main.conformance_check_traces(pnid, log, runs, -1, debug)
					write_result_to_file(name, len(pnid.transitions()), len(log[0]), result, time_info)

				counter = counter + 1

		if trace_increase:
			name = "Easy (trace increase)"
			if init == True:	
				init_results_file(name)
			while len(log[0]) < N:
				if counter == 0:
					log = increase_trace_easy(log, len(log[0]), minN-len(log[0]))
					(result, time_info) = main.conformance_check_traces(pnid, log, runs, -1, debug)
					write_result_to_file(name, len(pnid.transitions()), len(log[0]), result, time_info)
				else:
					log = increase_trace_easy(log, len(log[0]), interval)
					(result, time_info) = main.conformance_check_traces(pnid, log, runs, -1, debug)
					write_result_to_file(name, len(pnid.transitions()), len(log[0]), result, time_info)

				counter = counter + 1


def experiment_easy_alternative(model_increase, trace_increase, runs, minN, N, interval, init, match):
	pnid = PNID.read_pnml_input(
		os.path.join("data", "model", "experiments", "easy.pnml")
	)
	log = Log.load_log_from_CSV(os.path.join("data", "log", "experiments", "easy.csv"))

	runs = runs
	debug = False
	
	counter = 0
	if model_increase:
		if match == True:
			name = "Easy (model increase+all matching)"
		else:
			name = "Easy (model increase+not matching)"
		if init == True:
			init_results_file(name)
		while len(pnid.transitions()) < N:
			if counter == 0:
				log = increase_trace_easy(log, len(log[0]), 73, match)
				pnid = increase_model(pnid, len(pnid.transitions()), minN-len(pnid.transitions()))
				(result, time_info) = main.conformance_check_traces(pnid, log, runs, -1, debug)
				write_result_to_file(name, len(pnid.transitions()), len(log[0]), result, time_info)
			else:
				pnid = increase_model(pnid, len(pnid.transitions()), interval)
				(result, time_info) = main.conformance_check_traces(pnid, log, runs, -1, debug)
				write_result_to_file(name, len(pnid.transitions()), len(log[0]), result, time_info)

			counter = counter + 1

	if trace_increase:
		if match == True:
			name = "Easy (trace increase+all matching)"
		else:
			name = "Easy (trace increase+not matching)"
		if init == True:	
			init_results_file(name)
		while len(log[0]) < N:
			if counter == 0:
				log = increase_trace_easy(log, len(log[0]), minN-len(log[0]), match)
				pnid = increase_model(pnid, len(pnid.transitions()), 73)
				(result, time_info) = main.conformance_check_traces(pnid, log, runs, -1, debug)
				write_result_to_file(name, len(pnid.transitions()), len(log[0]), result, time_info)
			else:
				log = increase_trace_easy(log, len(log[0]), interval, match)
				(result, time_info) = main.conformance_check_traces(pnid, log, runs, -1, debug)
				write_result_to_file(name, len(pnid.transitions()), len(log[0]), result, time_info)

			counter = counter + 1

def increase_model(model, id, amount):
	while amount > 0:
		lastPlace = model.places()[len(model.places())-1]
		inArc = {
					"src": lastPlace["id"],
					"tgt": "dummy_t" + str(id),
					"id": "inArc" + str(id),
					"inscription": "",
				}
		newPlace = {"id": "dummy_p" + str(id+1), "vector_size": 0}
		outArc = {
					"src": "dummy_t" + str(id),
					"tgt": newPlace["id"],
					"id": "outArc"+ str(id),
					"inscription": "",
				}
		model.arcs().append(inArc)
		model.arcs().append(outArc)
		model.places().append(newPlace)
		t = {"id": "dummy_t" + str(id), "inArcs": [inArc], "outArcs": [outArc]}
		model.transitions().append(t)
		id = id + 1
		amount = amount - 1

	return model

def increase_trace_easy(log, id, amount, match=True):
	while amount > 0:
		if match == True:
			log[0]._list.append({'concept:instance': 1, 'concept:name': "dummy_t" + str(id), 'org:resource': None, 'time:timestamp': '2000-01-01 00:00:00+0000'})
		else:
			log[0]._list.append({'concept:instance': 1, 'concept:name': "wrong_t" + str(id), 'org:resource': None, 'time:timestamp': '2000-01-01 00:00:00+0000'})
		id = id + 1
		amount = amount - 1

	return log

def experiment_average(model_increase, trace_increase, runs, minN, N, interval, init):
	pnid = PNID.read_pnml_input(
		os.path.join("data", "model", "experiments", "average.pnml")
	)
	log = Log.load_log_from_CSV(os.path.join("data", "log", "experiments", "average.csv"))

	runs = runs
	debug = False
	
	counter = 0
	if model_increase:
		name = "Average (model increase)"
		if init == True:
			init_results_file(name)
		while len(pnid.transitions()) < N:
			if counter == 0:
				pnid = increase_model(pnid, len(pnid.transitions()), minN,-len(pnid.transitions()))
				(result, time_info) = main.conformance_check_traces(pnid, log, runs, -1, debug)
				write_result_to_file(name, len(pnid.transitions()), len(log[0]), result, time_info)
			else:
				pnid = increase_model(pnid, len(pnid.transitions()), interval)
				(result, time_info) = main.conformance_check_traces(pnid, log, runs, -1, debug)
				write_result_to_file(name, len(pnid.transitions()), len(log[0]), result, time_info)

			counter = counter + 1

	if trace_increase:
		name = "Average (trace increase)"
		if init == True:
			init_results_file(name)
		while len(log[0]) < N:
			if counter == 0:
				log = increase_trace_average(log, minN-len(log[0]), True)
				(result, time_info) = main.conformance_check_traces(pnid, log, runs, -1, debug)
				write_result_to_file(name, len(pnid.transitions()), len(log[0]), result, time_info)
			else:
				log = increase_trace_average(log, interval, True)
				(result, time_info) = main.conformance_check_traces(pnid, log, runs, -1, debug)
				write_result_to_file(name, len(pnid.transitions()), len(log[0]), result, time_info)

			counter = counter + 1
		
		log = Log.load_log_from_CSV(os.path.join("data", "log", "experiments", "average.csv"))
		counter = 0
		name = "Average (trace increase+constant id bound)"
		if init == True:
			init_results_file(name)
		while len(log[0]) < N:
			if counter == 0:
				log = increase_trace_average(log, minN-len(log[0]), False)
				(result, time_info) = main.conformance_check_traces(pnid, log, runs, -1, debug)
				write_result_to_file(name, len(pnid.transitions()), len(log[0]), result, time_info)
			else:
				log = increase_trace_average(log, interval, False)
				(result, time_info) = main.conformance_check_traces(pnid, log, runs, -1, debug)
				write_result_to_file(name, len(pnid.transitions()), len(log[0]), result, time_info)

			counter = counter + 1

def increase_trace_average(log, amount, increase_id):
	if increase_id == True:
		id = int(re.findall(r'\d+', log[0]._list[-2]['org:resource'])[0]) + 1
	else:
		id = int(re.findall(r'\d+', log[0]._list[-2]['org:resource'])[0])

	while amount > 0:
		log[0]._list.append({'concept:instance': 1, 'concept:name': "T", 'org:resource': "a" + str(id), 'time:timestamp': '2000-01-01 00:00:00+0000'})
		log[0]._list.append({'concept:instance': 1, 'concept:name': "U", 'org:resource': None, 'time:timestamp': '2000-01-01 00:00:00+0000'})
		if increase_id == True:
			id = id + 1
		amount = amount - 2

	return log

def experiment_hard(model_increase, trace_increase, runs, minN, N, interval, init):
	pnid = PNID.read_pnml_input(
		os.path.join("data", "model", "experiments", "hard.pnml")
	)
	log = Log.load_log_from_CSV(os.path.join("data", "log", "experiments", "hard.csv"))

	runs = runs
	debug = False
	
	counter = 0
	if model_increase:
		name = "Hard (model increase)"
		if init == True:
			init_results_file(name)
		while len(pnid.transitions()) < N:
			if counter == 0:
				pnid = increase_model(pnid, len(pnid.transitions()), minN-len(pnid.transitions()))
				(result, time_info) = main.conformance_check_traces(pnid, log, runs, -1, debug)
				write_result_to_file(name, len(pnid.transitions()), len(log[0]), result, time_info)
			else:
				pnid = increase_model(pnid, len(pnid.transitions())+1, interval)
				(result, time_info) = main.conformance_check_traces(pnid, log, runs, -1, debug)
				write_result_to_file(name, len(pnid.transitions()), len(log[0]), result, time_info)

			counter = counter + 1

	if trace_increase:
		name = "Hard (trace increase)"
		if init == True:
			init_results_file(name)
		id = 2
		while len(log[0]) < N:
			if counter == 0:
				(log, newID) = increase_trace_hard(log, id, minN-len(log[0]), False)
				id = newID
				(result, time_info) = main.conformance_check_traces(pnid, log, runs, -1, debug)
				write_result_to_file(name, len(pnid.transitions()), len(log[0]), result, time_info)
			else:
				(log, newID) = increase_trace_hard(log, id+1, interval, False)
				id = newID
				(result, time_info) = main.conformance_check_traces(pnid, log, runs, -1, debug)
				write_result_to_file(name, len(pnid.transitions()), len(log[0]), result, time_info)
			counter = counter + 1

		log = Log.load_log_from_CSV(os.path.join("data", "log", "experiments", "hard.csv"))
		counter = 0	
		id = 2
		name = "Hard (trace increase+constant id bound)"
		if init == True:
			init_results_file(name)
		while len(log[0]) < N:
			if counter == 0:
				(log, newID) = increase_trace_hard(log, id, minN-len(log[0]), False)
				(result, time_info) = main.conformance_check_traces(pnid, log, runs, -1, debug)
				write_result_to_file(name, len(pnid.transitions()), len(log[0]), result, time_info)
			else:
				(log, newID) = increase_trace_hard(log, id, interval, False)
				(result, time_info) = main.conformance_check_traces(pnid, log, runs, -1, debug)
				write_result_to_file(name, len(pnid.transitions()), len(log[0]), result, time_info)

			counter = counter + 1

def increase_model_hard(model, id, amount):
	firstPlace = model.places()[0]
	place = firstPlace
	
	arcs = []
	places = []
	transitions = []
	
	while amount > 0:	
		inArc = {
					"src": place["id"],
					"tgt": "dummy_t" + str(id),
					"id": "inArc" + str(id),
					"inscription": "",
				}
		newPlace = {"id": "dummy_p" + str(id+1), "vector_size": 0}
		outArc = {
					"src": "dummy_t" + str(id),
					"tgt": newPlace["id"],
					"id": "outArc"+ str(id),
					"inscription": "",
				}
			
		arcs.append(inArc)
		arcs.append(outArc)
		places.append(newPlace)

		t = {"id": "dummy_t" + str(id), "inArcs": [inArc], "outArcs": [outArc]}
		transitions.append(t)

		place = newPlace
		id = id + 1
		amount = amount - 1

	for arc in model.arcs():
		if arc["src"] == firstPlace["id"]:
			arc["src"] = newPlace["id"]

	for a in arcs:
		model.arcs().append(a)

	for p in places:
		model.places().append(p)

	for t in transitions:
		model.transitions().append(t)

	return model

def increase_trace_hard(log, id, amount, increase_id):
	orig_id = id
	orig_amount = amount

	temp = log[0]._list[-2:]
	tempItem = log[0]._list[-3:][0]

	log[0]._list = log[0]._list[:len(log[0]._list)-3]

	add_products = []
	add_items = []

	amount = amount / 2
	while amount > 0:
		add_products.append({'concept:instance': 1, 'concept:name': "AddProduct", 'org:resource': "o0,p" + str(id), 'time:timestamp': '2000-01-01 00:00:00+0000'})
		amount = amount - 1
		if increase_id == True:
			id = id + 1

	for row in add_products:
		log[0]._list.append(row)
	
	log[0]._list.append(tempItem)

	id = orig_id
	amount = orig_amount

	amount = amount / 2
	while amount > 0:
		add_items.append({'concept:instance': 1, 'concept:name': "AddItem", 'org:resource': "o0,p" + str(id) + ",d1", 'time:timestamp': '2000-01-01 00:00:00+0000'})
		amount = amount - 1
		if increase_id == True:
			id = id + 1

	for row in add_items:
		log[0]._list.append(row)

	log[0]._list.extend(temp)

	return (log, id)

def init_results_file(name):
	with open('results/times - ' + name + '.csv', 'w', newline='') as file:
		writer = csv.writer(file)
		writer.writerow(["Experiment", "Model size", "Trace size", "ID bound", "PN size", "matching", "avg_conv_time", "avg_encode_time", "avg_solve_time", "avg_total_time", "avg_memory"])

def write_result_to_file(name, model_size, log_size, result, info):
	pn_size = len([t for t in result[0][5].transitions() if ("invisible" not in t)])
	alignment = result[0][4]["alignment"]
	amount_sync = Counter(alignment)["parallel"]
	identifier_bound = result[0][5].get_identifier_bound()
	with open('results/times - ' + name + '.csv', 'a', newline='') as file:
		writer = csv.writer(file)
		writer.writerow([name, model_size, log_size, identifier_bound, pn_size, amount_sync, info[0], info[1], info[2], info[3], info[4]])