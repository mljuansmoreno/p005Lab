pipeline {
    agent { label 'linux-docker' }

    options {
        skipDefaultCheckout()
        disableConcurrentBuilds()
        timestamps()
        timeout(time: 45, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '20', artifactNumToKeepStr: '10'))
    }

    triggers {
        pollSCM('H/2 * * * *')
    }

    environment {
        PYTHONPATH = 'aplicacion:guiones'
        PYTHONUNBUFFERED = '1'
    }

    stages {
        stage('Obtener código') {
            steps {
                deleteDir()
                checkout scm
                script {
                    env.RUTA_CI_CAUSA = currentBuild.getBuildCauses().collect { causa ->
                        causa._class.tokenize('.').last()
                    }.join(', ')
                }
                sh 'git rev-parse HEAD'
            }
        }
        stage('Validar entorno') {
            steps {
                sh 'python3 guiones/ci/ejecutar.py preparar'
            }
        }
        stage('Analizar secretos') {
            steps {
                sh 'python3 guiones/ci/ejecutar.py secretos'
            }
        }
        stage('Probar web') {
            steps {
                sh 'python3 -m unittest discover -s pruebas/ci'
                sh 'python3 guiones/ci/ejecutar.py web'
            }
        }
        stage('Construir y verificar con Docker') {
            steps {
                sh 'python3 guiones/ci/ejecutar.py docker'
            }
        }
    }

    post {
        always {
            script {
                def salida = 'salidas/jenkins-ci'
                if (fileExists("${salida}/00-entorno.json")) {
                    try {
                        sh 'python3 guiones/ci/ejecutar.py finalizar'
                    } finally {
                        def archivos = sh(script: 'python3 guiones/ci/ejecutar.py archivos', returnStdout: true).trim()
                        archiveArtifacts artifacts: archivos, fingerprint: true, followSymlinks: false
                    }
                }
                for (def informe : ['web', 'integracion']) {
                    def ruta = "${salida}/reportes/${informe}.xml"
                    if (fileExists(ruta)) {
                        junit testResults: ruta
                    }
                }
            }
        }
    }
}
