import React, { useEffect, useMemo, useState } from "react";
import {
  AbsoluteFill, Audio, Img, OffthreadVideo, Sequence, staticFile,
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
type Punch = { at: number; hold: number; scale: number; x: number; y: number };
type Seg = { clip: string; span: number; still?: string; punch?: Punch };

const BEAT_SEGS: Record<number, Seg[]> = {
  1: [{ clip: "naive", span: 12 }],
  2: [{ clip: "site_fhd_xvfb_hero", span: 18,
        punch: { at: 2, hold: 12, scale: 1.45, x: -430, y: 100 } }],
  3: [
    { clip: "site_fhd_xvfb_successor_edge", span: 15,
      punch: { at: 2.5, hold: 8, scale: 1.7, x: 470, y: -235 } },
    { clip: "site_fhd_xvfb_tabs", span: 20,
      punch: { at: 2, hold: 16, scale: 1.18, x: -60, y: 120 } },
  ],
  4: [
    { clip: "site_fhd_xvfb_readme", span: 15,
      punch: { at: 2, hold: 11, scale: 1.35, x: -40, y: 40 } },
    { clip: "query", span: 21,
      punch: { at: 6, hold: 12, scale: 1.6, x: 250, y: 130 } },
    { clip: "site_fhd_xvfb_readme", span: 9, still: "readme_hold.png" },
  ],
  5: [
    { clip: "site_fhd_xvfb_gaps", span: 14,
      punch: { at: 2, hold: 10, scale: 1.4, x: -30, y: -60 } },
    { clip: "site_fhd_xvfb_gaps", span: 11, still: "gaps_hold.png",
      punch: { at: 0.5, hold: 9, scale: 1.3, x: -20, y: -80 } },
  ],
  6: [
    { clip: "refresh", span: 13,
      punch: { at: 3, hold: 8, scale: 1.5, x: 60, y: 20 } },
    { clip: "site_fhd_xvfb_actions", span: 5, punch: { at: 0.5, hold: 4, scale: 1.15, x: 0, y: 30 } },
    { clip: "assertions", span: 7, punch: { at: 1, hold: 5, scale: 1.5, x: 150, y: -40 } },
  ],
  7: [
    { clip: "site_fhd_xvfb_bugs", span: 10, punch: { at: 2, hold: 6, scale: 1.3, x: -20, y: 30 } },
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
    Promise.all([
      (document as any).fonts.load("400 64px Newsreader"),
      (document as any).fonts.load("600 40px Inter"),
      (document as any).fonts.load("400 32px Inter"),
    ]).then(() => (document as any).fonts.ready).then(() => continueRender(handle));
  }, [handle]);
}

const cameraFor = (seg: Seg, frameInSeg: number, segFrames: number) => {
  const p = seg.punch;
  if (!p) return "scale(1) translate(0px, 0px)";
  const enter = p.at * 60;
  const leave = Math.min(segFrames - 12, (p.at + p.hold) * 60);
  const s = interpolate(frameInSeg, [enter, enter + MOTION.punchIn, leave, leave + MOTION.punchOut],
    [1, p.scale, p.scale, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: expoOut });
  const settle = 1 - s;
  const x = p.x * (s - 1) / (p.scale - 1 || 1);
  const y = p.y * (s - 1) / (p.scale - 1 || 1);
  void settle;
  return `scale(${s}) translate(${x}px, ${y}px)`;
};

const SegmentView: React.FC<{ seg: Seg; meta: Record<string, number>; beatFrames: number }> = ({ seg, meta, beatFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const dur = meta[seg.clip] || 10;
  const spanFrames = Math.round(seg.span * fps);
  const rate = Math.max(0.55, Math.min(1, dur / seg.span));
  const videoFrames = Math.round((dur / rate) * fps);
  const showVideo = frame < videoFrames;
  const stillScale = 1 + 0.05 * (frame / Math.max(1, spanFrames));
  return (
    <AbsoluteFill style={{ transform: cameraFor(seg, frame, spanFrames), transformOrigin: "center" }}>
      {showVideo ? (
        <OffthreadVideo
          src={staticFile("clips/" + seg.clip + ".mp4")}
          playbackRate={rate}
          muted
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
      ) : seg.still ? (
        <Img src={staticFile("stills/" + seg.still)} style={{ width: "100%", height: "100%", objectFit: "cover", transform: `scale(${stillScale})` }} />
      ) : (
        <OffthreadVideo
          src={staticFile("clips/" + seg.clip + ".mp4")}
          playbackRate={rate}
          muted
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
      )}
    </AbsoluteFill>
  );
};

const Beat: React.FC<{ beat: any; meta: Record<string, number> }> = ({ beat, meta }) => {
  const { fps } = useVideoConfig();
  const segs = BEAT_SEGS[beat.beat] || [];
  const beatFrames = (beat.end - beat.start) * fps;
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
  return (
    <AbsoluteFill>
      {views}
      {caps.map((c, i) => (
        <Caption key={i} text={c.text} start={(c.t - beat.start) * fps} vo={false} />
      ))}
      {beatFrames > 0 ? null : null}
    </AbsoluteFill>
  );
};

const Caption: React.FC<{ text: string; start: number; vo: boolean }> = ({ text, start, vo }) => {
  const frame = useCurrentFrame();
  const shown = vo ? text.split(" ").slice(0, 3).join(" ") : text;
  const words = shown.split(" ");
  const visible = frame >= start - 4;
  if (!visible) return null;
  const local = frame - start;
  const fadeOut = interpolate(local, [320, 360], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: expoIn });
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
              {(b.captions || []).map((c: any, i: number) => (
                <Caption key={"c" + i} text={c.text} start={(c.t - b.start) * fps} vo={vo} />
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
