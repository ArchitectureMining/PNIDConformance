package org.architecturemining.pnidconformance.algorithms.naivecc;

import java.util.List;

import org.architecturemining.pnid.models.pnid.PNIDModel;
import org.architecturemining.pnid.models.xlog.LogModel;

/**
 * @author J. Ree
 * 
 * A naive approach to conformance checking on a Petri net with identifiers (PNID).
 * Given a PNID and a trace with identifier, computes the corresponding transition system, and find the closest firing sequence in the transition system, a.k.a. alignment.   
 *
 */
public class NaiveCC {
	
	public static PNIDModel naiveCC(PNIDModel pnid, LogModel log, int maxUnfold) {	
		// Generate flat petri net such that alignment technique can be applied
		PNIDModel flatPetriNet = FlattenPNID.generateFlatPN(pnid, maxUnfold);
		
		// Find closest trace - alignment technique
		List<Object> trace = null;
		
		return flatPetriNet;
	}
}