const formatBytes = (bytes, decimals = 2) => {
  /* Format storage size in bytes to be human friendly */
  if (bytes === 0) return "0";

  const k = 1000;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"];

  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + " " + sizes[i];
};

const minutesSince = (datetime) => {
  /* Time in minutes since a given time (or time string) */
  const testTime = typeof datetime == "string" ? new Date(datetime) : datetime;
  return Math.round((new Date() - testTime) / 1000 / 60);
};

export { formatBytes, minutesSince };
