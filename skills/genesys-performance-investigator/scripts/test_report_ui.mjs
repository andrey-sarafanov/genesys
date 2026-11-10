// Pure JavaScript unit test with a minimal DOM stub. This is NOT a browser/layout test.
import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const path=process.argv[2];
if(!path) throw new Error('Usage: node test_report_ui.mjs <generated-report.html>');
const page=fs.readFileSync(path,'utf8');
const data=page.match(/<script id="report-data" type="application\/json">([\s\S]*?)<\/script>/)[1];
const script=page.match(/<script>\s*([\s\S]*?)<\/script>/)[1];
assert(!/<(?:script|link)[^>]+(?:src|href)=["']https?:/i.test(page));
class Element {
  constructor(){this.value='';this.textContent='';this.innerHTML='';this.children=[];this.handlers={};this.classList={add(){}};}
  replaceChildren(...children){this.children=children;this.value=children[0]?.value??'';}
  addEventListener(name,fn){this.handlers[name]=fn;}
  click(){this.clicked=true;}
}
const elements=new Map();
const get=id=>{if(!elements.has(id))elements.set(id,new Element());return elements.get(id);};
get('report-data').textContent=data;
let exported,printCalled=false;
const context=vm.createContext({document:{getElementById:get,createElement:()=>new Element()},
  Blob,URL:{createObjectURL(blob){exported=blob;return 'blob:unit-test';},revokeObjectURL(){}},
  setTimeout:fn=>fn(),window:{print(){printCalled=true;}},console});
vm.runInContext(script,context,{timeout:3000});
assert(get('demo').innerHTML.includes('Synthetic demonstration'));
assert(get('chart').innerHTML.includes('<svg'));
assert(get('summary').innerHTML.includes('Customer care'));
get('entity').value='demo-q2';get('entity').handlers.change();
assert(get('table').innerHTML.includes('Billing'));
assert(!get('table').innerHTML.includes('Customer care'));
get('metric').value='Service level %';get('metric').handlers.change();
assert(get('table').innerHTML.includes('pp'));
get('csv').handlers.click();
assert((await exported.text()).includes('Billing'));
get('print').handlers.click();assert(printCalled);
get('dataset').value='queue-PT30M';get('dataset').handlers.change();
assert(get('chart').innerHTML.includes('<svg'));
get('dataset').value='flow-P1D';get('dataset').handlers.change();
assert(get('table').innerHTML.includes('Main IVR'));
assert(get('metric').children.some(e=>e.value==='Average flow seconds'));
get('entity').value='missing';get('entity').handlers.change();
assert(get('table').innerHTML.includes('No returned data'));
console.log('UI logic passed: initial render, entity/media structure, metric delta, dataset switch, flow view, empty state, CSV and print. Visual layout unverified.');
