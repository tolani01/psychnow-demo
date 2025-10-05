# PsychNow Demo Deployment Script
# Run this script to deploy the frontend to Firebase

Write-Host "🚀 Starting PsychNow Demo Deployment..." -ForegroundColor Green

# Step 1: Build the project
Write-Host "📦 Building frontend..." -ForegroundColor Yellow
npm run build

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Build successful!" -ForegroundColor Green

# Step 2: Check if Firebase is logged in
Write-Host "🔐 Checking Firebase authentication..." -ForegroundColor Yellow
firebase projects:list > $null 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Firebase not authenticated. Please run:" -ForegroundColor Yellow
    Write-Host "   firebase login" -ForegroundColor Cyan
    Write-Host "   Then run this script again." -ForegroundColor Cyan
    exit 1
}

# Step 3: Deploy to Firebase
Write-Host "🌐 Deploying to Firebase..." -ForegroundColor Yellow
firebase deploy --only hosting

if ($LASTEXITCODE -eq 0) {
    Write-Host "🎉 Deployment successful!" -ForegroundColor Green
    Write-Host "🌐 Your app is available at: https://psychnow-demo.web.app" -ForegroundColor Cyan
} else {
    Write-Host "❌ Deployment failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✨ Deployment complete!" -ForegroundColor Green
