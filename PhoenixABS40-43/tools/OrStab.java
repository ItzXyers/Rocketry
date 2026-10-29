// Headless OpenRocket 24.12 stability + D9 sim check.  Usage:
//   java -Djava.awt.headless=true -cp "C:/Program Files/OpenRocket/jar/OpenRocket-24.12.jar" tools/OrStab.java <file.ork> ...
import info.openrocket.core.startup.Application;
import info.openrocket.core.plugin.PluginModule;
import info.openrocket.swing.startup.GuiModule;
import info.openrocket.core.file.GeneralRocketLoader;
import info.openrocket.core.document.OpenRocketDocument;
import info.openrocket.core.document.Simulation;
import info.openrocket.core.rocketcomponent.FlightConfiguration;
import info.openrocket.core.aerodynamics.*;
import info.openrocket.core.masscalc.MassCalculator;
import info.openrocket.core.logging.WarningSet;
import com.google.inject.*;
import java.io.File;

public class OrStab {
    public static void main(String[] a) throws Exception {
        GuiModule gui = new GuiModule();
        Injector inj = Guice.createInjector(gui, new PluginModule());
        Application.setInjector(inj);
        gui.startLoader();
        for (String f : a) {
            OpenRocketDocument doc = new GeneralRocketLoader(new File(f)).load();
            FlightConfiguration conf = doc.getRocket().getSelectedConfiguration();
            FlightConditions fc = new FlightConditions(conf);
            fc.setMach(0.1);
            AerodynamicForces af = new BarrowmanCalculator().getAerodynamicForces(conf, fc, new WarningSet());
            double cp = af.getCP().x, cgL = MassCalculator.calculateLaunch(conf).getCM().x, cgB = MassCalculator.calculateBurnout(conf).getCM().x;
            double m = MassCalculator.calculateLaunch(conf).getMass(), d = 2 * conf.getRocket().getBoundingRadius();
            System.out.printf("%s: config '%s' len %.1f mm  mass %.1f g  CP %.1f  CG launch %.1f burnout %.1f  margin %.2f / %.2f cal (d %.1f)%n",
                f, conf.getName(), conf.getLength() * 1000, m * 1000, cp * 1000, cgL * 1000, cgB * 1000, (cp - cgL) / d, (cp - cgB) / d, d * 1000);
            for (Simulation s : doc.getSimulations()) {
                if (!s.getName().contains("D9")) continue;
                s.simulate();
                var fd = s.getSimulatedData();
                System.out.printf("  sim '%s': apogee %.1f m, vmax %.1f m/s, deploy v %.1f m/s, ground hit %.1f m/s, min stability %.2f cal%n",
                    s.getName(), fd.getMaxAltitude(), fd.getMaxVelocity(), fd.getDeploymentVelocity(), fd.getGroundHitVelocity(), fd.getBranch(0).getMinimum(info.openrocket.core.simulation.FlightDataType.TYPE_STABILITY));
            }
        }
        System.exit(0);
    }
}
