# Activity uploads

## Purpose

PerformanceLab accepts activity files to create factual workout
records for the authenticated athlete.

Supported inputs:

- FIT;
- FIT.GZ;
- GPX;
- Strava `activities.csv`, used only as metadata for activity
  titles and explicitly recorded running disciplines.

## Private alpha limits

One upload selection may contain no more than 20 files.

Each original file may contain no more than 20 MiB.

A compressed FIT.GZ file may expand to no more than 100 MiB.

Files that exceed these limits, are empty, truncated, use a false
extension or do not match a supported structure are rejected.

## Processing and retention

Original activity files are processed in memory.

PerformanceLab does not write the original FIT, FIT.GZ, GPX or CSV
file to its application storage. The in-memory stream is closed
after processing, whether the import succeeds or fails.

After processing, the Streamlit uploader is reset so that the
application releases its reference to the selected upload.

PerformanceLab retains only the data extracted into its athlete and
workout models. Depending on the source file, this may include:

- activity date and time;
- sport and title;
- duration, distance and elevation;
- route coordinates;
- heart rate, power and cadence samples;
- calories and other factual sensor data supported by the importer.

The original uploaded file cannot be downloaded again from
PerformanceLab because it is not retained.

Hosting and network infrastructure may hold request data transiently
while transmitting or processing an upload. That temporary
infrastructure handling is separate from PerformanceLab application
storage and must be covered by the hosting provider's privacy terms.

## Running discipline provenance

PerformanceLab stores the main sport and running discipline as
separate factual fields.

For example:

- `sport` may contain `Running`;
- `sub_sport` may contain `trail`;
- `terrain` describes the available environmental or surface
  information and is not a running discipline.

The running discipline may come from:

- the standard FIT `sub_sport` field, when present;
- an explicit `Trail Run` activity type in the associated Strava
  `activities.csv`;
- a manual correction made by the athlete in the activity editor.

PerformanceLab does not classify an activity as trail or road from
its title, distance, elevation gain, route or terrain.

A generic Strava `Run` value remains `Running`. It is not
automatically classified as road running.

When the FIT file does not contain `sub_sport`, the athlete can use
the activity editor to select the factual running discipline.

## Import results

Every selected file receives one result:

- imported;
- updated;
- duplicate;
- ignored;
- invalid.

Operational logs contain only aggregate result counts. They do not
contain file paths, original content, workout identifiers or
physiological data.

## Failure behaviour

A failure does not cause the original file to be retained.

Temporary in-memory streams are closed after success or failure.
The athlete is only persisted after the application rules complete
successfully.