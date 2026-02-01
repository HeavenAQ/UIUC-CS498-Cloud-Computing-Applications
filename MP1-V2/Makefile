all: run
	aws s3 rm "s3://uiuc-cca-bucket/results.csv"
	aws s3 cp results.csv "s3://uiuc-cca-bucket/results.csv"
	scp -i ./uiuc-ec2-keypair.pem results.csv ec2-user@13.112.159.231:/home/ec2-user/assignment/w1/results.csv
run:
	uv run main.py
