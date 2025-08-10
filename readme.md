# CI/CD Pipeline with Jenkins, Docker, and Google Cloud

This project demonstrates a complete CI/CD workflow to automate the building, containerization, and deployment of a Python-based ML application to **Google Cloud Run** using **Jenkins**, **Docker**, and **Google Cloud Registry (GCR)**.

---

## 🚀 Workflow Overview

1. **Create a VM** in Google Cloud (Compute Engine: `e2-standard`, Ubuntu OS).
2. **Integrate GitHub** with Jenkins.
3. **Write Jenkins Pipeline** for automated build and deployment.
4. **Build Docker Image** of the project.
5. **Push Image to GCR** (Google Container Registry).
6. **Deploy App** from GCR to Cloud Run.

---

## 🖥️ 1. Create VM in Google Cloud

- Machine type: `e2-standard`
- OS: **Ubuntu**
- Networking: Allow Http
- Allow Access to all API
- SSH into the VM once created.


---

## ⚙️ 2. Install Jenkins

Follow the official Jenkins installation guide for Ubuntu:  
[Install Jenkins on Ubuntu](https://phoenixnap.com/kb/install-jenkins-ubuntu)

- Open port 8080 from network firewall, make sure to give access to all instance
- Copy external IP address for VM:8080 in browser
- Copy password from /var with sudo in front of it and paste
- install all suggested plugins

---

## 🐳 3. Install Docker

Official Docker installation guide for Ubuntu:  
[Install Docker on Ubuntu](https://docs.docker.com/engine/install/ubuntu/)

---

## 🔑 4. Grant Docker Permissions to Jenkins User

```bash
sudo su
groupadd docker
usermod -aG docker jenkins
usermod -aG root jenkins
sudo systemctl restart jenkins

## 🐍 5. Install Python & Dependencies Inside VM

```bash
sudo su
apt update -y
apt install -y python3
python3 --version
ln -s /usr/bin/python3 /usr/bin/python
python --version
apt install -y python3-pip
apt install -y python3-venv
```

---

## 📄 6. Initial Jenkinsfile (GitHub Clone)

```groovy
pipeline {
    agent any

    stages {
        stage('Cloning Github repo to Jenkins') {
            steps {
                script {
                    echo 'Cloning Github repo to Jenkins............'
                    checkout scmGit(
                        branches: [[name: '*/main']],
                        extensions: [],
                        userRemoteConfigs: [[
                            credentialsId: 'github-token',
                            url: 'https://github.com/Joelfernandes30/mlops-project-1.git'
                        ]]
                    )
                }
            }
        }
    }
}
```

---

## 📦 7. Dockerfile

```dockerfile
# Use a lightweight Python image
FROM python:slim

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -e .

# Train the model
RUN python pipeline/training_pipeline.py

# Expose Flask port
EXPOSE 5000

# Run the app
CMD ["python", "application.py"]
```

---

## ⚙️ 8. Updated Jenkinsfile (with Python Env Setup)

```groovy
pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
    }

    stages {
        stage('Cloning Github repo to Jenkins') {
            steps {
                script {
                    echo 'Cloning Github repo to Jenkins............'
                    checkout scmGit(
                        branches: [[name: '*/main']],
                        extensions: [],
                        userRemoteConfigs: [[
                            credentialsId: 'github-token',
                            url: 'https://github.com/Joelfernandes30/mlops-project-1.git'
                        ]]
                    )
                }
            }
        }

        stage('Setting up Virtual Environment & Installing Dependencies') {
            steps {
                script {
                    echo 'Setting up Virtual Environment & Installing Dependencies............'
                    sh '''
                    python -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -e .
                    '''
                }
            }
        }
    }
}
```

---

## ☁️ 9. Install Google Cloud SDK

```bash
apt-get update
apt-get install -y curl apt-transport-https ca-certificates gnupg
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
echo "deb https://packages.cloud.google.com/apt cloud-sdk main" \
    | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
apt-get update && apt-get install -y google-cloud-sdk
gcloud --version
```

Restart Jenkins:

```bash
sudo systemctl restart jenkins
```

---

## 🔐 10. Add GCP Credentials to Jenkins

* Go to **Jenkins → Manage Jenkins → Credentials → Global Credentials**.
* Add a **Secret File** credential.
* Upload your GCP Service Account JSON file.
* Name it: `gcp-key`.

---

## 🔓 11. Enable Required Google Cloud APIs

Enable in Google Cloud Console:

1. **Google Container Registry API**
2. **Artifact Registry API**
3. **Cloud Resource Manager API**

Assign **Owner** role to your service account in **IAM**.

---

## 📜 12. Final Jenkinsfile (Build & Push to GCR)

```groovy
pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
        GCP_PROJECT = "eighth-cacao-455017-q1"
        GCLOUD_PATH = "/var/jenkins_home/google-cloud-sdk/bin"
    }

    stages {
        stage('Cloning Github repo to Jenkins') {
            steps {
                script {
                    echo 'Cloning Github repo to Jenkins............'
                    checkout scmGit(
                        branches: [[name: '*/main']],
                        extensions: [],
                        userRemoteConfigs: [[
                            credentialsId: 'github-token',
                            url: 'https://github.com/Joelfernandes30/mlops-project-1.git'
                        ]]
                    )
                }
            }
        }

        stage('Setting up Virtual Environment & Installing Dependencies') {
            steps {
                script {
                    echo 'Setting up Virtual Environment & Installing Dependencies............'
                    sh '''
                    python -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -e .
                    '''
                }
            }
        }

        stage('Building and Pushing Docker Image to GCR') {
            steps {
                withCredentials([file(credentialsId: 'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    script {
                        echo 'Building and Pushing Docker Image to GCR.............'
                        sh '''
                        export PATH=$PATH:${GCLOUD_PATH}

                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                        gcloud config set project ${GCP_PROJECT}
                        gcloud auth configure-docker --quiet

                        docker build -t gcr.io/${GCP_PROJECT}/ml-project:latest .
                        docker push gcr.io/${GCP_PROJECT}/ml-project:latest
                        '''
                    }
                }
            }
        }
    }
}
```

---

## 🌐 13. Deploy to Cloud Run

* Open **Google Cloud Console** → **Cloud Run**.
* Deploy using the image from **GCR**.
* Click on the **Service URL** to view your running app.

---

## ✅ Conclusion

This setup fully automates:

* Fetching the latest code from GitHub.
* Installing dependencies.
* Building & pushing Docker images to **GCR**.
* Deploying the application to **Cloud Run**.

You now have a complete **CI/CD pipeline** running on **Google Cloud**.


