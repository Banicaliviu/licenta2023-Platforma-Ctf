!/bin/bash
# Use the inbuit http module in python to serve the contents inside /app/flag dir
python3 -m http.server 3301 --bind 127.0.0.1 --directory /app/flag &
# Get the PID
P1=$!
# Run the node server
node app.js
P2=$!
# Wait forever for both processes to finish.
wait $P1 $P2
