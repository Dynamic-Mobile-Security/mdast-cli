pipeline {
    environment {
        registry = "mobilesecurity/mdast_cli"
        registryCredential = 'dockerhub_mobilesecurity'
        dockerImage = ''
    }
    agent { label 'master' }
    stages {
        stage('Cloning Git') {
          steps {
                git branch: 'main', url: 'https://github.com/Dynamic-Mobile-Security/mdast-cli.git'
            }
        }
        stage('Building image') {
            steps {
                script {
                    dockerImage = docker.build registry + ":latest"
                }
            }
        }
        stage('Deploy image') {
            steps {
                script {
                    docker.withRegistry( '', registryCredential ) {
                        dockerImage.push()
                    }
                }
            }
        }
        stage('Cleaning up') {
            steps {
                sh "docker rmi $registry:latest"
            }
        }
    }
}