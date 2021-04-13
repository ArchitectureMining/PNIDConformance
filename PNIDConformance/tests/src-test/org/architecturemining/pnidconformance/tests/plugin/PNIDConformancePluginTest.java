package org.architecturemining.pnidconformance.tests.plugin;
import java.io.File;
import java.nio.file.Paths;

import org.architecturemining.pnid.models.pnid.PNIDModel;
import org.architecturemining.pnidconformance.plugins.PNIDConformanceContext;
import org.architecturemining.pnidconformance.plugins.RunPNIDConformance;
import org.deckfour.xes.model.XLog;
import org.informationsystem.ismsuite.pnidprocessor.petrinet.MarkedPetriNet;
import org.junit.Test;

import junit.framework.TestCase;

public class PNIDConformancePluginTest extends TestCase {
 
  private PNIDConformanceContext context;
  private String basePath;
  private MarkedPetriNet model;
  private XLog log;
  
  private void initTest() {
	  context = new PNIDConformanceContext();
	  basePath = Paths.get("").toAbsolutePath() + "/tests/src-test/org/architecturemining/pnidconformance/tests/plugin/Input files (log)/";
  }
	
  @Test
  public void testTSOfPNIDWithoutVariables() throws Throwable {
	  	initTest();
		
		model = PNIDExampleNets.GetNoVariableNet();	
		log = RunPNIDConformance.createXESLogFromCSV(context.getMainPluginContext(), new File(basePath + "test1.csv"));		
		PNIDModel p = RunPNIDConformance.mineTSFromPNIDAndTrace(context.getMainPluginContext(), model, log, 2);
		
		System.out.print("\nFlat PNID\n");
		System.out.print("-----------------------------\n");
		System.out.print(p);
		
		assertNotNull(p);
		// Assert places
		assertEquals(2, p.GetNet().places().size());
		// Assert transitions
		assertEquals(1, p.GetNet().transitions().size());
		// Assert arcs
		assertTrue(p.GetNet().hasInArc("T", "p1"));
		assertTrue(p.GetNet().hasOutArc("T", "p2"));
  }

  @Test
  public void testTSOfPNIDWithSingleVariableAndTwoIdentifiers() throws Throwable {
	  	initTest();
		
		model = PNIDExampleNets.GetSingleVariableNet();
		log = RunPNIDConformance.createXESLogFromCSV(context.getMainPluginContext(), new File(basePath + "test2.csv"));		
		PNIDModel p = RunPNIDConformance.mineTSFromPNIDAndTrace(context.getMainPluginContext(), model, log, 2);
		
		System.out.print("\nFlat PNID\n");
		System.out.print("-----------------------------\n");
		System.out.print(p);
		
		assertNotNull(p);
		// Assert places
		assertEquals(6, p.GetNet().places().size());
		// Assert transitions
		assertEquals(3, p.GetNet().transitions().size());
		// Assert arcs
		assertTrue(p.GetNet().hasInArc("T {x=0}", "p1 [0]"));
		assertTrue(p.GetNet().hasInArc("T {x=1}", "p1 [1]"));
		assertTrue(p.GetNet().hasInArc("T {x=2}", "p1 [2]"));
		assertTrue(p.GetNet().hasOutArc("T {x=0}", "p2 [0]"));
		assertTrue(p.GetNet().hasOutArc("T {x=1}", "p2 [1]"));
		assertTrue(p.GetNet().hasOutArc("T {x=2}", "p2 [2]"));
  }
  
  @Test
  public void testTSOfPNIDWithSimpleCreator() throws Throwable {
	  	initTest();
		
		model = PNIDExampleNets.GetSimpleCreatorNet();
		log = RunPNIDConformance.createXESLogFromCSV(context.getMainPluginContext(), new File(basePath + "test3.csv"));	
		PNIDModel p = RunPNIDConformance.mineTSFromPNIDAndTrace(context.getMainPluginContext(), model, log, 2);
		
		System.out.print("\nFlat PNID\n");
		System.out.print("-----------------------------\n");
		System.out.print(p);
		
		assertNotNull(p);
		// Assert places
		assertEquals(7, p.GetNet().places().size());
		// Assert transitions
		assertEquals(9, p.GetNet().transitions().size());
		// Assert arcs
		assertTrue(p.GetNet().hasInArc("T {c=0}", "store"));
		assertTrue(p.GetNet().hasInArc("T {c=1}", "store"));
		assertTrue(p.GetNet().hasInArc("T {c=2}", "store"));
		assertTrue(p.GetNet().hasOutArc("T {c=0}", "p1 [0]"));
		assertTrue(p.GetNet().hasOutArc("T {c=1}", "p1 [1]"));
		assertTrue(p.GetNet().hasOutArc("T {c=2}", "p1 [2]"));
		
		assertTrue(p.GetNet().hasInArc("U {c=0}", "p1 [0]"));
		assertTrue(p.GetNet().hasInArc("U {c=1}", "p1 [1]"));
		assertTrue(p.GetNet().hasInArc("U {c=2}", "p1 [2]"));
		assertTrue(p.GetNet().hasOutArc("U {c=0}", "p2 [0]"));
		assertTrue(p.GetNet().hasOutArc("U {c=1}", "p2 [1]"));
		assertTrue(p.GetNet().hasOutArc("U {c=2}", "p2 [2]"));
		
		assertTrue(p.GetNet().hasInArc("V {c=0}", "p2 [0]"));
		assertTrue(p.GetNet().hasInArc("V {c=1}", "p2 [1]"));
		assertTrue(p.GetNet().hasInArc("V {c=2}", "p2 [2]"));
		assertTrue(p.GetNet().hasOutArc("V {c=0}", "store"));
		assertTrue(p.GetNet().hasOutArc("V {c=1}", "store"));
		assertTrue(p.GetNet().hasOutArc("V {c=2}", "store"));
  }
  
  @Test
  public void testTSOfPNIDWithMergingTransitionWithCounterPlace() throws Throwable {
	  	initTest();
		
		model = PNIDExampleNets.GetMergingTransitionNetWithCounterPlace();
		log = RunPNIDConformance.createXESLogFromCSV(context.getMainPluginContext(), new File(basePath + "test4.csv"));
		PNIDModel p = RunPNIDConformance.mineTSFromPNIDAndTrace(context.getMainPluginContext(), model, log, 2);

		System.out.print("\nFlat PNID\n");
		System.out.print("-----------------------------\n");
		System.out.print(p);
		
		assertNotNull(p);
		// Assert places
		assertEquals(24, p.GetNet().places().size());
		// Assert transitions
		assertEquals(17, p.GetNet().transitions().size());
		// Assert arcs
		assertTrue(p.GetNet().hasInArc("T1 {x=1, y=2}", "C 0"));
		assertTrue(p.GetNet().hasInArc("T2 {x=2, y=1}", "C 0"));
		assertTrue(p.GetNet().hasOutArc("T1 {x=1, y=2}", "C 2"));
		assertTrue(p.GetNet().hasOutArc("T1 {x=1, y=2}", "p1 [1]"));
		assertTrue(p.GetNet().hasOutArc("T1 {x=1, y=2}", "p2 [2]"));
		assertTrue(p.GetNet().hasOutArc("T1 {x=1, y=2}", "p3 [1, 2]"));
		assertTrue(p.GetNet().hasOutArc("T2 {x=2, y=1}", "C 2"));
		assertTrue(p.GetNet().hasOutArc("T2 {x=2, y=1}", "p1 [2]"));
		assertTrue(p.GetNet().hasOutArc("T2 {x=2, y=1}", "p2 [1]"));
		assertTrue(p.GetNet().hasOutArc("T2 {x=2, y=1}", "p3 [2, 1]"));
		
		assertTrue(p.GetNet().hasInArc("U {x=0}", "p1 [0]"));
		assertTrue(p.GetNet().hasInArc("U {x=1}", "p1 [1]"));
		assertTrue(p.GetNet().hasInArc("U {x=2}", "p1 [2]"));
		assertTrue(p.GetNet().hasOutArc("U {x=0}", "p4 [0]"));
		assertTrue(p.GetNet().hasOutArc("U {x=1}", "p4 [1]"));
		assertTrue(p.GetNet().hasOutArc("U {x=2}", "p4 [2]"));
		
		assertTrue(p.GetNet().hasInArc("V {x=0}", "p2 [0]"));
		assertTrue(p.GetNet().hasInArc("V {x=1}", "p2 [1]"));
		assertTrue(p.GetNet().hasInArc("V {x=2}", "p2 [2]"));
		assertTrue(p.GetNet().hasOutArc("V {x=0}", "p5 [0]"));
		assertTrue(p.GetNet().hasOutArc("V {x=1}", "p5 [1]"));
		assertTrue(p.GetNet().hasOutArc("V {x=2}", "p5 [2]"));
		
		assertTrue(p.GetNet().hasInArc("W {x=0, y=0}", "p3 [0, 0]"));
		assertTrue(p.GetNet().hasInArc("W {x=0, y=0}", "p4 [0]"));
		assertTrue(p.GetNet().hasInArc("W {x=0, y=0}", "p5 [0]"));
		assertTrue(p.GetNet().hasInArc("W {x=0, y=1}", "p3 [0, 1]"));
		assertTrue(p.GetNet().hasInArc("W {x=0, y=1}", "p4 [0]"));
		assertTrue(p.GetNet().hasInArc("W {x=0, y=1}", "p5 [1]"));
		assertTrue(p.GetNet().hasInArc("W {x=0, y=2}", "p3 [0, 2]"));
		assertTrue(p.GetNet().hasInArc("W {x=0, y=2}", "p4 [0]"));
		assertTrue(p.GetNet().hasInArc("W {x=0, y=2}", "p5 [2]"));	
		assertTrue(p.GetNet().hasInArc("W {x=1, y=0}", "p3 [1, 0]"));
		assertTrue(p.GetNet().hasInArc("W {x=1, y=0}", "p4 [1]"));
		assertTrue(p.GetNet().hasInArc("W {x=1, y=0}", "p5 [0]"));		
		assertTrue(p.GetNet().hasInArc("W {x=1, y=1}", "p3 [1, 1]"));
		assertTrue(p.GetNet().hasInArc("W {x=1, y=1}", "p4 [1]"));
		assertTrue(p.GetNet().hasInArc("W {x=1, y=1}", "p5 [1]"));	
		assertTrue(p.GetNet().hasInArc("W {x=1, y=2}", "p3 [1, 2]"));
		assertTrue(p.GetNet().hasInArc("W {x=1, y=2}", "p4 [1]"));
		assertTrue(p.GetNet().hasInArc("W {x=1, y=2}", "p5 [2]"));		
		assertTrue(p.GetNet().hasInArc("W {x=2, y=0}", "p3 [2, 0]"));
		assertTrue(p.GetNet().hasInArc("W {x=2, y=0}", "p4 [2]"));
		assertTrue(p.GetNet().hasInArc("W {x=2, y=0}", "p5 [0]"));	
		assertTrue(p.GetNet().hasInArc("W {x=2, y=1}", "p3 [2, 1]"));
		assertTrue(p.GetNet().hasInArc("W {x=2, y=1}", "p4 [2]"));
		assertTrue(p.GetNet().hasInArc("W {x=2, y=1}", "p5 [1]"));	
		assertTrue(p.GetNet().hasInArc("W {x=2, y=2}", "p3 [2, 2]"));
		assertTrue(p.GetNet().hasInArc("W {x=2, y=2}", "p4 [2]"));
		assertTrue(p.GetNet().hasInArc("W {x=2, y=2}", "p5 [2]"));	
  }
  
  public static void main(String[] args) {
	  //log = new XLogModel(path.toString() + "/tests/src-test/org/processmining/tests/pnidplugin/Input files (log)/simplenet1.xes");
	  System.out.print("Started test!");
  }
  
}
