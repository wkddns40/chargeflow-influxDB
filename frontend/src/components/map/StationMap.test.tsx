import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import type { Station } from "../../types";
import { markerPosition, SEOUL_GYEONGGI_MAP_BOUNDS, StationMap } from "./StationMap";

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
    ...overrides
  };
}

function percent(value: string): number {
  return Number(value.replace("%", ""));
}

describe("StationMap", () => {
  it("maps Seoul/Gyeonggi station coordinates to marker percentages", () => {
    const center = station({
      lat: (SEOUL_GYEONGGI_MAP_BOUNDS.minLat + SEOUL_GYEONGGI_MAP_BOUNDS.maxLat) / 2,
      lng: (SEOUL_GYEONGGI_MAP_BOUNDS.minLng + SEOUL_GYEONGGI_MAP_BOUNDS.maxLng) / 2
    });

    const position = markerPosition(center);

    expect(percent(position.left)).toBeCloseTo(50);
    expect(percent(position.top)).toBeCloseTo(50);
  });

  it("clamps marker positions at the map edge", () => {
    expect(
      markerPosition(
        station({
          lat: SEOUL_GYEONGGI_MAP_BOUNDS.maxLat + 1,
          lng: SEOUL_GYEONGGI_MAP_BOUNDS.minLng - 1
        })
      )
    ).toEqual({ left: "0%", top: "0%" });

    expect(
      markerPosition(
        station({
          lat: SEOUL_GYEONGGI_MAP_BOUNDS.minLat - 1,
          lng: SEOUL_GYEONGGI_MAP_BOUNDS.maxLng + 1
        })
      )
    ).toEqual({ left: "100%", top: "100%" });
  });

  it("renders 700 station markers by station_id", () => {
    const stations = Array.from({ length: 700 }, (_, index) =>
      station({
        station_id: `ST-${String(index + 1).padStart(4, "0")}`,
        name: `Station ${String(index + 1).padStart(4, "0")}`,
        lat: SEOUL_GYEONGGI_MAP_BOUNDS.minLat + (index / 699) * (SEOUL_GYEONGGI_MAP_BOUNDS.maxLat - SEOUL_GYEONGGI_MAP_BOUNDS.minLat),
        lng: SEOUL_GYEONGGI_MAP_BOUNDS.minLng + (index / 699) * (SEOUL_GYEONGGI_MAP_BOUNDS.maxLng - SEOUL_GYEONGGI_MAP_BOUNDS.minLng),
        connector_count: (index % 8) + 1
      })
    );

    const html = renderToStaticMarkup(
      <StationMap stations={stations} selectedStationId={null} loading={false} error={null} onSelect={() => undefined} />
    );

    expect(html.match(/class="station-marker"/g)?.length).toBe(700);
    expect(html).toContain('aria-label="Open Station 0001"');
    expect(html).toContain('title="Station 0700 (4)"');
  });
});
