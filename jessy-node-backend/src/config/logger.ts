import winston from "winston";
import path from "path";

const logFilePath = path.join(__dirname, "../logs/error.log");

const logger = winston.createLogger({
  level: "info",
  format: winston.format.json(),
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({
      filename: logFilePath,
      level: "error",
      maxsize: 2 * 1024 * 1024,
      maxFiles: 1,
      tailable: true
    })
  ]
});

export default logger;
