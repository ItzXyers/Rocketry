import info.openrocket.core.startup.OpenRocketCore;
import info.openrocket.core.file.GeneralRocketLoader;
import info.openrocket.core.document.*;
import info.openrocket.core.rocketcomponent.*;
import info.openrocket.core.aerodynamics.*;
import info.openrocket.core.masscalc.MassCalculator;
import info.openrocket.core.logging.WarningSet;
import info.openrocket.core.motor.MotorConfiguration;
import info.openrocket.core.simulation.*;
import java.io.File;
import java.util.*;

/** Verify the v5 nose (CAD mass/CG) on the as-built airframe; size tip ballast for a target margin.
 *  Args: <ork> <L_mm> <nose_g> <nose_cg_mm_from_tip> <ballast_centroid_mm_from_tip> <target_cal> */
public class Verify {
  public static void main(String[] a) throws Exception {
    OpenRocketCore.initialize();
    double L = Double.parseDouble(a[1]) / 1000, mN = Double.parseDouble(a[2]) / 1000, cgN = Double.parseDouble(a[3]) / 1000;
    double xB = Double.parseDouble(a[4]) / 1000, target = Double.parseDouble(a[5]);
    double bodyM = Double.parseDouble(System.getenv().getOrDefault("NS_BODY_G", "245")) / 1000;
    OpenRocketDocument doc = new GeneralRocketLoader(new File(a[0])).load();
    Rocket r = doc.getRocket();
    NoseCone nose = null; BodyTube body = null;
    for (RocketComponent c : r) { if (c instanceof NoseCone) nose = (NoseCone) c; if (c instanceof BodyTube) body = (BodyTube) c; }
    body.setLength(0.340); body.setMassOverridden(true); body.setOverrideMass(bodyM);
    body.setCGOverridden(true); body.setOverrideCGX(0.1927);
    body.setSubcomponentsOverriddenMass(true); body.setSubcomponentsOverriddenCG(true);
    nose.setShapeType(Transition.Shape.HAACK); nose.setShapeParameter(0.0); nose.setLength(L);
    nose.setAftShoulderRadius(0.01985); nose.setAftShoulderLength(0.042); nose.setThickness(0.002);
    nose.setMassOverridden(true); nose.setCGOverridden(true);
    Map<String, FlightConfigurationId> cf = new LinkedHashMap<>();
    for (FlightConfigurationId id : r.getIds())
      for (MotorConfiguration mc : r.getFlightConfiguration(id).getAllMotors()) {
        String k = mc.getMotor().getDesignation();
        if (mc.getMotor().getDigest().length() > 0 && !cf.containsKey(k) && (k.equals("A8") || k.equals("B4") || k.equals("C6"))) cf.put(k, id);
      }
    for (double b = 0; b <= 0.0301; b += 0.0025) {
      double m = mN + b, cg = (mN * cgN + b * xB) / m;
      nose.setOverrideMass(m); nose.setOverrideCGX(cg);
      StringBuilder sb = new StringBuilder(String.format(Locale.ROOT, "RESULT ballast=%4.1fg nose=%5.1fg cg=%5.1fmm", b * 1000, m * 1000, cg * 1000));
      boolean ok = true;
      for (Map.Entry<String, FlightConfigurationId> e : cf.entrySet()) {
        FlightConfiguration fc = r.getFlightConfiguration(e.getValue());
        double cgx = MassCalculator.calculateLaunch(fc).getCM().x;
        double lm = MassCalculator.calculateLaunch(fc).getMass();
        FlightConditions fcn = new FlightConditions(fc); fcn.setMach(0.1); fcn.setAOA(0);
        double cp = new BarrowmanCalculator().getCP(fc, fcn, new WarningSet()).x;
        double mg = (cp - cgx) / 0.043;
        Simulation s = new Simulation(doc, r); s.setFlightConfigurationId(e.getValue());
        s.getOptions().setWindSpeedAverage(0); s.getOptions().setWindSpeedDeviation(0); s.getOptions().setLaunchRodLength(1.0); s.getOptions().setTimeStep(0.01);
        s.simulate(); FlightData d = s.getSimulatedData();
        sb.append(String.format(Locale.ROOT, " | %s liftoff=%.0fg CP=%.0f CG=%.0f margin=%.2f apogee=%.1fm vmax=%.1f rail=%.1f",
          e.getKey(), lm * 1000, cp * 1000, cgx * 1000, mg, d.getMaxAltitude(), d.getMaxVelocity(), d.getLaunchRodVelocity()));
        if (mg < target) ok = false;
      }
      System.out.println(sb + (ok ? "  <-- meets " + target : ""));
    }
  }
}
