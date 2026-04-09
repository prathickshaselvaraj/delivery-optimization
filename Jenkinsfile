pipeline {
    agent any
    environment {
        DOCKER_CREDENTIALS = credentials('dockerhub-credentials')
        DOCKER_IMAGE       = "prathicksha15/delivery-optimization"
        IMAGE_TAG          = "${env.BUILD_NUMBER}"
        SONAR_URL          = "http://localhost:9000"
    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Build') {
            steps {
                sh '''
                    python3 -m venv venv
                    venv/bin/pip install --upgrade pip
                    venv/bin/pip install -r requirements.txt
                '''
            }
        }
        stage('Test') {
            steps {
                sh '''
                    venv/bin/pip install pytest pytest-cov
                    venv/bin/pytest --cov=. --cov-report=xml --junitxml=report.xml
                '''
            }
            post {
                always {
                    junit 'report.xml'
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                // ✅ withSonarQubeEnv injects token automatically — no manual -Dsonar.login needed
                withSonarQubeEnv('My Sonar Server') {
                    sh '''
                        sonar-scanner \
                          -Dsonar.projectKey=delivery-optimization \
                          -Dsonar.sources=. \
                          -Dsonar.tests=tests \
                          -Dsonar.exclusions=tests/**,venv/** \
                          -Dsonar.python.coverage.reportPaths=coverage.xml
                    '''
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    script {
                        def qg = waitForQualityGate()
                        if (qg.status != 'OK') {
                            error "Pipeline aborted: Quality Gate failed with status: ${qg.status}"
                        }
                    }
                }
            }
        }

        stage('Docker Build & Push') {
            steps {
                // ✅ Single quotes on outer sh — DOCKER_CREDENTIALS vars are env vars, safe to use
                sh '''
                    docker build -t $DOCKER_IMAGE:$IMAGE_TAG .
                    docker tag $DOCKER_IMAGE:$IMAGE_TAG $DOCKER_IMAGE:latest
                    echo $DOCKER_CREDENTIALS_PSW | docker login -u $DOCKER_CREDENTIALS_USR --password-stdin
                    docker push $DOCKER_IMAGE:$IMAGE_TAG
                    docker push $DOCKER_IMAGE:latest
                '''
            }
        }

        stage('Update GitOps Repo') {
    steps {
        withCredentials([usernamePassword(credentialsId: 'github-token', usernameVariable: 'GIT_USER', passwordVariable: 'GIT_TOKEN')]) {
            sh """
                git clone https://${GIT_USER}:${GIT_TOKEN}@github.com/prathickshaselvaraj/delivery-optimization-gitops.git
                cd delivery-optimization-gitops/k8s
                sed -i "s|image: .*|image: ${DOCKER_IMAGE}:${IMAGE_TAG}|g" deployment.yaml
                git config user.email "jenkins@example.com"
                git config user.name "jenkins"
                git add deployment.yaml
                git commit -m "Update image to ${IMAGE_TAG}"
                git push
            """
        }
    }
}
    }

    post {
        always {
            sh 'docker rmi $DOCKER_IMAGE:$BUILD_NUMBER || true'
            cleanWs()
        }
    }
}
