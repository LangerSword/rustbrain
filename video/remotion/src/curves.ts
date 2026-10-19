import { Easing } from "remotion";

// One family of curves for the whole video: expo out for things arriving,
// expo in for things leaving. Defined once, used everywhere.
export const expoOut = Easing.out(Easing.exp);
export const expoIn = Easing.in(Easing.exp);

export const MOTION = {
  captionWord: 16, // frames per word rise
  captionStagger: 4, // frames between words
  punchIn: 26,
  hold: 40,
  punchOut: 22,
};
