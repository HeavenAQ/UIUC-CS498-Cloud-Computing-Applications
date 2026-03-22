import requests
import json

YOUR_EMAIL = "yiminc2@illinois.edu"  # put your Coursera email
YOUR_SECRET = "bkbpwjvgAnbZynTX"  # put your secret token from Coursera

# 1. Frontend Deployment (S3 Endpoint)
FRONTEND_URL = "http://my-frontend-asset.s3-website-us-east-1.amazonaws.com"  # put your S3 endpoint

# 2. Backend Deployment (Elastic Beanstalk URL)
BEANSTALK_URL = "http://hw5-backend.eba-wqfum6je.us-east-1.elasticbeanstalk.com"  # put your Beanstalk backend URL

# 3. CICD (Frontend S3 Log URL) - a presigned URL to access the Frontend CodeBuild logs.
BACKEND_S3_LOG_URL = "https://ci-cd-log-files.s3.us-east-1.amazonaws.com/backend-logs/24a077dd-0021-4cd9-b3f1-03f9ec7542c1.gz?response-content-disposition=inline&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEFwaCXVzLWVhc3QtMSJHMEUCIDHYFnzfYo8t9%2BuWERMPuJicj0fqzdOBUYnArXShZmu%2BAiEA6eFwv8H2DDGUWGuh8xPQViaBRpk0Kcg2Dr9pcabs3q0quQMIJBACGgwyMjE4NDAyOTgwNTEiDN01yqP1retaBfov%2FiqWA98%2BpjyiYFH%2BdyDDCHmKBQ%2FWEf3OpwjpxLt7%2Fa3akFgz7dgz%2BadIf48zrPNhGx5i576NbvPrqJkYlDS0QO7hTqZHmKvoGGvS3i%2F0zBcOJuFWxcKtUT0iJzSgDek90592ILdu3x8cEFBB72H60k%2BfqPvw89zPKMvtz4IAu684LEjYCxEanaqPA%2FUQTGfmo8e4g01BjBpFTZKvzlWXNyzZw%2FnxzF8wmfeUDoldaEqb8iXlCkkzGy8BR1QzEfebXYuuJK9nHFUpnAsWqeJ%2F42JT4USZW8IsqKeamzikK0RoAbzGwOEI%2Bzb49TgZTv6GkKqnIzabsfQdYX%2BhD9RRW4V8z0RLy4WBBWPMqQznMmhemK3ozBDPoQjC%2FZ4qPB3HEJFq08SYrlDNeeEdWU3L6%2FVEfjQLjsVx7BR2x8DNWSOIj8XnDxt9Q2R7YiKD%2FTmYT1RLP%2F2DTM1%2BwWKFX0AjfmcGEJoS0q%2FB11gYLHdDp5%2FiAP9TQLe5fxrscTzJpA3RLkUa3%2BuhdiGqz051o7Tfiy83IDdRWT9%2F6PMw8862zQY63gJgOTNuO%2BgNWeg71q5eL81AT0HXcWusNuZir6ukMYKWaXwr2HxAm64%2BoKLi8GY1gjTQrohLWN8Rxbi%2BQNVZlNIEtlwuta5T%2BFix%2B6EHfsdnGT73xjQmd%2FsFY1RbpcTFeq%2FNT7h1mp4AzXf8quIox%2FRKl5MSYHF1PamSSrYwgo5quZeMH6wLhN8gc355eL97EeP86Rtep7mrjpwrROhSi8Eqq7R%2BdbvTZrhTjFMDsRmmlrER93uV%2FwrH%2Bue8%2FtWeHWgIXBEU4IZcigD5WRZR2bwIRVmtfssO5VjL7HtjLnPEuSLfUOTh8V3BrJMBtf2NFIpvnVpSnaJnlVdjqbAImw3JebDOM4%2B7vk7lXlKWIMy9HLq5JX3pxupbcQf2kYDt0SpPZ8TS0ac2LaOAJslRaucLR%2BgeJ9UsEC0i4JNaTO8tJMyDbc0N4k%2FcMq3TFSGoKyTS1KPaBlLMiH69zeWcjg%3D%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=ASIATHJVWKBB4LCDHREX%2F20260309%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20260309T031455Z&X-Amz-Expires=10800&X-Amz-SignedHeaders=host&X-Amz-Signature=4cf6073ec3d2cc363762ef8aebca388a8f8331634c835f09953e61daf42084d1"  # put your presigned S3 Backend log URL

# 4. CICD (Backend S3 Log URL) - a presigned URL to access the Backend CodeBuild logs.
FRONTEND_S3_LOG_URL = "https://ci-cd-log-files.s3.us-east-1.amazonaws.com/frontend-logs/3a07ed55-1438-4227-817b-275489e4df0c.gz?response-content-disposition=inline&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEFwaCXVzLWVhc3QtMSJHMEUCIDHYFnzfYo8t9%2BuWERMPuJicj0fqzdOBUYnArXShZmu%2BAiEA6eFwv8H2DDGUWGuh8xPQViaBRpk0Kcg2Dr9pcabs3q0quQMIJBACGgwyMjE4NDAyOTgwNTEiDN01yqP1retaBfov%2FiqWA98%2BpjyiYFH%2BdyDDCHmKBQ%2FWEf3OpwjpxLt7%2Fa3akFgz7dgz%2BadIf48zrPNhGx5i576NbvPrqJkYlDS0QO7hTqZHmKvoGGvS3i%2F0zBcOJuFWxcKtUT0iJzSgDek90592ILdu3x8cEFBB72H60k%2BfqPvw89zPKMvtz4IAu684LEjYCxEanaqPA%2FUQTGfmo8e4g01BjBpFTZKvzlWXNyzZw%2FnxzF8wmfeUDoldaEqb8iXlCkkzGy8BR1QzEfebXYuuJK9nHFUpnAsWqeJ%2F42JT4USZW8IsqKeamzikK0RoAbzGwOEI%2Bzb49TgZTv6GkKqnIzabsfQdYX%2BhD9RRW4V8z0RLy4WBBWPMqQznMmhemK3ozBDPoQjC%2FZ4qPB3HEJFq08SYrlDNeeEdWU3L6%2FVEfjQLjsVx7BR2x8DNWSOIj8XnDxt9Q2R7YiKD%2FTmYT1RLP%2F2DTM1%2BwWKFX0AjfmcGEJoS0q%2FB11gYLHdDp5%2FiAP9TQLe5fxrscTzJpA3RLkUa3%2BuhdiGqz051o7Tfiy83IDdRWT9%2F6PMw8862zQY63gJgOTNuO%2BgNWeg71q5eL81AT0HXcWusNuZir6ukMYKWaXwr2HxAm64%2BoKLi8GY1gjTQrohLWN8Rxbi%2BQNVZlNIEtlwuta5T%2BFix%2B6EHfsdnGT73xjQmd%2FsFY1RbpcTFeq%2FNT7h1mp4AzXf8quIox%2FRKl5MSYHF1PamSSrYwgo5quZeMH6wLhN8gc355eL97EeP86Rtep7mrjpwrROhSi8Eqq7R%2BdbvTZrhTjFMDsRmmlrER93uV%2FwrH%2Bue8%2FtWeHWgIXBEU4IZcigD5WRZR2bwIRVmtfssO5VjL7HtjLnPEuSLfUOTh8V3BrJMBtf2NFIpvnVpSnaJnlVdjqbAImw3JebDOM4%2B7vk7lXlKWIMy9HLq5JX3pxupbcQf2kYDt0SpPZ8TS0ac2LaOAJslRaucLR%2BgeJ9UsEC0i4JNaTO8tJMyDbc0N4k%2FcMq3TFSGoKyTS1KPaBlLMiH69zeWcjg%3D%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=ASIATHJVWKBB4LCDHREX%2F20260309%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20260309T031535Z&X-Amz-Expires=10800&X-Amz-SignedHeaders=host&X-Amz-Signature=652aa96009e1667a83cf51c7601848d63d24e178fb6c044b2c9a6fa5c79f9852"  # put your presigned S3 Backend log URL

# Autograder URL
LAMBDA_URL = (
    "https://ttrejw3rxf.execute-api.us-east-1.amazonaws.com/default/mp5_fullstack"
)

input_data = {
    "frontend_url": FRONTEND_URL,
    "beanstalk_url": BEANSTALK_URL,
    "frontend_s3_log_url": FRONTEND_S3_LOG_URL,
    "backend_s3_log_url": BACKEND_S3_LOG_URL,
    "submitterEmail": YOUR_EMAIL,
    "secret": YOUR_SECRET,
}

payload = {
    "input": json.dumps(input_data),
}

try:
    response = requests.post(LAMBDA_URL, json=payload)
    print(response.status_code, response.reason)
    print(response.text)
except Exception as e:
    print("Error during submission:", e)
