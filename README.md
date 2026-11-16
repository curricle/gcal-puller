# GCal Puller

What it does:
- pulls events from your specified Google Calendar
- creates templated markdown files for tracking and organizing in Obsidian

How it works:
- Calls Google Calendar API and authenticates
- Searches for events in a specified calendar from a saved "last synced" timestamp
- Creates markdown files for each event using a template
- Saves the current timestamp to an external file for future reference when syncing

Special features:
- Parses event descriptions for certain keywords (in this case, USPS route name/number)
- Determines if certain routes have "green card time" (a simple boolean)
- Reads the time of the events to determine the duration of the event and converts it to a float for easier calculation