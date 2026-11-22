"""Smoke tests. Run: pytest -q tests"""
import os, pathlib, tempfile
from fastapi.testclient import TestClient
ROOT=pathlib.Path(__file__).resolve().parents[1]

def make_client():
    os.environ['AURS_ADMIN_PASSWORD']='test-password-long-unique-2026'
    os.environ['AURS_SECRET_KEY']='test-key-long-enough-to-sign-sessions-2026-aaaaaaaa'
    os.environ['AURS_DATA_DIR']=tempfile.mkdtemp(prefix='aurs-smoke-')
    import importlib.util
    spec=importlib.util.spec_from_file_location('aurs_test_app',ROOT/'app.py')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return TestClient(mod.app)

def test_public_brand_and_privacy_gate():
    c=make_client()
    assert c.get('/').status_code==200
    assert c.get('/brand/santram').status_code==200
    assert c.get('/_health').json()['ok']
    assert c.get('/api/public/products').json()==[]
    assert c.get('/api/admin/products').status_code==401
    assert c.get('/api/public/media/1').status_code==404

def test_admin_approval_and_lead_order_flow():
    c=make_client()
    assert c.post('/api/admin/login',json={'password':'wrong-password'},headers={'X-AURS-Request':'1'}).status_code==401
    assert c.post('/api/admin/login',json={'password':'test-password-long-unique-2026'},headers={'X-AURS-Request':'1'}).status_code==200
    hdr={'X-AURS-Request':'1'}
    assert len(c.get('/api/admin/products').json())==3
    assert c.patch('/api/admin/products/1',json={'approval':'pending','is_public':True},headers=hdr).status_code==422
    assert c.patch('/api/admin/products/1',json={'approval':'approved','is_public':True},headers=hdr).status_code==422
    import io
    from PIL import Image
    img=Image.new('RGB',(32,32),(35,55,80))
    f=io.BytesIO();img.save(f,'PNG')
    upload=c.post('/api/admin/products/1/image',files={'file':('promo.png',f.getvalue(),'image/png')},headers=hdr)
    assert upload.status_code==200
    assert c.get('/api/public/media/1').status_code==404
    assert c.patch('/api/admin/products/1',json={'approval':'approved','is_public':True},headers=hdr).status_code==200
    assert c.get('/api/public/media/1').status_code==200
    assert len(c.get('/api/public/products').json())==1
    body={'full_name':'Buyer A','phone':'919876543210','city':'Tiruppur','quantity':500,'brand':'santram','product_id':1,'message':'B2B request','accepted_privacy':True}
    lead=c.post('/api/public/enquiries',json=body)
    assert lead.status_code==201
    assert c.get('/api/admin/summary').json()['new_leads']==1
    order=c.post('/api/admin/orders',json={'name':'Buyer A','brand':'santram','quantity':500,'quoted_price':10000},headers=hdr)
    assert order.status_code==201 and order.json()['status']=='draft'
    assert c.patch('/api/admin/orders/'+str(order.json()['id']),json={'status':'production'},headers=hdr).status_code==200
    assert c.post('/api/admin/logout',headers=hdr).status_code==200
    assert c.get('/api/admin/summary').status_code==401
