#!/bin/bash

# Script to revert the OR conditions in query templates

echo "Reverting OR conditions in queryTemplates.ts..."

# Use sed to replace all occurrences of the OR pattern back to simple ILIKE
sed -i 's/WHERE (tags_policy_area ILIKE \$1 OR summary ILIKE \$1)/WHERE tags_policy_area ILIKE $1/g' \
  ../sql-engine/src/services/queryTemplates.ts

# Also fix the params that use $3 instead of $1 in some places
sed -i 's/WHERE (tags_policy_area ILIKE \$3 OR summary ILIKE \$3)/WHERE tags_policy_area ILIKE $3/g' \
  ../sql-engine/src/services/queryTemplates.ts

# And fix the one with $4
sed -i 's/WHERE (tags_policy_area ILIKE \$4 OR summary ILIKE \$4)/WHERE tags_policy_area ILIKE $4/g' \
  ../sql-engine/src/services/queryTemplates.ts

echo "Done! Check the changes:"
grep -n "OR summary" ../sql-engine/src/services/queryTemplates.ts || echo "No OR conditions found - good!"

echo
echo "Also reverting nlToSql.ts..."
sed -i 's/WHERE (tags_policy_area ILIKE \$1 OR summary ILIKE \$1)/WHERE tags_policy_area ILIKE $1/g' \
  ../sql-engine/src/services/nlToSql.ts

echo "Done!"
