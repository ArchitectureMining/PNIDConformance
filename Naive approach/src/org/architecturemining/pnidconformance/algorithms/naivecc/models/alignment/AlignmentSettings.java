package org.architecturemining.pnidconformance.algorithms.naivecc.models.alignment;

import nl.tue.alignment.algorithms.ReplayAlgorithm.Debug;

public class AlignmentSettings {
	public Debug debugMode = Debug.NONE;
	public int timeoutPerTraceInSec = 10;
	public int timeout = timeoutPerTraceInSec * 1000;
	public int maxNumberOfStates = Integer.MAX_VALUE;
	public boolean moveSort = true;
	public boolean useInt = false;
	public boolean partialOrder = false;
	public boolean preferExact = true;
	public boolean queueSort = true;
	public boolean buildFullStatespace = true;
	public boolean preProcessUsingPlaceBasedConstraints = true;
	public int maxReducedSequenceLength = Integer.MAX_VALUE;
	public int costUpperBound = Integer.MAX_VALUE;
	public int threads = 1;
}
