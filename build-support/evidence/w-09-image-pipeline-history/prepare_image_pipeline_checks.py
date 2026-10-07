from pathlib import Path
r=Path.cwd()
for name in ('finish_native_chart_checks.py','audit_native_chart_legacy.py'):
    data=(r/'out/campaign'/name).read_text().replace('6cabd2c30ccdad1d97423dfaea643574cb6f840b','e503d290a2c905918abf04e71d85a38642458d1d').replace('native-chart','image-pipeline').replace('native_chart','image_pipeline').replace('tests/scene/chart_plot_oracle.py','tests/scene/image_fit_oracle.py')
    (r/'out/campaign'/name.replace('native_chart','image_pipeline')).write_text(data,encoding='utf-8',newline='\n')
