from flask import Flask, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

@app.route("/info")
def info():
    # IMDSv2: Get Token
    try:
        token = requests.put("http://169.254.169.254/latest/api/token", 
                             headers={"X-aws-ec2-metadata-token-ttl-seconds": "21600"}, 
                             timeout=1).text
        headers = {"X-aws-ec2-metadata-token": token}
    except Exception:
        # Fallback if token fails (e.g. not on AWS)
        headers = {}
        pass

    try:
        instance_id = requests.get("http://169.254.169.254/latest/meta-data/instance-id", 
                                   headers=headers, timeout=1).text
    except Exception:
        instance_id = "not running on an EC2 instance"

    try:
        availability_zone = requests.get("http://169.254.169.254/latest/meta-data/placement/availability-zone", 
                                         headers=headers, timeout=1).text
    except Exception:
        availability_zone = "not running on an EC2 instance"

    return jsonify({
        "instance_id": instance_id,
        "availability_zone": availability_zone,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
