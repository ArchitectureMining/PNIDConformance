package org.architecturemining.pnidconformance.plugins;

import org.processmining.framework.plugin.PluginContext;
import org.processmining.framework.plugin.PluginDescriptor;
import org.processmining.framework.plugin.impl.AbstractGlobalContext;

public class PNIDConformanceContext extends AbstractGlobalContext {

	private PluginContext mainContext;
	
	public PNIDConformanceContext() {
		mainContext = new PNIDConformancePluginContext(this, "experiment");
	}
	
	@Override
	public PluginContext getMainPluginContext() {
		return mainContext;
	}

	@Override
	public Class<? extends PluginContext> getPluginContextType() {
		return PNIDConformancePluginContext.class;
	}
	
	@Override
	public void invokePlugin(PluginDescriptor plugin, int index, Object... objects) {
		System.out.println("Call global invoke");
		super.invokePlugin(plugin, index, objects);
	}

}
