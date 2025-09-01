module.exports = {
  apps: [{
    name: 'weather-station',
    script: '/home/pi/apps/weather-station/env3_dht22_combined.py',
    interpreter: '/home/pi/apps/weather-station/venv/bin/python',
    cwd: '/home/pi/apps/weather-station',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production'
    },
    log_date_format: 'YYYY-MM-DD HH:mm:ss',
    error_file: './logs/weather-station-error.log',
    out_file: './logs/weather-station-out.log',
    log_file: './logs/weather-station-combined.log'
  }]
};
