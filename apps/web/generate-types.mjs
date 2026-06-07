import { writeFileSync } from 'fs';
import { execSync } from 'child_process';

console.log('📥 Downloading OpenAPI schema from backend...\n');

try {
  // Download OpenAPI schema
  const response = await fetch('http://localhost:8000/openapi.json');
  if (!response.ok) {
    throw new Error(Failed to fetch: );
  }
  
  const schema = await response.json();
  writeFileSync('src/lib/openapi.json', JSON.stringify(schema, null, 2));
  console.log('✅ Schema downloaded to src/lib/openapi.json');
  
  // Generate TypeScript types
  console.log('\n🔧 Generating TypeScript types...');
  execSync('npx openapi-typescript src/lib/openapi.json -o src/lib/api-types.ts', {
    stdio: 'inherit'
  });
  
  console.log('\n✅ Types generated at src/lib/api-types.ts');
  console.log('🎉 Done! You can now import types from "@/lib/api-types"');
  
} catch (error) {
  console.error('❌ Error:', error.message);
  process.exit(1);
}
