"""AES-GCM envelope encryption for local development."""
import base64,json,os,secrets
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
class VaultError(Exception): pass
class Vault:
    def __init__(self,root:Path,master_key:str,max_bytes:int=10*1024*1024):
        if not master_key: raise VaultError("QUANTUMSHIELD_MASTER_KEY is required")
        try: key=base64.urlsafe_b64decode(master_key.encode())
        except Exception as exc: raise VaultError("master key must be URL-safe base64") from exc
        if len(key)!=32: raise VaultError("master key must decode to 32 bytes")
        self.root=root; self.root.mkdir(parents=True,exist_ok=True); self.kek=key; self.max_bytes=max_bytes
    def encrypt(self,filename:str,data:bytes)->dict:
        if len(data)>self.max_bytes: raise VaultError("file exceeds configured size limit")
        oid=secrets.token_hex(16); aad=oid.encode(); dek=AESGCM.generate_key(256)
        dn=os.urandom(12); wn=os.urandom(12)
        ct=AESGCM(dek).encrypt(dn,data,aad); wrapped=AESGCM(self.kek).encrypt(wn,dek,aad)
        name=Path(filename).name[:180] or "file.bin"
        envelope={"v":1,"id":oid,"name":name,"dn":base64.b64encode(dn).decode(),"wn":base64.b64encode(wn).decode(),"dek":base64.b64encode(wrapped).decode(),"ct":base64.b64encode(ct).decode()}
        (self.root/f"{oid}.json").write_text(json.dumps(envelope),encoding="utf-8")
        return {"object_id":oid,"filename":name,"bytes":len(data),"algorithm":"AES-256-GCM"}
    def decrypt(self,oid:str)->tuple[str,bytes]:
        if len(oid)!=32 or not oid.isalnum(): raise VaultError("invalid object identifier")
        p=self.root/f"{oid}.json"
        if not p.exists(): raise VaultError("vault object not found")
        e=json.loads(p.read_text(encoding="utf-8"))
        if e.get("id")!=oid or e.get("v")!=1: raise VaultError("invalid envelope")
        aad=oid.encode()
        dek=AESGCM(self.kek).decrypt(base64.b64decode(e["wn"]),base64.b64decode(e["dek"]),aad)
        data=AESGCM(dek).decrypt(base64.b64decode(e["dn"]),base64.b64decode(e["ct"]),aad)
        return e["name"],data
