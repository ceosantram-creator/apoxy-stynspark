"""Single-worker server: SQLite + attached persistent image volume."""
import os
import uvicorn

if __name__ == '__main__':
    if os.environ.get('AURS_ENV','development') != 'production' and os.environ.get('AURS_STAGING_PREVIEW_ALLOW') != '1':
        raise SystemExit('Refusing network deployment: set AURS_ENV=production with HTTPS safeguards, or explicit AURS_STAGING_PREVIEW_ALLOW=1 for a private staging environment.')
    port = int(os.environ.get('PORT', '8000'))
    if port < 1 or port > 65535:
        raise ValueError('Invalid PORT')
    uvicorn.run('app:app', host='0.0.0.0', port=port, workers=1,
                proxy_headers=True,
                forwarded_allow_ips=os.environ.get('AURS_TRUSTED_PROXY_IPS', '127.0.0.1'))
