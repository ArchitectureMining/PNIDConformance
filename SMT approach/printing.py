import sys

def spaces(n):
	return "" if n <= 0 else " " + spaces(n - 1)

def fill_to(s, n):
	return s + spaces(n - len(s)) if len(s) < n else s[:n]

def print_sequence(seq, tab=12):
	a = spaces(tab + 1)
	# Print transition label sequence (or >> for skip step)
	for i in range(0, len(seq)):
		if seq[i] is not None and "concept:name" in seq[i]:
			eventLabel = str(seq[i]["concept:name"])
			eventResources = str(seq[i]["org:resource"]) if seq[i]["org:resource"] != None else ""
			a += (
				fill_to(
					eventLabel + " [" + eventResources + "]",
					tab,
				)
				+ " "
				if seq[i]
				else "  >>" + spaces(tab - 3)
			)
		else:
			a += (
				fill_to(seq[i]["label"], tab) + " "
				if seq[i]
				else "  >>" + spaces(tab - 3)
			)
	print(a)

def print_trace_info(trace, identifier_bound):
	print("\n##### LOG")
	print("ID : " + str(trace[0]["concept:instance"]), flush=True)
	print("Length : " + str(len(trace)), flush=True)
	print(
		"Bound on identifier (normalized from 0) : " + str(identifier_bound), flush=True
	)

def print_model_info(pn, bound):
	visible_transitions = []
	for t in pn.transitions():
		if "invisible" not in t:
			visible_transitions.append(t)

	print("##### MODEL")
	print("Amount of transitions : " + str(len(visible_transitions)), flush=True)
	print("Step upperbound : " + str(bound), flush=True)

def print_trace_distance(time_conv, time_enc, time_solve, distance):
	print("##### CONFORMANCE CHECKING")
	print("DISTANCE : " + str(distance), flush=True)
	print("time/conversion: %f time/encode: %f  time/solve: %f" % (time_conv, time_enc, time_solve))
	print("time/total: %f" % (time_conv + time_enc + time_solve))

def print_trace_alignment(pn, trace, decoding):
	places = dict([(p["id"], p) for p in pn.places()])
	print("\nMARKING:")
	for i in range(0, len(decoding["markings"])):
		marking = ""
		for (p, count) in list(decoding["markings"][i].items()):
			for c in range(0, count):
				marking = marking + (" " if marking else "") + str(places[p]["id"])
		print("  %d: %s" % (i, marking))

	# Shift in model and log sequences to account for the opposite sides of model or log moves in alignment (>>)
	modelseq = []
	idx = 0
	count = 0
	for i in range(0, len(decoding["alignment"])):
		if count != len(trace):
			if decoding["alignment"][i] != "log":
				# Sync or model move
				(tid, tlab) = decoding["transitions"][idx]
				if tlab != "tau":
					count = count + 1
					step = {"id": tid, "label": tlab}
					modelseq.append(step)
				if (idx < len(decoding["transitions"])-1):
					idx += 1
			else:
				modelseq.append(None)
	traceseq = []
	idx = 0
	for i in range(0, len(decoding["alignment"])):
		if decoding["alignment"][i] != "model":
			# Sync or log move
			traceseq.append(trace[idx])
			idx += 1
		else:
			if len(traceseq) + 1 <= len(modelseq):
				traceseq.append(None)

	print("LOG SEQUENCE:")
	print_sequence(traceseq)
	print("\nMODEL SEQUENCE:")
	print_sequence(modelseq)
	sys.stdout.flush()
