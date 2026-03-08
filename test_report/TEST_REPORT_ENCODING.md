# quant_platform 编码问题分析报告

**测试工程师**: 测试工程师
**测试时间**: 2026-03-08 21:59+
**问题**: 前端页面编码问题
**状态**: 🔴 **需要修复**

---

## 问题分析

### 🔴 根本原因：HTML文件编码问题

**问题确认**：
1. **响应头缺少编码**：`Content-Type: text/html` (缺少 `charset=utf-8`)
2. **源文件编码错误**：index.html 文件本身不是UTF-8编码

### 证据

**1. 响应头检查**：
```
Content-Type: text/html
```
缺少 `charset=utf-8`

**2. 源文件读取测试**：
```
Get-Content "index.html" -Encoding UTF8
```
输出显示乱码，证明文件不是UTF-8编码

**3. 页面显示问题**：
- 标题显示：`��???????��????13??��`
- 正常应为：`量化数据平台`

---

## 修复方案

### 方案1：重新保存HTML文件为UTF-8编码

1. 用文本编辑器（如VS Code）打开 `F:\quant-platform\frontend\index.html`
2. 选择 "另存为" -> 选择 "UTF-8" 编码
3. 保存文件

### 方案2：配置Vite添加响应头

在 `vite.config.js` 中添加：
```javascript
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    headers: {
      'Content-Type': 'text/html; charset=utf-8'
    },
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

### 方案3：使用构建版本

```bash
cd frontend
npm run build
# 然后用 Nginx 部署 dist 目录
```

---

## 影响范围

| 问题 | 影响 |
|------|------|
| 页面标题乱码 | 影响用户体验 |
| 中文字符乱码 | 影响数据展示 |
| 控制台警告 | 影响调试 |

---

## 测试结论

**🔴 需要修复**

**问题**：HTML文件编码 + Vite响应头配置

**修复优先级**：高

**修复后验证**：
1. 检查响应头：`Content-Type: text/html; charset=utf-8`
2. 检查页面标题正确显示
3. 检查所有中文正常显示
