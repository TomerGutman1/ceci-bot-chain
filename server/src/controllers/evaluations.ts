import { upsertDecision } from '../dal/decisions'
import { createEval } from '../dal/evaluations'
export const saveEvalAndDecisionInDB = async (
  evaluationText: string,
  decisionNumber: string,
  decisionDate: string,
  decisionText: string,
): Promise<[Error | undefined]> => {
  const [decisionUpsertErr] = await upsertDecision(
    decisionNumber,
    decisionDate,
    decisionText,
  )
  if (decisionUpsertErr) return [decisionUpsertErr]

  const [evalInsertErr] = await createEval(
    decisionNumber,
    decisionDate,
    evaluationText,
  )
  if (evalInsertErr) return [evalInsertErr]

  console.log(
    `Evaluation and decision number ${decisionNumber}|${decisionDate} saved successfully`,
  )
  return [undefined]
}
