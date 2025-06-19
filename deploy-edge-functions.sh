#!/bin/bash

# Deploy Supabase Edge Functions

echo "Deploying chat-completion edge function..."

# Make sure you're logged in to Supabase
supabase functions deploy chat-completion

# Set the OpenAI API key secret
echo "Setting OpenAI API key..."
supabase secrets set OPENAI_API_KEY=$OPENAI_API_KEY

echo "Deployment complete!"
