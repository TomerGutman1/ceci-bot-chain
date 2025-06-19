import createHttpError from "http-errors";
import { supabase } from "./supabaseClient";
// import { getDecisionId } from "../utils/decisions";
// import { upsertDecision } from "./decisions";

export const checkForExistingEvals = async (
  decisionNumber: string,
  decisionDate: string,
): Promise<[Error] | [undefined, string | null]> => {
  const { data, error } = await supabase
    .from('Evaluations')
    .select('eval')
    .eq('decision_num', decisionNumber)
    .eq('decision_date', decisionDate)
    .limit(2)

  if (error) return [error]
  if (data.length > 1)
    return [createHttpError(500, `More than one existing evaluation: ${data}`)]

  return [undefined, data.length === 1 ? data[0].eval : null]
}

export const createEval = async (
  decisionNumber: string,
  decisionDate: string,
  evalText: string,
): Promise<[Error | undefined]> => {
  const { error } = await supabase.from('Evaluations').insert({
    decision_num: decisionNumber,
    decision_date: decisionDate,
    eval: evalText,
  })

  if (error) return [createHttpError(500, error.message)]

  console.log(
    `Evaluation for decision number ${decisionNumber}|${decisionDate} saved successfully`,
  )
  return [undefined];
};

// TODO: adapt to new schema with decision_date
// export const saveEvalAndDecisionInDB = async (
//   evaluationText: string,
//   decisionNumber: number,
//   decisionText: string
// ): Promise<[Error | undefined]> => {
//   const [decisionUpsertErr] = await upsertDecision(decisionNumber, decisionText);
//   if (decisionUpsertErr) return [decisionUpsertErr];

//   const [evalInsertErr] = await createEval(decisionNumber, evaluationText);
//   if (evalInsertErr) return [evalInsertErr];

//   console.log(`Evaluation and decision number ${decisionNumber} saved successfully`);
//   return [undefined];
// };
