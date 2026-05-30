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
  profile: string;
  count: number;
  stations: Station[];
};

export type GrafanaUrlResponse = {
  station_id: string;
  url: string;
};
