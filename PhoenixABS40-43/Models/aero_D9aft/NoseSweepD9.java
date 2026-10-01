import info.openrocket.core.startup.OpenRocketCore;
import info.openrocket.core.file.GeneralRocketLoader;
import info.openrocket.core.document.*;
import info.openrocket.core.rocketcomponent.*;
import info.openrocket.core.rocketcomponent.position.AxialMethod;
import info.openrocket.core.aerodynamics.*;
import info.openrocket.core.masscalc.MassCalculator;
import info.openrocket.core.logging.WarningSet;
import info.openrocket.core.motor.MotorConfiguration;
import info.openrocket.core.simulation.*;
import java.io.File;
import java.util.*;

/** Nose shape x length sweep on the D9aft v2 vehicle (Klima D9-5, aft deploy on ejection, d500 canopy).
 *  Same patches as VerifyD9 (body 340 mm, non-nose mass/CG override from the CAD rollup, fin TE, motor overhang).
 *  Nose: v6-style 9.5 mm threaded shoulder, 2 mm printed shell. Nose mass = OpenRocket shell mass + OFFSET,
 *  where OFFSET makes Von Karman 65 mm equal the v6 CAD mass (solid tip + thread ring are not in OR's shell).
 *  env: NS_BODY_G, NS_BODY_CGX, NOSE_CAD_G (14.6), ROD (guided, m), NS_LENS "40;50;65;80;100;130". */
public class NoseSweepD9 {
  static String env(String k, String d) { return System.getenv().getOrDefault(k, d); }
  static double envd(String k, String d) { return Double.parseDouble(env(k, d)); }
  static NoseCone nose; static BodyTube body; static FinSet fins; static Parachute chute; static InnerTube mount;
  public static void main(String[] a) throws Exception {
    OpenRocketCore.initialize();
    OpenRocketDocument doc = new GeneralRocketLoader(new File(a[0])).load();
    Rocket r = doc.getRocket();
    for (RocketComponent c : r) {
      if (c instanceof NoseCone) nose = (NoseCone) c;
      if (c instanceof BodyTube) body = (BodyTube) c;
      if (c instanceof FinSet) fins = (FinSet) c;
      if (c instanceof Parachute) chute = (Parachute) c;
      if (c instanceof InnerTube && ((InnerTube) c).isMotorMount()) mount = (InnerTube) c;
    }
    body.setLength(0.340);
    body.setMassOverridden(true); body.setOverrideMass(envd("NS_BODY_G", "202.7") / 1000);
    body.setCGOverridden(true); body.setOverrideCGX(envd("NS_BODY_CGX", "165.3") / 1000);
    body.setSubcomponentsOverriddenMass(true); body.setSubcomponentsOverriddenCG(true);
    fins.setAxialMethod(AxialMethod.BOTTOM); fins.setAxialOffset(-0.0006);
    mount.setMotorOverhang(0.0141);
    chute.setDiameter(0.5);
    FlightConfigurationId d9 = null;
    for (FlightConfigurationId id : r.getIds()) {
      chute.getDeploymentConfigurations().get(id).setDeployEvent(DeploymentConfiguration.DeployEvent.EJECTION);
      chute.getDeploymentConfigurations().get(id).setDeployDelay(0.0);
      for (MotorConfiguration mc : r.getFlightConfiguration(id).getAllMotors()) if (mc.getMotor().getDesignation().equals("D9")) d9 = id;
    }
    chute.getDeploymentConfigurations().getDefault().setDeployEvent(DeploymentConfiguration.DeployEvent.EJECTION);
    mount.getMotorConfig(d9).setEjectionDelay(5.0);
    r.setSelectedConfiguration(d9);
    nose.setAftShoulderRadius(0.0199); nose.setAftShoulderLength(0.0095); nose.setAftShoulderThickness(0.0023); nose.setAftShoulderCapped(false);
    nose.setThickness(0.002);
    // calibrate the mass offset on the as-built v6 (Von Karman, 65 mm)
    setShape(Transition.Shape.HAACK, 0.0, 0.065);
    nose.setMassOverridden(false); nose.setCGOverridden(false);
    double offset = envd("NOSE_CAD_G", "14.6") / 1000 - nose.getComponentMass();
    Object[][] shapes = {
      {"VonKarman", Transition.Shape.HAACK, 0.0}, {"LV-Haack", Transition.Shape.HAACK, 1.0 / 3.0},
      {"Parabolic K=1", Transition.Shape.PARABOLIC, 1.0}, {"Parabolic K=0.75", Transition.Shape.PARABOLIC, 0.75},
      {"OGIVE(tangent)", Transition.Shape.OGIVE, 1.0}, {"ELLIPSOID", Transition.Shape.ELLIPSOID, 0.0},
      {"Power n=0.5 (kink)", Transition.Shape.POWER, 0.5}, {"CONICAL (kink)", Transition.Shape.CONICAL, 0.0}};
    String[] ls = env("NS_LENS", "40;50;65;80;100;130").split(";");
    System.out.printf(Locale.ROOT, "# mass offset %.1f g added to OR's shell mass (calibrated: VK 65 mm = %.1f g CAD)%n", offset * 1000, envd("NOSE_CAD_G", "14.6"));
    System.out.println("shape,L_mm,nose_g,CD_M0.3,CDfric,CDpress,CP_mm,CG_mm,margin_cal,apogee_m,vmax,t_apogee,eject_v,rail_exit,ground_hit");
    for (Object[] s : shapes) for (String lsS : ls) {
      double L = Double.parseDouble(lsS) / 1000;
      setShape((Transition.Shape) s[1], (Double) s[2], L);
      nose.setMassOverridden(false); nose.setCGOverridden(false);
      double m = nose.getComponentMass() + offset;
      nose.setMassOverridden(true); nose.setOverrideMass(m);
      FlightConfiguration fc = r.getFlightConfiguration(d9);
      BarrowmanCalculator calc = new BarrowmanCalculator();
      FlightConditions f3 = new FlightConditions(fc); f3.setMach(0.3); f3.setAOA(0);
      AerodynamicForces af = calc.getAerodynamicForces(fc, f3, new WarningSet());
      FlightConditions f1 = new FlightConditions(fc); f1.setMach(0.1); f1.setAOA(0);
      double cp = calc.getCP(fc, f1, new WarningSet()).x;
      double cg = MassCalculator.calculateLaunch(fc).getCM().x;
      Simulation sim = new Simulation(doc, r); sim.setFlightConfigurationId(d9);
      sim.getOptions().setWindSpeedAverage(0); sim.getOptions().setWindSpeedDeviation(0);
      sim.getOptions().setLaunchRodLength(envd("ROD", "2.0")); sim.getOptions().setTimeStep(0.01);
      sim.simulate(); FlightData d = sim.getSimulatedData();
      System.out.printf(Locale.ROOT, "%s,%.0f,%.1f,%.4f,%.4f,%.4f,%.1f,%.1f,%.2f,%.1f,%.1f,%.2f,%.1f,%.1f,%.2f%n", s[0], L * 1000, m * 1000,
        af.getCD(), af.getFrictionCD(), af.getPressureCD(), cp * 1000, cg * 1000, (cp - cg) / 0.043, d.getMaxAltitude(), d.getMaxVelocity(),
        d.getTimeToApogee(), d.getDeploymentVelocity(), d.getLaunchRodVelocity(), d.getGroundHitVelocity());
    }
    System.exit(0);
  }
  static void setShape(Transition.Shape sh, double p, double L) {
    nose.setShapeType(sh); if (sh.usesParameter()) nose.setShapeParameter(p); nose.setLength(L);
  }
}
