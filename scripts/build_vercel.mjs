// Build static assets without npm dependencies; never copy project files or .env.
import {mkdirSync,copyFileSync,writeFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
const root=fileURLToPath(new URL('../',import.meta.url));
let api=(process.env.API_BASE_URL||'').trim().replace(/\/+$/,'');
if(api){const url=new URL(api);if(url.protocol!=='https:'||url.username||url.password||url.search||url.hash||url.pathname!=='/')throw new Error('API_BASE_URL must be an HTTPS backend origin without path, query or credentials.');api=url.origin;}
const out=resolve(root,'dist','vercel');mkdirSync(out,{recursive:true});
for(const name of ['index.html','styles.css','review.css','workspace.css','app.js','review.js','demo-data.json'])copyFileSync(resolve(root,'frontend',name),resolve(out,name));
writeFileSync(resolve(out,'config.js'),`window.MEETING_CONFIG = ${JSON.stringify({apiBaseUrl:api})};\n`);
console.log('Static frontend ready: dist/vercel; API keys are not part of this build.');
