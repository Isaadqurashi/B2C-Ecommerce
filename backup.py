# backup.py

import os
import subprocess
import datetime

import firebase_admin
from firebase_admin import credentials, storage
from flask import current_app
from flask.cli import with_appcontext
import click

# Initialize Firebase Admin only once
def init_firebase():
    svc_key = current_app.config['FIREBASE_SERVICE_ACCOUNT']
    bucket_name = current_app.config['FIREBASE_BUCKET']
    cred = credentials.Certificate(svc_key)
    firebase_admin.initialize_app(cred, {
        'storageBucket': bucket_name
    })
    return storage.bucket()

def dump_and_upload():
    # PostgreSQL settings from Flask config
    pg_uri = current_app.config['SQLALCHEMY_DATABASE_URI']
    # parse uri: postgresql://user:pass@host:port/dbname
    parts = pg_uri.split('@')
    auth, host_db = parts[0].split('//')[1], parts[1]
    user, pwd = auth.split(':')
    host_port, dbname = host_db.rsplit('/', 1)
    host, port = host_port.split(':')

    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    dump_file = f"pg_backup_{ts}.sql"

    env = os.environ.copy()
    env['PGPASSWORD'] = pwd

    cmd = [
        'pg_dump',
        '-h', host,
        '-p', port,
        '-U', user,
        '-F', 'p',
        '-b',
        '-f', dump_file,
        dbname
    ]

    click.echo(f"Dumping DB to {dump_file}…")
    subprocess.run(cmd, check=True, env=env)
    bucket = init_firebase()
    blob = bucket.blob(f"backups/{dump_file}")
    click.echo(f"Uploading {dump_file} to Firebase Storage…")
    blob.upload_from_filename(dump_file)
    click.echo(f"✅ Uploaded to {current_app.config['FIREBASE_BUCKET']}/backups/{dump_file}")
    os.remove(dump_file)
    click.echo("Local dump removed.")

@click.command('backup-db')
@with_appcontext
def backup_db_command():
    """Dump Postgres and upload to Firebase Storage."""
    try:
        dump_and_upload()
    except subprocess.CalledProcessError as e:
        click.echo(click.style(f"❌ Backup failed: {e}", fg='red'))
    except Exception as ex:
        click.echo(click.style(f"❌ Unexpected error: {ex}", fg='red'))
