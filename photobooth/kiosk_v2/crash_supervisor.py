"""Opt-in exited-child restart budget; no kill/replay or payment authority."""
import json,time,math
from pathlib import Path
from photobooth.kiosk_v2.recovery import checked_path
from photobooth.manifest_io import write_json_atomic

CRASH_CODES=frozenset({1,-11,-6,139,134,3221225477})


def safe_context(env, *, child_exited):
    if (child_exited is not True or env.get('PHOTOBOOTH_V2_CHECKOUT_SANDBOX')!='1'
            or env.get('MEONG_QRIS_MODE')!='sandbox' or env.get('PHOTOBOOTH_LOCAL_ONLY')!='1'
            or any(env.get('PHOTOBOOTH_V2_'+key)!='0' for key in ('PRINT','DRIVE'))
            or any(env.get(key) for key in ('MIDTRANS_SERVER_KEY','MIDTRANS_MERCHANT_ID'))):
        return False
    try:
        if not Path(env['MEONG_QRIS_JOURNAL']).is_absolute():return False
        journal=checked_path(env['MEONG_QRIS_JOURNAL'])
        if journal.exists():
            if journal.stat().st_size>65536:return False
            data=json.loads(journal.read_text())
            if (data.get('version')!=1 or data.get('context')!={'mode':'sandbox',
                    'booth_id':env['MEONG_QRIS_BOOTH_ID'],'endpoint':env['MEONG_QRIS_API_URL'].rstrip('/')}):
                return False
        return True
    except (OSError,ValueError,KeyError,TypeError):
        return False


class CrashBudget:
    def __init__(self,path,*,clock=time.time):
        self.path=checked_path(path);self.clock=clock

    def reserve(self,exit_code,env,*,child_exited):
        if type(exit_code) is not int or exit_code not in CRASH_CODES or not safe_context(env,child_exited=child_exited):
            return None
        now=self.clock();attempts=[]
        if not math.isfinite(now) or now<0:raise RuntimeError('Restart clock requires review')
        if self.path.exists():
            if self.path.stat().st_size>4096:raise RuntimeError('Restart budget requires review')
            data=json.loads(self.path.read_text())
            if (data.get('version')!=1 or type(data.get('attempts')) is not list
                    or len(data['attempts'])>3 or type(data.get('observed_at')) not in (int,float)
                    or not math.isfinite(data['observed_at'])
                    or now<data['observed_at']):
                raise RuntimeError('Restart budget requires review')
            if any(type(t) not in (int,float) or not 0<=now-t for t in data['attempts']):
                raise RuntimeError('Restart clock requires review')
            attempts=[t for t in data['attempts'] if now-t<600]
        if len(attempts)>=3:return None
        cooldown=5*2**len(attempts)
        attempts.append(now)
        write_json_atomic(self.path,{'version':1,'attempts':attempts,'observed_at':now})
        return cooldown
