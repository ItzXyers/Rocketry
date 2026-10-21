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

/** Phoenix ABS 40-43, aft deployment on Klima D9 motor ejection (no spring, no altimeter deploy).
 *  Patches a COPY of the .ork in memory: v5 Von Karman nose (CAD mass/CG), body length + non-nose mass/CG
 *  override from the CAD rollup, fin trailing edge at the CAD station, canopy dia, parachute on EJECTION.
 *  Runs the Klima D9 config at each delay in D9_DELAYS and each rod length in RODS.
 *  env: NS_BODY_G, NS_BODY_LEN (mm), NS_BODY_CGX (mm from body top), NOSE_G, NOSE_CG (mm from tip),
 *       NOSE_LEN (mm), FIN_TE_FWD (mm the fin TE sits forward of the body aft end), CHUTE_D (mm),
 *       MOTOR_OVERHANG (mm), D9_DELAYS "3;5;7", RODS "1.0;1.5;2.0" (m),
 *       SAVE_ORK (path: write the patched doc there, D9-5 selected, with a stored D9-5 / 1.5 m rod simulation). */
public class VerifyD9v2 {
  static String env(String k, String d) { return System.getenv().getOrDefault(k, d); }
  static double envd(String k, String d) { return Double.parseDouble(env(k, d)); }
  public static void main(String[] a) throws Exception {
    OpenRocketCore.initialize();
    OpenRocketDocument doc = new GeneralRocketLoader(new File(a[0])).load();
    Rocket r = doc.getRocket();
    NoseCone nose = null; BodyTube body = null; FinSet fins = null; Parachute chute = null; InnerTube mount = null;
    for (RocketComponent c : r) {
      if (c instanceof NoseCone) nose = (NoseCone) c;
      if (c instanceof BodyTube) body = (BodyTube) c;
      if (c instanceof FinSet) fins = (FinSet) c;
      if (c instanceof Parachute) chute = (Parachute) c;
      if (c instanceof InnerTube && ((InnerTube) c).isMotorMount()) mount = (InnerTube) c;
    }
    double L = envd("NOSE_LEN", "65") / 1000;
    nose.setShapeType(Transition.Shape.HAACK); nose.setShapeParameter(0.0); nose.setLength(L);
    nose.setAftShoulderRadius(0.01985); nose.setAftShoulderLength(0.042); nose.setThickness(0.002);
    nose.setMassOverridden(true); nose.setOverrideMass(envd("NOSE_G", "43.4") / 1000);
    nose.setCGOverridden(true); nose.setOverrideCGX(envd("NOSE_CG", "69.7") / 1000);
    double bodyL = envd("NS_BODY_LEN", "340") / 1000;
    body.setLength(bodyL);
    body.setMassOverridden(true); body.setOverrideMass(envd("NS_BODY_G", "205") / 1000);
    body.setCGOverridden(true); body.setOverrideCGX(envd("NS_BODY_CGX", "177") / 1000);
    body.setSubcomponentsOverriddenMass(true); body.setSubcomponentsOverriddenCG(true);
    // fin TE: CAD fin root runs Zf 0.6..51.4 -> TE 0.6 mm forward of the body aft end
    fins.setAxialMethod(AxialMethod.BOTTOM); fins.setAxialOffset(-envd("FIN_TE_FWD", "0.6") / 1000);
    double bodyTop = body.getComponentLocations()[0].x, finTop = fins.getComponentLocations()[0].x;
    System.out.printf(Locale.ROOT, "GEOM nose L=%.1f body top=%.1f len=%.1f aft=%.1f | fin root LE=%.1f TE=%.1f (TE %.1f fwd of body aft) | mount motor overhang=%.1f%n",
      L * 1000, bodyTop * 1000, bodyL * 1000, (bodyTop + bodyL) * 1000, finTop * 1000, (finTop + fins.getLength()) * 1000,
      (bodyTop + bodyL - finTop - fins.getLength()) * 1000, mount.getMotorOverhang() * 1000);
    mount.setMotorOverhang(envd("MOTOR_OVERHANG", "14.1") / 1000);   // CAD: casing aft face 14.1 mm aft of the body (cap v1)
    chute.setDiameter(envd("CHUTE_D", "500") / 1000);
    chute.getDeploymentConfigurations().getDefault().setDeployEvent(DeploymentConfiguration.DeployEvent.EJECTION);
    chute.getDeploymentConfigurations().getDefault().setDeployDelay(0.0);
    FlightConfigurationId d9 = null;
    for (FlightConfigurationId id : r.getIds())
      for (MotorConfiguration mc : r.getFlightConfiguration(id).getAllMotors())
        if (mc.getMotor().getDesignation().equals("D9")) d9 = id;
    for (FlightConfigurationId id : r.getIds()) {
      chute.getDeploymentConfigurations().get(id).setDeployEvent(DeploymentConfiguration.DeployEvent.EJECTION);
      chute.getDeploymentConfigurations().get(id).setDeployDelay(0.0);
    }
    r.setSelectedConfiguration(d9);
    FlightConfiguration fc = r.getFlightConfiguration(d9);
    MotorConfiguration mcfg = mount.getMotorConfig(d9);
    System.out.printf(Locale.ROOT, "MOTOR %s %s dia=%.1f len=%.1f mLaunch=%.1f mBurnout=%.1f%n", ((info.openrocket.core.motor.ThrustCurveMotor) mcfg.getMotor()).getManufacturer().getSimpleName(),
      mcfg.getMotor().getDesignation(), mcfg.getMotor().getDiameter() * 1000, mcfg.getMotor().getLength() * 1000,
      ((info.openrocket.core.motor.ThrustCurveMotor) mcfg.getMotor()).getLaunchMass() * 1000, ((info.openrocket.core.motor.ThrustCurveMotor) mcfg.getMotor()).getBurnoutMass() * 1000);
    double cgL = MassCalculator.calculateLaunch(fc).getCM().x, mL = MassCalculator.calculateLaunch(fc).getMass();
    double cgB = MassCalculator.calculateBurnout(fc).getCM().x, mB = MassCalculator.calculateBurnout(fc).getMass();
    FlightConditions fcn = new FlightConditions(fc); fcn.setMach(0.1); fcn.setAOA(0);
    double cp = new BarrowmanCalculator().getCP(fc, fcn, new WarningSet()).x;
    System.out.printf(Locale.ROOT, "STAB liftoff %.1f g CG %.1f | burnout %.1f g CG %.1f | CP(M0.1) %.1f | margin liftoff %.2f burnout %.2f cal%n",
      mL * 1000, cgL * 1000, mB * 1000, cgB * 1000, cp * 1000, (cp - cgL) / 0.043, (cp - cgB) / 0.043);
    String[] delays = env("D9_DELAYS", "3;5;7").split(";"), rods = env("RODS", "1.0;1.5;2.0").split(";");
    for (String ds : delays) {
      double dly = Double.parseDouble(ds);
      mcfg.setEjectionDelay(dly);
      for (String rs : rods) {
        Simulation s = new Simulation(doc, r); s.setFlightConfigurationId(d9);
        s.getOptions().setWindSpeedAverage(0); s.getOptions().setWindSpeedDeviation(0);
        s.getOptions().setLaunchRodLength(Double.parseDouble(rs)); s.getOptions().setTimeStep(0.01);
        s.simulate(); FlightData d = s.getSimulatedData();
        FlightDataBranch b = d.getBranch(0);
        List<Double> t = b.get(FlightDataType.TYPE_TIME), alt = b.get(FlightDataType.TYPE_ALTITUDE), v = b.get(FlightDataType.TYPE_VELOCITY_TOTAL);
        double tEj = 0, altEj = 0;
        for (FlightEvent ev : b.getEvents()) if (ev.getType() == FlightEvent.Type.EJECTION_CHARGE) { tEj = ev.getTime(); }
        for (int i = 0; i < t.size(); i++) if (t.get(i) >= tEj) { altEj = alt.get(i); break; }
        System.out.printf(Locale.ROOT, "SIM D9-%.0f rod %.1f m | apogee %.1f m @ %.2f s | vmax %.1f m/s | rail exit %.1f m/s | eject t=%.2f alt %.1f m v %.1f m/s | optimum delay %.2f s | ground hit %.2f m/s | flight %.1f s%n",
          dly, Double.parseDouble(rs), d.getMaxAltitude(), d.getTimeToApogee(), d.getMaxVelocity(), d.getLaunchRodVelocity(),
          tEj, altEj, d.getDeploymentVelocity(), d.getOptimumDelay(), d.getGroundHitVelocity(), d.getFlightTime());
      }
    }
    String save = env("SAVE_ORK", "");
    if (!save.isEmpty()) {
      mcfg.setEjectionDelay(5.0);
      r.getFlightConfiguration(d9).setName("Klima D9-5 aft deploy");
      r.setSelectedConfiguration(d9);
      Simulation s = new Simulation(doc, r); s.setFlightConfigurationId(d9); s.setName(env("SIM_NAME", "D9-5 aft deploy, 1.5 m rod, no wind"));
      s.getOptions().setWindSpeedAverage(0); s.getOptions().setWindSpeedDeviation(0); s.getOptions().setLaunchRodLength(1.5); s.getOptions().setTimeStep(0.01);
      s.simulate(); doc.addSimulation(s);
      new info.openrocket.core.file.GeneralRocketSaver().save(new File(save), doc);
      System.out.println("SAVED " + save);
    }
    System.exit(0);
  }
}
