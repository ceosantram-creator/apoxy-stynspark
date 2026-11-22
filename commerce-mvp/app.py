"""AURS Commerce Network — small self-hosted MVP.
All public assets are approval-gated. Private production artwork is never uploaded here.
"""
import csv
import io
import os
import re
import secrets
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Optional

from fastapi import FastAPI, Request, Response, HTTPException, UploadFile, File, Depends
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from urllib.parse import urlsplit
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from pydantic import BaseModel, Field, field_validator
from PIL import Image

ROOT = Path(__file__).resolve().parent
AURS_ENV = os.getenv('AURS_ENV','development').strip().lower()
PUBLIC_ORIGIN = os.getenv('AURS_PUBLIC_ORIGIN','').rstrip('/')
if AURS_ENV not in ('development','staging','production'):
    raise RuntimeError('AURS_ENV must be development, staging or production')
if PUBLIC_ORIGIN:
    parsed = urlsplit(PUBLIC_ORIGIN)
    if parsed.scheme not in ('http','https') or not parsed.netloc or parsed.path or parsed.query or parsed.fragment:
        raise RuntimeError('AURS_PUBLIC_ORIGIN must be a scheme and host only, e.g. https://example.com')
if AURS_ENV == 'production':
    if not PUBLIC_ORIGIN.startswith('https://'):
        raise RuntimeError('Production requires HTTPS AURS_PUBLIC_ORIGIN')
    if os.getenv('AURS_COOKIE_SECURE','0') != '1':
        raise RuntimeError('Production requires AURS_COOKIE_SECURE=1')
    if not os.path.isabs(os.getenv('AURS_DATA_DIR','')):
        raise RuntimeError('Production requires an absolute AURS_DATA_DIR on a persistent volume')
DATA = Path(os.getenv('AURS_DATA_DIR', str(ROOT / 'data'))).resolve()
DATA.mkdir(parents=True, exist_ok=True)
UPLOADS = DATA / 'promo_images'
UPLOADS.mkdir(parents=True, exist_ok=True)
DB = DATA / 'commerce.sqlite3'
COOKIE_SECURE = os.getenv('AURS_COOKIE_SECURE','0') == '1'
ADMIN_PASSWORD = os.getenv('AURS_ADMIN_PASSWORD', '')
SECRET_KEY = os.getenv('AURS_SECRET_KEY', '')
if len(ADMIN_PASSWORD) < 12 or len(SECRET_KEY) < 32:
    raise RuntimeError('Set AURS_ADMIN_PASSWORD (12+ chars) and AURS_SECRET_KEY (32+ chars) before starting.')
serializer = URLSafeTimedSerializer(SECRET_KEY, salt='aurs-admin-session-v1')
app = FastAPI(title='AURS Commerce Network', docs_url=None, redoc_url=None)
app.mount('/assets', StaticFiles(directory=ROOT / 'web'), name='assets')

@app.middleware('http')
async def safe_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; connect-src 'self'; form-action 'self'; "
        "object-src 'none'; frame-ancestors 'none'; base-uri 'self'"
    )
    if request.url.scheme == 'https' or AURS_ENV == 'production':
        response.headers['Strict-Transport-Security'] = 'max-age=31536000'
    if request.url.path.startswith('/api/admin/') or request.url.path.startswith('/api/public/enquiries'):
        response.headers['Cache-Control'] = 'no-store'
    return response

failures = {}
lead_window = {}
lock = Lock()


def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def conn():
    db = sqlite3.connect(DB, timeout=10)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    db.execute('PRAGMA journal_mode=WAL')
    db.execute('PRAGMA busy_timeout=10000')
    return db


def init_db():
    with conn() as d:
        d.executescript('''
        CREATE TABLE IF NOT EXISTS products(
            id INTEGER PRIMARY KEY AUTOINCREMENT, slug TEXT UNIQUE NOT NULL,
            brand TEXT NOT NULL, title_hi TEXT NOT NULL, title_en TEXT NOT NULL,
            category TEXT NOT NULL, description_hi TEXT NOT NULL DEFAULT '',
            description_en TEXT NOT NULL DEFAULT '', approval TEXT NOT NULL DEFAULT 'pending',
            is_public INTEGER NOT NULL DEFAULT 0, image_file TEXT, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS leads(
            id INTEGER PRIMARY KEY AUTOINCREMENT, full_name TEXT NOT NULL,
            phone TEXT NOT NULL, city TEXT NOT NULL, quantity INTEGER NOT NULL,
            product_id INTEGER, message TEXT NOT NULL, brand TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'new', consent INTEGER NOT NULL,
            created_at TEXT NOT NULL, FOREIGN KEY(product_id) REFERENCES products(id));
        CREATE TABLE IF NOT EXISTS orders(
            id INTEGER PRIMARY KEY AUTOINCREMENT, lead_id INTEGER,
            name TEXT NOT NULL, brand TEXT NOT NULL, quantity INTEGER NOT NULL,
            quoted_price REAL NOT NULL DEFAULT 0, status TEXT NOT NULL DEFAULT 'draft',
            note TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL,
            FOREIGN KEY(lead_id) REFERENCES leads(id));
        CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS pageviews(
            id INTEGER PRIMARY KEY AUTOINCREMENT, route TEXT NOT NULL, created_at TEXT NOT NULL);
        ''')
        samples = [
            ('quadflux-demo','santram','क्वाडफ्लक्स — डेमो कॉन्सेप्ट','QUADFLUX — Demo Concept', 'Hotfix + Velvet','केवल डेमो रिकॉर्ड; प्रचार के लिए अप्रूवल आवश्यक।','Demo placeholder, requires explicit approval before publishing.'),
            ('stellar-shift-demo','stynspark','स्टेलर शिफ्ट — डेमो कॉन्सेप्ट','STELLAR SHIFT — Demo Concept','Premium embellishment','प्रोडक्शन फाइल इस सिस्टम में नहीं है।','No production files stored in this system.'),
            ('aurs-motion-demo','aurs','मोशन वेव — डेमो कॉन्सेप्ट','MOTION WAVE — Demo Concept','Wearable innovation','विचार का डेमो; वास्तविक प्रोडक्ट नहीं।','Idea demonstration, not an actual product.'),
        ]
        if d.execute('SELECT COUNT(*) FROM products').fetchone()[0] == 0:
            for slug,brand,hi,en,category,desc_hi,desc_en in samples:
                d.execute('INSERT INTO products(slug,brand,title_hi,title_en,category,description_hi,description_en,created_at) VALUES(?,?,?,?,?,?,?,?)',
                          (slug,brand,hi,en,category,desc_hi,desc_en,now()))
        d.execute("INSERT OR IGNORE INTO settings(key,value) VALUES ('wa_phone','')")
        d.execute("INSERT OR IGNORE INTO settings(key,value) VALUES ('site_notice','Demo MVP — no live campaigns or payments connected')")

init_db()


def check_rate(bucket, key, count, window):
    t = time.monotonic()
    with lock:
        old = [x for x in bucket.get(key,[]) if t-x < window]
        old.append(t)
        bucket[key] = old
        return len(old) <= count


def admin_required(request: Request):
    token = request.cookies.get('aurs_admin_session')
    try:
        value = serializer.loads(token or '', max_age=12*3600)
        if value.get('role') != 'admin':
            raise ValueError('no role')
        return True
    except (BadSignature, SignatureExpired, ValueError):
        raise HTTPException(401, 'Administrator login required')


def csrf_guard(request: Request):
    if request.headers.get('X-AURS-Request') != '1':
        raise HTTPException(403, 'Missing request header')
    origin = request.headers.get('origin')
    expected = PUBLIC_ORIGIN or str(request.base_url).rstrip('/')
    if origin and origin.rstrip('/') != expected:
        raise HTTPException(403, 'Cross-origin request denied')


class Login(BaseModel):
    password: str


class Lead(BaseModel):
    full_name: str = Field(min_length=2,max_length=90)
    phone: str = Field(min_length=8,max_length=18)
    city: str = Field(min_length=2,max_length=80)
    brand: str
    quantity: int = Field(ge=1,le=10000000)
    message: str = Field(default='',max_length=600)
    product_id: Optional[int] = None
    accepted_privacy: bool
    trap: str = ''

    @field_validator('brand')
    @classmethod
    def valid_brand(cls, v):
        if v not in ('santram','stynspark','aurs'):
            raise ValueError('Invalid brand')
        return v


class ProductCreate(BaseModel):
    brand: str
    title_hi: str = Field(min_length=2,max_length=100)
    title_en: str = Field(min_length=2,max_length=100)
    category: str = Field(min_length=2,max_length=75)
    description_hi: str = Field(default='',max_length=400)
    description_en: str = Field(default='',max_length=400)

    @field_validator('brand')
    @classmethod
    def valid_brand(cls, v):
        if v not in ('santram','stynspark','aurs'):
            raise ValueError('Invalid brand')
        return v


class Approval(BaseModel):
    approval: str
    is_public: bool = False


class LeadUpdate(BaseModel):
    status: str


class OrderCreate(BaseModel):
    lead_id: Optional[int] = None
    name: str = Field(min_length=2,max_length=100)
    brand: str
    quantity: int = Field(ge=1,le=10000000)
    quoted_price: float = Field(ge=0,le=1000000000)
    note: str = Field(default='',max_length=400)


class OrderUpdate(BaseModel):
    status: str


class SettingsUpdate(BaseModel):
    wa_phone: str = Field(default='',max_length=17)


@app.get('/api/public/brands')
def brands():
    return [
        {'id':'santram','name':'SANTRAM INDUSTRIES','segment':'Garment Decoration • B2B'},
        {'id':'stynspark','name':'STYNSPARK','segment':'Premium Apparel & Design'},
        {'id':'aurs','name':'AURS','segment':'Lifestyle Innovation'},
    ]


@app.get('/api/public/products')
def public_products(brand: Optional[str]=None):
    with conn() as d:
        if brand:
            rows = d.execute("SELECT id,slug,brand,title_hi,title_en,category,description_hi,description_en,image_file FROM products WHERE approval='approved' AND is_public=1 AND brand=? ORDER BY id DESC", (brand,)).fetchall()
        else:
            rows = d.execute("SELECT id,slug,brand,title_hi,title_en,category,description_hi,description_en,image_file FROM products WHERE approval='approved' AND is_public=1 ORDER BY id DESC").fetchall()
        return [dict(r) for r in rows]


@app.get('/api/public/settings')
def public_settings():
    with conn() as d:
        number=d.execute("SELECT value FROM settings WHERE key='wa_phone'").fetchone()[0]
    return {'wa_phone':number}


@app.post('/api/public/enquiries',status_code=201)
def new_lead(model:Lead, request:Request):
    if model.trap:
        return {'ok':True}
    if not model.accepted_privacy:
        raise HTTPException(422, 'Consent required')
    if not re.fullmatch(r'\+?[0-9\- ]{8,18}', model.phone):
        raise HTTPException(422,'Phone must contain a valid numeric pattern')
    if not check_rate(lead_window,request.client.host if request.client else 'unknown', 10,3600):
        raise HTTPException(429,'Too many enquiries')
    with conn() as d:
        if model.product_id is not None:
            target=d.execute("SELECT id,brand FROM products WHERE id=? AND approval='approved' AND is_public=1",(model.product_id,)).fetchone()
            if not target or target['brand']!=model.brand:
                raise HTTPException(422,'Product not available')
        cur=d.execute('INSERT INTO leads(full_name,phone,city,quantity,product_id,message,brand,consent,created_at) VALUES(?,?,?,?,?,?,?,?,?)',
            (model.full_name.strip(),model.phone.strip(),model.city.strip(),model.quantity,model.product_id,model.message.strip(),model.brand,1,now()))
        return {'ok':True,'lead_id':cur.lastrowid,'message':'Enquiry saved; not yet an order.'}


@app.post('/api/public/view', status_code=204)
def pageview(request: Request):
    # Anonymous page tally only; no IP address, cookies, tracking pixels, or fingerprinting.
    origin = request.headers.get('origin')
    expected = PUBLIC_ORIGIN or str(request.base_url).rstrip('/')
    if origin and origin.rstrip('/') != expected:
        raise HTTPException(403,'Origin denied')
    with conn() as d:
        d.execute('INSERT INTO pageviews(route,created_at) VALUES(?,?)',(request.query_params.get('route','/')[:100], now()))
    return Response(status_code=204)


@app.post('/api/admin/login')
def login(model:Login,request:Request):
    csrf_guard(request)
    host=request.client.host if request.client else 'unknown'
    if not check_rate(failures,host,8,900):
        raise HTTPException(429,'Login attempt limit reached; retry later')
    if not secrets.compare_digest(model.password.encode(),ADMIN_PASSWORD.encode()):
        raise HTTPException(401,'Invalid password')
    result=JSONResponse({'ok':True})
    result.set_cookie('aurs_admin_session',serializer.dumps({'role':'admin','nonce':secrets.token_hex(8)}),
                      httponly=True,secure=COOKIE_SECURE,samesite='strict',max_age=12*3600,path='/')
    return result


@app.post('/api/admin/logout')
def logout(request:Request,_=Depends(admin_required)):
    csrf_guard(request)
    result=JSONResponse({'ok':True})
    result.delete_cookie('aurs_admin_session',path='/')
    return result


@app.get('/api/admin/session')
def session(_=Depends(admin_required)):
    return {'authenticated':True}


@app.get('/api/admin/summary')
def summary(_=Depends(admin_required)):
    with conn() as d:
        return {
            'new_leads':d.execute("SELECT COUNT(*) FROM leads WHERE status='new'").fetchone()[0],
            'all_leads':d.execute('SELECT COUNT(*) FROM leads').fetchone()[0],
            'products_pending':d.execute("SELECT COUNT(*) FROM products WHERE approval='pending'").fetchone()[0],
            'published_products':d.execute("SELECT COUNT(*) FROM products WHERE approval='approved' AND is_public=1").fetchone()[0],
            'orders_in_progress':d.execute("SELECT COUNT(*) FROM orders WHERE status NOT IN ('dispatched','cancelled')").fetchone()[0],
            'anonymous_pageviews':d.execute('SELECT COUNT(*) FROM pageviews').fetchone()[0]
        }


@app.get('/api/admin/products')
def all_products(_=Depends(admin_required)):
    with conn() as d:
        return [dict(r) for r in d.execute('SELECT * FROM products ORDER BY id DESC').fetchall()]


@app.post('/api/admin/products',status_code=201)
def create_product(model:ProductCreate,request:Request,_=Depends(admin_required)):
    csrf_guard(request)
    slug=re.sub('[^a-z0-9]+','-',model.title_en.lower()).strip('-')[:44] or 'concept'
    slug=f'{slug}-{secrets.token_hex(3)}'
    with conn() as d:
        c=d.execute('INSERT INTO products(slug,brand,title_hi,title_en,category,description_hi,description_en,created_at) VALUES(?,?,?,?,?,?,?,?)',
         (slug,model.brand,model.title_hi.strip(),model.title_en.strip(),model.category.strip(),model.description_hi.strip(),model.description_en.strip(),now()))
        return {'id':c.lastrowid,'slug':slug,'approval':'pending','is_public':False}


@app.patch('/api/admin/products/{product_id}')
def update_product(product_id:int,model:Approval,request:Request,_=Depends(admin_required)):
    csrf_guard(request)
    if model.approval not in ('pending','approved','rejected'):
        raise HTTPException(422,'Invalid approval status')
    if model.is_public and model.approval != 'approved':
        raise HTTPException(422,'Cannot publish unapproved artwork')
    with conn() as d:
        old=d.execute('SELECT image_file FROM products WHERE id=?',(product_id,)).fetchone()
        if not old:raise HTTPException(404,'No product')
        if model.is_public and not old['image_file']:
            raise HTTPException(422,'Upload an approved promotional image before publishing')
        d.execute('UPDATE products SET approval=?,is_public=? WHERE id=?',(model.approval,int(model.is_public),product_id))
    return {'ok':True}


@app.post('/api/admin/products/{product_id}/image')
async def upload_promo_image(product_id:int,request:Request,file:UploadFile=File(...),_=Depends(admin_required)):
    csrf_guard(request)
    content=await file.read(5*1024*1024+1)
    if len(content)>5*1024*1024: raise HTTPException(413,'Maximum 5MB image')
    try:
        im=Image.open(io.BytesIO(content));im.verify()
        im=Image.open(io.BytesIO(content))
        if im.format not in ('JPEG','PNG','WEBP') or im.width*im.height>20_000_000:
            raise ValueError('Unsupported image or large pixel count')
        im=im.convert('RGB')
        output=io.BytesIO();im.save(output,format='WEBP',quality=86,method=4)
    except Exception:
        raise HTTPException(422,'Valid JPG/PNG/WEBP needed')
    with conn() as d:
        old=d.execute('SELECT image_file FROM products WHERE id=?',(product_id,)).fetchone()
        if not old:raise HTTPException(404,'No product')
        filename=f'{secrets.token_hex(16)}.webp'
        (UPLOADS/filename).write_bytes(output.getvalue())
        d.execute('UPDATE products SET image_file=?,approval=?,is_public=0 WHERE id=?',(filename,'pending',product_id))
    if old['image_file']:
        (UPLOADS/old['image_file']).unlink(missing_ok=True)
    return {'ok':True,'approval':'pending','note':'New image automatically unpublishes product until re-approved.'}


@app.get('/api/public/media/{product_id}')
def approved_media(product_id:int):
    with conn() as d:
        row=d.execute("SELECT image_file FROM products WHERE id=? AND approval='approved' AND is_public=1",(product_id,)).fetchone()
    if not row or not row['image_file']:raise HTTPException(404,'No approved public media')
    return FileResponse(UPLOADS/row['image_file'],media_type='image/webp',headers={'Cache-Control':'public,max-age=300'})


@app.get('/api/admin/media/{product_id}')
def admin_media(product_id:int,_=Depends(admin_required)):
    with conn() as d:
        row=d.execute('SELECT image_file FROM products WHERE id=?',(product_id,)).fetchone()
    if not row or not row['image_file']:raise HTTPException(404,'No media')
    return FileResponse(UPLOADS/row['image_file'],media_type='image/webp',headers={'Cache-Control':'no-store'})


@app.get('/api/admin/leads')
def leads(_=Depends(admin_required)):
    with conn() as d:
        return [dict(r) for r in d.execute('SELECT * FROM leads ORDER BY id DESC LIMIT 1000').fetchall()]


@app.patch('/api/admin/leads/{lead_id}')
def change_lead(lead_id:int,model:LeadUpdate,request:Request,_=Depends(admin_required)):
    csrf_guard(request)
    if model.status not in ('new','contacted','qualified','quoted','closed','lost'):
        raise HTTPException(422,'Invalid status')
    with conn() as d:
        c=d.execute('UPDATE leads SET status=? WHERE id=?',(model.status,lead_id))
        if not c.rowcount:raise HTTPException(404,'No lead')
    return {'ok':True}


@app.get('/api/admin/orders')
def orders(_=Depends(admin_required)):
    with conn() as d:
        return [dict(r) for r in d.execute('SELECT * FROM orders ORDER BY id DESC LIMIT 1000').fetchall()]


@app.post('/api/admin/orders',status_code=201)
def new_order(model:OrderCreate,request:Request,_=Depends(admin_required)):
    csrf_guard(request)
    if model.brand not in ('santram','stynspark','aurs'):
        raise HTTPException(422,'Invalid brand')
    with conn() as d:
        if model.lead_id is not None and not d.execute('SELECT 1 FROM leads WHERE id=?',(model.lead_id,)).fetchone():
            raise HTTPException(422,'Lead missing')
        c=d.execute('INSERT INTO orders(lead_id,name,brand,quantity,quoted_price,note,created_at) VALUES(?,?,?,?,?,?,?)',
         (model.lead_id,model.name.strip(),model.brand,model.quantity,model.quoted_price,model.note,now()))
        return {'id':c.lastrowid,'status':'draft','message':'Draft order only; customer has not confirmed.'}


@app.patch('/api/admin/orders/{order_id}')
def change_order(order_id:int,model:OrderUpdate,request:Request,_=Depends(admin_required)):
    csrf_guard(request)
    if model.status not in ('draft','approved','production','ready','dispatched','cancelled'):
        raise HTTPException(422,'Invalid status')
    with conn() as d:
        c=d.execute('UPDATE orders SET status=? WHERE id=?',(model.status,order_id))
        if not c.rowcount:raise HTTPException(404,'No order')
    return {'ok':True}


@app.get('/api/admin/settings')
def get_settings(_=Depends(admin_required)):
    with conn() as d:
        return dict(d.execute('SELECT key,value FROM settings').fetchall())


@app.put('/api/admin/settings')
def set_settings(model:SettingsUpdate,request:Request,_=Depends(admin_required)):
    csrf_guard(request)
    digits=re.sub('[^0-9]','',model.wa_phone)
    if digits and not (10<=len(digits)<=15):raise HTTPException(422,'WhatsApp number must be 10–15 digits incl. country code')
    with conn() as d:
        d.execute("INSERT INTO settings(key,value) VALUES ('wa_phone',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",(digits,))
    return {'ok':True,'wa_phone':digits}


@app.get('/api/admin/integrations/readiness')
def integrations_readiness(_=Depends(admin_required)):
    # No token, ID or account value is returned to the browser. Configure secrets only in host manager.
    flags = {
        'meta_ad_account_id_set': bool(os.getenv('AURS_META_AD_ACCOUNT_ID','')),
        'meta_pixel_id_set': bool(os.getenv('AURS_META_PIXEL_ID','')),
        'meta_capi_token_set': bool(os.getenv('AURS_META_CAPI_TOKEN','')),
        'whatsapp_phone_id_set': bool(os.getenv('AURS_WA_PHONE_NUMBER_ID','')),
        'whatsapp_access_token_set': bool(os.getenv('AURS_WA_ACCESS_TOKEN','')),
        'whatsapp_app_secret_set': bool(os.getenv('AURS_WA_APP_SECRET','')),
        'whatsapp_verify_token_set': bool(os.getenv('AURS_WA_VERIFY_TOKEN','')),
    }
    return {
        'status': 'configuration-only',
        'connectors_live': False,
        'pixels_active': False,
        'webhooks_active': False,
        'whatsapp_auto_messages': False,
        'ad_spending_enabled': False,
        'configured_flags': flags,
        'notice': 'No network integrations are enabled. Do not treat configured flags as verified Meta connectivity.'
    }

@app.delete('/api/admin/leads/{lead_id}', status_code=204)
def delete_lead(lead_id:int, request:Request, _=Depends(admin_required)):
    csrf_guard(request)
    # Manual erasure endpoint; refuse when financial/order records still reference the lead.
    with conn() as d:
        if d.execute('SELECT 1 FROM orders WHERE lead_id=? LIMIT 1',(lead_id,)).fetchone():
            raise HTTPException(409,'Lead is linked to an order; review retention obligations first')
        c=d.execute('DELETE FROM leads WHERE id=?',(lead_id,))
        if not c.rowcount:raise HTTPException(404,'No lead')
    return Response(status_code=204)

@app.get('/api/admin/export/leads.csv')
def export_leads(_=Depends(admin_required)):
    with conn() as d:
        rows=[dict(r) for r in d.execute('SELECT * FROM leads ORDER BY id DESC').fetchall()]
    s=io.StringIO(); cols=['id','full_name','phone','city','quantity','product_id','message','brand','status','consent','created_at']
    w=csv.DictWriter(s,fieldnames=cols);w.writeheader()
    # Prevent spreadsheet formula injection when exporting user-entered text.
    for item in rows:
        for k,v in item.items():
            if isinstance(v,str) and v.lstrip().startswith(('=','+','-','@')):
                item[k]="'"+v
        w.writerow(item)
    return Response(s.getvalue(),media_type='text/csv',headers={'Content-Disposition':'attachment; filename="aurs_leads.csv"','Cache-Control':'no-store'})


@app.get('/_health')
def health():return {'ok':True,'service':'AURS Commerce Network'}


@app.get('/')
@app.get('/brand/{slug}')
@app.get('/product/{slug}')
@app.get('/admin')
def index(slug:str=''):
    return FileResponse(ROOT/'web'/'index.html',headers={'Cache-Control':'no-store','X-Content-Type-Options':'nosniff'})


@app.get('/privacy')
def privacy():
    return FileResponse(ROOT/'web'/'privacy.html',headers={'Cache-Control':'no-store'})
