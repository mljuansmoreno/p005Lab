import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { createRequire } from 'node:module';
import { join, resolve } from 'node:path';

const [archivoCredencial, numero, revision] = process.argv.slice(2);
if (!archivoCredencial || !/^[1-9][0-9]{4,9}$/.test(numero) || !/^[0-9a-f]{40}$/.test(revision)) {
  throw new Error('Se requiere la credencial privada, el número de build y el SHA.');
}

const herramientas = resolve(process.env.RUNNER_TEMP, 'ruta-ci-capturas');
const require = createRequire(join(herramientas, 'package.json'));
const { chromium } = require('playwright-core');
const origen = 'http://127.0.0.1:9090';
const [username, password] = (await readFile(archivoCredencial, 'utf8')).trim().split(':', 2);
if (!username || !password) {
  throw new Error('Falta la autenticación del controlador temporal.');
}

const trabajo = '/job/ruta-estadistica-main/';
const build = `${trabajo}${numero}/`;
const paginas = [
  { archivo: 'estado-build.png', ruta: build },
  { archivo: 'resultado-junit.png', ruta: `${build}testReport/` },
  { archivo: 'etapas-pipeline.png', ruta: trabajo, etapa: 'Construir y verificar con Docker' },
];
const carpeta = resolve('salidas', 'jenkins-capturas', `build-${numero}`);
const capturas = [];
const navegador = await chromium.launch({ executablePath: process.env.RUTA_CI_CHROME });
try {
  const contexto = await navegador.newContext({
    httpCredentials: { username, password, origin: origen },
    viewport: { width: 1480, height: 950 },
    serviceWorkers: 'block',
  });
  await contexto.route('**/*', ruta => {
    return new URL(ruta.request().url()).origin === origen ? ruta.continue() : ruta.abort();
  });
  await mkdir(carpeta, { recursive: true });
  const pagina = await contexto.newPage();
  for (const pantalla of paginas) {
    const url = origen + pantalla.ruta;
    const respuesta = await pagina.goto(url, { waitUntil: 'domcontentloaded' });
    if (!respuesta?.ok() || pagina.url() !== url) {
      throw new Error(`La pantalla de Jenkins no respondió correctamente en ${pantalla.ruta}`);
    }
    if (pantalla.etapa) {
      await pagina.getByText(pantalla.etapa, { exact: true }).first().waitFor();
    }
    const ruta = join(carpeta, pantalla.archivo);
    await pagina.locator('#main-panel').screenshot({ path: ruta, animations: 'disabled' });
    const sha256 = createHash('sha256').update(await readFile(ruta)).digest('hex');
    capturas.push({ archivo: pantalla.archivo, url, sha256 });
  }
} finally {
  await navegador.close();
}

const { GITHUB_SERVER_URL, GITHUB_REPOSITORY, GITHUB_RUN_ID } = process.env;
const manifiesto = {
  build: Number(numero),
  revision,
  fecha_utc: new Date().toISOString(),
  acciones: `${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}/actions/runs/${GITHUB_RUN_ID}`,
  capturas,
};
await writeFile(join(carpeta, 'capturas.json'), JSON.stringify(manifiesto, null, 2) + '\n');
