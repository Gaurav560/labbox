# Dabba Express: on-call

- `access.log`: today's requests, one per line:
  `time ip method path status duration`, for example
  `2026-11-19T12:00:09 10.0.0.12 GET /menu 200 35ms`
- `count_5xx.sh`, `top_ips.sh`, `slowest.sh`: small tools for the next incident. Each takes the log
  file as its first argument: `bash count_5xx.sh access.log`.
- `server/`: a copy of the tiffin server's files (logs, scripts, config).
- `fix_perms.sh`: fixes the permissions of a server folder: `bash fix_perms.sh server`.
