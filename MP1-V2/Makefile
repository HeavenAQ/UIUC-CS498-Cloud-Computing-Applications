BUCKET := my-cca-bucket
PEM := ec2-keypair.pem
HOST := 

all: run
	aws s3 rm "s3://${BUCKET}/results.csv"
	aws s3 cp results.csv "s3://${BUCKET}/results.csv"
	scp -i ./ec2-keypair.pem results.csv ec2-user@${HOST}:/home/ec2-user/results.csv
	ssh ec2-user@${HOST} "python3 /home/ec2-user/submit.py"
run:
	uv run main.py
