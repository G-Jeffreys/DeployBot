#!/usr/bin/env node

/**
 * Setup script to prepare embedded Python runtime for packaging
 * This script:
 * 1. Copies the portable Python distribution to python_runtime/
 * 2. Installs our backend dependencies into the embedded Python
 * 3. Verifies the installation works
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('🐍 [SETUP] Setting up embedded Python runtime for DeployBot packaging...');

// Paths
const sourceDir = path.join(__dirname, '../node_modules/@bjia56/portable-python-3.12');
const targetDir = path.join(__dirname, '../python_runtime');
const requirementsFile = path.join(__dirname, '../requirements.txt');

// Find the actual Python distribution directory (it varies by platform)
let pythonDistDir;
const contents = fs.readdirSync(sourceDir);
for (const item of contents) {
  if (item.startsWith('python-headless-') && fs.statSync(path.join(sourceDir, item)).isDirectory()) {
    pythonDistDir = path.join(sourceDir, item);
    console.log(`📦 [SETUP] Found Python distribution: ${item}`);
    break;
  }
}

if (!pythonDistDir) {
  console.error('❌ [SETUP] Could not find Python distribution directory');
  process.exit(1);
}

// Clean and recreate target directory
console.log('🧹 [SETUP] Cleaning target directory...');
if (fs.existsSync(targetDir)) {
  fs.rmSync(targetDir, { recursive: true, force: true });
}
fs.mkdirSync(targetDir, { recursive: true });

// Copy Python distribution
console.log('📁 [SETUP] Copying Python distribution...');
function copyRecursiveSync(src, dest) {
  const exists = fs.existsSync(src);
  const stats = exists && fs.statSync(src);
  const isDirectory = exists && stats.isDirectory();
  
  if (isDirectory) {
    if (!fs.existsSync(dest)) {
      fs.mkdirSync(dest);
    }
    fs.readdirSync(src).forEach(childItemName => {
      copyRecursiveSync(
        path.join(src, childItemName),
        path.join(dest, childItemName)
      );
    });
  } else {
    fs.copyFileSync(src, dest);
    // Preserve executable permissions
    if (stats.mode & parseInt('111', 8)) {
      fs.chmodSync(dest, stats.mode);
    }
  }
}

copyRecursiveSync(pythonDistDir, targetDir);
console.log('✅ [SETUP] Python distribution copied successfully');

// Determine Python executable path
const pythonExe = process.platform === 'win32' 
  ? path.join(targetDir, 'python.exe')
  : path.join(targetDir, 'bin', 'python3');

// Verify Python works
console.log('🔍 [SETUP] Verifying Python installation...');
try {
  const pythonVersion = execSync(`"${pythonExe}" --version`, { encoding: 'utf8' });
  console.log(`✅ [SETUP] Python working: ${pythonVersion.trim()}`);
} catch (error) {
  console.error('❌ [SETUP] Python verification failed:', error.message);
  process.exit(1);
}

// Install pip dependencies
if (fs.existsSync(requirementsFile)) {
  console.log('📦 [SETUP] Installing Python dependencies...');
  try {
    // First upgrade pip to latest version
    console.log('🔧 [SETUP] Upgrading pip...');
    execSync(`"${pythonExe}" -m pip install --upgrade pip`, { 
      stdio: 'inherit',
      cwd: __dirname 
    });
    
    // Install our requirements
    console.log('📋 [SETUP] Installing requirements.txt...');
    execSync(`"${pythonExe}" -m pip install -r "${requirementsFile}"`, { 
      stdio: 'inherit',
      cwd: __dirname 
    });
    
    console.log('✅ [SETUP] Dependencies installed successfully');
  } catch (error) {
    console.error('❌ [SETUP] Dependency installation failed:', error.message);
    process.exit(1);
  }
} else {
  console.log('⚠️ [SETUP] No requirements.txt found, skipping dependency installation');
}

// Test that our backend dependencies are available
console.log('🧪 [SETUP] Testing backend dependencies...');
const testDependencies = [
  'websockets',
  'openai', 
  'langchain',
  'langchain_openai',
  'langgraph'
];

for (const dep of testDependencies) {
  try {
    execSync(`"${pythonExe}" -c "import ${dep}; print('${dep}: OK')"`, { 
      encoding: 'utf8',
      stdio: 'pipe'
    });
    console.log(`✅ [SETUP] ${dep}: Available`);
  } catch (error) {
    console.log(`⚠️ [SETUP] ${dep}: Not available (${error.message.split('\n')[0]})`);
  }
}

// Create a simple test script to verify everything works
const testScript = `
import sys
import os
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Python path: {sys.path}")

# Test key dependencies
try:
    import websockets
    print("✅ websockets: OK")
except ImportError as e:
    print(f"❌ websockets: {e}")

try:
    import openai
    print("✅ openai: OK") 
except ImportError as e:
    print(f"❌ openai: {e}")

try:
    import langchain
    print("✅ langchain: OK")
except ImportError as e:
    print(f"❌ langchain: {e}")

print("🎉 Embedded Python runtime test completed!")
`;

const testScriptPath = path.join(targetDir, 'test_runtime.py');
fs.writeFileSync(testScriptPath, testScript);

console.log('🧪 [SETUP] Running comprehensive runtime test...');
try {
  execSync(`"${pythonExe}" "${testScriptPath}"`, { stdio: 'inherit' });
  console.log('✅ [SETUP] Runtime test passed!');
} catch (error) {
  console.error('❌ [SETUP] Runtime test failed:', error.message);
  process.exit(1);
}

// Clean up test script
fs.unlinkSync(testScriptPath);

console.log('🎉 [SETUP] Embedded Python runtime setup completed successfully!');
console.log(`📍 [SETUP] Runtime location: ${targetDir}`);
console.log(`🐍 [SETUP] Python executable: ${pythonExe}`);
console.log('');
console.log('Next steps:');
console.log('1. Run: npm run build:electron');
console.log('2. Test the packaged app on a machine without Python installed'); 