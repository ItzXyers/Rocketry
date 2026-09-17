// No build step, no frameworks -- a couple of polling fetch() loops.

const POLL_MS = 1500;

let srbToken = null;
let srbExpiresAt = null; // ms, Date.now()-based

function setPill(id, ok, textOk, textBad, textUnknown) {
  const el = document.getElementById(id);
  if (ok === null || ok === undefined) {
    el.textContent = textUnknown;
    el.className = "pill pill-unknown";
  } else if (ok) {
    el.textContent = textOk;
    el.className = "pill pill-ok";
  } else {
    el.textContent = textBad;
    el.className = "pill pill-bad";
  }
}

async function pollFc() {
  try {
    const res = await fetch("/api/fc/status");
    const s = await res.json();
    setPill("fc-reachable", s.reachable, "ONLINE", "OFFLINE", "--");
    const d = s.data || {};
    document.getElementById("fc-state").textContent = d.flight_state ?? "--";
    document.getElementById("fc-armed").textContent =
      d.wireless_armed === undefined ? "--" : (d.wireless_armed ? "yes" : "no");
    document.getElementById("fc-deployed").textContent =
      d.deploy_has_fired === undefined ? "--" : (d.deploy_has_fired ? "YES" : "no");
    document.getElementById("fc-sample-age").textContent =
      d.sample_age_ms === undefined ? "--" : `${d.sample_age_ms} ms`;
  } catch (e) {
    setPill("fc-reachable", false, "ONLINE", "OFFLINE", "--");
  }
}

async function armFc() {
  const btn = document.getElementById("fc-arm-btn");
  const msg = document.getElementById("fc-arm-msg");
  btn.disabled = true;
  msg.textContent = "Arming -- this blocks a few seconds on the flight computer...";
  try {
    const res = await fetch("/api/fc/arm", { method: "POST" });
    const body = await res.json();
    if (body.ok) {
      msg.textContent = "Armed. Flight computer radio will drop shortly (expected).";
    } else if (body.ambiguous) {
      msg.textContent = "Connection dropped -- likely armed and radio went down as designed. Check status.";
    } else {
      msg.textContent = `Arm failed: ${body.reason}`;
    }
  } catch (e) {
    msg.textContent = "Arm request failed to send.";
  } finally {
    btn.disabled = false;
  }
}

async function pollSrb() {
  try {
    const res = await fetch("/api/ignition/status");
    const s = await res.json();
    setPill("srb-continuity", s.continuity_ok, "OK", "OPEN", "--");
    setPill("srb-arm-sense", s.arm_sense_closed, "CLOSED", "OPEN", "--");
    setPill("srb-fired", !s.fired, "READY", "FIRED", "--");

    const fireBtn = document.getElementById("srb-fire-btn");
    const haveToken = srbToken !== null && srbExpiresAt !== null && Date.now() < srbExpiresAt;
    fireBtn.disabled = !(haveToken && s.continuity_ok && s.arm_sense_closed && !s.fired);

    const windowMsg = document.getElementById("srb-window-msg");
    if (haveToken) {
      const remaining = Math.max(0, Math.round((srbExpiresAt - Date.now()) / 1000));
      windowMsg.textContent = `Armed -- fire window closes in ${remaining}s`;
    } else {
      srbToken = null;
      srbExpiresAt = null;
      windowMsg.textContent = "";
    }

    document.getElementById("srb-arm-btn").disabled = s.fired || s.firing;
  } catch (e) {
    // leave last-known state visible; don't thrash pills on a transient error
  }
}

async function armSrb() {
  const msg = document.getElementById("srb-msg");
  try {
    const res = await fetch("/api/ignition/arm", { method: "POST" });
    const body = await res.json();
    if (body.ok) {
      srbToken = body.token;
      srbExpiresAt = Date.now() + body.expires_in_s * 1000;
      msg.textContent = "Armed.";
    } else {
      srbToken = null;
      srbExpiresAt = null;
      msg.textContent = `Arm failed: ${body.reason}`;
    }
  } catch (e) {
    msg.textContent = "Arm request failed to send.";
  }
}

async function fireSrb() {
  const msg = document.getElementById("srb-msg");
  if (!srbToken) return;
  if (!confirm("Fire the SRB igniter now?")) return;
  const tokenToSend = srbToken;
  srbToken = null;
  srbExpiresAt = null;
  try {
    const res = await fetch("/api/ignition/fire", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token: tokenToSend }),
    });
    const body = await res.json();
    msg.textContent = body.ok ? "FIRING." : `Fire failed: ${body.reason}`;
  } catch (e) {
    msg.textContent = "Fire request failed to send.";
  }
}

document.getElementById("fc-arm-btn").addEventListener("click", armFc);
document.getElementById("srb-arm-btn").addEventListener("click", armSrb);
document.getElementById("srb-fire-btn").addEventListener("click", fireSrb);

setInterval(pollFc, POLL_MS);
setInterval(pollSrb, POLL_MS);
pollFc();
pollSrb();
