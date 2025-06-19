import { ErrorRequestHandler } from "express"

export const errorHandler: ErrorRequestHandler = (err, _req, res, next) => {
    
    if (res.headersSent) {
        if (err) console.log(`res.headersSent. "Error" was: ${err}`)
        return next(err)
    }
    
    console.error(err);
    res.status(err.status || 500).send(err.message || 'Internal Server Error')
}