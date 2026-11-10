import base64,secrets
import pytest
from quantumshield.services.vault import Vault,VaultError

def master(): return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()

def test_roundtrip_and_filename_sanitization(tmp_path):
    v=Vault(tmp_path,master())
    result=v.encrypt("../../private.txt",b"test payload")
    name,data=v.decrypt(result["object_id"])
    assert name=="private.txt"
    assert data==b"test payload"

def test_missing_key_rejected(tmp_path):
    with pytest.raises(VaultError): Vault(tmp_path,"")

def test_modified_ciphertext_rejected(tmp_path):
    v=Vault(tmp_path,master())
    obj=v.encrypt("hello.txt",b"secret")
    import json
    path=tmp_path/f'{obj["object_id"]}.json'
    envelope=json.loads(path.read_text())
    envelope["ct"]="AAAA"+envelope["ct"][4:]
    path.write_text(json.dumps(envelope))
    with pytest.raises(Exception): v.decrypt(obj["object_id"])
