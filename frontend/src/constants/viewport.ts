import type { ViewState } from "../types";

export const MAP_STYLE_URL = "https://tiles.openfreemap.org/styles/liberty";
export const REFERENCE_VIEWPORT_SIZE = {
  width: 2048,
  height: 1024
} as const;
export const MAP_MAX_BOUNDS: [[number, number], [number, number]] = [
  [126.35, 36.82],
  [127.95, 37.92]
];

export const INITIAL_VIEW_STATE: ViewState = {
  longitude: 127.061,
  latitude: 37.523,
  zoom: 13.31,
  pitch: 0,
  bearing: 0
};
