import os
import PNIDConformanceSMT as main
import log as Log
from pnid import PNID

def testID1():
    # No matching events lead to only log and model moves
    pnid = PNID.read_pnml_input(
        os.path.join("data", "model", "tests", "testID1.pnml")
    )
    log = Log.load_log_from_CSV(os.path.join("data", "log", "tests", "testID1.csv"))

    runs = 1
    debug = False

    (result, time_info) = main.conformance_check_traces(pnid, log, runs, -1, debug)
    alignment = result[0][4]["alignment"]
    print("Test 1: " + str(("sync" in alignment) == False) + " (no matching events)")

def testID2():
    # Partially events (events with matching label but not matching valuation, still lead to only log and model moves
    # NOTE: under the assumption that the normalized bound determined from trace is not less than the amount of identifiers used in the model. If this is the case the construction of the bounded rg is not possible (no transitions to fire) and a different result should be expected.
    pnid = PNID.read_pnml_input(
        os.path.join("data", "model", "tests", "testID2.pnml")
    )
    log = Log.load_log_from_CSV(os.path.join("data", "log", "tests", "testID2.csv"))

    runs = 1
    debug = False

    (result, time_info) = main.conformance_check_traces(pnid, log, runs, -1, debug)
    alignment = result[0][4]["alignment"]
    print("Test 2: " + str(("sync" in alignment) == False) + " (partial matching events)")

def testID3():
    # All events match leads to only sync moves
    pnid = PNID.read_pnml_input(
        os.path.join("data", "model", "tests", "testID3.pnml")
    )
    log = Log.load_log_from_CSV(os.path.join("data", "log", "tests", "testID3.csv"))

    runs = 1
    debug = False

    (result, time_info) = main.conformance_check_traces(pnid, log, runs, -1, debug)
    alignment = result[0][4]["alignment"][:2]
    print("Test 3: " + str(("log" in alignment) == False and ("model" in alignment) == False) + " (all events match)")

def testID4():
    # Non linear increment of identifier in the trace between events, starts with sync move but ends with model/log move
    pnid = PNID.read_pnml_input(
        os.path.join("data", "model", "tests", "testID4.pnml")
    )
    log = Log.load_log_from_CSV(os.path.join("data", "log", "tests", "testID4.csv"))

    runs = 1
    debug = False

    (result, time_info) = main.conformance_check_traces(pnid, log, runs, -1, debug)
    alignment = result[0][4]["alignment"]
    print("Test 4: " + str((alignment[0] == "sync") and (alignment[1] == "log") and (alignment[2] == "log") and (alignment[3] == "log")) + " (non-linear increment of identifier in trace)")

def testID5():
    # Identifier in trace is not increased while a new variable is created in model, starts with sync move but ends with model/log move
    # NOTE: under the assumption that the normalized bound determined from trace is not less than the amount of identifiers used in the model. If this is the case the construction of the bounded rg will only result in a single transition for example and, while the result can be as expected, a large part of the model is not conformance checked at all, which can cause missing transitions later on that could be sync.
    pnid = PNID.read_pnml_input(
        os.path.join("data", "model", "tests", "testID5.pnml")
    )
    log = Log.load_log_from_CSV(os.path.join("data", "log", "tests", "testID5.csv"))

    runs = 1
    debug = False

    # we provide a manual bound of 1 as the trace provided has lower bound than nr of variables on the inscriptions in the pnid which makes us skip a part of the model.
    (result, time_info) = main.conformance_check_traces(pnid, log, runs, 1, debug)
    alignment = result[0][4]["alignment"]
    print("Test 5: " + str((alignment[0] == "sync") and (alignment[1] == "sync") and (alignment[2] == "log") and (alignment[3] == "log")) + " (no increase of identifier in trace when new var)")

def testID6():
    # Trace is empty, leads to no result (conformance checking not possible)
    pnid = PNID.read_pnml_input(
        os.path.join("data", "model", "tests", "testID6.pnml")
    )
    log = Log.load_log_from_CSV(os.path.join("data", "log", "tests", "testID6.csv"))

    runs = 1
    debug = False

    (result, time_info) = main.conformance_check_traces(pnid, log, runs, -1, debug)
    print("Test 6: " + str((result == [])) + " (empty trace)") 

def testID7():
    # Model is empty, leads to no result
    pnid = PNID.read_pnml_input(
        os.path.join("data", "model", "tests", "testID7.pnml")
    )
    log = Log.load_log_from_CSV(os.path.join("data", "log", "tests", "testID7.csv"))

    runs = 1
    debug = False

    (result, time_info) = main.conformance_check_traces(pnid, log, runs, -1, debug)
    print("Test 7: " + str((result == [])) + " (empty model)")

def testID8a():
    # Model with a transition with input from 2 places and output to 1 place, and corresponding event sequence and matching event in trace, lead to only sync moves.
    pnid = PNID.read_pnml_input(
        os.path.join("data", "model", "tests", "testID8a.pnml")
    )
    log = Log.load_log_from_CSV(os.path.join("data", "log", "tests", "testID8a.csv"))

    runs = 1
    debug = False

    (result, time_info) = main.conformance_check_traces(pnid, log, runs, -1, debug)
    alignment = result[0][4]["alignment"]
    print("Test 8a: " + str((alignment[0] == "sync")) + " (transition with input from 2 places and output to 1 place)")

def testID8b():
    # Model with, after a matching transition, a transition with input from 2 places and output to 1 place, and corresponding event sequence and matching event in trace, leads to only sync moves.
    pnid = PNID.read_pnml_input(
        os.path.join("data", "model", "tests", "testID8b.pnml")
    )
    log = Log.load_log_from_CSV(os.path.join("data", "log", "tests", "testID8b.csv"))

    runs = 1
    debug = False

    (result, time_info) = main.conformance_check_traces(pnid, log, runs, -1, debug)
    alignment = result[0][4]["alignment"]
    print("Test 8b: " + str((alignment[0] == "sync") and (alignment[1] == "sync")) + " (transition with, after a matching transition, input from 2 places and output to 1 place)")

def testID9a():
    # Model with a transition with input from 3 places and output to 1 place, and corresponding event sequence and matching event in trace, leads to only sync moves.
    pnid = PNID.read_pnml_input(
        os.path.join("data", "model", "tests", "testID9a.pnml")
    )
    log = Log.load_log_from_CSV(os.path.join("data", "log", "tests", "testID9a.csv"))

    runs = 1
    debug = False

    (result, time_info) = main.conformance_check_traces(pnid, log, runs, -1, debug)
    alignment = result[0][4]["alignment"]
    print("Test 9a: " + str((alignment[0] == "sync")) + " (transition with input from 3 places and output to 1 place)")

def testID9b():
    # Model with, after a matching transition, a transition with input from 3 places and output to 1 place, and corresponding event sequence and matching event in trace, leads to only sync moves.
    pnid = PNID.read_pnml_input(
        os.path.join("data", "model", "tests", "testID9b.pnml")
    )
    log = Log.load_log_from_CSV(os.path.join("data", "log", "tests", "testID9b.csv"))

    runs = 1
    debug = False

    (result, time_info) = main.conformance_check_traces(pnid, log, runs, -1, debug)
    alignment = result[0][4]["alignment"]
    print("Test 9b: " + str((alignment[0] == "sync") and (alignment[1] == "sync")) + " (transition with, after a matching transition, input from 3 places and output to 1 place)")

def testID10():
    # Model with a transition with input from 1 place and output to 2 places, and corresponding event sequence and matching event in trace, leads to only sync moves.
    pnid = PNID.read_pnml_input(
        os.path.join("data", "model", "tests", "testID10.pnml")
    )
    log = Log.load_log_from_CSV(os.path.join("data", "log", "tests", "testID10.csv"))

    runs = 1
    debug = False

    (result, time_info) = main.conformance_check_traces(pnid, log, runs, -1, debug)
    alignment = result[0][4]["alignment"]
    print("Test 10: " + str((alignment[0] == "sync")) + " (transition with input from 1 place and output to 2 places)")

def testID11():
    # Model with a transition with input from 1 place and output to 3 places, and corresponding event sequence and matching event in trace, leads to only sync moves.
    pnid = PNID.read_pnml_input(
        os.path.join("data", "model", "tests", "testID11.pnml")
    )
    log = Log.load_log_from_CSV(os.path.join("data", "log", "tests", "testID11.csv"))

    runs = 1
    debug = False

    (result, time_info) = main.conformance_check_traces(pnid, log, runs, -1, debug)
    alignment = result[0][4]["alignment"]
    print("Test 11: " + str((alignment[0] == "sync")) + " (transition with input from 1 place and output to 3 places)")

def testID12():
    # Model a transition with 2 initial places and a transition afterwards, and a trace matching the trace afterwards, can still lead to a sync move.
    pnid = PNID.read_pnml_input(
        os.path.join("data", "model", "tests", "testID12.pnml")
    )
    log = Log.load_log_from_CSV(os.path.join("data", "log", "tests", "testID12.csv"))

    runs = 1
    debug = False

    (result, time_info) = main.conformance_check_traces(pnid, log, runs, -1, debug)
    alignment = result[0][4]["alignment"]
    print("Test 12: " + str(("sync" in alignment)) + " (transition matching after starting with 2 initial places)")

def testID13():
    # Model a transition with 3 initial places and a transition afterwards, and a trace matching the trace afterwards, can still lead to a sync move.
    pnid = PNID.read_pnml_input(
        os.path.join("data", "model", "tests", "testID13.pnml")
    )
    log = Log.load_log_from_CSV(os.path.join("data", "log", "tests", "testID13.csv"))

    runs = 1
    debug = False

    (result, time_info) = main.conformance_check_traces(pnid, log, runs, -1, debug)
    alignment = result[0][4]["alignment"]
    print("Test 13: " + str(("sync" in alignment)) + " (transition matching after starting with 3 initial places)")

def testID14():
    # Trace with an event with high identifier in resources field, leads to a normalized bound
    pnid = PNID.read_pnml_input(
        os.path.join("data", "model", "tests", "testID14.pnml")
    )
    log = Log.load_log_from_CSV(os.path.join("data", "log", "tests", "testID14.csv"))

    runs = 1
    debug = False

    (result, time_info) = main.conformance_check_traces(pnid, log, runs, -1, debug)
    transitions = result[0][4]["transitions"]
    print("Test 14: " + str((len(transitions) == 2 and transitions[0][1] == "T [0]")) + " (event with high identifier)")

def testID15():
    # Trace with an event with negative identifier in resources field, leads to no result or the negative symbol is ignored.
    pnid = PNID.read_pnml_input(
        os.path.join("data", "model", "tests", "testID15.pnml")
    )
    log = Log.load_log_from_CSV(os.path.join("data", "log", "tests", "testID15.csv"))

    runs = 1
    debug = False

    (result, time_info) = main.conformance_check_traces(pnid, log, runs, -1, debug)
    if result != []:
        transitions = result[0][4]["transitions"]
        alignment = result[0][4]["alignment"]
    print("Test 15: " + str((result != [] or transitions[0][1] == "T [0]")) + " (event with negative identifier in resources)")

def testID16():
    # Trace with an event with string identifier in resources field, leads to no result.
    pnid = PNID.read_pnml_input(
        os.path.join("data", "model", "tests", "testID16.pnml")
    )
    log = Log.load_log_from_CSV(os.path.join("data", "log", "tests", "testID16.csv"))

    runs = 1
    debug = False

    (result, time_info) = main.conformance_check_traces(pnid, log, runs, -1, debug)
    print("Test 16: " + str((result == [])) + " (event with string identifier in resources)")

def testID17():
    # Trace with an event with empty resources can still lead to sync move if model does not require identifiers.
    pnid = PNID.read_pnml_input(
        os.path.join("data", "model", "tests", "testID17.pnml")
    )
    log = Log.load_log_from_CSV(os.path.join("data", "log", "tests", "testID17.csv"))

    runs = 1
    debug = False

    (result, time_info) = main.conformance_check_traces(pnid, log, runs, -1, debug)
    alignment = result[0][4]["alignment"]
    print("Test 17: " + str((alignment[0] == "sync")) + " (event with no resources)")

def testID18():
    # Trace with an event with number as event label can still lead to sync move.
    pnid = PNID.read_pnml_input(
        os.path.join("data", "model", "tests", "testID18.pnml")
    )
    log = Log.load_log_from_CSV(os.path.join("data", "log", "tests", "testID18.csv"))

    runs = 1
    debug = False

    (result, time_info) = main.conformance_check_traces(pnid, log, runs, -1, debug)
    alignment = result[0][4]["alignment"]
    print("Test 18: " + str((alignment[0] == "sync")) + " (event with number as event label)")

def testID19():
    # Choice in manual bound should increase the size of generated internal model when PNID contains cycle.
    pnid = PNID.read_pnml_input(
        os.path.join("data", "model", "tests", "testID19.pnml")
    )
    log = Log.load_log_from_CSV(os.path.join("data", "log", "tests", "testID19.csv"))

    runs = 1
    debug = False

    (result1, time_info1) = main.conformance_check_traces(pnid, log, runs, 3, debug)
    internalPN1 = result1[0][5]
    (result2, time_info) = main.conformance_check_traces(pnid, log, runs, 4, debug)
    internalPN2 = result2[0][5]

    print("Test 19: " + str((len(internalPN2._transitions) > len(internalPN1._transitions))) + " (manual bound increases size generated internal model)")

def testID20a():
    # A trace with events with lower identifiers than the nr of variables in the model,
    # and the transition requiring the higher identifier is not fired,
    # leads to no log moves (part of the pnid is missing in internal model)
    pnid = PNID.read_pnml_input(
        os.path.join("data", "model", "tests", "testID20a.pnml")
    )
    log = Log.load_log_from_CSV(os.path.join("data", "log", "tests", "testID20a.csv"))

    runs = 1
    debug = False

    (result, time_info) = main.conformance_check_traces(pnid, log, runs, -1, debug)
    alignment = result[0][4]["alignment"]
    print("Test 20a: " + str(("log" in alignment) == False) + " (lower identifiers in trace than nr variables of transition in model)")

def testID20b():
    # A trace with events with lower identifiers than the nr of variables in the model,
    # and the transition requiring the higher identifier is fired,
    # leads to log moves (part of the pnid is missing in internal model)
    pnid = PNID.read_pnml_input(
        os.path.join("data", "model", "tests", "testID20b.pnml")
    )
    log = Log.load_log_from_CSV(os.path.join("data", "log", "tests", "testID20b.csv"))

    runs = 1
    debug = False

    (result, time_info) = main.conformance_check_traces(pnid, log, runs, -1, debug)
    alignment = result[0][4]["alignment"]
    print("Test 20b: " + str(("log" in alignment)) + " (lower identifiers in trace than nr variables of transition in model, and transition is fired)")

def testID20c():
    # A trace with events with lower identifiers than the nr of variables in the model,
    # and the transition requiring the higher identifier is fired and the bound is manually increased,
    # leads to no log moves (part of the pnid is not missing in internal model)
    pnid = PNID.read_pnml_input(
        os.path.join("data", "model", "tests", "testID20c.pnml")
    )
    log = Log.load_log_from_CSV(os.path.join("data", "log", "tests", "testID20c.csv"))

    runs = 1
    debug = False

    (result, time_info) = main.conformance_check_traces(pnid, log, runs, 2, debug)
    alignment = result[0][4]["alignment"]
    print("Test 20c: " + str(("log" in alignment) == False) + " (lower identifiers in trace than nr variables of transition in model, and transition is fired, but bound manually increased)")

def testID21a():
    # A trace with events with higher identifiers than the nr of variables in the model,
    # and the model contains a cycle,
    # leads to more transitions in the internal model with these higher identifiers
    pnid = PNID.read_pnml_input(
        os.path.join("data", "model", "tests", "testID21a.pnml")
    )
    log = Log.load_log_from_CSV(os.path.join("data", "log", "tests", "testID21a.csv"))

    runs = 1
    debug = False

    (result1, time_info1) = main.conformance_check_traces(pnid, log, runs, -1, debug)
    alignment1 = result1[0][4]["alignment"]
    transitions1 = result1[0][5]._transitions

    pnid = PNID.read_pnml_input(
        os.path.join("data", "model", "tests", "testID21a.pnml")
    )
    log = Log.load_log_from_CSV(os.path.join("data", "log", "tests", "testID21a (reduced).csv"))

    runs = 1
    debug = False

    (result2, time_info2) = main.conformance_check_traces(pnid, log, runs, -1, debug)
    transitions2 = result2[0][5]._transitions

    print("Test 21a: " + str(("log" in alignment1) == False and len(transitions1) > len(transitions2)) + " (higher identifiers in trace than nr variables of transition in model with cycle)")

def testID21b():
    # A trace with events with higher identifiers than the nr of variables in the model,
    # and the model contains no cycle,
    # leads to log moves as transitions are fired in the trace that are not in the model
    # NOTE: this needed a tweak to the sync and async step in order to result in log move. 
    #       We already checked whether the identifiers in the valuation match each in resources, but we should also check whether all identifiers of event resource are in the valuation.

    pnid = PNID.read_pnml_input(
        os.path.join("data", "model", "tests", "testID21b.pnml")
    )
    log = Log.load_log_from_CSV(os.path.join("data", "log", "tests", "testID21b.csv"))

    runs = 1
    debug = False

    (result, time_info) = main.conformance_check_traces(pnid, log, runs, -1, debug)
    alignment = result[0][4]["alignment"]
    print("Test 21b: " + str(("log" in alignment))  + " (higher identifiers in trace than nr variables of transition in model without cycle)")

def testID22():
    pnid = PNID.read_pnml_input(
        os.path.join("data", "model", "tests", "testID22.pnml")
    )
    log = Log.load_log_from_CSV(os.path.join("data", "log", "tests", "testID22.csv"))

    runs = 1
    debug = False

    (result, time_info) = main.conformance_check_traces(pnid, log, runs, -1, debug)
    alignment = result[0][4]["alignment"]
    print("Test 22: " + str(("sync" in alignment)) + " (matching event without variables)")