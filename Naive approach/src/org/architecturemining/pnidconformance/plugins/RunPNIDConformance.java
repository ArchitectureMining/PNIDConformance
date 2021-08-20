package org.architecturemining.pnidconformance.plugins;

import java.io.File;
import java.io.IOException;
import java.util.Arrays;
import java.util.concurrent.ExecutionException;

import org.architecturemining.pnid.models.pnid.PNIDModel;
import org.architecturemining.pnid.models.xlog.LogModel;
import org.architecturemining.pnidconformance.algorithms.naivecc.NaiveCC;
import org.deckfour.xes.model.XLog;
import org.informationsystem.ismsuite.pnidprocessor.petrinet.MarkedPetriNet;
import org.processmining.framework.plugin.PluginContext;
import org.processmining.framework.plugin.annotations.PluginVariant;
import org.processmining.log.csv.CSVFile;
import org.processmining.log.csv.CSVFileReferenceUnivocityImpl;
import org.processmining.log.csv.config.CSVConfig;
import org.processmining.log.csvimport.CSVConversion;
import org.processmining.log.csvimport.CSVConversion.ConversionResult;
import org.processmining.log.csvimport.config.CSVConversionConfig;
import org.processmining.log.csvimport.exception.CSVConversionException;
import org.processmining.plugins.petrinet.replayresult.PNRepResult;

public class RunPNIDConformance {
	
	@PluginVariant(variantLabel = "Convert CSV log with identifiers to XES log with identifiers", requiredParameterLabels = {0})
	public static XLog createXESLogFromCSV(final PluginContext context, File file) {	
		try {
			CSVFile csvFile = new CSVFileReferenceUnivocityImpl(file.toPath());
			CSVConfig importConfig = new CSVConfig(csvFile);
			CSVConversionConfig conversionConfig = new CSVConversionConfig(csvFile, importConfig);
			conversionConfig.autoDetect();
			
			// Preprocessing
			String[] columns = csvFile.readHeader(importConfig);;
			conversionConfig.setCaseColumns(Arrays.asList("concept:instance"));
			// conversionConfig.setEventNameColumns(Arrays.asList("Activity"));
			// conversionConfig.setCompletionTimeColumn("Timestamp");

			// Convert to XES
			CSVConversion converter = new CSVConversion();
			ConversionResult<XLog> result = converter.doConvertCSVToXES(csvFile, importConfig, conversionConfig);
			
			context.log(result.getConversionErrors());
			return result.getResult();
			
		} catch (CSVConversionException | IOException e) {
			context.log(e);
		}
		
		return null;
	}
	
	@PluginVariant(variantLabel = "Find alignment for trace in PNID", requiredParameterLabels = {0, 1})
	public static PNRepResult findAlignmenForTraceInPNID(PluginContext context, MarkedPetriNet pnid, XLog xlog) throws IOException, InterruptedException, ExecutionException {
		return RunPNIDConformance.findAlignmenForTraceInPNID(context, pnid, xlog, 2);
	}

	public static PNRepResult findAlignmenForTraceInPNID(PluginContext context, MarkedPetriNet pnid, XLog xlog, int maxUnfold) throws IOException, InterruptedException, ExecutionException {
		PNIDModel model = new PNIDModel(pnid);
		LogModel log = new LogModel(xlog);
		
		return NaiveCC.naiveCC(model, log, maxUnfold);
	}
}