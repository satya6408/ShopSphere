pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out ShopSphere source code'
                checkout scm
            }
        }

        stage('Product Service Tests') {
            steps {
                dir('services/product-service') {
                    sh '''
                        python3 -m venv venv
                        venv/bin/pip install -r requirements.txt
                        venv/bin/python -m pytest -v
                    '''
                }
            }
        }

        stage('Cart Service Tests') {
            steps {
                dir('services/cart-service') {
                    sh '''
                        python3 -m venv venv
                        venv/bin/pip install -r requirements.txt
                        venv/bin/python -m pytest -v
                    '''
                }
            }
        }

        stage('Trivy Filesystem Scan') {
            steps {
                sh '''
                    trivy fs \
                      --scanners vuln,secret,misconfig \
                      --severity HIGH,CRITICAL \
                      --exit-code 0 \
                      .
                '''
            }
        }

        stage('SonarQube Analysis') {
            steps {
                script {
                    def scannerHome = tool 'SonarScanner'

                    withSonarQubeEnv('ShopSphere-SonarQube') {
                        sh "${scannerHome}/bin/sonar-scanner"
                    }
                }
            }
        }

        stage('Docker Image Build') {
            steps {
                sh '''
                    docker build -t shopsphere-product:${BUILD_NUMBER} services/product-service
                    docker build -t shopsphere-cart:${BUILD_NUMBER} services/cart-service
                    docker build -t shopsphere-frontend:${BUILD_NUMBER} frontend
                    docker build -t shopsphere-database:${BUILD_NUMBER} database
                '''
            }
        }

        stage('Trivy Docker Image Scan') {
            steps {
                sh '''
                    for image in product cart frontend database; do
                        trivy image \
                          --severity HIGH,CRITICAL \
                          --exit-code 0 \
                          shopsphere-${image}:${BUILD_NUMBER}
                    done
                '''
            }
        }

        stage('Docker Hub Push') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerHubCred',
                        usernameVariable: 'DOCKERHUB_USERNAME',
                        passwordVariable: 'DOCKERHUB_TOKEN'
                    )
                ]) {
                    sh '''
                        set +x
                        echo "$DOCKERHUB_TOKEN" | docker login \
                          -u "$DOCKERHUB_USERNAME" \
                          --password-stdin

                        for image in product cart frontend database; do
                            docker tag shopsphere-${image}:${BUILD_NUMBER} \
                              "$DOCKERHUB_USERNAME/shopsphere-${image}:${BUILD_NUMBER}"

                            docker tag shopsphere-${image}:${BUILD_NUMBER} \
                              "$DOCKERHUB_USERNAME/shopsphere-${image}:latest"

                            docker push "$DOCKERHUB_USERNAME/shopsphere-${image}:${BUILD_NUMBER}"
                            docker push "$DOCKERHUB_USERNAME/shopsphere-${image}:latest"
                        done

                        docker logout
                    '''
                }
            }
        }

        stage('Ansible Deployment') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerHubCred',
                        usernameVariable: 'DOCKERHUB_USERNAME',
                        passwordVariable: 'DOCKERHUB_TOKEN'
                    ),
                    file(
                        credentialsId: 'shopsphere-env',
                        variable: 'ENV_FILE'
                    )
                ]) {
                    sh '''
                        set +x

                        cp "$ENV_FILE" .env
                        chmod 600 .env

                        trap 'docker logout >/dev/null 2>&1 || true; rm -f .env' EXIT

                        echo "$DOCKERHUB_TOKEN" | docker login \
                          -u "$DOCKERHUB_USERNAME" \
                          --password-stdin

                        ansible-playbook \
                          -i ansible/inventory.ini \
                          ansible/deploy.yml \
                          -e "image_tag=${BUILD_NUMBER}" \
                          -e "dockerhub_username=${DOCKERHUB_USERNAME}"
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'ShopSphere CI/CD pipeline completed successfully!'
        }

        failure {
            echo 'ShopSphere CI/CD pipeline failed. Check the console output.'
        }

        always {
            echo 'ShopSphere pipeline execution finished.'
        }
    }
}
