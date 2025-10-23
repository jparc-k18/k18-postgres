CREATE TABLE magnet(
  timestamp	TIMESTAMP WITH TIME ZONE,
  magnet_data 	JSONB NOT NULL,
  PRIMARY KEY(timestamp)
);
