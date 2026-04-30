export class SaveSystem{
  constructor(key='hs_custom_v17',legacyKeys=['hs_custom_v07']){this.key=key;this.legacyKeys=legacyKeys}
  load(d={}){try{let raw=localStorage.getItem(this.key);if(!raw){for(const k of this.legacyKeys||[]){raw=localStorage.getItem(k);if(raw){localStorage.setItem(this.key,raw);break}}}return{...d,...JSON.parse(raw||'{}')}}catch{return{...d}}}
  save(d){localStorage.setItem(this.key,JSON.stringify(d))}
  reset(){localStorage.removeItem(this.key);for(const k of this.legacyKeys||[])localStorage.removeItem(k)}
}
