#!/bin/bash

# Create backup of current files
echo "Creating backup of current files..."
cp ../sql-engine/src/services/nlToSql.ts ../sql-engine/src/services/nlToSql.ts.backup
cp ../sql-engine/src/services/queryTemplates.ts ../sql-engine/src/services/queryTemplates.ts.backup
cp ../sql-engine/src/services/executor.ts ../sql-engine/src/services/executor.ts.backup

echo "Backup created"

# Now let's check git status to see what changed
echo -e "\nChecking git status..."
cd ..
git status --porcelain | grep -E "(nlToSql|queryTemplates|executor)"

echo -e "\nTo restore files to last commit state, run:"
echo "git checkout -- sql-engine/src/services/nlToSql.ts"
echo "git checkout -- sql-engine/src/services/queryTemplates.ts"
echo "git checkout -- sql-engine/src/services/executor.ts"
