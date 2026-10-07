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
import java.io.*;
import java.util.*;

/** Phoenix ABS 40-43, D9aft: Monte Carlo on stability / flight with the same VerifyD9 patches (VK nose CAD
 *  mass/CG, body length + non-nose mass/CG override, fin TE at the CAD station, motor overhang, chute on EJECTION).
 *  Every configuration in CONFIGS sees the SAME random draws (common random numbers), so the difference
 *  between configurations is the configuration, not the dice.
 *
 *  Varied per run (1 sigma unless noted):
 *    printed-part density/flow scale  N(1, 0.04), one factor for every printed part incl. the nose (same filament)
 *    electronics + small parts        N(0, 4.0 g) at the e-bay      canopy + harness  N(0, 2.0 g) fwd in the bay
 *    Nomex / wadding                  N(0, 1.5 g) by the port       fin epoxy         N(0, 1.0 g) at the fin roots
 *    point-mass rollup CG error       N(0, 1.5 mm) on the body CG
 *    wind: mean U(0, WIND_MAX) m/s, turbulence intensity U(5, 20) %, direction U(0, 360)
 *    launch rod tilt |N(0, 2 deg)| capped at 5, direction U(0, 360) (not deliberately into the wind)
 *    fin cant N(0, 0.25 deg)          D9 delay N(5.0, 0.5 s) clipped 3.5..6.5
 *  NOT varied: motor thrust/total impulse (OpenRocket cannot scale a thrust curve), Cd beyond what wind/AoA do,
 *  Barrowman's own CP error (see the CP-shift line in the summary instead).
 *
 *  env: CONFIGS "name:bodyLenMM:bodyG:bodyCgxMM:aftTubeG:aftTubeSt;..."  (stations from the body top, v5 frame
 *       for the fixed list below; aft-frame parts are shifted by 340 - bodyLen), N (runs), SEED, WIND_MAX (m/s),
 *       ROD (guided m), CSV (path), NOSE_G, NOSE_CG. */
public class MonteCarloD9 {
  static String env(String k, String d) { return System.getenv().getOrDefault(k, d); }
  static double envd(String k, String d) { return Double.parseDouble(env(k, d)); }
  static final double CAL = 0.043;
  // name, mass g (printed: nominal CAD mass that scales with density; else sigma g), v5 station mm, printed?, aft-frame?
  static final Object[][] PARTS = {
    {"FwdTube", 21.9, 49.7, true, false}, {"EbayCap", 6.3, 11.9, true, false}, {"Sled v4", 7.2, 40.0, true, false},
    {"FinCan slotted + fins", 50.1, 310.7, true, true}, {"Cap v1", 9.0, 350.8, true, true},
    {"Electronics", 4.0, 43.0, false, false}, {"Canopy", 2.0, 127.7, false, false},
    {"Nomex", 1.5, 245.0, false, true}, {"Fin epoxy", 1.0, 310.0, false, true}};

  static double pct(double[] a, double p) { double[] b = a.clone(); Arrays.sort(b); return b[(int) Math.min(b.length - 1, Math.max(0, Math.round(p * (b.length - 1))))]; }
  static double frac(double[] a, java.util.function.DoublePredicate f) { int n = 0; for (double x : a) if (f.test(x)) n++; return (double) n / a.length; }

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
    nose.setShapeType(Transition.Shape.HAACK); nose.setShapeParameter(0.0); nose.setLength(0.065);
    nose.setAftShoulderRadius(0.01985); nose.setAftShoulderLength(0.042); nose.setThickness(0.002);
    nose.setMassOverridden(true); nose.setCGOverridden(true);
    double noseG = envd("NOSE_G", "14.6"), noseCg = envd("NOSE_CG", "43.8");
    body.setMassOverridden(true); body.setCGOverridden(true);
    body.setSubcomponentsOverriddenMass(true); body.setSubcomponentsOverriddenCG(true);
    fins.setAxialMethod(AxialMethod.BOTTOM); fins.setAxialOffset(-0.6 / 1000);
    mount.setMotorOverhang(14.1 / 1000);
    chute.setDiameter(0.5);
    FlightConfigurationId d9 = null;
    for (FlightConfigurationId id : r.getIds())
      for (MotorConfiguration mc : r.getFlightConfiguration(id).getAllMotors())
        if (mc.getMotor().getDesignation().equals("D9")) d9 = id;
    for (FlightConfigurationId id : r.getIds()) {
      chute.getDeploymentConfigurations().get(id).setDeployEvent(DeploymentConfiguration.DeployEvent.EJECTION);
      chute.getDeploymentConfigurations().get(id).setDeployDelay(0.0);
    }
    chute.getDeploymentConfigurations().getDefault().setDeployEvent(DeploymentConfiguration.DeployEvent.EJECTION);
    r.setSelectedConfiguration(d9);
    FlightConfiguration fc = r.getFlightConfiguration(d9);
    MotorConfiguration mcfg = mount.getMotorConfig(d9);

    String[] cfgs = env("CONFIGS", "v6_cad_bay150:313.5:204.7:155.7:36.5:174.6;v5_bay198:340:204.7:165.0:46.4:177.5").split(";");
    int N = Integer.parseInt(env("N", "300"));
    long seed = Long.parseLong(env("SEED", "20261006"));
    double windMax = envd("WIND_MAX", "8"), rod = envd("ROD", "2.0");
    PrintWriter csv = new PrintWriter(new FileWriter(env("CSV", "montecarlo_D9.csv")));
    csv.println("cfg,run,scale,body_g,body_cgx_mm,wind_ms,ti,wind_dir_deg,rod_tilt_deg,rod_dir_deg,cant_deg,delay_s,static_lo,static_bo,"
      + "rail_exit_ms,min_dyn_stab,max_aoa_pwr_deg,max_aoa_coast_deg,apogee_m,apogee_horiz_m,eject_v_ms,eject_alt_m,ground_hit_ms,landing_m");

    // draws, shared by all configs
    Random rng = new Random(seed);
    double[][] D = new double[N][];
    for (int i = 0; i < N; i++) {
      double[] d = new double[PARTS.length + 10];
      d[0] = 1.0 + 0.04 * rng.nextGaussian();
      for (int k = 0; k < PARTS.length; k++) d[1 + k] = rng.nextGaussian();
      int j = 1 + PARTS.length;
      d[j] = 1.5 * rng.nextGaussian();                                  // CG rollup error, mm
      d[j + 1] = windMax * rng.nextDouble();
      d[j + 2] = 0.05 + 0.15 * rng.nextDouble();
      d[j + 3] = 360 * rng.nextDouble();
      d[j + 4] = Math.min(5.0, Math.abs(2.0 * rng.nextGaussian()));
      d[j + 5] = 360 * rng.nextDouble();
      d[j + 6] = 0.25 * rng.nextGaussian();
      d[j + 7] = Math.max(3.5, Math.min(6.5, 5.0 + 0.5 * rng.nextGaussian()));
      d[j + 8] = rng.nextInt();
      D[i] = d;
    }

    StringBuilder sum = new StringBuilder();
    for (String cs : cfgs) {
      String[] p = cs.split(":");
      String name = p[0];
      double L = Double.parseDouble(p[1]), bG = Double.parseDouble(p[2]), bX = Double.parseDouble(p[3]);
      double atG = Double.parseDouble(p[4]), atX = Double.parseDouble(p[5]);
      double shift = 340.0 - L;
      body.setLength(L / 1000);
      double[] sLo = new double[N], sBo = new double[N], dyn = new double[N], aoaP = new double[N], aoaC = new double[N],
               apo = new double[N], ejv = new double[N], rail = new double[N], land = new double[N], horiz = new double[N];
      long t0 = System.currentTimeMillis();
      for (int i = 0; i < N; i++) {
        double[] d = D[i];
        double s = d[0], M = bG, mom = bG * bX;
        for (int k = 0; k < PARTS.length; k++) {
          double m = (Double) PARTS[k][1], st = (Double) PARTS[k][2] - (((Boolean) PARTS[k][4]) ? shift : 0.0);
          double dm = ((Boolean) PARTS[k][3]) ? m * (s - 1.0) : m * d[1 + k];
          M += dm; mom += dm * st;
        }
        double dmAT = atG * (s - 1.0); M += dmAT; mom += dmAT * atX;
        int j = 1 + PARTS.length;
        double cgx = mom / M + d[j];
        body.setOverrideMass(M / 1000); body.setOverrideCGX(cgx / 1000);
        nose.setOverrideMass(noseG * s / 1000); nose.setOverrideCGX(noseCg / 1000);
        fins.setCantAngle(Math.toRadians(d[j + 6]));
        mcfg.setEjectionDelay(d[j + 7]);
        double cgL = MassCalculator.calculateLaunch(fc).getCM().x, cgB = MassCalculator.calculateBurnout(fc).getCM().x;
        FlightConditions fcn = new FlightConditions(fc); fcn.setMach(0.1); fcn.setAOA(0);
        double cp = new BarrowmanCalculator().getCP(fc, fcn, new WarningSet()).x;
        sLo[i] = (cp - cgL) / CAL; sBo[i] = (cp - cgB) / CAL;

        Simulation sim = new Simulation(doc, r); sim.setFlightConfigurationId(d9);
        SimulationOptions o = sim.getOptions();
        o.setWindSpeedAverage(d[j + 1]); o.setWindTurbulenceIntensity(d[j + 2]); o.setWindDirection(Math.toRadians(d[j + 3]));
        o.setLaunchIntoWind(false); o.setLaunchRodAngle(Math.toRadians(d[j + 4])); o.setLaunchRodDirection(Math.toRadians(d[j + 5]));
        o.setLaunchRodLength(rod); o.setTimeStep(0.01); o.setRandomSeed((int) d[j + 8]);
        sim.simulate();
        FlightData fd = sim.getSimulatedData();
        FlightDataBranch b = fd.getBranch(0);
        List<Double> t = b.get(FlightDataType.TYPE_TIME), v = b.get(FlightDataType.TYPE_VELOCITY_TOTAL), alt = b.get(FlightDataType.TYPE_ALTITUDE),
                     st = b.get(FlightDataType.TYPE_STABILITY), aoa = b.get(FlightDataType.TYPE_AOA),
                     px = b.get(FlightDataType.TYPE_POSITION_X), py = b.get(FlightDataType.TYPE_POSITION_Y);
        double tRail = Double.NaN, tBurn = Double.NaN, tEj = Double.NaN, tApo = fd.getTimeToApogee();
        for (FlightEvent ev : b.getEvents()) {
          if (ev.getType() == FlightEvent.Type.LAUNCHROD && Double.isNaN(tRail)) tRail = ev.getTime();
          if (ev.getType() == FlightEvent.Type.BURNOUT && Double.isNaN(tBurn)) tBurn = ev.getTime();
          if (ev.getType() == FlightEvent.Type.EJECTION_CHARGE && Double.isNaN(tEj)) tEj = ev.getTime();
        }
        double tEnd = Math.min(Double.isNaN(tEj) ? tApo : tEj, tApo);
        double mDyn = Double.POSITIVE_INFINITY, mAP = 0, mAC = 0, hApo = 0, ejAlt = Double.NaN;
        for (int k = 0; k < t.size(); k++) {
          double tk = t.get(k);
          if (!Double.isNaN(tEj) && Double.isNaN(ejAlt) && tk >= tEj) ejAlt = alt.get(k);
          if (tk < tRail || tk > tEnd) continue;
          if (v.get(k) < 15.0) continue;                                  // AoA/margin near apogee are meaningless (v -> 0)
          double sv = st.get(k), av = Math.toDegrees(aoa.get(k));
          if (!Double.isNaN(sv)) mDyn = Math.min(mDyn, sv);
          if (!Double.isNaN(av)) { if (tk <= tBurn) mAP = Math.max(mAP, av); else mAC = Math.max(mAC, av); }
        }
        for (int k = 0; k < t.size(); k++) if (t.get(k) >= tApo) { hApo = Math.hypot(px.get(k), py.get(k)); break; }
        int last = t.size() - 1;
        double lnd = Math.hypot(px.get(last), py.get(last));
        dyn[i] = mDyn; aoaP[i] = mAP; aoaC[i] = mAC; apo[i] = fd.getMaxAltitude(); ejv[i] = fd.getDeploymentVelocity();
        rail[i] = fd.getLaunchRodVelocity(); land[i] = lnd; horiz[i] = hApo;
        csv.printf(Locale.ROOT, "%s,%d,%.4f,%.2f,%.2f,%.2f,%.3f,%.0f,%.2f,%.0f,%.3f,%.2f,%.3f,%.3f,%.2f,%.3f,%.2f,%.2f,%.1f,%.1f,%.2f,%.1f,%.2f,%.1f%n",
          name, i, s, M + 0, cgx, d[j + 1], d[j + 2], d[j + 3], d[j + 4], d[j + 5], d[j + 6], d[j + 7], sLo[i], sBo[i],
          rail[i], dyn[i], aoaP[i], aoaC[i], apo[i], hApo, ejv[i], ejAlt, fd.getGroundHitVelocity(), lnd);
        if (i % 50 == 49) System.err.printf(Locale.ROOT, "%s %d/%d  %.1f s%n", name, i + 1, N, (System.currentTimeMillis() - t0) / 1000.0);
      }
      sum.append(String.format(Locale.ROOT, "%n== %s  (body %.1f mm, %.1f g @ %.1f; N=%d, wind 0-%.0f m/s, %.1f m guided rod) ==%n", name, L, bG, bX, N, windMax, rod));
      String hdr = "%-34s %8s %8s %8s %8s %8s %8s%n";
      sum.append(String.format(Locale.ROOT, hdr, "metric", "p1", "p5", "p50", "p95", "p99", "worst"));
      Object[][] rows = {{"static margin liftoff, cal", sLo, true}, {"static margin burnout, cal", sBo, true},
        {"min in-flight margin (v>15), cal", dyn, true}, {"max AoA powered, deg", aoaP, false}, {"max AoA coast (v>15), deg", aoaC, false},
        {"rail exit, m/s", rail, true}, {"apogee, m", apo, true}, {"apogee drift from pad, m", horiz, false},
        {"speed at ejection, m/s", ejv, false}, {"landing distance, m", land, false}};
      for (Object[] row : rows) {
        double[] x = (double[]) row[1]; boolean lowBad = (Boolean) row[2];
        double w = lowBad ? pct(x, 0) : pct(x, 1);
        sum.append(String.format(Locale.ROOT, "%-34s %8.2f %8.2f %8.2f %8.2f %8.2f %8.2f%n", row[0], pct(x, .01), pct(x, .05), pct(x, .5), pct(x, .95), pct(x, .99), w));
      }
      sum.append(String.format(Locale.ROOT, "P(static liftoff < 1.5) = %.1f %%   P(< 1.0) = %.1f %%%n", 100 * frac(sLo, x -> x < 1.5), 100 * frac(sLo, x -> x < 1.0)));
      sum.append(String.format(Locale.ROOT, "P(min in-flight margin < 1.0) = %.1f %%   P(< 0.5) = %.1f %%   P(max AoA > 10 deg) = %.1f %%%n",
        100 * frac(dyn, x -> x < 1.0), 100 * frac(dyn, x -> x < 0.5), 100 * frac(aoaP, x -> x > 10) ));
      sum.append(String.format(Locale.ROOT, "P(ejection faster than 10 m/s) = %.1f %%   P(> 20 m/s) = %.1f %%%n", 100 * frac(ejv, x -> x > 10), 100 * frac(ejv, x -> x > 20)));
      sum.append(String.format(Locale.ROOT, "CP error that eats the p1 static margin down to 1.0 cal: %.0f mm forward (Barrowman is typically good to ~5-10%% of length)%n",
        (pct(sLo, .01) - 1.0) * 43));
      System.err.printf(Locale.ROOT, "%s done in %.1f s%n", name, (System.currentTimeMillis() - t0) / 1000.0);
    }
    csv.close();
    System.out.println(sum);
    System.exit(0);
  }
}
