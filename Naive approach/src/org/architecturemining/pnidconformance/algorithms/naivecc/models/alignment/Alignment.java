package org.architecturemining.pnidconformance.algorithms.naivecc.models.alignment;

import java.util.ArrayList;
import java.util.List;

public class Alignment {

	protected List<AlignmentMove> alignment = null;
	
	public Alignment() {
		this.alignment = new ArrayList<AlignmentMove>();
	}
	
	public void addMove(AlignmentMove move) {	
		this.alignment.add(move);	
	}
	
	public void addMoveToPosition(AlignmentMove move, int index) {	
		this.alignment.add(index, move);	
	}
	
	public void removeMove(int index) {	
		this.alignment.remove(index);	
	}
	
	public List<AlignmentMove> getAlignment() {
		return this.alignment;
	}
}
