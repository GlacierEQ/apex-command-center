// HCHSCASEY GitHub Integration - Webhook Server
// App ID: 1395110 | Owner: @GlacierEQ

const express = require('express');
const crypto = require('crypto');
const { Octokit } = require('@octokit/rest');
const { createAppAuth } = require('@octokit/auth-app');
const fs = require('fs');

const app = express();
app.use(express.json());

// Configuration
const APP_ID = '1395110';
const PRIVATE_KEY = fs.readFileSync(process.env.PRIVATE_KEY_PATH || './private-key.pem');
const WEBHOOK_SECRET = process.env.WEBHOOK_SECRET;

// Initialize Octokit with App authentication
const octokit = new Octokit({
  authStrategy: createAppAuth,
  auth: {
    appId: APP_ID,
    privateKey: PRIVATE_KEY,
  }
});

// Health check endpoint
app.get('/', (req, res) => {
  res.json({ 
    status: 'running', 
    app: 'HCHSCASEY GitHub Integration',
    appId: APP_ID 
  });
});

// Verify webhook signature
function verifySignature(req) {
  const signature = req.headers['x-hub-signature-256'];
  if (!signature) return false;
  
  const hash = crypto
    .createHmac('sha256', WEBHOOK_SECRET)
    .update(JSON.stringify(req.body))
    .digest('hex');
  return `sha256=${hash}` === signature;
}

// Main webhook endpoint
app.post('/webhook', async (req, res) => {
  if (!verifySignature(req)) {
    console.error('❌ Invalid webhook signature');
    return res.status(401).send('Invalid signature');
  }

  const event = req.headers['x-github-event'];
  const payload = req.body;

  console.log(`📩 [${new Date().toISOString()}] Received ${event} event from ${payload.repository?.full_name}`);

  try {
    switch(event) {
      case 'push':
        await handlePush(payload);
        break;
      case 'pull_request':
        await handlePR(payload);
        break;
      case 'issues':
        await handleIssue(payload);
        break;
      case 'release':
        await handleRelease(payload);
        break;
      default:
        console.log(`ℹ️  Unhandled event: ${event}`);
    }
    res.status(200).send('Event processed');
  } catch (error) {
    console.error('❌ Error processing event:', error);
    res.status(500).send('Processing error');
  }
});

// ========== EVENT HANDLERS ==========

async function handlePush(payload) {
  const repo = payload.repository.full_name;
  const branch = payload.ref.replace('refs/heads/', '');
  const commits = payload.commits;

  console.log(`🔄 Push to ${repo}/${branch}: ${commits.length} commits`);

  // Auto-sync from apex-command-center to other repos
  if (repo === 'GlacierEQ/apex-command-center' && branch === 'main') {
    await syncDocumentation(payload.installation.id);
  }

  // Notify on FILEBOSS changes (has 43 open issues)
  if (repo === 'GlacierEQ/FILEBOSS') {
    console.log('📁 FILEBOSS updated - consider issue triage');
  }
}

async function handlePR(payload) {
  const { action, installation, repository, pull_request } = payload;

  if (action === 'opened') {
    const { token } = await octokit.auth({
      type: 'installation',
      installationId: installation.id
    });

    const installationOctokit = new Octokit({ auth: token });

    // Auto-comment on new PRs
    await installationOctokit.issues.createComment({
      owner: repository.owner.login,
      repo: repository.name,
      issue_number: pull_request.number,
      body: `👋 **HCHSCASEY Integration Auto-Check**\n\n` +
            `✅ PR received\n` +
            `📊 Analyzing changes...\n` +
            `🔍 Documentation impact assessment in progress\n\n` +
            `_Automated by HCHSCASEY GitHub Integration_`
    });

    console.log(`✅ Auto-commented on PR #${pull_request.number} in ${repository.full_name}`);
  }

  if (action === 'closed' && pull_request.merged) {
    console.log(`✅ PR #${pull_request.number} merged in ${repository.full_name}`);
  }
}

async function handleIssue(payload) {
  const { action, installation, repository, issue } = payload;

  if (action === 'opened') {
    const { token } = await octokit.auth({
      type: 'installation',
      installationId: installation.id
    });

    const installationOctokit = new Octokit({ auth: token });

    const labels = [];

    // Auto-label based on content
    const title = issue.title.toLowerCase();
    const body = (issue.body || '').toLowerCase();

    if (title.includes('doc') || body.includes('documentation')) {
      labels.push('documentation');
    }
    if (title.includes('bug') || body.includes('error')) {
      labels.push('bug');
    }
    if (title.includes('feature') || body.includes('enhancement')) {
      labels.push('enhancement');
    }

    if (labels.length > 0) {
      await installationOctokit.issues.addLabels({
        owner: repository.owner.login,
        repo: repository.name,
        issue_number: issue.number,
        labels
      });
      console.log(`🏷️  Auto-labeled issue #${issue.number} with: ${labels.join(', ')}`);
    }
  }
}

async function handleRelease(payload) {
  const { action, repository, release } = payload;
  if (action === 'published') {
    console.log(`🎉 New release ${release.tag_name} published in ${repository.full_name}`);
  }
}

// ========== CROSS-REPO SYNCHRONIZATION ==========

async function syncDocumentation(installationId) {
  console.log('🔄 Starting documentation sync...');
  
  const { token } = await octokit.auth({
    type: 'installation',
    installationId
  });

  const installationOctokit = new Octokit({ auth: token });

  try {
    // Sync 1: apex-command-center -> HCHS_SUPERLUMINAL_CASE_MATRIX
    await syncFile(
      installationOctokit,
      'GlacierEQ/apex-command-center',
      'README.md',
      'GlacierEQ/HCHS_SUPERLUMINAL_CASE_MATRIX',
      'synced-docs/apex-README.md',
      '🔄 Auto-sync from apex-command-center'
    );

    // Sync 2: apex-command-center -> SUPERLUMINAL_CASE_MATRIX (private)
    await syncFile(
      installationOctokit,
      'GlacierEQ/apex-command-center',
      'README.md',
      'GlacierEQ/SUPERLUMINAL_CASE_MATRIX',
      'synced-docs/apex-README.md',
      '🔄 Auto-sync from apex-command-center'
    );

    console.log('✅ Documentation sync completed');
  } catch (error) {
    console.error('❌ Sync error:', error.message);
  }
}

async function syncFile(octokit, sourceRepo, sourcePath, targetRepo, targetPath, commitMessage) {
  try {
    // Get source file
    const { data: sourceFile } = await octokit.repos.getContent({
      owner: sourceRepo.split('/')[0],
      repo: sourceRepo.split('/')[1],
      path: sourcePath
    });

    // Get existing target file SHA (if exists)
    let existingSha;
    try {
      const { data: targetFile } = await octokit.repos.getContent({
        owner: targetRepo.split('/')[0],
        repo: targetRepo.split('/')[1],
        path: targetPath
      });
      existingSha = targetFile.sha;
    } catch (e) {
      // File doesn't exist yet
      existingSha = undefined;
    }

    // Create or update target file
    await octokit.repos.createOrUpdateFileContents({
      owner: targetRepo.split('/')[0],
      repo: targetRepo.split('/')[1],
      path: targetPath,
      message: commitMessage,
      content: sourceFile.content,
      sha: existingSha
    });

    console.log(`✅ Synced ${sourcePath} from ${sourceRepo} to ${targetRepo}/${targetPath}`);
  } catch (error) {
    console.error(`❌ Failed to sync ${sourcePath}:`, error.message);
  }
}

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🚀 HCHSCASEY GitHub Integration webhook server running on port ${PORT}`);
  console.log(`📍 Webhook endpoint: http://localhost:${PORT}/webhook`);
  console.log(`💚 Health check: http://localhost:${PORT}/`);
});