// Motion tokens, defined once. Starting values come from the measured
// references recorded in out/revamp/10_picks.md; the values the built site
// actually ships are measured again in stage 6 and recorded there.
export const E = {
  arrive: "expo.out", // things arriving
  leave: "expo.in", // things leaving
  ui: "power2.out", // small state changes
};

export const D = {
  reveal: 1.05, // masked line reveal, seconds
  quote: 0.6, // the recorded quote rising into view
  ui: 0.18, // small UI state changes
  count: 1.2, // a counter running to its final value
  rowOut: 0.5,
  rowIn: 0.55,
  fade: 0.2,
  draw: 1.2, // the hop edge drawing itself
  stub: 0.9, // the gap stub drawing to its stop
  flip: 0.5, // result panel re-grouping
  curtain: 0.62, // the veil lifting off a scene
  camera: 1.4, // the graph push during the hop
};

export const ST = {
  line: 0.07,
  char: 0.0175,
  row: 0.06,
  fan: 0.05,
  tier: 0.12,
};

export const SCRUB = {
  hop: 0.3,
};
