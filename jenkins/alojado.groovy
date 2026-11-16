import hudson.model.Node
import hudson.security.FullControlOnceLoggedInAuthorizationStrategy
import hudson.security.HudsonPrivateSecurityRealm
import hudson.slaves.DumbSlave
import hudson.slaves.JNLPLauncher
import java.nio.file.Files
import java.nio.file.attribute.PosixFilePermissions
import java.util.UUID
import jenkins.model.Jenkins
import jenkins.model.JenkinsLocationConfiguration
import jenkins.security.ApiTokenProperty

// Este inicializador se monta únicamente en el controlador desechable del runner.
def numero = System.getenv('RUTA_CI_NUMERO_ALOJADO') as int
assert numero >= 10_000
def controlador = Jenkins.get()
assert controlador.getItem('ruta-estadistica-main') == null

def seguridad = new HudsonPrivateSecurityRealm(false)
def usuario = seguridad.createAccount('operador-ci', UUID.randomUUID().toString())
def autorizacion = new FullControlOnceLoggedInAuthorizationStrategy()
autorizacion.setAllowAnonymousRead(false)
controlador.setSecurityRealm(seguridad)
controlador.setAuthorizationStrategy(autorizacion)
controlador.setNumExecutors(0)
controlador.setSlaveAgentPort(-1)
JenkinsLocationConfiguration.get().setUrl('http://127.0.0.1:9090/')
controlador.save()

def agente = new DumbSlave('linux-docker', '/var/tmp/ruta-estadistica-agente', new JNLPLauncher())
agente.setMode(Node.Mode.EXCLUSIVE)
agente.setNumExecutors(1)
controlador.addNode(agente)
new File('/opt/ruta-ci/trabajo-main.xml').withInputStream { xml ->
    def trabajo = controlador.createProjectFromXML('ruta-estadistica-main', xml)
    trabajo.updateNextBuildNumber(numero)
}

def token = usuario.getProperty(ApiTokenProperty).generateNewToken('ejecucion-alojada')
def privado = Files.createDirectory(controlador.rootDir.toPath().resolve('arranque-alojado'),
    PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString('rwx------')))
privado.resolve('agente').toFile().text = agente.toComputer().getJnlpMac()
privado.resolve('api').toFile().text = "operador-ci:${token.plainValue}"
