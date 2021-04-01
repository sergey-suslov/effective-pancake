package utils

import "time"

func FormatTime(timestamp time.Time) string {
	return timestamp.Format(time.RFC3339)
}

func ParseTimestamp(timestamp int64) string {
	return time.Unix(timestamp, 0).Format(time.RFC3339)
}
