import subprocess
import json
import requests
import sys
import shutil

# ----------------------------------
# Add your variable values here!
# ----------------------------------

# Submission configuration
COURSERA_TOKEN = ""  # Replace with your Coursera token
S3_URI = ""  # Replace with your S3 URI
SUBMITTER_EMAIL = ""  # Replace with your email

# ----------------------------------
# Do not edit below this part!
# ----------------------------------

# API endpoint
API_URL = "https://seorwrpmwh.execute-api.us-east-1.amazonaws.com/prod/mp1-v2"


def check_aws_cli_installed():
    """Check if AWS CLI is installed and available in PATH."""
    if not shutil.which("aws"):
        print("Error: AWS CLI is not installed or not in your PATH.")
        print(
            "Please install AWS CLI: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
        )
        sys.exit(1)


def run_command(cmd):
    """Run a shell command and return the JSON-decoded output."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON output from command '{cmd}'")
            print(f"Command output: {result.stdout}")
            print(f"JSON error: {e}")
            sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(
            "Please confirm IAM role is attached to the EC2 instance. Look at the MP instructions carefully."
        )
        sys.exit(1)


def extract_role_name(association_data):
    """
    Extracts the role name from the describe-iam-instance-profile-associations output.
    This function first checks if 'RoleName' exists directly.
    If not, it parses the instance profile ARN to get the instance profile name,
    then retrieves the full instance profile details and extracts the RoleName from it.
    """
    try:
        associations = association_data.get("IamInstanceProfileAssociations", [])
        if not associations:
            print("No IAM instance profile associations found.")
            print(
                "Make sure you're running this on an EC2 instance with an IAM role attached."
            )
            sys.exit(1)

        assoc = associations[0]
        role_name = assoc.get("RoleName")

        if not role_name:
            instance_profile = assoc.get("IamInstanceProfile", {})
            arn = instance_profile.get("Arn", "")
            if not arn:
                print("Neither RoleName nor IamInstanceProfile.Arn found.")
                print("Make sure your EC2 instance has an IAM role properly attached.")
                sys.exit(1)

            instance_profile_name = arn.split("/")[-1]

            cmd_get_profile = f"aws iam get-instance-profile --instance-profile-name {instance_profile_name}"
            profile_data = run_command(cmd_get_profile)
            roles = profile_data.get("InstanceProfile", {}).get("Roles", [])
            if not roles:
                print("No roles found in the instance profile.")
                print(
                    "This EC2 instance has an instance profile without an attached role."
                )
                sys.exit(1)

            role_name = roles[0].get("RoleName")

        if not role_name:
            print("Failed to extract a role name.")
            print("Please make sure your EC2 instance has a valid IAM role attached.")
            sys.exit(1)

        return role_name
    except Exception as e:
        print(f"Error extracting role name: {str(e)}")
        print(
            "Please make sure you have the necessary IAM permissions to describe instance profiles."
        )
        sys.exit(1)


def main():
    # Validate S3 URI format
    if not S3_URI.startswith("s3://"):
        print("Error: S3 URI must start with 's3://'")
        print("Example format: s3://bucket-name/path/to/file.csv")
        sys.exit(1)

    # Check if AWS CLI is installed
    check_aws_cli_installed()

    try:
        # Get IAM instance profile associations
        cmd1 = "aws ec2 describe-iam-instance-profile-associations"
        assoc_data = run_command(cmd1)

        # Extract role name
        role_name = extract_role_name(assoc_data)

        # Get attached policies
        cmd2 = f"aws iam list-attached-role-policies --role-name {role_name}"
        policies_data = run_command(cmd2)
    except Exception as e:
        print(f"Error accessing AWS resources: {str(e)}")
        print(
            "Please ensure you have the necessary permissions and are running on an EC2 instance."
        )
        sys.exit(1)

    payload = {
        "coursera_token": COURSERA_TOKEN,
        "s3_url": S3_URI,
        "submitterEmail": SUBMITTER_EMAIL,
        "attached_role_policies": policies_data,
    }

    payload_json = json.dumps(payload, indent=4)
    print("Submitting assignment to autograder...")

    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(API_URL, data=payload_json, headers=headers)
        if response.status_code == 200:
            print("Submission successful!")
            print("Response Body:", response.text)
        else:
            print(f"Submission failed with status code: {response.status_code}")
            print("Response Body:", response.text)
            print("\nPlease check your submission details and try again.")
    except requests.RequestException as e:
        print(f"Error sending request to API: {e}")
        print("Please check your internet connection and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()
