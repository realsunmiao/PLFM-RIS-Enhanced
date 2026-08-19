# GitHub 推送指南

## 前置步骤

### 1. 在 GitHub 上创建仓库

1. 访问 https://github.com/new
2.  Repository name: `PLFM-RIS-Enhanced`
3.  Description: `RIS-enhanced PLFM phased array radar system with spacetime coding`
4.  选择 **Public** (公开) 或 **Private** (私有)
5.  **不要** 勾选 "Initialize this repository with a README"
6.  点击 **Create repository**

### 2. 获取仓库 URL

创建成功后,GitHub 会显示类似以下的 URL:
```
https://github.com/你的用户名/PLFM-RIS-Enhanced.git
```

复制这个 URL。

## 推送代码到 GitHub

打开命令行,执行以下命令:

```bash
# 进入项目目录
cd PLFM-RIS-Enhanced

# 添加远程仓库 (替换为你的实际 URL)
git remote add origin https://github.com/你的用户名/PLFM-RIS-Enhanced.git

# 验证远程仓库
git remote -v

# 推送到 GitHub
git push -u origin main
```

### 如果需要身份验证

首次推送时,GitHub 会要求输入用户名和密码:
- **Username**: 你的 GitHub 用户名
- **Password**: 使用 **Personal Access Token** (不是账户密码)

#### 如何生成 Personal Access Token

1. 访问 https://github.com/settings/tokens
2. 点击 **Generate new token (classic)**
3. 填写 Note (例如: "PLFM-RIS-Enhanced")
4. 选择权限: 至少勾选 **repo** (Full control of private repositories)
5. 点击 **Generate token**
6. **立即复制 token** (只显示一次!)
7. 在 Git 提示输入密码时,粘贴这个 token

## 验证推送

推送成功后,访问你的 GitHub 仓库页面:
```
https://github.com/你的用户名/PLFM-RIS-Enhanced
```

你应该能看到所有文件已上传。

## 常见问题

### Q1: 提示 "remote origin already exists"

**解决方法**:
```bash
# 删除现有远程仓库
git remote remove origin

# 重新添加
git remote add origin https://github.com/你的用户名/PLFM-RIS-Enhanced.git
```

### Q2: 推送被拒绝 (rejected)

**可能原因**: 远程仓库已有内容

**解决方法**:
```bash
# 强制推送 (谨慎使用,会覆盖远程内容)
git push -u origin main --force

# 或者先拉取再合并
git pull origin main --allow-unrelated-histories
git push -u origin main
```

### Q3: 认证失败

**检查项**:
1. URL 是否正确
2. Personal Access Token 是否有效
3. Token 是否有 repo 权限
4. Token 是否已过期

**重新配置认证**:
```bash
# Windows: 清除凭据缓存
git credential-manager erase

# 然后重新推送,会提示重新输入凭据
git push -u origin main
```

## 后续更新

以后修改代码后,使用以下命令推送更新:

```bash
# 添加修改的文件
git add .

# 提交
git commit -m "描述你的修改"

# 推送
git push
```

## 协作开发

如果要邀请他人协作:

1. 在 GitHub 仓库页面点击 **Settings** → **Collaborators**
2. 输入协作者的 GitHub 用户名
3. 对方接受邀请后即可贡献代码

或使用 **Pull Request** 流程:
1. 他人 Fork 你的仓库
2. 在他们的 Fork 上修改
3. 提交 Pull Request 到你的仓库
4. 你审查后合并

---

**祝推送顺利! 🚀**
