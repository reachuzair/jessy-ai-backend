import { Request, Response, NextFunction } from "express";
import jwt from "jsonwebtoken";
import { sendResponse } from "../utils/res";
import { verifyToken, generateAccessToken } from "../utils/jwt";
import User from "../models/user.model";
import logger from "../config/logger";

interface IUserRequest extends Request {
  user?: {
    id: string;
    email: string;
    role: string;
  };
}

const handleTokenRefresh = async (
  refreshToken: string,
  res: Response
): Promise<{ success: boolean; user?: any }> => {
  try {
    const refreshDecoded = verifyToken(refreshToken) as {
      id: string;
      email: string;
    };
    const user = await User.findByPk(refreshDecoded.id);
    if (!user) {
      sendResponse(res, 401, false, "User not found. Please login again.");
      return { success: false };
    }
    const newAccessToken = generateAccessToken(user);
    res.cookie("access_token", newAccessToken, {
      httpOnly: true,
      secure: process.env["NODE_ENV"] === "production",
      maxAge: 6 * 60 * 60 * 1000,
      sameSite: "strict",
    });
    return { success: true, user };
  } catch (refreshError) {
    logger.error("Refresh token is also expired", refreshError);
    res.clearCookie("access_token");
    res.clearCookie("refresh_token");
    sendResponse(res, 401, false, "Session expired. Please login again.");
    return { success: false };
  }
};

export const auth = async (
  req: IUserRequest,
  res: Response,
  next: NextFunction
): Promise<void> => {
  const accessToken = req.cookies?.["access_token"];
  const refreshToken = req.cookies?.["refresh_token"];
  if (!accessToken && !refreshToken) {
    sendResponse(res, 401, false, "Unauthorized: No tokens provided");
    return;
  }
  try {
    if (accessToken) {
      const decoded = verifyToken(accessToken) as {
        id: string;
        email: string;
        role: string;
      };
      if (decoded?.id) {
        req.user = {
          id: decoded.id,
          email: decoded.email,
          role: decoded.role,
        };
        next();
        return;
      }
    }
  } catch (error) {
    if (
      error instanceof jwt.TokenExpiredError ||
      error instanceof jwt.JsonWebTokenError
    ) {
      if (!refreshToken) {
        sendResponse(
          res,
          401,
          false,
          "Access token expired. Please login again."
        );
        return;
      }
      const { success, user } = await handleTokenRefresh(refreshToken, res);
      if (success && user) {
        req.user = {
          id: user.id,
          email: user.email,
          role: user.role || "user",
        };
        next();
        return;
      }
    }
  }
  sendResponse(res, 401, false, "Unauthorized: Invalid token");
};
