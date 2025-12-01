# HCHSCASEY GitHub Integration

**Production webhook server** for automating documentation sync and workflow orchestration across GlacierEQ repositories.

## 🎯 App Details

- **App ID**: 1395110
- **Client ID**: Iv23li379QcqaLJI8Vo1
- **Owner**: @GlacierEQ
- **Public URL**: https://github.com/apps/hchscasey-github-integration

## 📦 Installation

### 1. Install App on Repositories

Visit: https://github.com/apps/hchscasey-github-integration/installations/new

**Recommended repos for initial installation:**
- apex-command-center (MCP integration hub)
- SUPERLUMINAL_CASE_MATRIX (private docs)
- HCHS_SUPERLUMINAL_CASE_MATRIX (public docs)
- FILEBOSS (file management)
- unified-browser-automation
- MEGA-PDF

### 2. Setup Environment

```bash
cd github-app
cp .env.example .env
# Edit .env with your credentials
```

### 3. Install Dependencies

```bash
npm install
```

### 4. Run Locally (with Smee.io for testing)

```bash
# Terminal 1: Start smee proxy
npx smee -u https://smee.io/YOUR_CHANNEL -p 3000

# Terminal 2: Start webhook server
npm start
```

Update your GitHub App webhook URL to the smee.io channel URL.

## 🚀 Deployment Options

### Option A: Render.com (Recommended)

1. Create new Web Service on [Render](https://render.com)
2. Connect this repository
3. Set build command: `cd github-app && npm install`
4. Set start command: `cd github-app && npm start`
5. Add environment variables from `.env`
6. Deploy!
7. Update GitHub App webhook URL to your Render URL + `/webhook`

### Option B: Railway.app

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### Option C: Replit

1. Import this repository to Replit
2. Add secrets (environment variables)
3. Run `npm start`
4. Use Replit URL + `/webhook` for GitHub App

## 🎯 Current Automation Features

### Push Events
- **Auto-sync documentation**: When apex-command-center updates, automatically propagates changes to:
  - HCHS_SUPERLUMINAL_CASE_MATRIX
  - SUPERLUMINAL_CASE_MATRIX

### Pull Request Events
- **Auto-comment**: Welcomes contributors and initiates automated checks
- **Status tracking**: Logs PR lifecycle events

### Issue Events
- **Auto-labeling**: Intelligently labels issues based on keywords:
  - `documentation` for doc-related issues
  - `bug` for error reports
  - `enhancement` for feature requests

### Release Events
- **Release notifications**: Logs and can trigger cross-repo updates

## 🔧 Customization

Edit `webhook-server.js` to add custom automation:

```javascript
// Example: Add custom sync rules
if (repo === 'GlacierEQ/FILEBOSS' && branch === 'main') {
  await customWorkflow(payload.installation.id);
}
```

## 📊 Testing Your Setup

```bash
# Test authentication
node test-auth.js

# Monitor webhook deliveries
# Go to: https://github.com/settings/apps/hchscasey-github-integration/advanced
```

## 🔐 Security Notes

- Private key is stored locally/in environment variables (never commit)
- Webhook secret verifies all incoming requests
- Installation tokens expire after 1 hour (auto-refreshed)
- SSL verification enabled on all webhook deliveries

## 🌐 Webhook Events Subscribed

Configure in GitHub App settings which events to receive:
- Push
- Pull requests
- Issues
- Releases
- Repository changes

## 📝 Logs

Monitor real-time logs:
```bash
tail -f webhook.log
```

## 🆘 Troubleshooting

**Webhook not receiving events?**
1. Check Recent Deliveries in app settings
2. Verify webhook URL is publicly accessible
3. Confirm signature verification passes

**Authentication errors?**
1. Verify private key matches the one in GitHub settings
2. Check APP_ID is correct (1395110)
3. Ensure installation exists on target repos

## 🔗 Resources

- [GitHub Apps Documentation](https://docs.github.com/en/apps)
- [Webhook Events Guide](https://docs.github.com/en/webhooks)
- [Octokit.js Documentation](https://octokit.github.io/rest.js/)

---

**Built for orchestrating documentation across the GlacierEQ ecosystem** 🌊❄️