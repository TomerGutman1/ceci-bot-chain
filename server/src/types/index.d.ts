import type { Database as DB } from './database.types'

declare global {
    type Database = DB
    type Evaluation = Database['public']['Tables']['Evaluations']['Row']
    type Decision = Database['public']['Tables']['Decisions']['Row']
}