from pathlib import Path
r=Path.cwd()
for name in ('finish_chart_history_checks.py','audit_chart_history_legacy.py'):
    data=(r/'out/campaign'/name).read_text().replace('b3d7bf22f696cc00e615a7686298ea63f952b29e','6cabd2c30ccdad1d97423dfaea643574cb6f840b').replace('chart-history','native-chart').replace('chart_history','native_chart')
    if name.startswith('finish'):
        data=data.replace("commands += [[python,'-X','utf8','-m','unittest'", "commands += [[python,'-X','utf8','tests/scene/chart_plot_oracle.py','--check']]\ncommands += [[python,'-X','utf8','-m','unittest'")
    (r/'out/campaign'/name.replace('chart_history','native_chart')).write_text(data,encoding='utf-8',newline='\n')
