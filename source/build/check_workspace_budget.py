"""Read-only Windows coordinator check of both existing campaign output roots."""
import argparse
import json
import os
from pathlib import Path, PurePosixPath
import subprocess

ROOT=Path(__file__).resolve().parents[2]
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--action',choices=('build','test','package','inspect'),default='inspect')
    args=parser.parse_args()
    if os.name!='nt': raise ValueError('run this coordinator in the admitted Windows checkout')
    budget=json.loads((ROOT/'source/build/campaign-workspace.json').read_text(encoding='utf-8'))
    output=(ROOT/'out').resolve(strict=True)
    if output!=ROOT/'out': raise ValueError('unexpected output root')
    archive=output/'evidence'
    windows=retained=0
    for p in output.rglob('*'):
        if not p.is_file() or p.is_symlink():continue
        if p.is_relative_to(archive):retained+=p.stat().st_size
        else:windows+=p.stat().st_size
    binding=output/'campaign/workspace.json'
    if not binding.is_file():raise ValueError('Create out/campaign/workspace.json from source/build/workspace.example.json and explicitly name the admitted non-root Linux workspace.')
    local=json.loads(binding.read_text(encoding='utf-8'));native=local['linux_root'];user=local['linux_user']
    allowed=PurePosixPath('/home')/user/'.cache/syspane';path=PurePosixPath(native)
    if user in ('','root') or '/' in user or '\\' in user or '..' in path.parts or path==allowed or not path.is_relative_to(allowed):raise ValueError('unadmitted native root or privileged user')
    linux=int(subprocess.check_output(['wsl','-d',local['linux_distribution'],'-u',user,'--','du','-sb',native],text=True).split()[0])
    reserved=budget['reserved_growth'][args.action]
    result={'action':args.action,'maximum_bytes':budget['maximum_bytes'],'checkout_out_bytes':windows,
        'linux_campaign_bytes':linux,'retained_local_evidence_bytes':retained,'reserved_growth_bytes':reserved,'status':'pass' if windows+linux+reserved<=budget['maximum_bytes'] else 'stop',
        'scope':'Active-output reservation, not an OS quota. Retained evidence is reported separately, preserving its previous exclusion before relocation.'}
    print(json.dumps(result,indent=2))
    if result['status']!='pass':raise SystemExit(1)
if __name__=='__main__':main()
