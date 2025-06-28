import winston from 'winston';
import path from 'path';
import fs from 'fs';

// Create logs directory if it doesn't exist
const logsDir = path.join(process.cwd(), 'logs');
if (!fs.existsSync(logsDir)) {
  fs.mkdirSync(logsDir);
}

// Create a custom format that includes timestamp and colorizes console output
const customFormat = winston.format.combine(
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
  winston.format.errors({ stack: true }),
  winston.format.splat(),
  winston.format.json()
);

// Console format with colors
const consoleFormat = winston.format.combine(
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
  winston.format.colorize(),
  winston.format.printf(({ level, message, timestamp, ...metadata }) => {
    let msg = `${timestamp} [${level}]: ${message}`;
    if (Object.keys(metadata).length > 0) {
      msg += ` ${JSON.stringify(metadata)}`;
    }
    return msg;
  })
);

// Create logger instance
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'debug',
  format: customFormat,
  transports: [
    // Console transport - always output to console
    new winston.transports.Console({
      format: consoleFormat,
      stderrLevels: ['error'],
      handleExceptions: true,
      handleRejections: true
    }),
    // File transport for all logs
    new winston.transports.File({
      filename: path.join(logsDir, 'app.log'),
      maxsize: 5242880, // 5MB
      maxFiles: 5,
      handleExceptions: true,
      handleRejections: true
    }),
    // Separate file for errors
    new winston.transports.File({
      filename: path.join(logsDir, 'error.log'),
      level: 'error',
      maxsize: 5242880, // 5MB
      maxFiles: 5
    }),
    // Debug file for detailed logging
    new winston.transports.File({
      filename: path.join(logsDir, 'debug.log'),
      level: 'debug',
      maxsize: 10485760, // 10MB
      maxFiles: 3
    })
  ],
  exitOnError: false
});

// Add a stream for Morgan (Express request logging)
export const stream = {
  write: (message: string) => {
    logger.info(message.trim());
  }
};

// Override console methods to use winston
if (process.env.NODE_ENV !== 'test') {
  console.log = (...args: any[]) => logger.info(args.join(' '));
  console.error = (...args: any[]) => logger.error(args.join(' '));
  console.warn = (...args: any[]) => logger.warn(args.join(' '));
  console.info = (...args: any[]) => logger.info(args.join(' '));
  console.debug = (...args: any[]) => logger.debug(args.join(' '));
}

export default logger;
