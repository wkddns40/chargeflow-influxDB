import { describe, expect, it } from "vitest";

import { INITIAL_VIEW_STATE, REFERENCE_VIEWPORT_SIZE } from "../constants/viewport";
import type { Station } from "../types";
import { getBboxFitViewState, getStationFocusViewState, getStationScreenPosition, getStationsBbox, getValidData } from "./geo";

function station(overrides: Partial<Station> = {}): Station {
  return {
    station_id: "ST-0001",
    name: "Station 0001",
    address: "Seoul test address",
    region: "Seoul",
    operator: "ChargeFlow",
    lat: 37.5,
    lng: 127.0,
    connector_count: 6,
    max_kw: 100,
    ...overrides
  };
}

describe("geo helpers", () => {
  it("keeps all valid Seoul/Gyeonggi station points for deck.gl layers", () => {
    const stations = Array.from({ length: 700 }, (_, index) =>
      station({
        station_id: `ST-${String(index + 1).padStart(4, "0")}`,
        lat: 37.1 + index * 0.0001,
        lng: 126.8 + index * 0.0001
      })
    );

    expect(getValidData(stations)).toHaveLength(700);
  });

  it("builds a fit view and a focus view from Station coordinates", () => {
    const stations = [station({ lat: 37.2, lng: 126.7 }), station({ station_id: "ST-0002", lat: 37.8, lng: 127.4 })];
    const bounds = getStationsBbox(stations);

    expect(bounds).toEqual({ west: 126.7, south: 37.2, east: 127.4, north: 37.8 });
    expect(getBboxFitViewState(bounds!, REFERENCE_VIEWPORT_SIZE, INITIAL_VIEW_STATE).zoom).toBeGreaterThan(9);
    expect(
      getBboxFitViewState(bounds!, REFERENCE_VIEWPORT_SIZE, INITIAL_VIEW_STATE, {
        top: 120,
        right: 430,
        bottom: 180,
        left: 420
      }).zoom
    ).toBeGreaterThan(9);

    const focused = getStationFocusViewState(stations[0], INITIAL_VIEW_STATE);
    expect(focused.longitude).toBe(126.7);
    expect(focused.latitude).toBe(37.2);
    expect(focused.zoom).toBeGreaterThan(INITIAL_VIEW_STATE.zoom);
    expect(getStationScreenPosition(stations[0], focused, REFERENCE_VIEWPORT_SIZE)).not.toBeNull();
  });
});
