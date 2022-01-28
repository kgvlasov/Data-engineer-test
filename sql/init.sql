CREATE SCHEMA test_task_kgvlasov;

CREATE TABLE test_task_kgvlasov.weather_raw_data (
  id SERIAL PRIMARY KEY,
  date timestamp NOT NULL,
  last_updated timestamp NOT NULL, 
  temp_c float4,
  feelslike_c float4
);

CREATE TABLE test_task_kgvlasov.data_mart (
  date timestamp NOT NULL, 
  state varchar(15) NOT NULL,
  value float4
);
