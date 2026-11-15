import jenkins.model.Jenkins

def controlador = Jenkins.get()
controlador.setNumExecutors(0)
controlador.setSlaveAgentPort(-1)
controlador.save()
