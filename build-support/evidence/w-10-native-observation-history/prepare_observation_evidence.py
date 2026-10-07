from pathlib import Path
r=Path(__file__).resolve().parents[2]
s=(r/'out/campaign/archive_creation.py').read_text().replace('w-10-widget-creation','w-10-native-observation')
s=s.replace("('LARGE-COMMANDS-DIAGNOSTIC',","('NATIVE-OBSERVATION','EDITOR-OBSERVATION','LARGE-COMMANDS-DIAGNOSTIC',")
s=s.replace("if v['outcome']=='pass':assert not changed","if v['outcome'] in ('pass','observed'):assert not changed")
(r/'out/campaign/archive_observation.py').write_text(s,encoding='utf-8',newline='\n')
s=(r/'out/campaign/finish_creation_checks.py').read_text().replace('w-10-widget-creation-','w-10-native-observation-').replace('8ecf403ebef7622c967f10b90d337d6c3d7037de','066657a89472b0476e3d30a1a1d51a944c88789b')
(r/'out/campaign/finish_observation_checks.py').write_text(s,encoding='utf-8',newline='\n')
