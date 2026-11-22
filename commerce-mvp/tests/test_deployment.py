import importlib.util
import os
import pathlib
import sqlite3
import subprocess
import sys
import tempfile
import io
from PIL import Image
from fastapi.testclient import TestClient
ROOT = pathlib.Path(__file__).resolve().parents[1]

def make():
    os.environ.update(AURS_ENV='development',AURS_ADMIN_PASSWORD='unique-nonpublic-test-password',AURS_SECRET_KEY='x'*64,AURS_COOKIE_SECURE='0',AURS_PUBLIC_ORIGIN='')
    os.environ['AURS_DATA_DIR']=tempfile.mkdtemp(prefix='aurs-persist-')
    spec=importlib.util.spec_from_file_location('aurs_deploy_app',ROOT/'app.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return TestClient(module.app),module

def login(c):
    return c.post('/api/admin/login',json={'password':'unique-nonpublic-test-password'},headers={'X-AURS-Request':'1'})

def test_security_headers_and_private_connector_flags():
    c,m=make()
    r=c.get('/')
    assert r.status_code==200
    assert "script-src 'self'" in r.headers['content-security-policy']
    assert r.headers['x-content-type-options']=='nosniff'
    assert c.get('/api/admin/integrations/readiness').status_code==401
    assert c.post('/api/admin/login',json={'password':'unique-nonpublic-test-password'}).status_code==403
    assert login(c).status_code==200
    os.environ['AURS_META_CAPI_TOKEN']='sentinel-no-leak'
    readiness=c.get('/api/admin/integrations/readiness')
    assert readiness.status_code==200
    assert readiness.json()['configured_flags']['meta_capi_token_set']
    assert readiness.json()['ad_spending_enabled'] is False
    assert 'sentinel-no-leak' not in readiness.text
    del os.environ['AURS_META_CAPI_TOKEN']
    assert c.get('/privacy').status_code==200
    assert b'PRE-LAUNCH DRAFT' in c.get('/privacy').content

def test_origin_rejection_and_manual_delete():
    c,m=make()
    assert login(c).status_code==200
    body={'full_name':'B2B Buyer','phone':'919876543210','city':'Tiruppur','quantity':200,'brand':'santram','accepted_privacy':True}
    r=c.post('/api/public/enquiries',json=body)
    assert r.status_code==201
    lid=r.json()['lead_id']
    assert c.delete(f'/api/admin/leads/{lid}',headers={'X-AURS-Request':'1','Origin':'https://evil.invalid'}).status_code==403
    assert c.delete(f'/api/admin/leads/{lid}',headers={'X-AURS-Request':'1'}).status_code==204
    assert c.get('/api/admin/leads').json()==[]

def test_no_publish_without_media_and_persistent_sqlite():
    c,m=make()
    login(c)
    pid=1
    assert c.patch(f'/api/admin/products/{pid}',json={'approval':'approved','is_public':True},headers={'X-AURS-Request':'1'}).status_code==422
    png=io.BytesIO();Image.new('RGB',(22,22),(20,70,80)).save(png,format='PNG')
    result=c.post(f'/api/admin/products/{pid}/image',files={'file':('approved.png',png.getvalue(),'image/png')},headers={'X-AURS-Request':'1'})
    assert result.status_code==200
    assert c.get(f'/api/public/media/{pid}').status_code==404
    assert c.patch(f'/api/admin/products/{pid}',json={'approval':'approved','is_public':True},headers={'X-AURS-Request':'1'}).status_code==200
    data_dir=os.environ['AURS_DATA_DIR']
    with sqlite3.connect(pathlib.Path(data_dir)/'commerce.sqlite3') as db:
        assert db.execute("select count(*) from products where is_public=1").fetchone()[0]==1
    assert (pathlib.Path(data_dir)/'promo_images').is_dir()

def test_production_fail_closed():
    with tempfile.TemporaryDirectory() as path:
        env={**os.environ,'AURS_ENV':'production','AURS_ADMIN_PASSWORD':'unique-nonpublic-test-password','AURS_SECRET_KEY':'x'*64,'AURS_DATA_DIR':path,'AURS_COOKIE_SECURE':'0','AURS_PUBLIC_ORIGIN':'https://example.invalid'}
        p=subprocess.run([sys.executable,'-c','import app'],cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        assert p.returncode!=0
        assert b'AURS_COOKIE_SECURE=1' in p.stderr

def test_encrypted_backup_restore():
    c,m=make();login(c)
    sys.path.insert(0,str(ROOT))
    from scripts.backup import backup,restore
    data=pathlib.Path(os.environ['AURS_DATA_DIR'])
    os.environ['AURS_BACKUP_PASSPHRASE']='strong-offline-backup-passphrase-2026'
    with tempfile.TemporaryDirectory() as temp:
        encrypted=pathlib.Path(temp)/'one.aurs-backup'
        backup(data,encrypted)
        raw=encrypted.read_bytes()
        assert raw.startswith(b'AURS-ENC-BACKUP-v1\n')
        assert b'SQLite format 3' not in raw
        recover=pathlib.Path(temp)/'recover'
        restore(recover,encrypted,True)
        with sqlite3.connect(recover/'commerce.sqlite3') as d:
            assert d.execute('pragma integrity_check').fetchone()[0]=='ok'
        import pytest
        with pytest.raises(RuntimeError): restore(recover,encrypted,True)
    del os.environ['AURS_BACKUP_PASSPHRASE']
