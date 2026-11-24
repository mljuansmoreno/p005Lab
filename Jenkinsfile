pipeline {
    agent { label 'linux-docker' }

    options {
        skipDefaultCheckout()
        disableRestartFromStage()
        disableConcurrentBuilds()
        timestamps()
        timeout(time: 65, unit: 'MINUTES')
    }

    triggers {
        pollSCM('H/2 * * * *')
    }

    environment {
        PYTHONPATH = 'aplicacion:guiones'
        PYTHONUNBUFFERED = '1'
    }

    stages {
        stage('Checkout') {
            steps {
                deleteDir()
                script {
                    def datosGit = checkout scm
                    env.RUTA_CI_RAMA = datosGit.GIT_BRANCH ?: ''
                    env.RUTA_CI_ORIGEN = datosGit.GIT_URL ?: ''
                    env.RUTA_CI_CAUSA = currentBuild.getBuildCauses().collect { causa ->
                        causa._class.tokenize('.').last()
                    }.join(', ')
                }
                sh 'git rev-parse HEAD'
            }
        }
        stage('Build') {
            steps {
                sh 'python3 guiones/ci/ejecutar.py preparar'
                sh 'python3 guiones/ci/ejecutar.py secretos'
                script {
                    def opciones = params.RUTA_CI_SIN_CACHE ? ' --sin-cache' : ''
                    sh "python3 guiones/ci/ejecutar.py construir${opciones}"
                }
            }
        }
        stage('Test') {
            steps {
                sh 'python3 guiones/ci/probar_junit.py pruebas/ci salidas/jenkins-ci/reportes/coordinacion.xml'
                sh 'RUTA_QA_REPORTES=salidas/jenkins-ci/reportes python3 guiones/ci/probar_python.py --suite resiliencia'
                sh 'python3 guiones/ci/ejecutar.py web'
                sh 'python3 guiones/ci/ejecutar.py probar-imagenes'
            }
        }
    }

    post {
        always {
            script {
                def salida = 'salidas/jenkins-ci'
                try {
                    if (fileExists("${salida}/00-entorno.json")) {
                        def limpieza = sh(script: 'python3 guiones/ci/ejecutar.py limpiar-build', returnStatus: true)
                        try {
                            sh 'python3 guiones/ci/ejecutar.py finalizar'
                        } finally {
                            def archivos = sh(script: 'python3 guiones/ci/ejecutar.py archivos', returnStdout: true).trim()
                            archiveArtifacts artifacts: archivos, fingerprint: true, followSymlinks: false
                        }
                        if (limpieza != 0) {
                            currentBuild.result = 'FAILURE'
                        }
                    }
                } finally {
                    for (def informe : ['web', 'integracion', 'coordinacion', 'resiliencia']) {
                        def ruta = "${salida}/reportes/${informe}.xml"
                        if (fileExists(ruta)) {
                            junit testResults: ruta
                            if (informe in ['coordinacion', 'resiliencia']) {
                                archiveArtifacts artifacts: ruta, fingerprint: true, followSymlinks: false
                            }
                        } else if (currentBuild.currentResult == 'SUCCESS') {
                            error("Falta el informe obligatorio ${ruta}")
                        }
                    }
                }
            }
        }
    }
}
