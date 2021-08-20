package org.architecturemining.pnidconformance.algorithms.naivecc;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.PrintStream;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutionException;

import org.architecturemining.pnid.models.pnid.PNIDModel;
import org.architecturemining.pnidconformance.algorithms.naivecc.models.alignment.AlignmentSettings;
import org.deckfour.xes.classification.XEventClass;
import org.deckfour.xes.classification.XEventClasses;
import org.deckfour.xes.classification.XEventClassifier;
import org.deckfour.xes.extension.std.XConceptExtension;
import org.deckfour.xes.extension.std.XOrganizationalExtension;
import org.deckfour.xes.info.XLogInfo;
import org.deckfour.xes.info.XLogInfoFactory;
import org.deckfour.xes.model.XAttribute;
import org.deckfour.xes.model.XEvent;
import org.deckfour.xes.model.XLog;
import org.deckfour.xes.model.XVisitor;
import org.processmining.models.graphbased.directed.petrinet.Petrinet;
import org.processmining.models.graphbased.directed.petrinet.PetrinetGraph;
import org.processmining.models.graphbased.directed.petrinet.elements.Transition;
import org.processmining.models.semantics.petrinet.Marking;
import org.processmining.plugins.connectionfactories.logpetrinet.TransEvClassMapping;
import org.processmining.plugins.petrinet.replayresult.PNRepResult;
import org.processmining.plugins.replayer.replayresult.SyncReplayResult;

import nl.tue.alignment.Progress;
import nl.tue.alignment.Replayer;
import nl.tue.alignment.ReplayerParameters;
import nl.tue.alignment.Utils;
import nl.tue.alignment.algorithms.ReplayAlgorithm;
import nl.tue.alignment.algorithms.ReplayAlgorithm.Debug;

class CustomEventClassifier implements XEventClassifier {

	public void accept(XVisitor arg0, XLog arg1) {
		arg0.visitClassifierPre(this, arg1);
		arg0.visitClassifierPost(this, arg1);	
	}

	public String getClassIdentity(XEvent arg0) {
		String[] keys = new String[] { XConceptExtension.KEY_NAME, XOrganizationalExtension.KEY_RESOURCE };
		StringBuilder sb = new StringBuilder();
		for (int i = 0; i < keys.length; i++) {
			XAttribute attribute = arg0.getAttributes().get(keys[i]);
			if (i == 1 && attribute != null) {
				sb.append(" {");
			}
			if (attribute != null) {
				sb.append(attribute.toString().trim());
			}
			if (i == 1 && attribute != null) {
				sb.append("}");
			}
		}
		return sb.toString();
	}

	public String[] getDefiningAttributeKeys() {
		return new String[] { XConceptExtension.KEY_NAME, XOrganizationalExtension.KEY_RESOURCE };
	}

	public String name() {
		return "Transition resource independent";
	}

	public boolean sameEventClass(XEvent arg0, XEvent arg1) {
		return getClassIdentity(arg0).equals(getClassIdentity(arg1));
	}

	public void setName(String arg0) {
		// TODO Auto-generated method stub
		
	}
	
}

public class AlignmentSearch {
	
	public static PNRepResult alignmentSearch(PNIDModel flatPN, XLog log) throws FileNotFoundException, InterruptedException, ExecutionException {
		Marking initialMarking = new Marking();
		Marking finalMarking = new Marking();		
		
		// First convert the flat PN to a different data type
		PetrinetGraph net = flatPN.convertToPetriNetGraph(initialMarking, finalMarking);
		
		// Init alignment settings
		AlignmentSettings settings = new AlignmentSettings();
		
		// Init mapping and event classes
		XEventClassifier eventClassifier = new CustomEventClassifier();
		XEventClass dummyEvClass = new XEventClass("DUMMY", 99999);
		TransEvClassMapping mapping = constructMapping(net, log, dummyEvClass, eventClassifier);
		XLogInfo summary = XLogInfoFactory.createLogInfo(log, eventClassifier);
		
		XEventClasses classes = summary.getEventClasses();
		
		// Find closest firing sequence, the sequence with minimal cost
		ReplayerParameters parameters = new ReplayerParameters.AStar(settings.moveSort, settings.queueSort,
				settings.preferExact, settings.threads, settings.useInt, settings.debugMode, settings.timeout,
				settings.maxNumberOfStates, settings.costUpperBound, settings.partialOrder);
		
		PNRepResult result = doReplay(settings.debugMode, "replay", "AStar", net, initialMarking, finalMarking,
						log, mapping, classes, parameters);
				
		return result;
	}
	
	// Create a link between the transitions (with valuations) in the model and the events with resources in the log.
	// Note that valuations and resources are converted to a hash for easier comparison with each other - easier creation of this mapping.
	private static TransEvClassMapping constructMapping(PetrinetGraph net, XLog log, XEventClass dummyEvClass, XEventClassifier eventClassifier) {
		TransEvClassMapping mapping = new TransEvClassMapping(eventClassifier, dummyEvClass);
		
		XLogInfo summary = XLogInfoFactory.createLogInfo(log, eventClassifier);

		for (Transition t : net.getTransitions()) {
			boolean mapped = false;
			
			int lengthTransitionName = t.getLabel().contains("{") ? t.getLabel().indexOf('{') : t.getLabel().length()-1;
			String transitionName = ((String) t.getLabel().subSequence(0, lengthTransitionName)).replaceAll("\\s+","");
			String[] transitionResources = t.getLabel().contains("{") ? ((String) t.getLabel().subSequence(lengthTransitionName + 1, t.getLabel().length()-1)).split(",") : new String[] {};
			List<Integer> transitionResourcesHash = new ArrayList<Integer>();
			for (String s : transitionResources) {
				// Convert transition resources to Hash
				transitionResourcesHash.add(s.replaceAll("\\s+","").replaceAll("=","").hashCode());
			}
			
			// TECH DOUBT
			// Convert valuation earlier into hash to avoid computing similar hash multiple times? -> for example. "T {hash(x=0)}"
			
			for (XEventClass evClass : summary.getEventClasses().getClasses()) {
				int lengthEventName = evClass.getId().indexOf('{');
				String eventName = ((String) evClass.getId().subSequence(0, lengthEventName)).replaceAll("\\s+","");
				String[] eventResources = ((String) evClass.getId().subSequence(lengthEventName + 1, evClass.getId().length()-1)).split(",");
				List<Integer> eventResourcesHash = new ArrayList<Integer>();
				for (String s : eventResources) {
					eventResourcesHash.add(s.replaceAll("\\s+","").hashCode());
				}
				
				if (transitionName.toLowerCase().hashCode() == eventName.toLowerCase().hashCode() && transitionResourcesHash.containsAll(eventResourcesHash) && eventResourcesHash.containsAll(transitionResourcesHash)) {
					mapping.put(t, evClass);
					mapped = true;
					break;
				}
			}

			if (!mapped && !t.isInvisible()) {
				mapping.put(t, dummyEvClass);
			}

		}

		return mapping;
	}
	
	private static PNRepResult doReplay(Debug debug, String folder, String postfix, PetrinetGraph net, Marking initialMarking,
			Marking finalMarking, XLog log, TransEvClassMapping mapping, XEventClasses classes,
			ReplayerParameters parameters) throws FileNotFoundException, InterruptedException, ExecutionException {
		PrintStream stream;
		if (debug == Debug.STATS) {
			stream = new PrintStream(new File(folder + " " + postfix + ".csv"));
		} else if (debug == Debug.DOT) {
			stream = new PrintStream(new File(folder + "_" + postfix + ".dot"));
		} else {
			stream = System.out;
		}
		ReplayAlgorithm.Debug.setOutputStream(stream);

		long start = System.nanoTime();
		Replayer replayer = new Replayer(parameters, (Petrinet) net, initialMarking, finalMarking, classes, mapping,
				true);

		PNRepResult result = replayer.computePNRepResult(new Progress() {
			public boolean isCanceled() {
//				System.out.println("Replayer: canceled");
				return false;
			}

			public void setMaximum(int maximum) {
//				System.out.println("Replayer: set max to " + maximum);
			}

			public void inc() {
				// TODO Auto-generated method stub
//				System.out.println("Replayer: inc");
			}

			public void log(String message) {
//				System.out.println("Replayer: " + message);
				
			}}, log);//, SINGLETRACE);
		long end = System.nanoTime();

		int cost = (int) Double.parseDouble((String) result.getInfo().get(Replayer.MAXMODELMOVECOST));
		int timeout = 0;
		double time = 0;
		int mem = 0;
		int lps = 0;
		double pretime = 0;
		for (SyncReplayResult res : result) {
			cost += res.getTraceIndex().size() * res.getInfo().get(PNRepResult.RAWFITNESSCOST);
			timeout += res.getTraceIndex().size() * (res.getInfo().get(Replayer.TRACEEXITCODE).intValue() != 1 ? 1 : 0);
			time += res.getInfo().get(PNRepResult.TIME);
			pretime += res.getInfo().get(Replayer.PREPROCESSTIME);
			lps += res.getInfo().get(Replayer.HEURISTICSCOMPUTED);
			mem = Math.max(mem, res.getInfo().get(Replayer.MEMORYUSED).intValue());
		}

		if (stream != System.out) {
			//			System.out.println(result.getInfo().toString());
			stream.close();
		}

		// number timeouts
		System.out.print(timeout + Utils.SEP);
		// clocktime
		System.out.print(String.format("%.3f", (end - start) / 1000000.0) + Utils.SEP);
		// cpu time
		System.out.print(String.format("%.3f", time) + Utils.SEP);
		// preprocess time
		System.out.print(String.format("%.3f", pretime) + Utils.SEP);
		// max memory
		System.out.print(mem + Utils.SEP);
		// solves lps.
		System.out.print(lps + Utils.SEP);
		// total cost.
		System.out.print(cost + Utils.SEP);

		System.out.flush();

		return result;
	}
}