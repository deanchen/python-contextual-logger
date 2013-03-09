CREATE DATABASE logs;

CREATE TABLE "logs" (
	"_ip" text NOT NULL,
	"_priority" int2 NOT NULL,
	"_timestamp" int8 NOT NULL,
	"_event" text NOT NULL DEFAULT '',

	"_function" text NOT NULL DEFAULT '',
	"_file" text NOT NULL DEFAULT '',

	"_data" text NOT NULL DEFAULT ''

-- 	"index1" int4 NOT NULL DEFAULT 0,
-- 	"index2" int4 NOT NULL DEFAULT 0
);

CREATE INDEX logs__ip_index ON logs (_ip);
CREATE INDEX logs__priority_index ON logs (_priority);
CREATE INDEX logs__timestamp_index ON logs (_timestamp);
CREATE INDEX logs__event_index ON logs (_event);
CREATE INDEX logs__function_index ON logs (_function);
CREATE INDEX logs__file_index ON logs (_file);

-- CREATE INDEX logs_index1_index ON logs (index1);
-- CREATE INDEX logs_index2_index ON logs (index2);
