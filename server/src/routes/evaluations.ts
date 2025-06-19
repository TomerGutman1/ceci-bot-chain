// TODO: remove this file and use the code from the chat controller

import { Router, Request, Response, NextFunction } from 'express'
import createHttpError from 'http-errors'

// import {
//   // evaluateDecision,
//   saveEvalAndDecisionInDB,
// } from '../controllers/evaluations'
import { checkForExistingEvals } from '../dal/evaluations'
import { Message } from 'openai/resources/beta/threads/messages'

const router = Router()

// POST /api/evaluations/
// a special route used for @ai-sdk/react. stream response only via @ai-sdk/openai
router.post('/', async (req: Request, res: Response, next: NextFunction) => {
  const { decisionNumber, decisionDate, messages } = req.body as {
    decisionNumber: string
    decisionDate: string
    messages: Message[]
  }

  if (
    typeof decisionNumber !== 'number' ||
    isNaN(decisionNumber) ||
    !decisionDate ||
    !messages?.length
  ) {
    next(createHttpError(400, 'Missing decision number or decision text'))
    return
  }

  if (messages[messages.length - 1]?.role !== 'user') {
    next(createHttpError(400, 'Last message must be from user'))
    return
  }

  // const decisionText = messages[messages.length - 1].content
  // const streamTextResult = evaluateDecision(decisionText)

  try {
    // Stream the response to the client
    // streamTextResult.pipeDataStreamToResponse(res)

    // const evaluationText = await streamToText(streamTextResult)
    // const [dbError] = await saveEvalAndDecisionInDB(
    //   evaluationText,
    //   decisionNumber,
    //   decisionDate,
    //   decisionText,
    // )

    // if (dbError) {
    //   next(dbError)
    //   return
    // }

    return
  } catch (error: Error | unknown) {
    if (!res.headersSent) {
      console.error('Error streaming response:', error)
      next(createHttpError(500, `Error streaming response: ${error}`))
    }
  }
})

// GET /api/evaluations/:decisionNumber
router.get(
  '/:decisionNumber',
  async (req: Request, res: Response, next: NextFunction) => {
    const decisionNumber = req.params.decisionNumber
    const decisionDate = req.params.decisionDate

    if (!decisionNumber || !decisionDate) {
      next(createHttpError(400, 'Invalid or missing decision number'))
      return
    }

    const [existingEvalCheckErr, existingEval] = await checkForExistingEvals(
      decisionNumber,
      decisionDate,
    )

    if (existingEvalCheckErr) {
      next(existingEvalCheckErr)
      return
    }

    res.json({ evaluation: existingEval })
  },
)

export default router
