// Test authentication and list installations
require('dotenv').config();
const { Octokit } = require('@octokit/rest');
const { createAppAuth } = require('@octokit/auth-app');
const fs = require('fs');

async function testAuth() {
  const APP_ID = '1395110';
  const PRIVATE_KEY = fs.readFileSync(process.env.PRIVATE_KEY_PATH);

  const octokit = new Octokit({
    authStrategy: createAppAuth,
    auth: {
      appId: APP_ID,
      privateKey: PRIVATE_KEY,
    }
  });

  try {
    console.log('🔐 Testing GitHub App authentication...');
    
    // Get app details
    const { data: app } = await octokit.apps.getAuthenticated();
    console.log('✅ App authenticated:', app.name);
    console.log('   App ID:', app.id);
    console.log('   Owner:', app.owner.login);

    // List installations
    const { data: installations } = await octokit.apps.listInstallations();
    console.log('\n📦 Installations:', installations.length);
    
    for (const installation of installations) {
      console.log(`\n   Installation ID: ${installation.id}`);
      console.log(`   Account: ${installation.account.login}`);
      console.log(`   Type: ${installation.target_type}`);
      
      // Get installation token
      const { token } = await octokit.auth({
        type: 'installation',
        installationId: installation.id
      });

      const installationOctokit = new Octokit({ auth: token });
      const { data: repos } = await installationOctokit.apps.listReposAccessibleToInstallation();
      
      console.log(`   Repositories (${repos.total_count}):`);
      repos.repositories.forEach(repo => {
        console.log(`     - ${repo.full_name}`);
      });
    }

    console.log('\n✅ Authentication test completed successfully!');
  } catch (error) {
    console.error('❌ Authentication failed:', error.message);
    process.exit(1);
  }
}

testAuth();