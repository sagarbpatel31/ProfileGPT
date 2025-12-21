#!/bin/bash

# ProfileGPT Vercel Environment Variables Setup
echo "🔧 Setting up Vercel environment variables for ProfileGPT"
echo ""
echo "Please get the following values from your Supabase project:"
echo "1. Go to https://supabase.com/dashboard"
echo "2. Open your project"
echo "3. Go to Settings → API"
echo ""

# Add NEXT_PUBLIC_SUPABASE_URL
echo "📝 Adding NEXT_PUBLIC_SUPABASE_URL..."
echo "Please enter your Supabase Project URL (e.g., https://your-project.supabase.co):"
read -r SUPABASE_URL
npx vercel env add NEXT_PUBLIC_SUPABASE_URL production <<< "$SUPABASE_URL"
npx vercel env add NEXT_PUBLIC_SUPABASE_URL preview <<< "$SUPABASE_URL"
npx vercel env add NEXT_PUBLIC_SUPABASE_URL development <<< "$SUPABASE_URL"

echo ""

# Add SUPABASE_SERVICE_ROLE_KEY
echo "🔐 Adding SUPABASE_SERVICE_ROLE_KEY..."
echo "Please enter your Supabase Service Role Secret Key (starts with 'eyJ'):"
read -r SERVICE_KEY
npx vercel env add SUPABASE_SERVICE_ROLE_KEY production <<< "$SERVICE_KEY"
npx vercel env add SUPABASE_SERVICE_ROLE_KEY preview <<< "$SERVICE_KEY"
npx vercel env add SUPABASE_SERVICE_ROLE_KEY development <<< "$SERVICE_KEY"

echo ""
echo "✅ Environment variables added successfully!"
echo ""
echo "🚀 Now redeploy your application:"
echo "   npx vercel --prod"
echo ""
echo "📋 Test the integration:"
echo "   1. Visit https://profile-gpt.vercel.app"
echo "   2. Try uploading a document"
echo "   3. Ask questions about the document"