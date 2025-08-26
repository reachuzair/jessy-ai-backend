import jwt from "jsonwebtoken";
import { IUser } from "../models/user.model";

export const generateAccessToken = (user: IUser): string => {
  return jwt.sign(
    {
      id: user.id,
      email: user.email,
      role: user.role,
    },
    process.env["JWT_SECRET"] as string,
    {
      expiresIn: "6h",
    }
  );
};

export const generateRefreshToken = (user: IUser): string => {
  return jwt.sign(
    {
      id: user.id,
      email: user.email,
    },
    process.env["JWT_SECRET"] as string,
    {
      expiresIn: "7d",
    }
  );
};

export const verifyToken = (token: string) => {
  return jwt.verify(token, process.env["JWT_SECRET"] as string);
};
