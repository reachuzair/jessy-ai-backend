import User from "../models/user.model";
import { Request, Response } from "express";
import logger from "../config/logger";
import { sendResponse } from "../utils/res";
import { generateAccessToken, generateRefreshToken } from "../utils/jwt";

export interface IUserRequest extends Request {
  user?: {
    id: string;
    email: string;
    role: string;
  };
}

export const signup = async (
  req: IUserRequest,
  res: Response
): Promise<void> => {
  try {
    const { email, password } = req.body;
    if (!email || !password) {
      sendResponse(res, 400, false, "Email and password are required");
      return;
    }
    const existingUser = await User.findOne({ where: { email } });
    if (existingUser) {
      sendResponse(res, 400, false, "User already exists with this email");
      return;
    }
    const user = await User.create({
      email,
      password,
      role: "user",
    });
    const userResponse = {
      id: user.id,
      email: user.email,
      role: user.role,
    };
    sendResponse(res, 201, true, "User created successfully", userResponse);
  } catch (error) {
    logger.error("Error creating user:", error);
    sendResponse(res, 500, false, "Error creating user");
  }
};

export const signin = async (
  req: IUserRequest,
  res: Response
): Promise<void> => {
  try {
    const { email, password } = req.body;
    if (!email || !password) {
      sendResponse(res, 400, false, "Email and password are required");
      return;
    }
    const user = await User.findOne({ where: { email } });
    if (!user) {
      sendResponse(res, 404, false, "User not found");
      return;
    }
    const isPasswordValid = await user.comparePassword(password);
    if (!isPasswordValid) {
      sendResponse(res, 403, false, "Invalid credentials");
      return;
    }
    const accessToken = generateAccessToken(user);
    const refreshToken = generateRefreshToken(user);
    res.cookie("access_token", accessToken, {
      httpOnly: true,
      secure: process.env["NODE_ENV"] === "production",
      maxAge: 6 * 60 * 60 * 1000,
      sameSite: "strict",
    });
    res.cookie("refresh_token", refreshToken, {
      httpOnly: true,
      secure: process.env["NODE_ENV"] === "production",
      maxAge: 7 * 24 * 60 * 60 * 1000,
      sameSite: "strict",
    });
    const userResponse = {
      id: user.id,
      name: user.name,
      email: user.email,
      role: user.role,
    };
    sendResponse(res, 200, true, "Sign-in successful", userResponse);
  } catch (error) {
    logger.error("Error signing in:", error);
    sendResponse(res, 500, false, "Error signing in");
  }
};
