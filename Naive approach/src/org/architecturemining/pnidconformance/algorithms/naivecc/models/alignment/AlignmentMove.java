package org.architecturemining.pnidconformance.algorithms.naivecc.models.alignment;

public class AlignmentMove {

	private String moveOnModel;
	private String moveOnLog;
	
	public AlignmentMove(String momTransition, String molTransition) {
		this.moveOnModel = momTransition;
		this.moveOnLog = molTransition;
	}
	
	public void setMom(String momTransition){
		this.moveOnModel = momTransition;
	};
	
	public void setMol(String molTransition){
		this.moveOnLog = molTransition;
	};
}
  