export const STATION_PROFILE_VALUES = ["smoke", "seoul-gyeonggi", "dev", "perf"] as const;

export type StationProfile = (typeof STATION_PROFILE_VALUES)[number];

export type Station = {
  station_id: string;
  name: string;
  address: string;
  region: string;
  operator: string;
  lat: number;
  lng: number;
  connector_count: number;
};

export type StationsResponse = {
  profile: StationProfile;
  count: number;
  stations: Station[];
};

export type GrafanaUrlResponse = {
  station_id: string;
  url: string;
};
