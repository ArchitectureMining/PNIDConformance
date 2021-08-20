from functools import reduce
import re

class Encoding:
	def __init__(self, pn, solver, bound):
		self._pn = pn
		self._solver = solver
		self._bound = bound
		self._vs_trans = self.trans_vars()
		self._vs_mark = self.marking_vars()

	def pn(self):
		return self._pn

	def solver(self):
		return self._solver

	def bound(self):
		return self._bound

	# Create integer variable to capture transition for every instant
	def trans_vars(self):
		name = lambda i: "trans" + str(i)
		return [self._solver.intvar(name(i)) for i in range(0, self._bound)]

	# Returns list mcs such that mvs[i] is dictionary mapping place id to integer
	# variable for number of tokens n, i.e. mvs[i][place_id] = n
	def marking_vars(self):
		s = self._solver

		def mvar(i, id):
			name = "marked_" + str(i) + "_" + str(id)
			return s.boolvar(name)

		mvs = lambda i: dict([(p["id"], mvar(i, p["id"])) for p in self._pn.places()])
		return [mvs(i) for i in range(0, self._bound + 1)]

	# All transition variables tvs[i] have as value a transition id that is reachable in i steps in the net
	def transition_range(self):
		s = self._solver
		pn = self._pn
		tvs = self._vs_trans

		rng = lambda i, v: s.lor(
			[s.eq(v, s.num(t["id"])) for t in pn.reachable_in_steps(i)]
		)
		rng_constr = [rng(i, v) for (i, v) in enumerate(tvs)]
		tau_transs = [t for t in pn.transitions() if not t["label"]]
		is_tau = lambda v: s.lor([s.eq(v, s.num(t["id"])) for t in tau_transs])
		butlast = range(0, len(tvs) - 1)
		tau_constr = [s.implies(is_tau(tvs[i]), is_tau(tvs[i + 1])) for i in butlast]

		return s.land(rng_constr + tau_constr)

	def initial_state(self):
		s = self._solver
		mvs = self._vs_mark
		mcount = [
			(p["id"], p["initial"] if "initial" in p else 0) for p in self._pn.places()
		]
		marking0 = [mvs[0][p] if c > 0 else s.neg(mvs[0][p]) for (p, c) in mcount]
		return s.land(marking0)

	def edit_distance_vars(self, trace_len):
		s = self._solver

		def var(i, j):
			return s.intvar("d" + str(i) + "_" + str(j)) if i > 0 or j > 0 else s.num(0)

		return [
			[var(i, j) for j in range(0, trace_len + 1)]
			for i in range(0, self._bound + 1)
		]

	def prepare_edit_distance(self, len_trace):
		self._vs_dist = self.edit_distance_vars(len_trace)

	def edit_distance(self, trace):
		self._vs_dist = self.edit_distance_vars(len(trace))
		delta = self._vs_dist
		n = self._bound
		m = len(trace)
		s = self._solver
		pn = self._pn
		vs_trans = self._vs_trans
		etrans = [(t["id"], t) for t in pn.transitions()]

		# Cost of a transition
		def cost(t):
			return 0 if "invisible" in t and t["invisible"] else 1

		costvars = [s.intvar("cost" + str(t["id"])) for t in pn.transitions()]
		ws = [s.eq(v, s.num(cost(t))) for (v, t) in zip(costvars, pn.transitions())]
		cost = dict([(t["id"], v) for (t, v) in zip(pn.transitions(), costvars)])

		def sync_step(i, j):
			return [
				(s.eq(self._vs_trans[i], s.num(t["id"])))
				for t in self._pn.reachable_in_steps(i)
				if "invisible" not in t and t["label"].split("[")[0].replace(" ", "") == str(trace[j]["concept:name"])
				and (trace[j]["org:resource"] == None or all(
					c in [re.split("(\d.*)", e)[1] for e in trace[j]["org:resource"].replace(" ", "").split(",")]
					for c in (t["label"].replace(" ", ""))[
						(t["label"].replace(" ", "")).find("[") + 1 : (t["label"].replace(" ", "")).find("]")
					].split(",")))
				and (trace[j]["org:resource"] == None or all(
						re.split("(\d.*)", c)[1] in (t["label"].replace(" ", ""))[(t["label"].replace(" ", "")).find("[") + 1 : (t["label"].replace(" ", "")).find("]")].split(",")
						for c in trace[j]["org:resource"].split(",")
					))
			]

		def async_step(i, j):
			return [
				(s.eq(vs_trans[i], s.num(t["id"])), cost[t["id"]])
				for t in pn.reachable_in_steps(i)
				if "invisible" not in t and (t["label"].split("[")[0].replace(" ", "") != str(trace[j]["concept:name"])
				or (trace[j]["org:resource"] != None and all(
					c in [re.split("(\d.*)", e)[1] for e in trace[j]["org:resource"].replace(" ", "").split(",")]
					for c in (t["label"].replace(" ", ""))[
						(t["label"].replace(" ", "")).find("[") + 1 : (t["label"].replace(" ", "")).find("]")
					].split(",")
				)
				== False)
				or (trace[j]["org:resource"] != None and all(
					re.split("(\d.*)", c)[1] in (t["label"].replace(" ", ""))[(t["label"].replace(" ", "")).find("[") + 1 : (t["label"].replace(" ", "")).find("]")].split(",")
					for c in trace[j]["org:resource"].split(",")
				)
				== False))
			]
			
		# Costs for vs_trans[i], optional alternative over all transitions
		def costs(i):
			var = vs_trans[i]
			return reduce(
				lambda c, t: s.ite(s.eq(var, s.num(t[0])), cost[t[1]["id"]], c),
				etrans,
				s.num(0),
			)

		def is_invisible(i): # Transition i is invisible
			return s.lor(
				[
					s.eq(vs_trans[i], s.num(id))
					for (id, t) in etrans
					if t in pn.reachable_in_steps(i) and "invisible" in t and t["invisible"]
				]
			)

		invisibles = [is_invisible(i) for i in range(0, n)]
		self._invisibles = [s.boolvar("invisible" + str(i)) for i in range(0, n)]
		iis = [s.iff(v, e) for (v, e) in zip(self._invisibles, invisibles)]

		# delta[i][j] represents the edit distance of transition sequence up to
		# including i, and the log up to including j
		# 1. Intermediate distances delta[i][j] are non-negative
		non_neg = [
			s.ge(delta[i][j], s.num(0))
			for i in range(0, n + 1)
			for j in range(0, m + 1)
		]
		# 2. If the ith transition is visible, delta[i+1][0] = delta[i][0] + cost(i)
		#	where cost(i) is the cost of the ith transition in the model
		incdelta0 = [s.intvar("incd0" + str(i)) for i in range(0, n)]
		bm = [s.eq(incdelta0[i], s.plus(delta[i][0], costs(i))) for i in range(0, n)]
		base_model = [
			s.implies(s.neg(self._invisibles[i]), s.ge(delta[i + 1][0], incdelta0[i]))
			for i in range(0, n)
		]
		# 3. delta[0][j+1] = (j + 1)
		base_log = [s.eq(delta[0][j + 1], s.num(j + 1)) for j in range(0, m)]
		# 4. If the ith step in the model and the jth step in the log have the
		#	the same label and resources, delta[i+1][j+1] = delta[i][j]
		step_equal = [
			s.implies(
				is_t,
				s.ge(
					delta[i + 1][j + 1],
					delta[i][j]
				),
			)
			for i in range(0, n)
			for j in range(0, m)
			for is_t in sync_step(i, j)
		]

		# 5. The ith step in the model and the jth step in the log have different
		#	labels or resources: delta[i+1][j+1] is minimum of delta[i][j+1], delta[i+1][j]
		#	plus respective penalty values
		side_constr = []
		for i in range(0, n):
			reachable_labels = set(
				[t["label"].split("[")[0].replace(" ", "") for k in range(i, n) for t in pn.reachable_in_steps(k) if t["label"] != None]
			)
			for j in range(0, m):
				lstep = s.intvar("delta_log" + str(i) + str(j))
				side_constr.append(s.eq(lstep, s.inc(delta[i + 1][j])))

				if trace[j]["concept:name"] in reachable_labels or j == 0 or j == m - 1:
					for (is_t, penalty) in async_step(i, j):
						mstep = s.plus(penalty, delta[i][j + 1])
						imp = s.implies(
							is_t,
							s.lor(
								[
									s.ge(delta[i + 1][j + 1], mstep),
									s.ge(delta[i + 1][j + 1], lstep),
								]
							),
						)
						side_constr.append(imp)
				else:
					side_constr.append(s.ge(delta[i + 1][j + 1], lstep))

		# 6. If the ith step in the model is invisible, delta[i+1][j] = delta[i][j],
		#	that is, invisible transitions are dummy transitions and do not increase the distance
		invisible_constr = [
			s.implies(self._invisibles[i], s.eq(delta[i + 1][j], delta[i][j]))
			for i in range(0, n)
			for j in range(0, m + 1)
		]

		constraints_f_edit_distance = (
			non_neg
			+ base_model
			+ base_log
			+ step_equal
			+ side_constr
			+ invisible_constr
			+ iis
			+ ws
			+ bm
		)

		return (delta[n][m], s.land(constraints_f_edit_distance))

	def decode_alignment(self, trace, model):
		pn = self._pn
		transs = dict([(p["id"], p) for p in pn.transitions()])
		tlabel = lambda i: "tau" if transs[i]["label"] == None else transs[i]["label"]
		vs_mark = self._vs_mark
		vs_dist = self._vs_dist
		markings = []
		transitions = []

		for i in range(0, self.bound()):
			mark = [(p, model.eval_int(c)) for (p, c) in list(vs_mark[i].items())]
			markings.append(dict(mark))
			if i < self.bound()+1:
				tid = model.eval_int(self._vs_trans[i])
				transitions.append((tid, tlabel(tid)))

		alignment = []  # Sequence of {"log", "model", "sync"}
		i = self._bound  # n
		j = len(trace)  # m

		while i > 0 or j > 0:
			if j == 0 or model.eval_bool(self._invisibles[i - 1]):
				alignment.append("model")
				i -= 1
			elif i == 0:
				alignment.append("log")
				j -= 1
			elif transitions[i - 1][1].split("[")[0].replace(" ", "") == str(trace[j - 1]["concept:name"]) and (trace[j-1]["org:resource"] == None or all(
				c in trace[j - 1]["org:resource"]
				for c in (transitions[i - 1][1].replace(" ", ""))[
					(transitions[i - 1][1].replace(" ", "")).find("[")
					+ 1 : (transitions[i - 1][1].replace(" ", "")).find("]")
				]
			)):
				alignment.append("sync")
				i -= 1
				j -= 1
			else:
				dist = model.eval_int(vs_dist[i][j])
				dist_log = model.eval_int(vs_dist[i][j - 1]) + 1
				dist_model = model.eval_int(vs_dist[i - 1][j]) + 1
				assert dist == dist_log or dist == dist_model
				if dist == dist_log:
					alignment.append("log")
					j -= 1
				else:
					alignment.append("model")
					i -= 1
		alignment.reverse()
		return {
			"transitions": transitions,
			"markings": markings,
			"alignment": alignment,
		}
