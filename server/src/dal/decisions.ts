import createHttpError from 'http-errors'
import { supabase } from './supabaseClient'

export const upsertDecision = async (
  decisionNumber: string,
  decisionDate: string,
  decisionText: string,
): Promise<[Error | undefined]> => {
  console.log(`Upserting decision with ID: ${decisionNumber}|${decisionDate}`)

  const { error } = await supabase
    .from('Decisions')
    .upsert({ num: decisionNumber, date: decisionDate, text: decisionText })

  if (error) return [createHttpError(500, error.message)]

  console.log(`Decision ${decisionNumber}|${decisionDate} saved successfully`)
  return [undefined]
}
