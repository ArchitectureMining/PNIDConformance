package org.architecturemining.pnidconformance.tests.plugin;

import java.util.Arrays;

import org.informationsystem.ismsuite.pnidprocessor.petrinet.MarkedPetriNet;

public class PNIDExampleNets {
	public static MarkedPetriNet GetNoVariableNet() {
		MarkedPetriNet net = new MarkedPetriNet();
		net.addPlace("p1", 0);
		net.addPlace("p2", 0);

		net.addInArc("T", "p1");
		net.addOutArc("T", "p2");

		// Add tokens
		for (int i = 0; i < 1; i++) {
			net.addToken("p1");
		}

		return net;
	}

	public static MarkedPetriNet GetSingleVariableNet() {
		MarkedPetriNet net = new MarkedPetriNet();
		net.addPlace("p1", 1);
		net.addPlace("p2", 1);

		net.addInArc("T", "p1", "x");
		net.addOutArc("T", "p2", "x");

		// Add tokens
		for (int i = 0; i < 1; i++) {
			net.addToken("p1");
		}

		return net;
	}

	public static MarkedPetriNet GetSimpleCreatorNet() {
		MarkedPetriNet net = new MarkedPetriNet();
		net.addPlace("store");
		net.addPlace("p1", 1);
		net.addPlace("p2", 1);

		net.addInArc("T", "store", "c");
		net.addOutArc("T", "p1", "c");
		net.addInArc("U", "p1", "c");
		net.addOutArc("U", "p2", "c");
		net.addInArc("V", "p2", "c");
		net.addOutArc("V", "store");

		// Add tokens
		for (int i = 0; i < 3; i++) {
			net.addToken("store");
		}

		return net;
	}

	public static MarkedPetriNet GetMergingTransitionNetWithCounterPlace() {
		MarkedPetriNet net = new MarkedPetriNet();
		net.addPlace("C", 1); // Counter place
		net.addPlace("p1", 1);
		net.addPlace("p2", 1);
		net.addPlace("p3", 2);
		net.addPlace("p4", 1);
		net.addPlace("p5", 1);

		net.addInArc("T", "C", "v-");
		net.addOutArc("T", "C", "v+");

		net.addOutArc("T", "p1", "x");
		net.addOutArc("T", "p2", "y");
		net.addOutArc("T", "p3", Arrays.asList("x", "y"));

		net.addInArc("U", "p1", "x");
		net.addOutArc("U", "p4", "x");

		net.addInArc("V", "p2", "x");
		net.addOutArc("V", "p5", "x");

		net.addInArc("W", "p3", Arrays.asList("x", "y"));
		net.addInArc("W", "p4", "x");
		net.addInArc("W", "p5", "y");

		// Add tokens
		for (int i = 0; i < 1; i++) {
			net.addToken("C");
		}

		return net;
	}
}
