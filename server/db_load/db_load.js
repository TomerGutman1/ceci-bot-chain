const xlsx = require('xlsx')
const { createClient } = require('@supabase/supabase-js')
const dotenv = require('dotenv')

dotenv.config({ path: '../.env.production' })

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_KEY,
)

async function loadExcelToSupabase(filePath, tableName) {
  try {
    const workbook = xlsx.readFile(filePath)
    const sheetName = workbook.SheetNames[0]
    let data = xlsx.utils.sheet_to_json(workbook.Sheets[sheetName])

    data = data.map((item) => ({
      num: item['Decision Number'],
      date: item['Decision Date'].split('/').reverse().join('-'), // YYYY-MM-DD
      pathname: item['Decision URL'].split('/').slice(-1)[0], // get the last part of the URL
      title: item['Decision Title'],
      content: item['Decision Content'],
      summary: item['Summary'],
      gov_num: parseInt(item['Government Number'].replace(/\D/g, '')), // remove non-digit characters
      prime_minister: item['Government Number'].split(', ')?.[1], // get the second part of the string
      committee: item['Committee'],
      operativity: item['Operativity'] === 'אופרטיבית',
      field: item['Field'],
      offices: item['Offices'],
    }))
    const dedup = {}
    data.forEach((item) => {
      const key = item.num.toString() + '|' + item.date
      if (!dedup[key]) dedup[key] = item
    })
    data = Object.values(dedup)

    for (let i = 0; i < data.length; i += 1000) {
      const chunk = data.slice(i, i + 1000)
      const { error } = await supabase.from(tableName).insert(chunk)

      if (error) {
        console.error('Error inserting chunk:', error)
      } else {
        console.log(`Inserted chunk ${i / 1000 + 1}`)
      }
    }
  } catch (err) {
    console.error('Error loading Excel file:', err)
  }
}

loadExcelToSupabase('./decisions.xlsx', 'Decisions').then()
