import { describe, expect, it } from "vitest";

import { hasStationVariable, stationTimelinePath } from "./grafana";

describe("grafana helpers", () => {
  it("builds station timeline API path", () => {
    expect(stationTimelinePath("ST-0001")).toBe("/api/grafana/station-timeline-url?station_id=ST-0001");
  });

  it("detects selected station variable", () => {
    expect(hasStationVariable("http://localhost:3001/d/x?var-station_id=ST-0001", "ST-0001")).toBe(true);
  });
});
