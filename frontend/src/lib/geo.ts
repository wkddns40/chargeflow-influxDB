import type { Station, ViewState } from "../types";

const WEB_MERCATOR_TILE_SIZE = 512;
const WEB_MERCATOR_LAT_LIMIT = 85.051129;
const BBOX_FIT_PADDING_PX = 160;
const BBOX_FIT_MIN_ZOOM = 5;
const BBOX_FIT_MAX_ZOOM = 15.5;
const STATION_FOCUS_ZOOM = 14.5;

export type BboxBounds = {
  west: number;
  south: number;
  east: number;
  north: number;
};

export type ViewportSize = {
  width: number;
  height: number;
};

export type ScreenPosition = {
  x: number;
  y: number;
};

export type ViewportPadding =
  | number
  | {
      top?: number;
      right?: number;
      bottom?: number;
      left?: number;
    };

export function getValidData(stations: Station[]): Station[] {
  return stations.filter(
    (station) => Number.isFinite(station.lng) && Number.isFinite(station.lat) && station.lng !== 0 && station.lat !== 0
  );
}

export function getStationFocusViewState(station: Station, currentViewState: ViewState): ViewState {
  if (!Number.isFinite(station.lng) || !Number.isFinite(station.lat)) {
    return currentViewState;
  }

  return {
    ...currentViewState,
    longitude: station.lng,
    latitude: station.lat,
    zoom: Math.max(currentViewState.zoom, STATION_FOCUS_ZOOM),
    pitch: 0,
    bearing: 0
  };
}

export function getStationScreenPosition(
  station: Station,
  viewState: ViewState,
  viewport: ViewportSize
): ScreenPosition | null {
  if (!Number.isFinite(station.lng) || !Number.isFinite(station.lat)) {
    return null;
  }

  const zoom = clamp(viewState.zoom, 0, 24);
  const [centerX, centerY] = lngLatToWorld(viewState.longitude, viewState.latitude, zoom);
  const [pointX, pointY] = lngLatToWorld(station.lng, station.lat, zoom);

  return {
    x: viewport.width / 2 + pointX - centerX,
    y: viewport.height / 2 + pointY - centerY
  };
}

export function getStationsBbox(stations: Station[]): BboxBounds | null {
  const validStations = getValidData(stations);
  if (validStations.length === 0) {
    return null;
  }

  return validStations.reduce<BboxBounds>(
    (bounds, station) => ({
      west: Math.min(bounds.west, station.lng),
      south: Math.min(bounds.south, station.lat),
      east: Math.max(bounds.east, station.lng),
      north: Math.max(bounds.north, station.lat)
    }),
    {
      west: validStations[0].lng,
      south: validStations[0].lat,
      east: validStations[0].lng,
      north: validStations[0].lat
    }
  );
}

export function getBboxFitViewState(
  bounds: BboxBounds,
  viewport: ViewportSize,
  fallback: ViewState,
  padding: ViewportPadding = BBOX_FIT_PADDING_PX
): ViewState {
  if (viewport.width <= 0 || viewport.height <= 0 || !isValidBounds(bounds)) {
    return fallback;
  }

  const fitPadding = normalizeViewportPadding(padding);
  const centerLongitude = (bounds.west + bounds.east) / 2;
  const centerLatitude = (bounds.south + bounds.north) / 2;
  const westNorth = lngLatToNormalizedWorld(bounds.west, bounds.north);
  const eastSouth = lngLatToNormalizedWorld(bounds.east, bounds.south);
  const spanX = Math.max(Math.abs(eastSouth[0] - westNorth[0]), Number.EPSILON);
  const spanY = Math.max(Math.abs(eastSouth[1] - westNorth[1]), Number.EPSILON);
  const usableWidth = Math.max(1, viewport.width - fitPadding.left - fitPadding.right);
  const usableHeight = Math.max(1, viewport.height - fitPadding.top - fitPadding.bottom);
  const zoomX = Math.log2(usableWidth / (WEB_MERCATOR_TILE_SIZE * spanX));
  const zoomY = Math.log2(usableHeight / (WEB_MERCATOR_TILE_SIZE * spanY));
  const zoom = clamp(Math.min(zoomX, zoomY), BBOX_FIT_MIN_ZOOM, BBOX_FIT_MAX_ZOOM);
  const roundedZoom = Math.round(zoom * 100) / 100;
  const [centerX, centerY] = lngLatToWorld(centerLongitude, centerLatitude, roundedZoom);
  const offsetX = (fitPadding.left - fitPadding.right) / 2;
  const offsetY = (fitPadding.top - fitPadding.bottom) / 2;
  const [longitude, latitude] = worldToLngLat(centerX - offsetX, centerY - offsetY, roundedZoom);

  return {
    longitude,
    latitude,
    zoom: roundedZoom,
    pitch: fallback.pitch,
    bearing: fallback.bearing
  };
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

function worldSizeForZoom(zoom: number): number {
  return WEB_MERCATOR_TILE_SIZE * 2 ** zoom;
}

function lngLatToWorld(longitude: number, latitude: number, zoom: number): [number, number] {
  const worldSize = worldSizeForZoom(zoom);
  const clampedLat = clamp(latitude, -WEB_MERCATOR_LAT_LIMIT, WEB_MERCATOR_LAT_LIMIT);
  const sinLat = Math.sin((clampedLat * Math.PI) / 180);
  const x = ((longitude + 180) / 360) * worldSize;
  const y = (0.5 - Math.log((1 + sinLat) / (1 - sinLat)) / (4 * Math.PI)) * worldSize;
  return [x, y];
}

function worldToLngLat(x: number, y: number, zoom: number): [number, number] {
  const worldSize = worldSizeForZoom(zoom);
  const longitude = (clamp(x, 0, worldSize) / worldSize) * 360 - 180;
  const latitude =
    (Math.atan(Math.sinh(Math.PI * (1 - (2 * clamp(y, 0, worldSize)) / worldSize))) * 180) / Math.PI;
  return [longitude, latitude];
}

function lngLatToNormalizedWorld(longitude: number, latitude: number): [number, number] {
  const [x, y] = lngLatToWorld(longitude, latitude, 0);
  return [x / WEB_MERCATOR_TILE_SIZE, y / WEB_MERCATOR_TILE_SIZE];
}

function normalizeViewportPadding(padding: ViewportPadding): Required<Exclude<ViewportPadding, number>> {
  if (typeof padding === "number") {
    return {
      top: padding,
      right: padding,
      bottom: padding,
      left: padding
    };
  }

  return {
    top: padding.top ?? BBOX_FIT_PADDING_PX,
    right: padding.right ?? BBOX_FIT_PADDING_PX,
    bottom: padding.bottom ?? BBOX_FIT_PADDING_PX,
    left: padding.left ?? BBOX_FIT_PADDING_PX
  };
}

function isValidBounds(bounds: BboxBounds): boolean {
  return (
    Number.isFinite(bounds.west) &&
    Number.isFinite(bounds.south) &&
    Number.isFinite(bounds.east) &&
    Number.isFinite(bounds.north) &&
    bounds.west <= bounds.east &&
    bounds.south <= bounds.north
  );
}
