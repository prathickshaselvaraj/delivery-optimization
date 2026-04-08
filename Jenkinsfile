pipeline {
    agent any

    environment {
        // ── Credentials stored in Jenkins Credentials Manager ──
        DOCKER_CREDENTIALS = credentials('dockerhub-credentials')
        SONAR_TOKEN        = credentials('sonarqube-token')
        GITOPS_TOKEN       = credentials('github-token')

        // ── Config ──────────────────────────────────────────────
        DOCKER_IMAGE       = "your-dockerhub-username/delivery-optimization"
        GITOPS_REPO        = "https://github.com/prathickshaselvaraj/delivery-optimization-gitops"
        GITOPS_REPO_NAME   = "delivery-optimization-gitops"
        IMAGE_TAG          = "${env.BUILD_NUMBER}-${env.GIT_COMMIT.take(7)}"
        SONAR_URL          = "http://<your-sonarqube-host>:9000"
    }

    stages {

        // ── Stage 1: Checkout ────────────────────────────────────
        stage('Checkout') {
            steps {
                checkout scm
                echo "✅ Code checked out — Branch: ${env.BRANCH_NAME}, Commit: ${env.GIT_COMMIT}"
            }
        }

        // ── Stage 2: Install & Test ──────────────────────────────
        stage('Install & Test') {
            steps {
                sh '''
                    npm ci
                    npm test -- --coverage --watchAll=false
                '''
            }
            post {
                always {
                    junit 'test-results/**/*.xml'
                }
            }
        }

        // ── Stage 3: SonarQube Analysis ──────────────────────────
        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    sh """
                        npx sonar-scanner \
                          -Dsonar.projectKey=delivery-optimization \
                          -Dsonar.sources=. \
                          -Dsonar.host.url=${SONAR_URL} \
                          -Dsonar.login=${SONAR_TOKEN}
                    """
                }
            }
        }

        // ── Stage 4: Quality Gate (BLOCKS pipeline if failed) ────
        stage('Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                    // ↑ If SonarQube gate FAILS, pipeline stops here.
                    // Docker build and push are SKIPPED entirely.
                }
            }
        }

        // ── Stage 5: Docker Build & Push ─────────────────────────
        stage('Docker Build & Push') {
            steps {
                sh """
                    echo "🐳 Building image: ${DOCKER_IMAGE}:${IMAGE_TAG}"
                    docker build -t ${DOCKER_IMAGE}:${IMAGE_TAG} .
                    docker tag  ${DOCKER_IMAGE}:${IMAGE_TAG} ${DOCKER_IMAGE}:latest

                    echo ${DOCKER_CREDENTIALS_PSW} | docker login \
                        -u ${DOCKER_CREDENTIALS_USR} --password-stdin

                    docker push ${DOCKER_IMAGE}:${IMAGE_TAG}
                    docker push ${DOCKER_IMAGE}:latest
                    echo "✅ Image pushed: ${IMAGE_TAG}"
                """
            }
        }

        // ── Stage 6: Update GitOps Repo (triggers ArgoCD) ────────
        stage('Update GitOps Repo') {
            steps {
                sh """
                    git clone https://${GITOPS_TOKEN}@github.com/prathickshaselvaraj/${GITOPS_REPO_NAME}.git
                    cd ${GITOPS_REPO_NAME}

                    # Replace IMAGE_TAG in deployment.yaml
                    sed -i 's|${DOCKER_IMAGE}:.*|${DOCKER_IMAGE}:${IMAGE_TAG}|g' k8s/deployment.yaml

                    git config user.email "jenkins@ci.local"
                    git config user.name  "Jenkins CI"
                    git add k8s/deployment.yaml
                    git commit -m "ci: update image to ${IMAGE_TAG} [skip ci]"
                    git push origin main

                    echo "✅ GitOps repo updated — ArgoCD will deploy shortly"
                """
            }
        }
    }

    // ── Post Actions ─────────────────────────────────────────────
    post {
        success {
            echo "🎉 Pipeline PASSED — ${DOCKER_IMAGE}:${IMAGE_TAG} deployed to production"
        }
        failure {
            echo "❌ Pipeline FAILED — Quality Gate or build step blocked deployment"
        }
        always {
            sh "docker rmi ${DOCKER_IMAGE}:${IMAGE_TAG} || true"
            cleanWs()
        }
    }
}
