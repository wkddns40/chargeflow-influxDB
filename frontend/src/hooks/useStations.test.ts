import { describe, expect, it } from "vitest";

import { DEFAULT_STATION_LIMIT, DEFAULT_STATION_PROFILE, stationListPath } from "./useStations";

describe("useStations helpers", () => {
  it("defaults to the Seoul/Gyeonggi 700 station contract", () => {
    expect(DEFAULT_STATION_PROFILE).toBe("seoul-gyeonggi");
    expect(DEFAULT_STATION_LIMIT).toBe(700);
    expect(stationListPath()).toBe("/api/stations?profile=seoul-gyeonggi&limit=700");
  });

  it("builds station list paths for explicit profiles", () => {
    expect(stationListPath("smoke", 300)).toBe("/api/stations?profile=smoke&limit=300");
  });
});
