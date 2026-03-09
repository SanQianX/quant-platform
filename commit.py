# -*- coding: utf-8 -*-
import subprocess
import os
os.chdir('F:/quant-platform')
result = subprocess.run(['git', 'add', '-A'], capture_output=True)
result = subprocess.run(['git', 'commit', '-m', '''feat: 添加期权数据查询API (迭代#27)

- 新增 GET /api/options/{code} - 期权列表查询
- 新增 GET /api/options/{code}/quote - 期权实时行情
- 使用模拟数据实现'''], capture_output=True, text=True)
print(result.stdout)
print(result.stderr)
