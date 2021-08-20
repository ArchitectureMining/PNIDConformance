package org.architecturemining.pnidconformance.algorithms.naivecc;

import java.io.FileNotFoundException;
import java.util.concurrent.ExecutionException;

import org.architecturemining.pnid.models.pnid.PNIDModel;
import org.architecturemining.pnid.models.xlog.LogModel;
import org.processmining.plugins.petrinet.replayresult.PNRepResult;

/**
 * @author J. Ree
 * 
 * A naive approach to conformance checking on a Petri net with identifiers (PNID).
 * Given a PNID and a trace with identifier, flattens the PNID to a classic petri net (up to a bound of identifiers),
 * computes the corresponding transition system, and finds the closest firing sequence in the transition system, a.k.a. alignment.   
 *
 */
public class NaiveCC {
	
	public static PNRepResult naiveCC(PNIDModel pnid, LogModel log, int maxUnfold) throws FileNotFoundException, InterruptedException, ExecutionException {	
		printTraceInfo(log);
		
		long start = System.nanoTime();
		
		// Generate flat petri net such that alignment technique can be applied
		PNIDModel flatPN = FlattenPNID.generateFlatPN(pnid, maxUnfold);
		
		long finish = System.nanoTime();		
		
		printModelInfo(flatPN, maxUnfold);
		
		// Find closest trace - alignment technique (AStar)
		PNRepResult result = AlignmentSearch.alignmentSearch(flatPN, log.GetXLog());		
		
		printTraceDistance(result, finish - start);

		
		return result;
	}
	
	public static void printTraceInfo(LogModel log) {
		System.out.println("\n##### LOG");
		System.out.println("ID : " + log.GetXLog().get(0).get(0).toString());
		System.out.println("Length : " + log.GetXLog().size());
		System.out.println(
	        "Bound on identifier (normalized from 0) : NOT IMPLEMENTED PRINT"
	    );
	}
	
	public static void printModelInfo(PNIDModel flatPN, int maxUnfold) {
		System.out.println("##### MODEL");
		System.out.println("Amount of transitions : " + flatPN.transitions().size());
		System.out.println("Bound : " + maxUnfold);
	}
	
	public static void printTraceDistance(PNRepResult result, long flatteningTime) {
		System.out.println("##### CONFORMANCE CHECKING");
		System.out.println("Fitness : " + result.getInfo().get("Trace Fitness"));
		System.out.println("time/Flattening: " + flatteningTime / (double)1000000);
		System.out.println("time/AStar: " + result.getInfo().get("Calculation Time (ms)"));
		System.out.println("time/total: " + (flatteningTime  / (double)1000000 +  Double.parseDouble(result.getInfo().get("Calculation Time (ms)").toString())));
	}
	
	public static void printTraceAlignment(PNRepResult result) {
		// WIP: Print here the alignment
	}
}