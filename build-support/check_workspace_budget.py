"""Read-only Windows coordinator check of both existing campaign output roots."""
import argparse
import json
import os
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--action',choices=('build','test','package','inspect'),default='inspect')
    args=parser.parse_args()
    if os.name!='nt': raise ValueError('run this coordinator in the admitted Windows checkout')
    budget=json.loads((ROOT/'build-support/campaign-workspace.json').read_text(encoding='utf-8'))
    output=(ROOT/'out').resolve(strict=True)
    if output!=ROOT/'out': raise ValueError('unexpected output root')
    windows=sum(p.stat().st_size for p in output.rglob('*') if p.is_file() and not p.is_symlink())
    native=budget['linux_root']
    if native!='/home/ir4runner/.cache/syspane/campaign-229a498': raise ValueError('unadmitted native root')
    linux=int(subprocess.check_output(['wsl','-d',budget['linux_distribution'],'-u',budget['linux_user'],'--','du','-sb',native],text=True).split()[0])
    reserved=budget['reserved_growth'][args.action]
    result={'action':args.action,'maximum_bytes':budget['maximum_bytes'],'checkout_out_bytes':windows,
        'linux_campaign_bytes':linux,'reserved_growth_bytes':reserved,'status':'pass' if windows+linux+reserved<=budget['maximum_bytes'] else 'stop',
        'scope':'Preflight reservation, not an OS quota or continuous filesystem monitor.'}
    print(json.dumps(result,indent=2))
    if result['status']!='pass':raise SystemExit(1)
if __name__=='__main__':main()
