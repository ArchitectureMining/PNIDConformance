package org.architecturemining.pnidconformance.plugins;

import java.io.File;
import java.io.IOException;
import java.util.concurrent.ExecutionException;

import org.deckfour.xes.model.XLog;
import org.informationsystem.ismsuite.pnidprocessor.petrinet.MarkedPetriNet;
import org.processmining.contexts.uitopia.annotations.UITopiaVariant;
import org.processmining.framework.plugin.PluginContext;
import org.processmining.framework.plugin.annotations.Plugin;

public class PNIDConformancePlugin {

	@UITopiaVariant(
            affiliation = "Utrecht University", 
            author = "Janjaap Ree", 
            email = "j.ree@students.uu.nl"
    )
	@Plugin(
			name = "Convert CSV log with identifiers to XES log with identifiers", 
			parameterLabels = { "CSV" },
			returnLabels = {"XES Event Log"}, 
			returnTypes = {XLog.class},
			userAccessible = true,
			help = "Converts a given CSV event log with identifiers into an XES event log with identifiers"
	)
	public XLog CSVToXES(PluginContext context, File file) {
		return RunPNIDConformance.createXESLogFromCSV(context, file);
	}
	
	@UITopiaVariant(
            affiliation = "Utrecht University", 
            author = "Janjaap Ree", 
            email = "j.ree@students.uu.nl"
    )
	@Plugin(
			name = "Mine TS from PNID and trace", 
			parameterLabels = { "Process model (PNID)", "XES event log" },
			returnLabels = {"Transition system"}, 
			returnTypes = {MarkedPetriNet.class},
			userAccessible = true,
			help = "Converts a given CSV event log with identifiers into an transition system"
	)
	public Object MineTS(PluginContext context, MarkedPetriNet pnid, XLog trace) throws IOException, InterruptedException, ExecutionException {
		return RunPNIDConformance.findAlignmenForTraceInPNID(context, pnid, trace);
	}
}
