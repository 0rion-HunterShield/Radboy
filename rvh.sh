while test 1 -eq 1 ; do
	clear
	wc -l combos.json.csv
	tail -n1 combos.json.csv
	free -h
	ls -lh combos.json.csv
	sleep 1s
done
