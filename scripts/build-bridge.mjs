import {build} from 'esbuild';
import {readFile,writeFile} from 'node:fs/promises';
const result = await build({entryPoints:['viewer/bridge.js'],outfile:'viewer/bridge.bundle.js',bundle:true,minify:true,format:'iife',platform:'browser',target:'es2022',legalComments:'eof',metafile:true});
const packages = new Set(Object.keys(result.metafile.inputs).filter(p=>p.includes('node_modules/')).map(p=>{const rest=p.split('node_modules/').pop().split('/');return rest[0].startsWith('@')?rest.slice(0,2).join('/'):rest[0];}));
const notices = ['# Third-party notices','', 'The prebuilt viewer/bridge.bundle.js includes the following packages. Runtime Python uses the standard library.',''];
for(const name of [...packages].sort()) {
 const base='node_modules/'+name;
 const pkg=JSON.parse(await readFile(base+'/package.json','utf8'));
 notices.push('## '+name+' '+pkg.version,'','Declared license: '+pkg.license,'');
 let found=false;
 for(const file of ['LICENSE','LICENSE.md','LICENSE-MIT','LICENSE-APACHE','NOTICE','NOTICE.md'])try{const content=await readFile(base+'/'+file,'utf8');notices.push('### '+file,'',content,'');found=true;}catch{}
 if(!found)throw new Error('No license notice found for '+name);
}
await writeFile('THIRD_PARTY_NOTICES.md',notices.join('\n'));
console.log('Bundled official MCP Apps bridge; notices:',[...packages].join(', '));
