@echo off
echo ====================================================
echo 🧪 Testing New Features  
echo ====================================================

echo.
echo 1️⃣ === TESTING SPECIFIC NUMBER OF DECISIONS ===
echo.

echo 📝 Testing: Request 20 decisions
echo Query: "הבא 20 החלטות"
curl -s -X POST http://localhost:8002/api/process-query -H "Content-Type: application/json" -d "{\"query\": \"הבא 20 החלטות\"}" | findstr /C:"row_count" /C:"error"
echo.

echo 📝 Testing: Request 50 recent decisions  
echo Query: "תן לי 50 החלטות אחרונות"
curl -s -X POST http://localhost:8002/api/process-query -H "Content-Type: application/json" -d "{\"query\": \"תן לי 50 החלטות אחרונות\"}" | findstr /C:"row_count" /C:"error"
echo.

echo 📝 Testing: Display 15 decisions
echo Query: "הצג 15 החלטות"  
curl -s -X POST http://localhost:8002/api/process-query -H "Content-Type: application/json" -d "{\"query\": \"הצג 15 החלטות\"}" | findstr /C:"row_count" /C:"error"
echo.

echo.
echo 2️⃣ === TESTING COUNT BY TOPIC AND YEAR ===
echo.

echo 📝 Testing: Medical decisions in 2022
echo Query: "כמה החלטות בנושא רפואה היו ב2022?"
curl -s -X POST http://localhost:8002/api/process-query -H "Content-Type: application/json" -d "{\"query\": \"כמה החלטות בנושא רפואה היו ב2022?\"}" | findstr /C:"count" /C:"error"
echo.

echo 📝 Testing: Education decisions in 2021  
echo Query: "כמה החלטות בנושא חינוך היו ב2021?"
curl -s -X POST http://localhost:8002/api/process-query -H "Content-Type: application/json" -d "{\"query\": \"כמה החלטות בנושא חינוך היו ב2021?\"}" | findstr /C:"count" /C:"error"
echo.

echo.
echo 3️⃣ === TESTING CONTEXTUAL YEAR QUERY ===
echo.

echo 📝 Testing: Transport decisions in 2022
echo Query: "כמה החלטות בנושא תחבורה היו ב2022?"
curl -s -X POST http://localhost:8002/api/process-query -H "Content-Type: application/json" -d "{\"query\": \"כמה החלטות בנושא תחבורה היו ב2022?\"}" | findstr /C:"count" /C:"error"
echo.

echo 📝 Testing: And in 2021? (contextual)
echo Query: "וב2021?"
curl -s -X POST http://localhost:8002/api/process-query -H "Content-Type: application/json" -d "{\"query\": \"וב2021?\"}" | findstr /C:"count" /C:"error"
echo.

echo.
echo ====================================================
echo 🏁 Tests completed!
echo ====================================================
