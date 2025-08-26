import express from "express";
import helmet from "helmet";
import compression from "compression";
import morgan from "morgan";
import dotenv from "dotenv";
import cookieParser from "cookie-parser";
import { rateLimit } from "./middlewares/rateLimit";
import logger from "./config/logger";
import { initializeDatabase, closeDatabase } from "./config/db";
import routes from "./routes/index";
import corsMiddleware from "./config/cors";

dotenv.config();
const app = express();

// Middlewares
app.use(corsMiddleware);
app.use(helmet());
app.use(compression());
app.use(
  morgan("combined", {
    stream: { write: (message) => logger.info(message.trim()) },
  })
);
app.use(express.json());
app.use(cookieParser(process.env["JWT_SECRET"]));
app.use(rateLimit);

// Routes
app.use("/", routes);
app.use((_req, res) => {
  res.status(404).json({
    success: false,
    message: "Route not found.",
  });
});
app.get("/", (_req, res) => {
  res.status(200).json({ message: "Server working" });
});

// Database connection
initializeDatabase();

// Start the server
const PORT = process.env["PORT"] || 5000;
app.listen(PORT, () => {
  try {
    logger.info(`Server running on port ${PORT}`);
  } catch (error) {
    logger.error("Error starting server:", error);
  }
});

// Graceful shutdown
const gracefulShutdown = () => {
  logger.info("Server shutting down...");
  closeDatabase();
  logger.info("Disconnected from PostgreSQL");
  process.exit(0);
};

process.on("SIGTERM", gracefulShutdown);
process.on("SIGINT", gracefulShutdown);
process.on("unhandledRejection", (error) => {
  logger.error("Unhandled Rejection:", error);
  process.exit(1);
});
process.on("uncaughtException", (error) => {
  logger.error("Uncaught Exception:", error);
  process.exit(1);
});
