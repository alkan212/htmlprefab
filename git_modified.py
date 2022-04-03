import os
import subprocess
import re

data = "git status"
proc = subprocess.Popen(data, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
out, err = proc.communicate()
out_utf = out.decode("utf-8")

r2 = r"(?!modified:)(   .*)"
r = r"(modified:\s*)+(.*)\S"
m = re.compile(r2, re.MULTILINE)
a = m.finditer(out_utf)

command = "git add"

for i in m.findall(out_utf):
    command = command + " " + i.strip()
print(command)
os.system(command)

