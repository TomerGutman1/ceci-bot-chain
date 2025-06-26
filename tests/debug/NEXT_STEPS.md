# Next Steps - Debug Plan

## 1. Run the tests to check current status
```bash
cd /root/ceci-ai
cd tests
chmod +x test_improvements_quick.sh
./test_improvements_quick.sh
```

## 2. If Date normalization still fails:
- Run debug script: `./debug/test_date_normalization.sh`
- Check if the DECISIONS_BY_HEBREW_MONTH template is being matched

## 3. If Limit extraction still fails:
- Run debug script: `./debug/test_limit_extraction.sh`
- Check the template matching output

## 4. If Confidence gates still fail:
- Run debug script: `./debug/test_template_matching.sh`
- Check if the isUnclearQuery function is working

## 5. For Government filter issue:
- Need to check the GPT prompt to ensure it doesn't default to government 37
- Look for where government_number = '37' is added unnecessarily

## Remember:
- After each change, rebuild the sql-engine:
```bash
cd /root/ceci-ai
docker compose up -d --build sql-engine
```
