package org.architecturemining.pnidconformance.algorithms.naivecc;

import java.util.List;
import java.util.Map;

import org.architecturemining.pnid.models.pnid.PNIDModel;
import org.architecturemining.pnid.models.xlog.EventModel;
import org.architecturemining.pnid.models.xlog.LogModel;

public class AlignmentSearch {
	
	public static List<EventModel> alignmentSearch(PNIDModel flatPN, LogModel log) {
		// Compute a mapping between transitions of the flatPN and the events in the log, which are the sync moves.
		// for (String t : flatPN.GetNet().transitions()) {
			// Strip transition name (?)
			// For example, "T {x0}" is in the log event "T" with resource field "x=0".
			
			// LogModel.getByTransitionFromFlatPN(t);
		//}
		
		// Find closest firing sequence, the sequence with minimal cost.
		
		return null;
	}
	
	public static Map<String,String> computeTransitionEventMapping(){
		return null;
		
	}
}
