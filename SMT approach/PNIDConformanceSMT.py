import os
import time
import printing as printer
import log as Log
import tests as Tester
import experiments as Exp
import analyser as Analyser
import psutil
from pnid import PNID
from pn import PN
from smt.ysolver import YicesSolver
from encoding import Encoding

def get_process_memory():
	process = psutil.Process(os.getpid())
	return process.memory_info().rss / 1024 ** 2

def conformance_check_traces(pnid, traces, repeat, manualBound, debug):
	results = []	
	for n in range(0, repeat):
		# Conformance check each trace
		for trace in traces:
			solver = YicesSolver()
			time_conversion_start = time.perf_counter()

			mem_before = get_process_memory()

			pn = PN.pnid_to_bounded_rg_pn(pnid, trace, manualBound, debug)
			# Or, if you wish to provide the bounded RG as a file:
			# model = PN(
			#	 PN.read_pnml_input(os.path.join("data", "rg", "ExampleBoundedRG.pnml"))
			# )

			time_conversion = time.perf_counter() - time_conversion_start

			# Only try conformance checking if there is a model
			if len(pn.transitions()) > 0:
				# First compute the upper bound: length trace * 2
				trace_length = len(trace)
				bound = trace_length * 2
				if debug:
					printer.print_model_info(pn, bound)

				# Create a structure with all possible states combined with the steps needed, given the upperbound
				pn.compute_reachable_in_steps(bound)

				# Encode model
				encoding = Encoding(pn, solver, bound)

				# Start encode timer
				time_encode_start = time.perf_counter()

				# Encode other parts
				f_initial = encoding.initial_state()
				f_trans_range = encoding.transition_range()
				encoding.prepare_edit_distance(trace_length)
				solver.require([f_initial, f_trans_range])

				# End encode timer
				time_encode = time.perf_counter() - time_encode_start

				# Encode distance
				(dist, f_distance) = encoding.edit_distance(trace)
				encoding.solver().require([f_distance])

				model = encoding.solver().minimize_upordown(dist, encoding.bound())
				time_solve = encoding.solver().t_solve
				if model == None:
					results.append((None, time_conversion, time_encode, time_solve, alignment_decoded, pn))

				distance = model.eval_int(dist)
				alignment_decoded = encoding.decode_alignment(trace, model)
				mem_after = get_process_memory() - mem_before

				if debug:
					printer.print_trace_distance(
						time_conversion, time_encode, time_solve, distance
					)
					printer.print_trace_alignment(encoding._pn, trace, alignment_decoded)

				results.append((distance, time_conversion, time_encode, time_solve, alignment_decoded, pn, mem_after))

				if repeat > 1:
					# We try to clean up as much memory as we can for the next run
					del pn
					del trace_length
					del bound
					del encoding
					del f_initial
					del f_trans_range
					del model
					del distance
					del alignment_decoded
			else:
				if debug:
					print("Error: Petri net contains no transitions so conformance checking is impossible. Quitting..")

	avg_conversion_time = 0
	avg_encode_time = 0
	avg_solve_time = 0
	avg_total_time = 0
	avg_mem = 0

	times_conv = []
	times_encode = []
	times_solve = []
	memory = []
	distances = {}

	for (d, time_conv, time_enc, time_solve, alignment, pn, mem) in results:
		distances[d] = distances[d] + 1 if d in distances else 1
		times_conv.append(time_conv)
		times_encode.append(time_enc)
		times_solve.append(time_solve)
		memory.append(mem)

	if len(times_conv) > 0 and len(times_encode) > 0 and len(times_solve) > 0:
		mid = int(len(times_encode) / 2)
		avg_conversion_time = sum(times_conv) / len(times_conv)
		avg_encode_time = sum(times_encode) / len(times_encode)
		avg_solve_time = sum(times_solve) / len(times_solve)
		avg_total_time = sum(times_conv + times_encode + times_solve) / len(times_solve)
		avg_mem = sum(memory) / len(times_solve)

		if debug:
			print("\n##### AVERAGE RESULT")
			print(
				"conversion time: total %f avg %f median %f"
				% (sum(times_conv), avg_conversion_time, times_conv[mid])
			)
			print(
				"encoding time: total %f avg %f median %f"
				% (sum(times_encode), avg_encode_time, times_encode[mid])
			)
			print(
				"solving time:  total %f avg %f median %f"
				% (sum(times_solve), avg_solve_time, times_solve[mid])
			)
			print(
				"total time:  total %f avg %f"
				% (sum(times_solve + times_encode + times_solve), avg_total_time)
			)
			print(
				"memory:  avg %f" % (avg_mem)
			)
			for (d, cnt) in distances.items():
				print("distance %d: %d trace(s)" % (d, cnt))	 

	return (results, (avg_conversion_time, avg_encode_time, avg_solve_time, avg_total_time, avg_mem))

def testGeneralScenarios():
	print("\nGeneral scenarios:")
	Tester.testID1()
	Tester.testID2()
	Tester.testID3()
	Tester.testID4()
	Tester.testID5()
	Tester.testID6()
	Tester.testID7()

def testSpecificScenarios():
	print("\nSpecific scenarios:")
	Tester.testID8a()
	Tester.testID8b()
	Tester.testID9a()
	Tester.testID9b()
	Tester.testID10()
	Tester.testID11()
	Tester.testID12()
	Tester.testID13()
	Tester.testID14()
	Tester.testID15()
	Tester.testID16()
	Tester.testID17()
	Tester.testID18()
	Tester.testID19()
	Tester.testID20a()
	Tester.testID20b()
	Tester.testID20c()
	Tester.testID21a()
	Tester.testID21b()
	Tester.testID22()

def runExperiments():
	# Start experiment timer
	time_experiment_start = time.perf_counter()

	# Experiment config 
	# Note: the gc does not clean up everything of the Yices solver, so watch memory available
	runs = 1
	interval = 5
	N = 75

	# TIME EXPERIMENTS
	print("\nExperiment - easy:")
	if N == 5:
		Exp.experiment_easy(True, False, runs, N, N, interval, True)
	else:
		Exp.experiment_easy(True, False, runs, N, N, interval, False)

	if N == 5:
		Exp.experiment_easy(False, True, runs, N, N, interval, True)
	else:
		Exp.experiment_easy(False, True, runs, N, N, interval, False)

	# As the model contains no cycle it might be interesting to try to see effect of matching transitions opposed to non matching in previous two
	if N == 5:
		Exp.experiment_easy(True, True, runs, N, N, interval, True)
	else:
		Exp.experiment_easy(True, True, runs, N, N, interval, False)

	print("\nExperiment - easy (all matching):")
	if N == 5:
		Exp.experiment_easy_alternative(True, False, runs, N, N, interval, True, True)
	else:
		Exp.experiment_easy_alternative(True, False, runs, N, N, interval, False, True)

	if N == 5:
		Exp.experiment_easy_alternative(False, True, runs, N, N, interval, True, True)
	else:
		Exp.experiment_easy_alternative(False, True, runs, N, N, interval, False, True)

	print("\nExperiment - easy (only two matching):")
	if N == 5:
		Exp.experiment_easy_alternative(True, False, runs, N, N, interval, True, False)
	else:
		Exp.experiment_easy_alternative(True, False, runs, N, N, interval, False, False)

	if N == 5:
		Exp.experiment_easy_alternative(False, True, runs, N, N, interval, True, False)
	else:
		Exp.experiment_easy_alternative(False, True, runs, N, N, interval, False, False)

	print("\nExperiment - average:")
	if N == 5:
		Exp.experiment_average(True, False, runs, N, N, interval, True)
	else:
		Exp.experiment_average(True, False, runs, N, N, interval, False)

	if N == 5:
		Exp.experiment_average(False, True, runs, N, N, interval, True)
	else:
		Exp.experiment_average(False, True, runs, N, N, interval, False)

	print("\nExperiment - hard:")
	if N == 5:
		Exp.experiment_hard(False, True, runs, N, N, interval, True)
	else:
		Exp.experiment_hard(False, True, runs, N, N, interval, False)

	if N == 5:
		Exp.experiment_hard(False, True, runs, N, N, interval, True)
	else:
		Exp.experiment_hard(False, True, runs, N, N, interval, False)

	# MEMORY EXPERIMENTS
	print("\nExperiment - easy:")
	Exp.experiment_easy(True, False, 1, 10, 100, interval, True)
	Exp.experiment_easy(True, False, 1, 110, 200, interval, False)
	Exp.experiment_easy(True, False, 1, 210, 300, interval, False)
	Exp.experiment_easy(False, True, 1, 10, 100, interval, True)
	Exp.experiment_easy(False, True, 1, 110, 200, interval, False)
	Exp.experiment_easy(False, True, 1, 210, 300, interval, False)
	Exp.experiment_easy(True, True, 1, 10, 100, interval, True)
	Exp.experiment_easy(True, True, 1, 110, 200, interval, False)
	Exp.experiment_easy(True, True, 1, 210, 300, interval, False)

	print("\nExperiment - average:")
	Exp.experiment_average(True, False, 1, 10, 100, interval, True)
	Exp.experiment_average(True, False, 1, 110, 200, interval, False)
	Exp.experiment_average(True, False, 1, 210, 300, interval, False)
	Exp.experiment_average(False, True, 1, 10, 100, interval, True)
	Exp.experiment_average(False, True, 1, 110, 200, interval, False)
	Exp.experiment_average(False, True, 1, 210, 300, interval, False)
	
	print("\nExperiment - hard:")
	Exp.experiment_hard(True, False, 1, 10, 100, interval, True)
	Exp.experiment_hard(True, False, 1, 110, 200, interval, False)
	Exp.experiment_hard(True, False, 1, 210, 300, interval, False)
	Exp.experiment_hard(False, True, 1, 10, 100, interval, True)
	Exp.experiment_hard(False, True, 1, 110, 200, interval, False)
	Exp.experiment_hard(False, True, 1, 210, 300, interval, False)

	# End encode timer
	time_experiment = time.perf_counter() - time_experiment_start
	print("\nExperiment - total time (s): %f " % time_experiment)

def experiment_results_to_plot():
	Analyser.analyse_time("times - Easy (model increase).csv", "Model size")
	Analyser.analyse_time("times - Easy (trace increase).csv", "Trace size")
	Analyser.analyse_time("times - Easy (model+trace increase).csv", "Trace size")
	Analyser.analyse_time("times - Easy (model increase+all matching).csv", "Model size")
	Analyser.analyse_time("times - Easy (model increase+not matching).csv", "Model size")
	Analyser.analyse_time("times - Easy (trace increase+all matching).csv", "Trace size")
	Analyser.analyse_time("times - Easy (trace increase+not matching).csv", "Trace size")
	Analyser.analyse_time("times - Average (model increase).csv", "Model size")
	Analyser.analyse_time("times - Average (trace increase).csv", "Trace size")
	Analyser.analyse_time("times - Average (trace increase+constant id bound).csv", "Trace size")
	Analyser.analyse_time("times - Hard (model increase).csv", "Model size")
	Analyser.analyse_time("times - Hard (trace increase).csv", "Trace size")
	Analyser.analyse_time("times - Hard (trace increase+constant id bound).csv", "Trace size")

if __name__ == "__main__":

	# Tests
	testGeneralScenarios()
	testSpecificScenarios()

	# Experiments
	# runExperiments()

	# Results to plot images
	# experiment_results_to_plot()