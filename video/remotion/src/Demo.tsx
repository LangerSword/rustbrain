import React, { useEffect, useMemo, useState } from "react";
import {
  AbsoluteFill, Audio, Freeze, Img, OffthreadVideo, Sequence, staticFile,
  continueRender, delayRender, interpolate, useCurrentFrame, useVideoConfig,
} from "remotion";
import captions from "./captions.json";
import { expoOut, expoIn, MOTION } from "./curves";

// ---------------------------------------------------------------------------
// Footage plan. Every segment is real footage, recorded from the live site,
// the real repo, the real run page and real terminal sessions. Spans are
// derived from the storyboard beats; playback rates are computed at render
// time from the measured clip durations in clips_meta.json. Still frames are
// real extracted frames used for slow holds, never re-drawn UI.
type Punch = { at: number; hold: number; scale: number; tx: number; ty: number };
type Seg = { clip: string; span: number; still?: string; from?: number; punch?: Punch };

const BEAT_SEGS: Record<number, Seg[]> = {
  1: [{ clip: "naive", span: 12, from: 1.5,
        punch: { at: 1.2, hold: 7, scale: 1.15, tx: 160, ty: 70 } }],
  2: [{ clip: "site_uhd_xvfb_hero", span: 18, from: 3.2,
        punch: { at: 2, hold: 12, scale: 1.5, tx: 0, ty: 110 } }],
  3: [
    { clip: "site_uhd_xvfb_successor_edge", span: 15, from: 2.2,
      punch: { at: 2.5, hold: 8, scale: 1.6, tx: -600, ty: 350 } },
    { clip: "site_fhd_xvfb_tabs", span: 20, from: 2.2,
      punch: { at: 2, hold: 14, scale: 1.22, tx: -240, ty: -160 } },
  ],
  4: [
    { clip: "site_uhd_xvfb_readme", span: 15, from: 4.0,
      punch: { at: 2, hold: 10, scale: 1.3, tx: 0, ty: -310 } },
    { clip: "query", span: 21, from: 1.0,
      punch: { at: 5, hold: 12, scale: 1.5, tx: 270, ty: 40 } },
    { clip: "site_uhd_xvfb_readme", span: 9, still: "readme_hold.png",
      punch: { at: 0.5, hold: 7, scale: 1.3, tx: 0, ty: -310 } },
  ],
  5: [
    { clip: "site_uhd_xvfb_gaps", span: 14, from: 2.5,
      punch: { at: 2, hold: 10, scale: 1.45, tx: 0, ty: -20 } },
    { clip: "site_uhd_xvfb_gaps", span: 11, still: "gaps_hold.png",
      punch: { at: 0.5, hold: 9, scale: 1.45, tx: 0, ty: -20 } },
  ],
  6: [
    { clip: "refresh", span: 13,
      punch: { at: 3, hold: 8, scale: 1.3, tx: 160, ty: 70 } },
    { clip: "site_fhd_xvfb_actions", span: 5, from: 2.0,
      punch: { at: 0.5, hold: 4, scale: 1.15, tx: 0, ty: 110 } },
    { clip: "assertions", span: 7, punch: { at: 1, hold: 5, scale: 1.35, tx: 200, ty: -180 } },
  ],
  7: [
    { clip: "site_uhd_xvfb_bugs", span: 10, from: 3.0, punch: { at: 2, hold: 6, scale: 1.35, tx: 0, ty: -80 } },
  ],
};

const ENDCARD = { start: 170, end: 180 };

function useClipMeta() {
  const [meta, setMeta] = useState<Record<string, number> | null>(null);
  const [handle] = useState(() => delayRender("clip meta"));
  useEffect(() => {
    fetch(staticFile("clips_meta.json"))
      .then((r) => r.json())
      .then((m) => { setMeta(m); continueRender(handle); })
      .catch(() => { setMeta({}); continueRender(handle); });
  }, [handle]);
  return meta;
}

function useFonts() {
  const [handle] = useState(() => delayRender("fonts"));
  useEffect(() => {
    const faces = [
      new FontFace("Newsreader", `url(${staticFile("fonts/newsreader-400-normal.woff2")})`, { weight: "400" }),
      new FontFace("Inter", `url(${staticFile("fonts/inter-100-900-normal.woff2")})`, { weight: "100 900" }),
    ];
    Promise.all(faces.map((f) => f.load().then((l) => { document.fonts.add(l); return l; })))
      .then(() => continueRender(handle))
      .catch(() => continueRender(handle));
  }, [handle]);
}

const cameraFor = (seg: Seg, frameInSeg: number, segFrames: number) => {
  const p = seg.punch;
  if (!p) return "scale(1) translate(0px, 0px)";
  const enter = p.at * 60;
  const leave = Math.min(segFrames - 12, (p.at + p.hold) * 60);
  const s = interpolate(frameInSeg, [enter, enter + MOTION.punchIn, leave, leave + MOTION.punchOut],
    [1, p.scale, p.scale, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: expoOut });
  // tx, ty are the full-strength translation that brings the chosen point to
  // the frame center; k ramps it in with the scale so the move is one motion.
  const k = p.scale === 1 ? 0 : (s - 1) / (p.scale - 1);
  return `scale(${s}) translate(${p.tx * k}px, ${p.ty * k}px)`;
};

const SegmentView: React.FC<{ seg: Seg; meta: Record<string, number>; beatFrames: number }> = ({ seg, meta, beatFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const dur = Math.max(0.5, (meta[seg.clip] || 10) - (seg.from || 0));
  const spanFrames = Math.round(seg.span * fps);
  const rate = Math.max(0.55, Math.min(1, dur / seg.span));
  const videoFrames = Math.round((dur / rate) * fps);
  const showVideo = frame < videoFrames;
  const stillScale = 1 + 0.05 * (frame / Math.max(1, spanFrames));
  const startFrom = Math.round((seg.from || 0) * fps);
  return (
    <AbsoluteFill style={{ transform: cameraFor(seg, frame, spanFrames), transformOrigin: "center" }}>
      {showVideo ? (
        <OffthreadVideo
          src={staticFile("clips/" + seg.clip + ".mp4")}
          startFrom={startFrom}
          playbackRate={rate}
          muted
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
      ) : seg.still ? (
        <Img src={staticFile("stills/" + seg.still)} style={{ width: "100%", height: "100%", objectFit: "cover", transform: `scale(${stillScale})` }} />
      ) : (
        // fallback hold: freeze near the end of the clip instead of seeking
        // past it (the clamp at rate 0.55 can leave frames beyond the source)
        <Freeze frame={0}>
          <OffthreadVideo
            src={staticFile("clips/" + seg.clip + ".mp4")}
            startFrom={Math.max(0, Math.round((Math.max(0.5, (meta[seg.clip] || 10)) - 1.2) * fps))}
            playbackRate={1}
            muted
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
          />
        </Freeze>
      )}
    </AbsoluteFill>
  );
};

const Beat: React.FC<{ beat: any; meta: Record<string, number> }> = ({ beat, meta }) => {
  const { fps } = useVideoConfig();
  const segs = BEAT_SEGS[beat.beat] || [];
  let acc = 0;
  const views = segs.map((s, i) => {
    const from = acc;
    const span = Math.round(s.span * fps);
    acc += span;
    return (
      <Sequence key={i} from={from} durationInFrames={span} layout="none">
        <SegmentView seg={s} meta={meta} beatFrames={span} />
      </Sequence>
    );
  });
  const caps: any[] = beat.captions || [{ t: beat.start, text: beat.caption }];
  const capEnds = caps.map((c: any, i: number) =>
    (((i + 1 < caps.length ? caps[i + 1].t : beat.end) - beat.start) * fps));
  return (
    <AbsoluteFill>
      {views}
      {caps.map((c: any, i: number) => (
        <Caption key={i} text={c.text} start={(c.t - beat.start) * fps} endLocal={capEnds[i]} vo={false} />
      ))}
    </AbsoluteFill>
  );
};

const Caption: React.FC<{ text: string; start: number; endLocal: number; vo: boolean }> = ({ text, start, endLocal, vo }) => {
  const frame = useCurrentFrame();
  const shown = vo ? text.split(" ").slice(0, 3).join(" ") : text;
  const words = shown.split(" ");
  const visible = frame >= start - 4;
  if (!visible) return null;
  const local = frame - start;
  const fadeOut = interpolate(local, [Math.max(0, endLocal - 46), Math.max(1, endLocal - 16)], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: expoIn });
  return (
    <div style={{
      position: "absolute", left: 120, right: 120, bottom: 84, display: "flex", justifyContent: "center",
      opacity: fadeOut,
    }}>
      <div style={{
        background: "rgba(20,17,14,0.80)", borderTop: "1px solid rgba(242,237,228,0.18)",
        padding: "26px 38px", maxWidth: 1500,
      }}>
        <div style={{ fontFamily: "Inter", fontWeight: 600, fontSize: 40, lineHeight: 1.22, color: "#f2ede4" }}>
          {words.map((w, i) => {
            const wStart = i * MOTION.captionStagger;
            const rise = interpolate(local - wStart, [0, MOTION.captionWord], [110, 0], {
              extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: expoOut,
            });
            const op = interpolate(local - wStart, [0, MOTION.captionWord], [0, 1], {
              extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: expoOut,
            });
            return (
              <span key={i} style={{ display: "inline-block", overflow: "hidden", verticalAlign: "bottom", marginRight: 14 }}>
                <span style={{ display: "inline-block", transform: `translateY(${rise}%)`, opacity: op }}>{w}</span>
              </span>
            );
          })}
        </div>
      </div>
    </div>
  );
};

const EndCard: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame; // local frames
  const draw = interpolate(t, [10, 70], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: expoOut });
  const up = (at: number) => interpolate(t, [at, at + 22], [40, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: expoOut });
  const op = (at: number) => interpolate(t, [at, at + 18], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: expoOut });
  const facts: any[] = (captions as any).facts;
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", background: "#14110e" }}>
      <svg width={260} height={110} viewBox="0 0 260 110" style={{ marginBottom: 28 }}>
        <path d="M22 78 L92 30 L162 78" fill="none" stroke="#ff6a3d" strokeWidth={5}
              strokeDasharray={240} strokeDashoffset={240 * draw} strokeLinejoin="round" strokeLinecap="round" />
        <circle cx={22} cy={78} r={7} fill="none" stroke="#f2ede4" strokeWidth={3} strokeDasharray={44} strokeDashoffset={44 * draw} />
        <circle cx={92} cy={30} r={7} fill="none" stroke="#f2ede4" strokeWidth={3} strokeDasharray={44} strokeDashoffset={44 * draw} />
        <rect x={196} y={34} width={22} height={22} fill="none" stroke="#f2705e" strokeWidth={3}
              strokeDasharray={88} strokeDashoffset={88 * draw} />
      </svg>
      <div style={{ fontFamily: "Newsreader", fontSize: 92, color: "#f2ede4", opacity: op(30), transform: `translateY(${up(30)}px)` }}>
        rustbrain
      </div>
      <div style={{ fontFamily: "Inter", fontSize: 30, color: "#c9c0b2", marginTop: 14, opacity: op(50), transform: `translateY(${up(50)}px)` }}>
        {(captions as any).endcard.domain}
      </div>
      <div style={{ fontFamily: "Inter", fontSize: 26, color: "#918877", marginTop: 6, opacity: op(60), transform: `translateY(${up(60)}px)` }}>
        {(captions as any).endcard.track}
      </div>
      <div style={{ display: "flex", gap: 64, marginTop: 52, opacity: op(90) }}>
        {facts.map((f, i) => (
          <div key={i} style={{ textAlign: "center", transform: `translateY(${up(90 + i * 8)}px)` }}>
            <div style={{ fontFamily: "Newsreader", fontSize: 58, color: "#ff6a3d" }}>{String(f.value)}</div>
            <div style={{ fontFamily: "Inter", fontSize: 22, color: "#c9c0b2", marginTop: 6, maxWidth: 320 }}>{f.label}</div>
          </div>
        ))}
      </div>
      {fps ? null : null}
    </AbsoluteFill>
  );
};

export const Demo: React.FC<{ vo?: boolean; skipAudio?: boolean }> = ({ vo = false, skipAudio = false }) => {
  const meta = useClipMeta();
  useFonts();
  const { fps } = useVideoConfig();
  const beats = (captions as any).beats;
  if (!meta) return <AbsoluteFill style={{ background: "#14110e" }} />;
  return (
    <AbsoluteFill style={{ background: "#14110e" }}>
      {!skipAudio ? <Audio src={staticFile(vo ? "audio/cut_b.wav" : "audio/premix.wav")} /> : null}
      {beats.map((b: any) => (
        <Sequence key={b.beat} from={b.start * fps} durationInFrames={(b.end - b.start) * fps}>
          {b.beat === 7 ? (
            <>
              {(BEAT_SEGS[7] || []).map((s, i) => {
                const span = Math.round(s.span * fps);
                return (
                  <Sequence key={i} from={0} durationInFrames={span} layout="none">
                    <SegmentView seg={s} meta={meta} beatFrames={span} />
                  </Sequence>
                );
              })}
              <Sequence from={(ENDCARD.start - b.start) * fps} durationInFrames={(ENDCARD.end - ENDCARD.start) * fps} layout="none">
                <EndCard />
              </Sequence>
              {(b.captions || []).map((c: any, i: number, arr: any[]) => (
                <Caption key={"c" + i} text={c.text} start={(c.t - b.start) * fps}
                  endLocal={((i + 1 < arr.length ? arr[i + 1].t : Math.min(b.end, ENDCARD.start)) - b.start) * fps} vo={vo} />
              ))}
            </>
          ) : (
            <Beat beat={b} meta={meta} />
          )}
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
