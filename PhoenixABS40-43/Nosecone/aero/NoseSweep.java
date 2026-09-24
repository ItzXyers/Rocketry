import info.openrocket.core.startup.OpenRocketCore;
import info.openrocket.core.file.GeneralRocketLoader;
import info.openrocket.core.document.OpenRocketDocument;
import info.openrocket.core.document.Simulation;
import info.openrocket.core.rocketcomponent.*;
import info.openrocket.core.aerodynamics.*;
import info.openrocket.core.masscalc.MassCalculator;
import info.openrocket.core.logging.WarningSet;
import info.openrocket.core.motor.MotorConfiguration;
import info.openrocket.core.simulation.SimulationOptions;
import info.openrocket.core.simulation.FlightData;
import java.io.File;
import java.util.*;

/**
 * Nose-shape sweep for Phoenix ABS 40-43 on a COPY of the .ork.
 * Args: <ork> <massMode: fixed|real> [fixedNoseGrams]
 * Airframe patched to the as-built T5 stack: body 340 mm, non-nose dry mass
 * 245 g with CG 192.7 mm aft of the body top (see nose v5 build report).
 */
public class NoseSweep {
    static final double BODY_LEN = 0.340, BODY_CG = 0.1927;
    static final double BODY_MASS = System.getenv("NS_BODY_G") != null ? Double.parseDouble(System.getenv("NS_BODY_G")) / 1000.0 : 0.245;
    static final double R = 0.0215;

    public static void main(String[] a) throws Exception {
        OpenRocketCore.initialize();
        String mode = a[1];
        double fixedNose = a.length > 2 ? Double.parseDouble(a[2]) / 1000.0 : 0.030;
        double wall = a.length > 3 ? Double.parseDouble(a[3]) / 1000.0 : 0.002;

        OpenRocketDocument doc = new GeneralRocketLoader(new File(a[0])).load();
        Rocket rocket = doc.getRocket();
        NoseCone nose = null; BodyTube body = null;
        for (RocketComponent c : rocket) {
            if (c instanceof NoseCone) nose = (NoseCone) c;
            if (c instanceof BodyTube) body = (BodyTube) c;
        }
        body.setLength(BODY_LEN);
        body.setMassOverridden(true); body.setOverrideMass(BODY_MASS);
        body.setCGOverridden(true); body.setOverrideCGX(BODY_CG);
        body.setSubcomponentsOverriddenMass(true); body.setSubcomponentsOverriddenCG(true);

        // Nose: ⌀39.7 shoulder, 42 mm long (DESIGN 7.4 / 9), thin printed shell.
        nose.setAftShoulderRadius(0.01985); nose.setAftShoulderLength(0.042);
        nose.setAftShoulderThickness(0.0015); nose.setAftShoulderCapped(true);
        nose.setThickness(wall);

        // motor configs: Estes B4-4 and Estes C6-3 (binding for stability)
        Map<String, FlightConfigurationId> cfgs = new LinkedHashMap<>();
        for (FlightConfigurationId id : rocket.getIds()) {
            FlightConfiguration fc = rocket.getFlightConfiguration(id);
            for (MotorConfiguration mc : fc.getAllMotors()) {
                String d = mc.getMotor().getDesignation() + "|" + mc.getMotor().getDigest().substring(0, 6);
                String key = mc.getMotor().getDesignation();
                if ((key.equals("C6") || key.equals("B4")) && !cfgs.containsKey(key)) cfgs.put(key, id);
            }
        }

        Object[][] shapes = {
            {"ELLIPSOID", Transition.Shape.ELLIPSOID, 0.0},
            {"OGIVE(tangent)", Transition.Shape.OGIVE, 1.0},
            {"VonKarman", Transition.Shape.HAACK, 0.0},
            {"LV-Haack", Transition.Shape.HAACK, 1.0 / 3.0},
            {"Parabolic K=1", Transition.Shape.PARABOLIC, 1.0},
            {"Parabolic K=0.5", Transition.Shape.PARABOLIC, 0.5},
            {"Power n=0.5", Transition.Shape.POWER, 0.5},
            {"CONICAL", Transition.Shape.CONICAL, 0.0},
        };
        double[] lens = {0.040, 0.060, 0.080, 0.100, 0.130, 0.160};
        if (System.getenv("NS_LENS") != null) lens = Arrays.stream(System.getenv("NS_LENS").split(";")).mapToDouble(x -> Double.parseDouble(x) / 1000.0).toArray();

        System.out.println("shape,L_mm,fineness,nose_g,CD_M0.2,CDfric,CDpress,CDbase,nose_CDpress,CP_mm,CG_C6_mm,margin_C6_cal,apogee_C6_m,vmax_C6,mach_C6,apogee_B4_m,margin_B4_cal,railexit_C6");
        for (Object[] s : shapes) for (double L : lens) {
            nose.setShapeType((Transition.Shape) s[1]);
            if (((Transition.Shape) s[1]).usesParameter()) nose.setShapeParameter((Double) s[2]);
            nose.setLength(L);
            if (mode.equals("fixed")) {
                nose.setMassOverridden(true); nose.setOverrideMass(fixedNose);
                nose.setCGOverridden(true); nose.setOverrideCGX(L * 0.6);
            } else {
                nose.setMassOverridden(false); nose.setCGOverridden(false);
            }
            StringBuilder row = new StringBuilder();
            row.append(String.format(Locale.ROOT, "%s,%.0f,%.2f", s[0], L * 1000, L / (2 * R)));

            FlightConfiguration cfgC6 = rocket.getFlightConfiguration(cfgs.get("C6"));
            double noseMass = nose.getMass(); // structural, before override
            if (nose.isMassOverridden()) noseMass = nose.getOverrideMass();
            row.append(String.format(Locale.ROOT, ",%.1f", noseMass * 1000));

            BarrowmanCalculator calc = new BarrowmanCalculator();
            FlightConditions fcnd = new FlightConditions(cfgC6);
            fcnd.setMach(0.2); fcnd.setAOA(0.0);
            WarningSet w = new WarningSet();
            AerodynamicForces f = calc.getAerodynamicForces(cfgC6, fcnd, w);
            double nosePress = 0;
            Map<RocketComponent, AerodynamicForces> fa = calc.getForceAnalysis(cfgC6, fcnd, w);
            for (Map.Entry<RocketComponent, AerodynamicForces> e : fa.entrySet())
                if (e.getKey() instanceof NoseCone) nosePress = e.getValue().getPressureCD();
            FlightConditions low = new FlightConditions(cfgC6); low.setMach(0.1); low.setAOA(0.0);
            double cp = calc.getCP(cfgC6, low, new WarningSet()).x;
            row.append(String.format(Locale.ROOT, ",%.4f,%.4f,%.4f,%.4f,%.5f,%.1f",
                f.getCD(), f.getFrictionCD(), f.getPressureCD(), f.getBaseCD(), nosePress, cp * 1000));

            double[] c6 = run(doc, rocket, cfgs.get("C6"), calc);
            double[] b4 = run(doc, rocket, cfgs.get("B4"), calc);
            row.append(String.format(Locale.ROOT, ",%.1f,%.2f,%.1f,%.1f,%.3f,%.1f,%.2f,%.1f",
                c6[0] * 1000, c6[1], c6[2], c6[3], c6[4], b4[2], b4[1], c6[5]));
            System.out.println(row);
        }
    }

    /** returns {CG_x, margin_cal, apogee, vmax, machmax} */
    static double[] run(OpenRocketDocument doc, Rocket rocket, FlightConfigurationId id, BarrowmanCalculator calc) throws Exception {
        FlightConfiguration fc = rocket.getFlightConfiguration(id);
        double cg = MassCalculator.calculateLaunch(fc).getCM().x;
        if (System.getenv("NS_DEBUG") != null) System.out.println("DBG launchmass=" + MassCalculator.calculateLaunch(fc).getMass() + " struct=" + MassCalculator.calculateStructure(fc).getMass());
        FlightConditions low = new FlightConditions(fc); low.setMach(0.1); low.setAOA(0.0);
        double cp = calc.getCP(fc, low, new WarningSet()).x;
        double margin = (cp - cg) / (2 * R);
        Simulation sim = new Simulation(doc, rocket);
        sim.setFlightConfigurationId(id);
        SimulationOptions o = sim.getOptions();
        o.setWindSpeedAverage(0.0); o.setWindSpeedDeviation(0.0); o.setWindTurbulenceIntensity(0.0);
        o.setLaunchRodLength(1.0); o.setTimeStep(0.01);
        sim.simulate();
        FlightData d = sim.getSimulatedData();
        if (System.getenv("NS_DEBUG") != null) { for (info.openrocket.core.simulation.FlightEvent e : d.getBranch(0).getEvents()) System.out.println("DBG ev " + e); System.out.println("DBG warn " + sim.getSimulatedWarnings()); System.exit(0);}
        return new double[]{cg, margin, d.getMaxAltitude(), d.getMaxVelocity(), d.getMaxMachNumber(), d.getLaunchRodVelocity()};
    }
}
