import { describe, expect, it } from "vitest";

import type { Station } from "../../types";
import { getStationMarkerColor, getStationMarkerSize } from "./MapShell";

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

describe("MapShell helpers", () => {
  it("matches chargeflow-kr marker radius rules", () => {
    const slow = station({ max_kw: 50 });
    const fast = station({ station_id: "ST-0002", max_kw: 350 });

    expect(getStationMarkerSize(slow, null, 10)).toBe(5);
    expect(getStationMarkerSize(fast, null, 10)).toBe(13);
    expect(getStationMarkerSize(slow, null, 10, true)).toBe(13);
    expect(getStationMarkerSize(fast, null, 10, true)).toBe(13);
    expect(getStationMarkerSize(slow, "ST-0001", 14)).toBe(28);
    expect(getStationMarkerSize(slow, "ST-0001", 14, true)).toBe(26);
    expect(getStationMarkerSize(slow, "ST-0001", 14, true)).toBeGreaterThan(
      getStationMarkerSize(fast, null, 10, true)
    );
    expect(getStationMarkerSize({ ...slow, max_kw: undefined }, null, 10)).toBe(5);
  });

  it("assigns the requested map marker color mix", () => {
    const red = getStationMarkerColor(station({ station_id: "ST-0001" }), null);
    const orange = getStationMarkerColor(station({ station_id: "ST-0002" }), null);
    const gray = getStationMarkerColor(station({ station_id: "ST-0003" }), null);
    const green = getStationMarkerColor(station({ station_id: "ST-0004" }), null);

    expect(new Set([red.join(","), orange.join(","), gray.join(","), green.join(",")]).size).toBe(4);
    expect(getStationMarkerColor(station({ station_id: "ST-0001" }), "ST-0001")).toEqual(red);
  });
});
