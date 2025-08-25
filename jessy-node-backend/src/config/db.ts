import { Sequelize } from "sequelize";
import logger from "./logger";

const sequelize = new Sequelize({
  dialect: "postgres",
  host: process.env["DB_HOST"] || "localhost",
  port: parseInt(process.env["DB_PORT"] || "5432"),
  username: process.env["DB_USER"] || "postgres",
  password: process.env["DB_PASSWORD"] || "postgres",
  database: process.env["DB_NAME"] || "jessy_ai",
  logging: false,
  pool: {
    max: 5,
    min: 0,
    acquire: 30000,
    idle: 10000
  },
  define: {
    timestamps: true,
    underscored: true,
    freezeTableName: true
  }
});

const initializeDatabase = async (): Promise<void> => {
  try {
    await sequelize.authenticate();
    logger.info("PostgreSQL database connected successfully");
    
    // Sync all models
    await sequelize.sync({ alter: true });
    logger.info("Database models synchronized");
  } catch (error) {
    logger.error("Database connection failed:", error);
    throw error;
  }
};

const closeDatabase = async (): Promise<void> => {
  try {
    await sequelize.close();
    logger.info("Database connection closed");
  } catch (error) {
    logger.error("Error closing database:", error);
  }
};

export { sequelize, initializeDatabase, closeDatabase };
