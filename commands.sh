// Check Queue of Printer
lpstat -o

// Check Printer Status
lpstat -p Canon_SELPHY_CP1500

// Cancel all jobs
cancel -a Canon_SELPHY_CP1500

// Restart Cups
sudo service cups restart

// Cups interface
http://localhost:631

// Logs
cd /var/log/cups
cat access_log
