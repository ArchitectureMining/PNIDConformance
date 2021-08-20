package org.architecturemining.pnidconformance.algorithms.naivecc;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import org.architecturemining.pnid.models.pnid.PNIDModel;
import org.architecturemining.pnidconformance.algorithms.naivecc.models.flatpnid.ArcInfoMap;
import org.architecturemining.pnidconformance.algorithms.naivecc.models.flatpnid.PlaceVariables;
import org.architecturemining.pnidconformance.algorithms.naivecc.models.flatpnid.PlaceVector;
import org.architecturemining.pnidconformance.algorithms.naivecc.models.flatpnid.PlaceVectorInfo;
import org.architecturemining.pnidconformance.algorithms.naivecc.models.flatpnid.PlaceVectorInfoList;
import org.architecturemining.pnidconformance.algorithms.naivecc.models.flatpnid.TransitionValuationInfo;
import org.architecturemining.pnidconformance.algorithms.naivecc.models.flatpnid.TransitionValuationInfoList;
import org.informationsystem.ismsuite.pnidprocessor.petrinet.MarkedPetriNet;

import com.google.common.primitives.Ints;

import javafx.util.Pair;

/**
 * @author J. Ree
 * 
 *  We flatten the PNID; unfold process model to a classic petri net up to max unfold parameter (bound on identifiers)
 *  That is, create a place for each possible vector of identifiers in a classic Petri net and create a transition for each possible valuation.
 *  Using a well-order on the set of identifiers we ensure identifiers are not modelled twice.
 *
 *	Note: For some PNIDs a counter place is required to be able to flatten the PNID correctly.
 *  	  A counter place can be added to the PNID manually with "c+" and "c-" on the in and out arcs.
 */

public class FlattenPNID {
	
	public static PNIDModel generateFlatPN(PNIDModel pnid, int maxIdentifierUnfold) {
		MarkedPetriNet net = pnid.GetNet();
		Set<String> transitions = net.transitions();
		Set<String> places = net.places();
		
		// Init classic Petri net
		MarkedPetriNet pn = new MarkedPetriNet();

		// Init set of places with linked transitions
		ArcInfoMap placeInArcs = new ArcInfoMap();
				
		// Init set of places with linked transitions
		ArcInfoMap transitionInArcs = new ArcInfoMap();
		
		// Init set of created places with their vector of identifiers
		PlaceVectorInfoList placeVectors = new PlaceVectorInfoList();
		
		// Init set of created transitions with their valuation
		TransitionValuationInfoList transitionValuations = new TransitionValuationInfoList();
		
		// Init set of created transitions with their valuation of counter places
		TransitionValuationInfoList transitionCounterValuations = new TransitionValuationInfoList();
		
		// 1. We create new places for each possible identifier of each place, defined by the cardinality of a place and set of possible identifiers.
		// 	  Additionally, we store the ingoing and outgoing variables of the places in "placeVectors".
		for(String p : places) {	
			List<String> inArcs = new ArrayList<String>();
			List<String> inVars = new ArrayList<>();
			List<String> outVars = new ArrayList<>();
			int cardinality = net.getCardinality(p);
			Boolean counterPlace = false;
			String transition = null;
			
			for(String t : transitions) {
				if(net.hasOutArc(t, p)) {
					inVars = net.getVariablesOnOutputArc(t, p);
					transition = t;
					inArcs.add(t);
				}
				if(net.hasInArc(t, p)) {
					outVars = net.getVariablesOnInputArc(t, p);
					if(net.getVariablesOnInputArc(t, p).contains("v-")) {
						//inVars = outVars;
						transition = t;
						counterPlace = true;
					}
				}
			}
			
			if(cardinality > 0) {
				if(counterPlace) {
					createCounterPlacesWithCorrTransitions(net, pn, transition, p, places, transitionCounterValuations, maxIdentifierUnfold);
				}
				else {
					Map<Integer,Set<String>> identifiers = getCandidateVectorsOfIdentifiers(cardinality, maxIdentifierUnfold);				
					addPlaceForVector(pn, placeVectors, p, new HashMap<>(), identifiers, 0, inVars, outVars);
				}
			}
			else {
				// Black place; just copy.
				pn.addPlace(p);
				placeVectors.add(new PlaceVectorInfo(p, new PlaceVector("", new PlaceVariables("", ""))));
			}
			
			// Store arc information.
			placeInArcs.put(p, inArcs);
		}
		
		// 2. We create new transitions for each possible valuation of each transition.
		for(String t : transitions) {
			List<String> inArcs = new ArrayList<String>();
			List<String> vars = new ArrayList<String>();
			List<String> newVars = new ArrayList<String>();
			
			// Check which inscription(variables) are on the arc towards the transition.
			for(String p : places) {
				if (net.hasInArc(t, p)) {
					inArcs.add(p);
					newVars = net.getVariablesOnInputArc(t, p);
					if (newVars.size() > vars.size())
						vars = newVars;
				}
			}
			
			if(vars.size() > 0) {
				// Only consider transitions not leading to counter places, since transitions for counter places are already created.
				if(!vars.contains("v-")) {
					Map<String,Set<String>> valuations = getCandidateValuations(vars, maxIdentifierUnfold);
					addTransitionForValuation(pn, transitionValuations, t, vars, new HashMap<>(), valuations, 0);
				}
			}
			else {
				// Connected to black place;
				// Ingoing and outgoing arcs have no inscription for this transition, just copy.
				pn.addTransition(t);
			}
			
			// Store arc information.
			transitionInArcs.put(t, inArcs);
		}
		
		// 3. Create in arcs from place to transition.
		for (Entry<String, List<String>> e : transitionInArcs.entrySet()) {
			String t = e.getKey();
			
			// Find all created transitions (valuations) with this transition.
			List<Pair<String, String>> createdTransitions = transitionValuations.stream().distinct()
					.filter((pair) -> pair.getKey().replaceAll("[^a-zA-Z ]+", "").equals(t))
					.collect(Collectors.toList());
		
			for(String p : e.getValue()) {
				// Find all created places with this place.
				List<PlaceVectorInfo> createdPlaces = placeVectors.stream().distinct()
						.filter((pair) -> pair.getKey() == p).collect(Collectors.toList());

				if (!createdTransitions.isEmpty()) {
					// Link created transitions with created places based upon valuations.
					for (Pair<String,String> ctpair : createdTransitions) {
						String valuation = cleanValuation(ctpair.getValue());
						
						if(valuation.length() > 0) {
							Stream<PlaceVectorInfo> stream = createdPlaces.stream();
							stream = stream.filter(pair -> (instantiatePlaceIdentifiers(pair.getValue(), true).contains(valuation) 
									|| valuation.contains(instantiatePlaceIdentifiers(pair.getValue(), true))));		
							Pair<String, PlaceVector> place = stream.findFirst().orElse(null);
							
							if(place != null) {
								String identifiers = place.getValue().getKey();
								pn.addInArc(ctpair.getKey() + " " + ctpair.getValue(), place.getKey() + (identifiers.isEmpty() ?  "" : " " + identifiers));
							}
							else
								System.out.println("ARC TO TRANSITION NOT FOUND FOR " + ctpair.getKey() + " " + ctpair.getValue());
						}
						else {
							pn.addInArc(ctpair.getKey(), p);
						}	
					}
				}
				else if (transitionValuations.isEmpty()){
					// No new created transitions / no valuations. Copy the arcs like in the original net.
					pn.addInArc(t, p);
				}
			}
		}

		// 4. Create out arcs from transition to place.
		for (Entry<String, List<String>> e : placeInArcs.entrySet()) {
			String p = e.getKey();
			
			// Find all created places (with vector of identifiers) with this place.
			List<PlaceVectorInfo> createdPlaces = placeVectors.stream().distinct()
					.filter((pair) -> pair.getKey().equals(p)).collect(Collectors.toList());

			for(String t : e.getValue()) {
				// Add the transitions created by counter places to transition valuations.
				transitionValuations.addAll(transitionCounterValuations);
				
				// Find all created places with this transition.
				List<Pair<String, String>> createdTransitions = transitionValuations.stream().distinct()
						.filter((pair) -> pair.getKey().replaceAll("[^a-zA-Z ]+", "").equals(t))
						.collect(Collectors.toList());
				
				for (PlaceVectorInfo cppair : createdPlaces) {
					String identifiers = instantiatePlaceIdentifiers(cppair.getValue(), false);
							
					if(!identifiers.isEmpty() && !createdTransitions.isEmpty() && createdTransitions.get(0).getValue().length() > 1) {
						Stream<Pair<String, String>> stream = createdTransitions.stream();
						stream = stream.filter(pair -> (cleanValuation(pair.getValue()).contains(identifiers)
								|| identifiers.contains(cleanValuation(pair.getValue()))));							
						Pair<String, String> transition = stream.findFirst().orElse(null);
						
						if(transition != null)
							pn.addOutArc(transition.getKey() + " " + transition.getValue(), cppair.getKey() + " " + cppair.getValue().getKey());
						else if (t != "T") // FOR DEBUG PURPOSES: T = transition connected to counter places, so ignore errors here			
							System.out.println("ARC TO PLACE NOT FOUND FOR " + cppair.getKey() + " " + cppair.getValue());
					}
					else if(identifiers.isEmpty() && !createdTransitions.isEmpty() && createdTransitions.get(0).getValue().length() > 1) {
						// Transitions have valuations but place is black. Copy the arcs for each created transition.
						for(Pair<String,String> pair : createdTransitions) {
							pn.addOutArc(pair.getKey() + " " + pair.getValue(), p);
						}
					}
					else {
						// No new created transitions / no valuations. Copy the arc like in the original net.
						pn.addOutArc(t, p);
					}
				}
			}
		}
		
		return new PNIDModel(pn);
	}
	
	private static void createCounterPlacesWithCorrTransitions(MarkedPetriNet net, MarkedPetriNet pn, String transition, String place, Set<String> places, TransitionValuationInfoList transitionCounterValuations, int maxIdentifierUnfold ) {
		// 1. Find the new variables after the transition.
		List<String> createVars = new ArrayList<>();
		for(String placeAfterT : places) {
			if(net.hasOutArc(transition, placeAfterT)) {
				List<String> newVars = net.getVariablesOnOutputArc(transition, placeAfterT);
				if(newVars.size() > createVars.size())
					createVars = newVars;
			}
		}
		
		// 2. Create counter places for each succ identifier up to maxIdentifierUnfold.
		int transitionCount = 1;
		for(int counter = 0; counter <= maxIdentifierUnfold; counter++) {
			// Add new place.
			String newPlace = place + " " + String.valueOf(counter);
			pn.addPlace(newPlace);
			
			List<Integer> assignments = new ArrayList<>();
			int tempCount = counter;
			for(String var : createVars) {
				assignments.add(tempCount+1);
				tempCount = tempCount + 1;
			}
			
			if(tempCount <= maxIdentifierUnfold) {				
				ArrayList<int[]> combs = new ArrayList<int[]>();
				permutation(Ints.toArray(assignments), 0, combs);
				
				// Add transition and corresponding arcs for each permutation allowed by the counter value.
				for(int[] comb : combs){
					String newTransitionName = "T" + String.valueOf(transitionCount);
					String valuation = "{";
					
					for(String var : createVars) {
						if(createVars.indexOf(var) == createVars.size()-1)
							valuation = valuation + var + "=" + comb[createVars.indexOf(var)] + "}";
						else
							valuation = valuation + var + "=" + comb[createVars.indexOf(var)] +", ";
					}
					
					String newTransition = newTransitionName + " " + valuation;
					pn.addTransition(newTransition);
					transitionCounterValuations.add(new TransitionValuationInfo(newTransitionName, valuation));
					transitionCount = transitionCount+ 1;
					
					pn.addInArc(newTransition, newPlace);
					String newCounterPlace = place + " " + String.valueOf(tempCount);
					pn.addOutArc(newTransition, newCounterPlace);
				}
			}
		}
	}

	private static Map<Integer,Set<String>> getCandidateVectorsOfIdentifiers(int cardinality, int maxIdentifierUnfold){
		Map<Integer, Set<String>> candidateVectors = new HashMap<>();
		
		for(int i = 0; i < cardinality; i++) {
			Set<String> values = new HashSet<String>();
			for (int j = 0; j <= maxIdentifierUnfold; j++) {
				values.add(String.valueOf(j));
			}
			candidateVectors.put(i, values);
		}
		
		return candidateVectors;
	}
	
	private static Map<String,Set<String>> getCandidateValuations(List<String> vars, int maxIdentifierUnfold){
		Map<String, Set<String>> candidateValuations = new HashMap<>();
		
		for(String var : vars) {
			Set<String> values = new HashSet<String>();
			for (int j = 0; j <= maxIdentifierUnfold; j++) {
				values.add(String.valueOf(j));
			}
			candidateValuations.put(var, values);
		}
		
		return candidateValuations;
	}
	
	private static MarkedPetriNet addPlaceForVector(MarkedPetriNet pn, PlaceVectorInfoList placeVectors, String place, Map<Integer,String> current, Map<Integer,Set<String>> vectors, int index, List<String> inVars, List<String> outVars) {
		if (index >= vectors.size()) {
			// Add place and corresponding valuation to data structure for linking transitions
			placeVectors.add(new PlaceVectorInfo(place.replaceAll("\\s", ""), new PlaceVector(current.values().toString(),
							 new PlaceVariables(inVars.toString(), outVars.toString()))));	

			// Add place
			pn.addPlace(place + " " + current.values());
		}
		else {
			for(String id : vectors.get(index)) {
				current.put(index, id);
				addPlaceForVector(pn, placeVectors, place, current, vectors, index+1, inVars, outVars);
			}
		}
		
		return pn;
	}

	private static MarkedPetriNet addTransitionForValuation(MarkedPetriNet pn, TransitionValuationInfoList transitionValuations, String transition, List<String> variables, Map<String,String> current, Map<String,Set<String>> valuations, int index) {
		if (index >= variables.size()) {
			// Add transition and corresponding valuation to data structure for linking places
			transitionValuations.add(new TransitionValuationInfo(transition.replaceAll("\\s", ""), current.toString()));
			
			// Add transition
			pn.addTransition(transition + " " + current.toString());	
		}
		else {
			String var = variables.get(index);
			for(String id : valuations.get(var)) {
				current.put(var, id);
				addTransitionForValuation(pn, transitionValuations, transition, variables, current, valuations, index+1);
			}
		}
		
		return pn;
	}

	public static void permutation(int[] arr, int pos, List<int[]> list){
	    if(arr.length - pos == 1)
	        list.add(arr.clone());
	    else
	        for(int i = pos; i < arr.length; i++){
	            swap(arr, pos, i);
	            permutation(arr, pos+1, list);
	            swap(arr, pos, i);
	        }
	}

	public static void swap(int[] arr, int pos1, int pos2){
	    int x = arr[pos1];
	    arr[pos1] = arr[pos2];
	    arr[pos2] = x;
	}	
	
	private static String instantiatePlaceIdentifiers(PlaceVector placeVector, Boolean outVars) {
		Pair<String, String> varInfo = placeVector.getValue();
		List<String> identifiers = Arrays.asList(cleanIdentifierList(placeVector.getKey()).split(","));
		List<String> variables = Arrays.asList(cleanIdentifierList(outVars ? varInfo.getValue() : varInfo.getKey()).split(","));	
		
		for (String id : identifiers) {
			if(!id.isEmpty()) {
				int index = identifiers.indexOf(id);
				identifiers.set(index, variables.get(index) + "=" + id); 
			}
		}

		return cleanIdentifierList(identifiers.toString());
	}
	
	private static String cleanIdentifierList(String identifierList) {
		return identifierList.replaceAll("\\[", "").replaceAll("\\]", "").replaceAll(" ", "");
	}

	private static String cleanValuation(String valuation) {
		return valuation.replaceAll("\\{", "").replaceAll("\\}", "").replaceAll(" ", "");
	}

}
