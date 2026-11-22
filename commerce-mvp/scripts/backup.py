"""Manual encrypted ZIP backup/restore. NEVER store passphrase in repo or logs.

Usage:
  AURS_DATA_DIR=/data AURS_BACKUP_PASSPHRASE=... python scripts/backup.py backup --output /secure/aurs_2026.aurs-backup
  AURS_DATA_DIR=/data AURS_BACKUP_PASSPHRASE=... python scripts/backup.py restore --input /secure/aurs_2026.aurs-backup --apply

Restore refuses non-empty data directory. Always test offline before production.
"""
from __future__ import annotations
import argparse
import base64
import io
import os
import pathlib
import secrets
import sqlite3
import tempfile
import zipfile
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

HEADER = b'AURS-ENC-BACKUP-v1\n'

def cipher(salt: bytes) -> Fernet:
    password = os.environ.get('AURS_BACKUP_PASSPHRASE','')
    if len(password) < 20:
        raise RuntimeError('Set AURS_BACKUP_PASSPHRASE to a private 20+ character value')
    key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=600_000).derive(password.encode('utf-8'))
    return Fernet(base64.urlsafe_b64encode(key))

def backup(data_dir: pathlib.Path, dest: pathlib.Path):
    database = data_dir/'commerce.sqlite3'
    if not database.is_file():
        raise RuntimeError('Database missing; not an initialized deployment')
    if dest.is_relative_to(data_dir) or dest.exists():
        raise RuntimeError('Backup destination must be outside live DATA and not already exist')
    with tempfile.TemporaryDirectory() as td:
        snap = pathlib.Path(td)/'commerce.sqlite3'
        source = sqlite3.connect(f'file:{database}?mode=ro', uri=True)
        try:
            with sqlite3.connect(snap) as target:
                source.backup(target)
        finally:
            source.close()
        memory = io.BytesIO()
        with zipfile.ZipFile(memory,'w',compression=zipfile.ZIP_DEFLATED) as z:
            z.write(snap,'commerce.sqlite3')
            for img in sorted((data_dir/'promo_images').glob('*.webp')):
                if img.is_file():
                    z.write(img,f'promo_images/{img.name}')
        salt=secrets.token_bytes(16)
        ciphertext=HEADER+salt+cipher(salt).encrypt(memory.getvalue())
        dest.parent.mkdir(parents=True,exist_ok=True)
        fd=os.open(dest,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'wb') as f: f.write(ciphertext)
    print(f'Encrypted backup created: {dest} (NO passphrase stored)')

def restore(data_dir:pathlib.Path,src:pathlib.Path,apply:bool):
    if not apply:
        raise RuntimeError('Refusing restore without --apply; do this on offline empty data directory')
    if data_dir.exists() and any(data_dir.iterdir()):
        raise RuntimeError('Restore destination must be an EMPTY directory; never overwrite running database')
    raw=src.read_bytes()
    if not raw.startswith(HEADER) or len(raw)<len(HEADER)+17:
        raise RuntimeError('Not an AURS encrypted backup')
    n=len(HEADER); salt=raw[n:n+16]
    payload=cipher(salt).decrypt(raw[n+16:])
    with zipfile.ZipFile(io.BytesIO(payload)) as z:
        members=z.namelist()
        for name in members:
            parts=pathlib.PurePosixPath(name).parts
            if (not parts or '..' in parts or parts[0] not in ('commerce.sqlite3','promo_images')
                or name.startswith('/') or ('promo_images' in parts and (len(parts)!=2 or not name.endswith('.webp')))):
                raise RuntimeError(f'Unsafe path in archive: {name}')
        if 'commerce.sqlite3' not in members:
            raise RuntimeError('No database in backup')
        data_dir.mkdir(parents=True,exist_ok=True)
        z.extractall(data_dir)
    print(f'Restored offline to {data_dir}; run integrity checks before startup')

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('action',choices=['backup','restore'])
    p.add_argument('--output',type=pathlib.Path);p.add_argument('--input',type=pathlib.Path)
    p.add_argument('--apply',action='store_true');a=p.parse_args()
    dat=pathlib.Path(os.environ.get('AURS_DATA_DIR','./data')).resolve()
    if a.action=='backup':
        if not a.output:p.error('backup needs --output')
        backup(dat,a.output.resolve())
    else:
        if not a.input:p.error('restore needs --input')
        restore(dat,a.input.resolve(),a.apply)
