import React from "react";
import { Composition } from "remotion";
import { Demo } from "./Demo";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="Demo"
      component={Demo}
      durationInFrames={180 * 60}
      fps={60}
      width={1920}
      height={1080}
      defaultProps={{ vo: false }}
    />
  );
};
