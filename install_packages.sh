#!/bin/bash
echo "📦 Installing recommended packages..."

cd apps/web

pnpm add react-hook-form zod @hookform/resolvers react-hot-toast framer-motion react-icons

echo "✅ All packages installed!"
